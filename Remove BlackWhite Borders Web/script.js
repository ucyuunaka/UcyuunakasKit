document.addEventListener('DOMContentLoaded', () => {
    const imageUpload = document.getElementById('imageUpload');
    const cropButton = document.getElementById('cropButton');
    const originalCanvas = document.getElementById('originalCanvas');
    const croppedCanvas = document.getElementById('croppedCanvas');
    const downloadLink = document.getElementById('downloadLink');
    const borderColorSelect = document.getElementById('borderColor');
    const toleranceInput = document.getElementById('tolerance');
    const fileUploadLabel = document.querySelector('.file-upload-label');
    const originalCanvasContainer = originalCanvas.parentElement;
    const croppedCanvasContainer = croppedCanvas.parentElement;

    const originalCtx = originalCanvas.getContext('2d');
    const croppedCtx = croppedCanvas.getContext('2d');

    const removeExifCheckbox = document.getElementById('removeExif');

    let originalImage = null;
    let originalFileName = 'cropped_image.png';
    const CROP_BUTTON_DEFAULT_TEXT = '<i class="ri-crop-line"></i> 裁剪图片';
    let currentCropParams = null; // 存储当前裁剪参数，用于窗口调整大小时重新调整画布
    let manualCropSelection = null; // 存储用户手动选择的裁剪区域
    let currentCropMode = 'auto'; // 'auto' 或 'manualAuto'

    // 手动裁剪元素
    const cropSelectionOverlay = document.getElementById('cropSelectionOverlay');
    const cropBox = document.getElementById('cropBox');
    let cropHandles = {
        nw: cropBox.querySelector('.nw'),
        ne: cropBox.querySelector('.ne'),
        sw: cropBox.querySelector('.sw'),
        se: cropBox.querySelector('.se'),
        n: cropBox.querySelector('.n'),
        s: cropBox.querySelector('.s'),
        w: cropBox.querySelector('.w'),
        e: cropBox.querySelector('.e'),
    };

    let isDragging = false;
    let isResizing = false;
    let resizeHandle = '';
    let startX, startY, initialCropX, initialCropY, initialCropWidth, initialCropHeight;
    let imageScale = 1; // 显示图像相对于实际图像的缩放比例


    // 状态消息元素
    const statusMessageDiv = document.getElementById('statusMessage');

    // 宽高比建议元素
    const aspectRatioSuggestionDiv = document.getElementById('aspectRatioSuggestion');
    const suggestionTextEl = document.getElementById('suggestionText');
    const confirmRatioCropButton = document.getElementById('confirmRatioCrop');
    const rejectRatioCropButton = document.getElementById('rejectRatioCrop');

    const cropModeRadios = document.querySelectorAll('input[name="cropMode"]');

    let initialCropParams = null; // 存储从初始边框检测的 {x, y, width, height}
    let suggestedAspectRatio = null; // 存储建议的比例对象 {name, value, orientation}

    const COMMON_RATIOS = [
        { name: '16:9 (横向)', value: 16 / 9, orientation: 'landscape' },
        { name: '9:16 (纵向)', value: 9 / 16, orientation: 'portrait' },
        { name: '4:3 (横向)', value: 4 / 3, orientation: 'landscape' },
        { name: '3:4 (纵向)', value: 3 / 4, orientation: 'portrait' },
        { name: '1:1 (方形)', value: 1 / 1, orientation: 'square' },
        { name: '3:2 (横向)', value: 3 / 2, orientation: 'landscape' },
        { name: '2:3 (纵向)', value: 2 / 3, orientation: 'portrait' },
    ];
    const ASPECT_RATIO_TOLERANCE = 0.05; // 匹配宽高比的5%容差

    function resetCropButtonState(enable = true) {
        cropButton.innerHTML = CROP_BUTTON_DEFAULT_TEXT;
        cropButton.disabled = !enable || !originalImage; // 如果没有图像或明确指示不启用，则禁用
    }

    function showStatusMessage(message, type = 'info') {
        statusMessageDiv.textContent = message;
        statusMessageDiv.className = `status-message ${type}`; // 应用'error'或'info'类
        statusMessageDiv.style.display = 'block';
    }

    function hideStatusMessage() {
        statusMessageDiv.style.display = 'none';
    }

    // 调整画布大小以适应容器
    function adjustCanvasSize(canvas, containerWidth, imgWidth, imgHeight) {
        if (imgWidth > containerWidth) {
            const ratio = containerWidth / imgWidth;
            canvas.style.width = containerWidth + 'px';
            canvas.style.height = (imgHeight * ratio) + 'px';
        } else {
            canvas.style.width = imgWidth + 'px';
            canvas.style.height = imgHeight + 'px';
        }
    }

    // 窗口大小变化时重新调整画布大小
    function handleResize() {
        if (originalImage) {
            const originalContainerWidth = originalCanvasContainer.clientWidth - 30;
            adjustCanvasSize(originalCanvas, originalContainerWidth, originalImage.width, originalImage.height);
            
            // 如果手动裁剪处于活动状态，重新初始化以适应新的画布大小
            if (cropSelectionOverlay.style.display === 'block') {
                initializeManualCrop();
            }

            if (currentCropParams && !cropSelectionOverlay.style.display === 'block') { // 仅在非手动模式下调整裁剪后的图像
                const croppedContainerWidth = croppedCanvasContainer.clientWidth - 30;
                adjustCanvasSize(croppedCanvas, croppedContainerWidth, currentCropParams.width, currentCropParams.height);
            }
        }
    }

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize);

    cropModeRadios.forEach(radio => {
        radio.addEventListener('change', (event) => {
            currentCropMode = event.target.value;
            if (currentCropMode === 'manualAuto') {
                if (originalImage) {
                    initializeManualCrop();
                    cropSelectionOverlay.style.display = 'block';
                    cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
                    showStatusMessage('请手动框选预处理区域，然后点击裁剪按钮。', 'info');
                } else {
                    showStatusMessage('请先上传图片再选择手动框选模式。', 'error');
                    event.target.checked = false; // 恢复选择
                    document.getElementById('cropModeAuto').checked = true;
                    currentCropMode = 'auto';
                }
            } else { // 自动模式
                cropSelectionOverlay.style.display = 'none';
                manualCropSelection = null; // 切换到自动模式时清除手动选择
                resetCropButtonState(originalImage ? true : false);
                hideStatusMessage();
            }
        });
    });

    imageUpload.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (file) {
            if (!file.type.startsWith('image/')) {
                showStatusMessage('上传失败：请选择有效的图片文件。', 'error');
                // 如果需要，重置文件输入，尽管浏览器可能会处理这个
                imageUpload.value = ''; // 清除选定的文件
                fileUploadLabel.innerHTML = `<i class="ri-image-add-line"></i> 选择图片文件`;
                originalImage = null;
                currentCropParams = null;
                manualCropSelection = null; // 重置手动选区
                resetCropButtonState(false);
                originalCtx.clearRect(0, 0, originalCanvas.width, originalCanvas.height);
                croppedCtx.clearRect(0, 0, croppedCanvas.width, croppedCanvas.height);
                downloadLink.style.display = 'none';
                aspectRatioSuggestionDiv.style.display = 'none';
                return;
            }
            hideStatusMessage(); // 清除之前的消息
            const fileName = file.name;
            fileUploadLabel.innerHTML = `<i class="ri-file-list-line"></i> ${fileName.length > 25 ? fileName.substring(0, 22) + '...' : fileName}`;
            
            originalFileName = file.name.replace(/\.[^/.]+$/, "") + "_cropped.png";
            const reader = new FileReader();
            reader.onload = (e) => {
                originalImage = new Image();
                originalImage.onload = () => {
                    originalCanvas.width = originalImage.width;
                    originalCanvas.height = originalImage.height;
                    originalCtx.drawImage(originalImage, 0, 0);

                    // 显示原始图片信息
                    originalImageInfo.innerHTML = `尺寸: ${originalImage.width} x ${originalImage.height}px<br>大小: ${(file.size / 1024).toFixed(2)} KB`;
                    croppedImageInfo.innerHTML = ''; // 清空裁剪后的图片信息

                    // 调整画布显示大小
                    const containerWidth = originalCanvasContainer.clientWidth - 30; // 减去一些内边距
                    adjustCanvasSize(originalCanvas, containerWidth, originalImage.width, originalImage.height);
                    
                    resetCropButtonState(true); // 启用裁剪按钮
                    manualCropSelection = null; // 重置手动选区
                    
                    croppedCtx.clearRect(0, 0, croppedCanvas.width, croppedCanvas.height);
                    croppedCanvas.width = 1;
                    croppedCanvas.height = 1;
                    currentCropParams = null;
                    downloadLink.style.display = 'none';
                    aspectRatioSuggestionDiv.style.display = 'none';
                    hideStatusMessage(); // 隐藏之前的状态消息
                    // initializeManualCrop(); // 图像加载时初始化手动裁剪
                    if (currentCropMode === 'manualAuto') {
                        initializeManualCrop();
                        cropSelectionOverlay.style.display = 'block';
                        cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
                        showStatusMessage('请手动框选预处理区域，然后点击裁剪按钮。', 'info');
                    } else {
                        cropSelectionOverlay.style.display = 'none';
                    }
                };
                originalImage.onerror = () => {
                    showStatusMessage('图片加载失败：无法读取图片内容。', 'error');
                    originalImage = null;
                    resetCropButtonState(false);
                    originalImageInfo.innerHTML = '';
                    croppedImageInfo.innerHTML = '';
                };
                originalImage.src = e.target.result;
            };
            reader.readAsDataURL(file);
        } else {
            fileUploadLabel.innerHTML = `<i class="ri-image-add-line"></i> 选择图片文件`;
            originalImage = null;
            currentCropParams = null;
            manualCropSelection = null; // 重置手动选区
            resetCropButtonState(false); // 禁用裁剪按钮
            originalCtx.clearRect(0, 0, originalCanvas.width, originalCanvas.height);
            croppedCtx.clearRect(0, 0, croppedCanvas.width, croppedCanvas.height);
            downloadLink.style.display = 'none';
            aspectRatioSuggestionDiv.style.display = 'none';
            hideStatusMessage();
            originalImageInfo.innerHTML = '';
            croppedImageInfo.innerHTML = '';
            cropSelectionOverlay.style.display = 'none'; // 隐藏裁剪覆盖层
        }
    });

    function findClosestAspectRatio(contentWidth, contentHeight) {
        if (contentWidth <= 0 || contentHeight <= 0) return null;
        const currentRatioValue = contentWidth / contentHeight;
        let bestMatch = null;
        let minDifference = Infinity;

        COMMON_RATIOS.forEach(ratio => {
            const difference = Math.abs(currentRatioValue - ratio.value);
            if (difference / ratio.value < ASPECT_RATIO_TOLERANCE) {
                if (difference < minDifference) {
                    minDifference = difference;
                    bestMatch = ratio;
                }
            }
        });
        return bestMatch;
    }

    function performStrictRatioCrop(sourceX, sourceY, sourceWidth, sourceHeight, targetRatioValue) {
        let newCropWidth = sourceWidth;
        let newCropHeight = sourceWidth / targetRatioValue;

        if (newCropHeight > sourceHeight) {
            newCropHeight = sourceHeight;
            newCropWidth = sourceHeight * targetRatioValue;
        }

        const newCropX = sourceX + (sourceWidth - newCropWidth) / 2;
        const newCropY = sourceY + (sourceHeight - newCropHeight) / 2;

        return {
            x: Math.round(newCropX),
            y: Math.round(newCropY),
            width: Math.round(newCropWidth),
            height: Math.round(newCropHeight)
        };
    }

    function applyCropAndDisplay(cropParams, isManualPreCrop = false) {
        if (!originalImage) {
            showStatusMessage('裁剪失败：原始图片未加载。', 'error');
            resetCropButtonState(false); // 应该已经禁用，但确保一下
            croppedImageInfo.innerHTML = '';
            return false;
        }

        // 如果是手动预裁剪，我们还不在croppedCanvas上显示。
        // 我们更新原始图像视图或准备对此选择进行自动裁剪。
        if (isManualPreCrop) {
            // 目前，我们只记录它。实际的自动裁剪将使用这些参数。
            console.log("应用手动预裁剪:", cropParams);
            // 可能会重绘带有裁剪框的原始图像以提供视觉反馈，
            // 或者直接将这些坐标传递给自动裁剪逻辑。
            initialCropParams = cropParams; // 存储用于自动裁剪
            // 预裁剪后隐藏手动裁剪覆盖层
            // cropSelectionOverlay.style.display = 'none'; 
            // 我们可能希望保持可见，以便用户仍然可以调整
            return true; 
        }

        if (!cropParams || cropParams.width <= 0 || cropParams.height <= 0) {
            console.error("无法应用裁剪，参数无效或没有图像。");
            showStatusMessage('裁剪失败：未检测到有效图像内容。请检查边框颜色或容差。', 'error');
            croppedCtx.clearRect(0, 0, croppedCanvas.width, croppedCanvas.height);
            croppedCanvas.width = 1;
            croppedCanvas.height = 1;
            currentCropParams = null;
            downloadLink.style.display = 'none';
            resetCropButtonState(true); // 允许用户重试
            croppedImageInfo.innerHTML = '';
            return false; // 表示失败
        }
        hideStatusMessage(); // 清除之前的消息
        croppedCanvas.width = cropParams.width;
        croppedCanvas.height = cropParams.height;
        croppedCtx.drawImage(
            originalImage,
            cropParams.x, cropParams.y, cropParams.width, cropParams.height,
            0, 0, cropParams.width, cropParams.height
        );

        // 显示裁剪后图片信息
        const croppedImageDataUrl = croppedCanvas.toDataURL(imageUpload.files[0]?.type || 'image/png');
        const approxSizeKB = (croppedImageDataUrl.length * 0.75 / 1024).toFixed(2); // 估算大小
        croppedImageInfo.innerHTML = `尺寸: ${cropParams.width} x ${cropParams.height}px<br>预估大小: ${approxSizeKB} KB (实际大小以保存后为准)`;

        // 存储当前裁剪参数
        currentCropParams = cropParams;

        // 调整裁剪后画布的显示大小
        const containerWidth = croppedCanvasContainer.clientWidth - 30; // 减去一些内边距
        adjustCanvasSize(croppedCanvas, containerWidth, cropParams.width, cropParams.height);

        const imageMimeType = imageUpload.files[0]?.type || 'image/png';
        const removeExif = removeExifCheckbox.checked;

        if (removeExif) {
            downloadLink.href = croppedCanvas.toDataURL(imageMimeType);
        } else {
            // 尝试保留 EXIF 的情况
            // 注意：canvas.toDataURL() 通常会丢失EXIF数据。
            // 客户端保留 EXIF 非常复杂，通常需要第三方库。
            // 此处我们发出警告，并按常规方式下载（很可能不含 EXIF）。
            console.warn("用户选择保留EXIF，但浏览器Canvas API通常会移除EXIF数据。下载的图片可能不包含原始元数据。");
            downloadLink.href = croppedCanvas.toDataURL(imageMimeType);
        }

        downloadLink.download = originalFileName;
        downloadLink.style.display = 'block';
        downloadLink.innerHTML = `<i class="ri-download-line"></i> 下载 ${originalFileName}`;
        return true; // 表示成功
    }

    function hexToRgb(hex) {
        const bigint = parseInt(hex.slice(1), 16);
        return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
    }

    function findBorderPixelLimits(imageData, imgWidth, imgHeight, R, G, B, toleranceVal) {
        const data = imageData.data;
        let top = 0, bottom = imgHeight - 1, left = 0, right = imgWidth - 1;

        // 查找上边框
        for (let y = 0; y < imgHeight; y++) {
            let isBorderRow = true;
            for (let x = 0; x < imgWidth; x++) {
                const i = (y * imgWidth + x) * 4;
                if (Math.abs(data[i] - R) > toleranceVal || Math.abs(data[i+1] - G) > toleranceVal || Math.abs(data[i+2] - B) > toleranceVal) {
                    isBorderRow = false; break;
                }
            }
            if (!isBorderRow) { top = y; break; }
            if (y === imgHeight - 1) top = imgHeight; // 整张图片都是边框
        }

        // 查找下边框
        for (let y = imgHeight - 1; y >= top; y--) {
            let isBorderRow = true;
            for (let x = 0; x < imgWidth; x++) {
                const i = (y * imgWidth + x) * 4;
                if (Math.abs(data[i] - R) > toleranceVal || Math.abs(data[i+1] - G) > toleranceVal || Math.abs(data[i+2] - B) > toleranceVal) {
                    isBorderRow = false; break;
                }
            }
            if (!isBorderRow) { bottom = y; break; }
            if (y === top) bottom = top - 1; // 剩余的图像都是边框
        }
        
        // 查找左边框（仅在新的上/下边界内扫描）
        for (let x = 0; x < imgWidth; x++) {
            let isBorderCol = true;
            for (let y = top; y <= bottom; y++) {
                const i = (y * imgWidth + x) * 4;
                if (Math.abs(data[i] - R) > toleranceVal || Math.abs(data[i+1] - G) > toleranceVal || Math.abs(data[i+2] - B) > toleranceVal) {
                    isBorderCol = false; break;
                }
            }
            if (!isBorderCol) { left = x; break; }
            if (x === imgWidth - 1) left = imgWidth;
        }

        // 查找右边框（仅在新的上/下边界内扫描）
        for (let x = imgWidth - 1; x >= left; x--) {
            let isBorderCol = true;
            for (let y = top; y <= bottom; y++) {
                const i = (y * imgWidth + x) * 4;
                if (Math.abs(data[i] - R) > toleranceVal || Math.abs(data[i+1] - G) > toleranceVal || Math.abs(data[i+2] - B) > toleranceVal) {
                    isBorderCol = false; break;
                }
            }
            if (!isBorderCol) { right = x; break; }
            if (x === left) right = left - 1;
        }
        return { top, bottom, left, right };
    }

    cropButton.addEventListener('click', () => {
        if (!originalImage) {
            // alert("请先上传一张图片。"); // 被状态消息替代
            showStatusMessage('请先上传一张图片。', 'error');
            resetCropButtonState(false); // 如果按钮莫名其妙启用了，确保禁用
            return;
        }

        cropButton.disabled = true;
        cropButton.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> 处理中...';
        showStatusMessage('正在处理图片...', 'info'); 
        aspectRatioSuggestionDiv.style.display = 'none';
        downloadLink.style.display = 'none'; // 隐藏之前的下载链接

        // // 优先使用手动裁剪区域
        // if (manualCropSelection && manualCropSelection.width > 0 && manualCropSelection.height > 0) {
        //     showStatusMessage('正在应用手动选择的区域进行裁剪...', 'info');
        //     setTimeout(() => {
        //         if (applyCropAndDisplay(manualCropSelection)) {
        //             showStatusMessage('手动区域裁剪成功！', 'info');
        //         } else {
        //             // applyCropAndDisplay 会显示自己的错误信息
        //         }
        //         resetCropButtonState(true);
        //         manualCropSelection = null; // 使用后重置手动选区
        //     }, 50);
        //     return; // 跳过自动检测
        // }


        // 使用setTimeout允许UI更新为"处理中..."
        setTimeout(() => {
            try { // 为整个过程添加try-catch
                const selectedColorMode = borderColorSelect.value;
                const tolerance = parseInt(toleranceInput.value, 10);

                let imageDataToProcess, imgWidth, imgHeight, offsetX = 0, offsetY = 0;

                if (currentCropMode === 'manualAuto' && manualCropSelection && manualCropSelection.width > 0 && manualCropSelection.height > 0) {
                    showStatusMessage('正在从手动选区提取图像数据...', 'info');
                    // 确保选区在图像边界内
                    const selX = Math.max(0, manualCropSelection.x);
                    const selY = Math.max(0, manualCropSelection.y);
                    const selW = Math.min(manualCropSelection.width, originalImage.width - selX);
                    const selH = Math.min(manualCropSelection.height, originalImage.height - selY);

                    if (selW <= 0 || selH <= 0) {
                        showStatusMessage('手动选区无效或超出图像范围。', 'error');
                        resetCropButtonState(true);
                        if (currentCropMode === 'manualAuto') cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
                        return;
                    }

                    imageDataToProcess = originalCtx.getImageData(selX, selY, selW, selH);
                    imgWidth = selW;
                    imgHeight = selH;
                    offsetX = selX;
                    offsetY = selY;
                    showStatusMessage('已提取手动选区，正在此区域内检测边框...', 'info');
                } else {
                    const tempCanvas = document.createElement('canvas');
                    const tempCtx = tempCanvas.getContext('2d');
                    tempCanvas.width = originalImage.width;
                    tempCanvas.height = originalImage.height;
                    tempCtx.drawImage(originalImage, 0, 0);
                    imageDataToProcess = tempCtx.getImageData(0, 0, tempCanvas.width, tempCanvas.height);
                    imgWidth = tempCanvas.width;
                    imgHeight = tempCanvas.height;
                    showStatusMessage('正在检测整张图片的边框...', 'info');
                }

                let limits;

                if (selectedColorMode === 'auto') {
                    // showStatusMessage('正在检测白色边框...', 'info'); // 消息基于模式已在上方设置
                    const whiteRgb = [255, 255, 255];
                    limits = findBorderPixelLimits(imageDataToProcess, imgWidth, imgHeight, whiteRgb[0], whiteRgb[1], whiteRgb[2], tolerance);
                    let contentWidth = limits.right - limits.left + 1;
                    let contentHeight = limits.bottom - limits.top + 1;
                    
                    const whiteRemovedSomething = (limits.top > 0 || limits.left > 0 || limits.bottom < imgHeight - 1 || limits.right < imgWidth - 1) && contentWidth > 0 && contentHeight > 0;

                    if (!whiteRemovedSomething) { 
                        showStatusMessage((currentCropMode === 'manualAuto' ? '手动区域内' : '') + '未检测到白色边框或移除后无有效内容，尝试检测黑色边框...', 'info');
                        const blackRgb = [0, 0, 0];
                        limits = findBorderPixelLimits(imageDataToProcess, imgWidth, imgHeight, blackRgb[0], blackRgb[1], blackRgb[2], tolerance);
                    }
                } else {
                    showStatusMessage((currentCropMode === 'manualAuto' ? '手动区域内' : '') + `正在检测 ${selectedColorMode === 'white' ? '白色' : '黑色'} 边框...`, 'info');
                    const [r, g, b] = hexToRgb(selectedColorMode === 'white' ? '#FFFFFF' : '#000000');
                    limits = findBorderPixelLimits(imageDataToProcess, imgWidth, imgHeight, r, g, b, tolerance);
                }

                initialCropParams = {
                    x: limits.left + offsetX,
                    y: limits.top + offsetY,
                    width: limits.right - limits.left + 1,
                    height: limits.bottom - limits.top + 1
                };

                if (initialCropParams.width <= 0 || initialCropParams.height <= 0) {
                    showStatusMessage('裁剪失败：未检测到有效图像内容。请检查边框颜色、容差或手动选区。', 'error');
                    resetCropButtonState(true);
                    if (currentCropMode === 'manualAuto') cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
                    croppedCtx.clearRect(0, 0, croppedCanvas.width, croppedCanvas.height);
                    croppedCanvas.width = 1;
                    croppedCanvas.height = 1;
                    currentCropParams = null;
                    downloadLink.style.display = 'none';
                    return;
                }
                
                showStatusMessage('边框检测完成，正在分析内容...', 'info');

                suggestedAspectRatio = findClosestAspectRatio(initialCropParams.width, initialCropParams.height);

                if (suggestedAspectRatio) {
                    showStatusMessage('检测到可能的标准比例，请确认。', 'info');
                    suggestionTextEl.innerHTML = `检测到的内容区域宽高比 (${initialCropParams.width}x${initialCropParams.height}) 接近 <b>${suggestedAspectRatio.name}</b>。您希望严格按照此比例裁剪吗？`;
                    aspectRatioSuggestionDiv.style.display = 'block';
                    resetCropButtonState(true); // 重新启用主裁剪按钮，虽然用户将与建议交互
                } else {
                    showStatusMessage('正在应用检测到的边框进行裁剪...', 'info');
                    if(applyCropAndDisplay(initialCropParams)) {
                        showStatusMessage('裁剪成功！', 'info'); // 成功消息
                    } else {
                        // 如果失败，错误消息已由applyCropAndDisplay处理
                    }
                    resetCropButtonState(true);
                }
            } catch (error) {
                console.error("裁剪过程中发生错误:", error);
                showStatusMessage(`处理失败：发生意外错误 (${error.message})。请重试或检查控制台。`, 'error');
                resetCropButtonState(true);
                if (currentCropMode === 'manualAuto') cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
            }
        }, 50); // 为UI更新的小延迟
    });

    confirmRatioCropButton.addEventListener('click', () => {
        if (!initialCropParams || !suggestedAspectRatio) return;
        
        cropButton.disabled = true;
        cropButton.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> 应用比例...';
        showStatusMessage(`正在按 ${suggestedAspectRatio.name} 比例裁剪...`, 'info');
        aspectRatioSuggestionDiv.style.display = 'none';

        setTimeout(() => {
            try {
                const strictCropParams = performStrictRatioCrop(
                    initialCropParams.x,
                    initialCropParams.y,
                    initialCropParams.width,
                    initialCropParams.height,
                    suggestedAspectRatio.value
                );

                if (applyCropAndDisplay(strictCropParams)) {
                    showStatusMessage(`已按 ${suggestedAspectRatio.name} 比例裁剪成功！`, 'info');
                } else {
                    // 错误消息由applyCropAndDisplay处理
                    // 如果严格比例失败但初始有效，则回退到初始
                    if (initialCropParams.width > 0 && initialCropParams.height > 0) {
                         showStatusMessage('按标准比例裁剪失败，已回退到检测边框裁剪。', 'info');
                         applyCropAndDisplay(initialCropParams); // 尝试原始裁剪
                    }
                }
            } catch (error) {
                console.error("按比例裁剪过程中发生错误:", error);
                showStatusMessage(`按比例裁剪失败：发生意外错误 (${error.message})。`, 'error');
                 if (initialCropParams && initialCropParams.width > 0 && initialCropParams.height > 0) {
                     showStatusMessage('按标准比例裁剪失败，已回退到检测边框裁剪。', 'info');
                     applyCropAndDisplay(initialCropParams);
                 }
            } finally {
                resetCropButtonState(true);
                if (currentCropMode === 'manualAuto') cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
            }
        }, 50);
    });

    rejectRatioCropButton.addEventListener('click', () => {
        if (!initialCropParams) return;

        cropButton.disabled = true;
        cropButton.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> 应用检测...';
        showStatusMessage('正在按检测到的边框裁剪...', 'info');
        aspectRatioSuggestionDiv.style.display = 'none';

        setTimeout(() => {
            try {
                if (applyCropAndDisplay(initialCropParams)) {
                     showStatusMessage('已按检测到的边框裁剪成功！', 'info');
                }
                // 错误消息由applyCropAndDisplay处理
            } catch (error) {
                 console.error("按检测边框裁剪过程中发生错误:", error);
                showStatusMessage(`按检测边框裁剪失败：发生意外错误 (${error.message})。`, 'error');
            } finally {
                resetCropButtonState(true);
                if (currentCropMode === 'manualAuto') cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
            }
        }, 50);
    });


    // --- 手动裁剪逻辑 ---
    function initializeManualCrop() {
        if (!originalImage) return;

        cropSelectionOverlay.style.display = 'block';
        const canvasRect = originalCanvas.getBoundingClientRect();
        const displayWidth = canvasRect.width;
        const displayHeight = canvasRect.height;

        imageScale = displayWidth / originalImage.width;
        if (originalImage.height * imageScale > displayHeight) {
            imageScale = displayHeight / originalImage.height;
        }

        // 将初始裁剪框设置为覆盖整个图像
        const initialBoxWidth = originalImage.width * imageScale;
        const initialBoxHeight = originalImage.height * imageScale;
        
        // 如果画布大于缩放后的图像，则将裁剪框居中
        const offsetX = (displayWidth - initialBoxWidth) / 2;
        const offsetY = (displayHeight - initialBoxHeight) / 2;

        Object.assign(cropBox.style, {
            left: `${offsetX}px`,
            top: `${offsetY}px`,
            width: `${initialBoxWidth}px`,
            height: `${initialBoxHeight}px`,
        });

        updateCropHandles();
    }

    function updateCropHandles() {
        const { offsetWidth, offsetHeight } = cropBox;
        // 把手相对于cropBox定位
    }

    cropBox.addEventListener('mousedown', (e) => {
        e.stopPropagation(); // 如果点击框，防止画布mousedown
        isDragging = true;
        isResizing = false;
        startX = e.clientX;
        startY = e.clientY;
        initialCropX = cropBox.offsetLeft;
        initialCropY = cropBox.offsetTop;
        document.addEventListener('mousemove', handleMouseMove);
        document.addEventListener('mouseup', handleMouseUp);
    });

    Object.values(cropHandles).forEach(handle => {
        handle.addEventListener('mousedown', (e) => {
            e.stopPropagation();
            isResizing = true;
            isDragging = false;
            resizeHandle = e.target.className.split(' ')[1]; // 例如，'nw'，'n'
            startX = e.clientX;
            startY = e.clientY;
            initialCropX = cropBox.offsetLeft;
            initialCropY = cropBox.offsetTop;
            initialCropWidth = cropBox.offsetWidth;
            initialCropHeight = cropBox.offsetHeight;
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        });
    });

    function handleMouseMove(e) {
        if (!isDragging && !isResizing) return;
        e.preventDefault();

        const dx = e.clientX - startX;
        const dy = e.clientY - startY;
        const canvasRect = originalCanvas.getBoundingClientRect();

        if (isDragging) {
            let newLeft = initialCropX + dx;
            let newTop = initialCropY + dy;

            // 拖动的边界检查
            newLeft = Math.max(0, Math.min(newLeft, canvasRect.width - cropBox.offsetWidth));
            newTop = Math.max(0, Math.min(newTop, canvasRect.height - cropBox.offsetHeight));

            cropBox.style.left = `${newLeft}px`;
            cropBox.style.top = `${newTop}px`;
        }

        if (isResizing) {
            let newLeft = initialCropX;
            let newTop = initialCropY;
            let newWidth = initialCropWidth;
            let newHeight = initialCropHeight;

            if (resizeHandle.includes('e')) newWidth += dx;
            if (resizeHandle.includes('s')) newHeight += dy;
            if (resizeHandle.includes('w')) { newWidth -= dx; newLeft += dx; }
            if (resizeHandle.includes('n')) { newHeight -= dy; newTop += dy; }

            const minSize = 20; // 裁剪框的最小尺寸
            newWidth = Math.max(minSize, newWidth);
            newHeight = Math.max(minSize, newHeight);

            // 调整大小的边界检查
            if (newLeft < 0) { newWidth += newLeft; newLeft = 0; }
            if (newTop < 0) { newHeight += newTop; newTop = 0; }
            if (newLeft + newWidth > canvasRect.width) { newWidth = canvasRect.width - newLeft; }
            if (newTop + newHeight > canvasRect.height) { newHeight = canvasRect.height - newTop; }
            
            // 确保宽度/高度在调整推动它们时不会变为负值
            newWidth = Math.max(minSize, newWidth);
            newHeight = Math.max(minSize, newHeight);


            cropBox.style.left = `${newLeft}px`;
            cropBox.style.top = `${newTop}px`;
            cropBox.style.width = `${newWidth}px`;
            cropBox.style.height = `${newHeight}px`;
        }
        updateCropHandles();
    }

    function handleMouseUp() {
        if (isDragging || isResizing) {
            // 将显示的裁剪框坐标转换为实际图像坐标
            const finalCropParams = {
                x: Math.round(cropBox.offsetLeft / imageScale),
                y: Math.round(cropBox.offsetTop / imageScale),
                width: Math.round(cropBox.offsetWidth / imageScale),
                height: Math.round(cropBox.offsetHeight / imageScale)
            };
            // 将这些存储为手动裁剪选择
            manualCropSelection = finalCropParams;
            console.log("已保存手动选择:", manualCropSelection);
            showStatusMessage('手动选区已更新。请点击裁剪按钮在选区内检测边框。', 'info');
            cropButton.innerHTML = '<i class="ri-crop-line"></i> 在选定区域内检测边框并裁剪';
            cropButton.disabled = !originalImage; // 如果图像已加载则启用
            // applyCropAndDisplay(finalCropParams, true); // 不再在此处调用
        }
        isDragging = false;
        isResizing = false;
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
    }
    

    // 在页面首次加载时隐藏裁剪覆盖层
    cropSelectionOverlay.style.display = 'none';
    
    // 初始化原始元素，以防止在加载图像之前引用它们时出错
    originalImageInfo = document.getElementById('originalImageInfo');
    croppedImageInfo = document.getElementById('croppedImageInfo');

    // 如果图像在DOMContentLoaded之前已经加载完成
    if (originalImage) {
        resetCropButtonState(true);
    } else {
        resetCropButtonState(false);
    }

});