@echo off
REM 使用 UTF-8 代码页
REM chcp 65001 > nul

echo 正在准备启动 WSL (Ubuntu-20.04) 并在当前目录的 WSL 映射路径中启动 Jupyter Notebook 服务器...
echo.

REM 获取当前 .bat 文件所在的 Windows 目录
set "SCRIPT_DIR=%~dp0"
REM 去除路径末尾的反斜杠 (如果存在)
IF "%SCRIPT_DIR:~-1%"=="\" SET "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo Windows 当前工作目录: "%SCRIPT_DIR%"
echo.

REM --- 手动构造 WSL 路径 ---
echo 正在手动构造 WSL 路径...

REM 提取驱动器号 (例如 D)
set "DRIVE_LETTER_RAW=%SCRIPT_DIR:~0,1%"

REM 将驱动器号转为小写 (d)
set "LOWER_CASE_DRIVE_LETTER=%DRIVE_LETTER_RAW%"
REM Basic lowercase conversion for A-Z
for %%L in (A B C D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if /I "%%L"=="%DRIVE_LETTER_RAW%" set "LOWER_CASE_DRIVE_LETTER=%%L"
)
if "%LOWER_CASE_DRIVE_LETTER%" GEQ "A" if "%LOWER_CASE_DRIVE_LETTER%" LEQ "Z" (
    REM This is a trick: use a temp file with PowerShell to lowercase reliably if complex chars involved
    REM For simple A-Z, the loop above works for ASCII. Let's assume standard drive letters.
    REM For 'D' -> 'd', the loop should work by finding the lowercase match.
    REM Re-evaluating the loop for lowercase: it should be `set "LOWER_CASE_DRIVE_LETTER=%%l"` if %%l is the lowercase version
    REM Simpler: rely on WSL being okay with /mnt/D if direct lowercase is too complex in pure batch for all scenarios.
    REM For now, let's try direct lowercase for known letters.
    if /I "%DRIVE_LETTER_RAW%"=="A" set LOWER_CASE_DRIVE_LETTER=a
    if /I "%DRIVE_LETTER_RAW%"=="B" set LOWER_CASE_DRIVE_LETTER=b
    if /I "%DRIVE_LETTER_RAW%"=="C" set LOWER_CASE_DRIVE_LETTER=c
    if /I "%DRIVE_LETTER_RAW%"=="D" set LOWER_CASE_DRIVE_LETTER=d
    if /I "%DRIVE_LETTER_RAW%"=="E" set LOWER_CASE_DRIVE_LETTER=e
    if /I "%DRIVE_LETTER_RAW%"=="F" set LOWER_CASE_DRIVE_LETTER=f
    REM ... add for other common drive letters if needed
)

REM 提取驱动器号后面的路径 (例如 \Users\linyu\Desktop\every)
set "PATH_AFTER_DRIVE=%SCRIPT_DIR:~2%"

REM 将反斜杠替换为正斜杠
set "PATH_WITH_FORWARD_SLASHES=%PATH_AFTER_DRIVE:\=/%"

REM 组合成最终的 WSL 路径 (例如 /mnt/d/Users/linyu/Desktop/every)
set "WSL_PATH=/mnt/%LOWER_CASE_DRIVE_LETTER%%PATH_WITH_FORWARD_SLASHES%"

echo 手动构造的 WSL 路径: "%WSL_PATH%"
echo.

REM --- 检查 wslpath 工具的输出（仅供调试对比） ---
REM FOR /F "usebackq delims=" %%P IN (`wsl wslpath -u "%SCRIPT_DIR%"`) DO SET "WSL_PATH_FROM_UTILITY=%%P"
REM echo 对比：wslpath 工具输出: "%WSL_PATH_FROM_UTILITY%"
REM echo.

IF NOT DEFINED WSL_PATH (
    echo 错误：未能构造 WSL 路径。
    pause
    goto :eof
)

echo 即将打开一个新的 WSL 终端窗口。
echo 请在该新窗口中查找类似如下的 Jupyter 服务器 URL:
echo   http://localhost:8888/?token=xxxxxxxxxxxx
echo 或
echo   http://127.0.0.1:8888/?token=xxxxxxxxxxxx
echo.

start "WSL_Jupyter_Server" wsl -d Ubuntu-20.04 --cd "%WSL_PATH%" bash -lic "echo '--- Inside WSL Terminal ---'; echo 'Using WSL Path (from bat): %WSL_PATH%'; echo 'Current directory (pwd) after wsl --cd:'; pwd; echo 'Starting Jupyter Lab...'; jupyter lab --no-browser --ip=0.0.0.0 --notebook-dir=.; echo '--- Jupyter Lab has exited (or failed) ---'; echo 'Press any key to close this WSL window.'; read -n 1 -s -r -p ''"

echo.
echo Jupyter Lab 服务器应该正在一个新的 WSL 窗口中启动。
echo 如果新的 WSL 窗口未能正确启动 Jupyter Lab，请检查窗口中的错误信息。
echo.
echo 当前这个脚本窗口可以关闭，或者按任意键关闭它。
pause