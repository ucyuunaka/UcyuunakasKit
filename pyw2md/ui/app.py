"""
主应用窗口
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from core.constants import (
    MSG_FILE_MODIFIED, MSG_FILE_DELETED, MSG_REFRESH_COMPLETE,
    MSG_NO_CHANGES, MSG_REFRESH_FAILED, UI_UPDATE_DEBOUNCE_MS
)

# 拖放功能安全降级导入
try:
    from utils.packaging import safe_import_tkinterdnd2, print_packaging_debug_info
    # 在打包环境中打印调试信息
    if __import__('utils.packaging', fromlist=['packaging']).is_packaged():
        print_packaging_debug_info()

    # 安全导入tkinterdnd2
    DRAG_DROP_AVAILABLE, import_error = safe_import_tkinterdnd2()
    if DRAG_DROP_AVAILABLE:
        from tkinterdnd2 import DND_FILES, TkinterDnD
    else:
        print(f"tkinterdnd2导入失败: {import_error}")
        print("提示: 安装 tkinterdnd2 以启用拖放功能: pip install tkinterdnd2")
except ImportError:
    DRAG_DROP_AVAILABLE = False
    print("提示: 安装 tkinterdnd2 以启用拖放功能: pip install tkinterdnd2")

from config.theme import MD
from config.settings import Settings
from core.file_handler import FileHandler
from core.converter import Converter
from core.file_watcher import FileWatcher
from ui.components.file_list_panel import FileListPanel
from ui.components.control_panel import ControlPanel
from ui.components.status_bar import StatusBar
from ui.components.dialogs import TemplatePreviewDialog, ConversionPreviewDialog

# UI更新防抖时间常量（毫秒）
UI_UPDATE_DEBOUNCE = UI_UPDATE_DEBOUNCE_MS


# ============ 优雅降级基类 ============
class DragDropMixin:

    def drop_target_register(self, *args, **kwargs):
        if DRAG_DROP_AVAILABLE and hasattr(super(), 'drop_target_register'):
            return super().drop_target_register(*args, **kwargs)
        return None

    def dnd_bind(self, *args, **kwargs):
        if DRAG_DROP_AVAILABLE and hasattr(super(), 'dnd_bind'):
            return super().dnd_bind(*args, **kwargs)
        return None


if DRAG_DROP_AVAILABLE:
    class AppBase(DragDropMixin, TkinterDnD.Tk):
        """
        支持拖放功能的应用基类

        设计理念：
        - 当拖放功能可用时，继承TkinterDnD.Tk获得完整的拖放支持
        - 通过多重继承组合拖放混合类的功能
        - 提供统一的初始化接口，简化上层代码

        技术优势：
        - 运行时动态选择最合适的基类
        - 保持API一致性，上层代码无需关心底层实现差异
        - 最大化功能可用性，同时确保向后兼容性
        """
        def __init__(self):
            # 初始化TkinterDnD.Tk基类，获得拖放功能支持
            TkinterDnD.Tk.__init__(self)
else:
    class AppBase(DragDropMixin, ctk.CTk):
        """
        不支持拖放功能的降级基类

        设计思路：
        - 当拖放功能不可用时，退而求其次使用ctk.CTk
        - 保持与拖放版本的API兼容性
        - 确保应用在没有拖放支持的环境下仍能正常运行

        降级策略：
        - 提供基础的应用框架功能
        - 通过其他方式（如文件选择对话框）补充文件操作能力
        - 保持用户界面的一致性体验
        """
        def __init__(self):
            # 初始化ctk.CTk基类，获得现代化的UI支持
            ctk.CTk.__init__(self)


class MaterialApp(AppBase):
    """
    主应用程序 - 性能优化版

    核心职责：
    - 管理应用生命周期和全局状态
    - 协调各功能模块的交互
    - 提供用户界面和交互逻辑
    - 处理文件操作和转换任务
    - 监控系统事件和文件变化

    架构特点：
    - 采用依赖注入模式管理核心组件
    - 实现观察者模式处理文件系统事件
    - 使用异步编程避免UI阻塞
    - 提供统一的事件处理和错误恢复机制

    性能优化：
    - 防抖处理减少窗口调整频率
    - 异步文件处理避免界面卡顿
    - 文件变化批量处理和通知合并
    - 延迟加载和按需初始化策略
    """

    def __init__(self):
        """
        应用初始化

        初始化流程：
        1. 调用父类构造函数建立基础框架
        2. 初始化核心组件（设置、文件处理器、转换器）
        3. 配置文件监控系统
        4. 设置UI组件和布局
        5. 加载保存的应用状态
        6. 启动后台服务（文件监控）
        7. 绑定系统事件处理函数

        设计考量：
        - 按照依赖关系顺序初始化组件
        - 提供完整的错误处理机制
        - 支持功能降级和可选组件
        - 确保所有资源都能正确清理
        """
        super().__init__()

        # 初始化配置管理器，负责应用设置的读写和持久化
        self.settings = Settings()

        # 初始化文件处理器，管理文件列表和元数据
        self.file_handler = FileHandler()

        # 初始化转换器，负责代码到Markdown的转换逻辑
        self.converter = Converter()

        # 初始化文件监控器，实时跟踪文件系统变化
        # 使用回调模式处理文件变化事件，FileWatcher内部使用统一状态管理
        self.file_watcher = FileWatcher(self._on_file_changed)
        self.watch_enabled = self.settings.get('auto_watch_files', True)

        # 窗口调整防抖机制，避免频繁的UI重绘
        self._resize_after_id = None  # 存储防抖定时器ID

        # 状态栏更新防抖机制
        self._status_update_after_id = None  # 存储状态栏更新防抖定时器ID

        # 按顺序初始化UI组件和系统功能
        self._setup_window()      # 配置窗口属性
        self._build_ui()          # 构建用户界面
        self._setup_drag_drop()   # 配置拖放功能
        self._load_saved_state()  # 加载保存的状态

        # 启动文件监控系统（如果启用）
        if self.watch_enabled:
            self.file_watcher.start()

        # 绑定系统事件处理
        self.protocol("WM_DELETE_WINDOW", self._on_closing)  # 窗口关闭事件
        self.bind('<Configure>', self._on_window_configure)  # 窗口调整事件
    
    def _setup_window(self):
        """
        配置应用窗口属性

        功能说明：
        - 设置窗口标题和基本属性
        - 根据保存的设置或默认值配置窗口尺寸
        - 计算并设置窗口在屏幕中央的位置
        - 配置窗口最小尺寸限制
        - 统一设置背景颜色以匹配主题

        设计考量：
        - 支持用户自定义窗口尺寸的记忆功能
        - 确保窗口在不同分辨率屏幕上都能合理显示
        - 提供最小尺寸限制，保证UI组件的正常布局
        - 采用居中显示策略，提升用户体验
        """
        self.title("代码转Markdown工具 - 性能优化版")

        # 从设置中读取窗口尺寸，如无设置则使用默认值
        width = self.settings.get('window', {}).get('width', 1280)
        height = self.settings.get('window', {}).get('height', 800)

        # 计算窗口居中位置
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2

        # 设置窗口位置和尺寸
        self.geometry(f"{width}x{height}+{x}+{y}")

        # 设置最小窗口尺寸，确保UI组件正常显示
        min_width = self.settings.get('window', {}).get('min_width', 1000)
        min_height = self.settings.get('window', {}).get('min_height', 600)
        self.minsize(min_width, min_height)

        # 统一背景色设置，确保视觉一致性
        self._set_background_color()

    def _set_background_color(self):
        """
        设置窗口背景色 - 兼容不同父类

        技术说明：
        - 根据拖放功能是否可用选择不同的配置方式
        - TkinterDnD.Tk和ctk.CTk的配置属性不同
        - 提供异常处理，确保配置失败不会影响应用启动

        设计思路：
        - 运行时检测父类类型，选择适当的配置方法
        - 使用主题配置中的背景色，保持视觉一致性
        - 提供降级处理，避免配置失败导致应用崩溃
        """
        try:
            if DRAG_DROP_AVAILABLE:
                # TkinterDnD.Tk使用bg属性设置背景色
                self.configure(bg=MD.BG_MAIN)
            else:
                # ctk.CTk使用fg_color属性设置背景色
                self.configure(fg_color=MD.BG_MAIN)
        except Exception as e:
            # 配置失败时记录日志，不影响应用继续运行
            print(f"设置背景色失败: {e}")

    def _setup_drag_drop(self):
        """
        配置拖放功能 - 安全降级处理

        功能说明：
        - 检测拖放功能是否可用
        - 为应用窗口注册拖放事件处理
        - 提供降级提示和用户引导

        安全策略：
        - 功能检测失败时自动降级到文件选择模式
        - 提供用户友好的提示信息
        - 确保应用在没有拖放支持的环境下仍能正常工作

        技术实现：
        - 使用try-except捕获拖放初始化异常
        - 为主窗口和文件列表面板分别注册拖放事件
        - 提供延迟初始化，确保UI组件已创建完成
        """
        if not DRAG_DROP_AVAILABLE:
            # 拖放功能不可用时的降级处理
            print("拖放功能不可用，已降级为文件选择模式")
            self._show_drag_drop_hint()
            return

        try:
            # 为主窗口注册拖放文件支持
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)

            # 为文件列表面板注册拖放支持（如果已创建）
            if hasattr(self, 'file_panel'):
                self.file_panel.drop_target_register(DND_FILES)
                self.file_panel.dnd_bind('<<Drop>>', self._on_drop)

            print("拖放功能已启用")
        except Exception as e:
            # 拖放初始化失败的处理
            print(f"警告: 拖放功能初始化失败: {e}")

    def _show_drag_drop_hint(self):
        """
        显示拖放功能不可用提示

        用户体验设计：
        - 以非侵入式方式提示用户功能限制
        - 提供解决方案指导（安装必要组件）
        - 自动消失避免干扰用户操作

        视觉设计：
        - 使用温和的颜色和图标
        - 采用临时显示策略
        - 保持良好的可读性
        """
        hint = ctk.CTkLabel(
            self,
            text="提示: 安装 tkinterdnd2 启用拖放功能",
            font=MD.get_font_label(),
            text_color=MD.WARNING
        )
        hint.grid(row=0, column=0, columnspan=2, pady=MD.PAD_S, sticky='ew')
        # 5秒后自动移除提示
        self.after(5000, hint.destroy)

    def _on_drop(self, event):
        """
        处理拖放事件

        事件处理流程：
        1. 解析拖放数据获取文件路径列表
        2. 验证文件路径的有效性
        3. 异步处理文件添加操作
        4. 更新UI显示处理结果

        设计思路：
        - 将耗时的文件处理操作放到后台线程
        - 保持UI响应性，避免拖放操作卡顿
        - 提供完整的错误处理和用户反馈

        技术特点：
        - 支持多文件和文件夹同时拖放
        - 自动识别文件类型和过滤不支持格式
        - 与文件监控系统集成，实现自动监控
        """
        files = self._parse_drop_files(event.data)

        if not files:
            # 没有有效文件时直接返回
            return

        # 异步处理拖放文件，避免阻塞UI线程
        self._process_dropped_files_async(files)

    def _process_dropped_files_async(self, files):
        """
        异步处理拖放的文件

        性能优化策略：
        - 在独立线程中处理文件扫描和添加
        - 批量处理文件和文件夹，减少系统调用
        - 使用线程安全的UI更新机制
        - 提供处理进度和结果反馈

        处理逻辑：
        - 区分文件和文件夹，采用不同的处理策略
        - 递归扫描文件夹获取所有支持的文件
        - 与文件监控系统集成，自动添加监控
        - 统计处理结果，提供用户反馈

        线程安全：
        - UI更新必须通过after方法调度到主线程
        - 使用daemon线程确保应用退出时能够正确清理
        - 避免共享状态竞争，使用局部变量存储处理结果
        """
        import threading

        def process():
            # 统计处理结果
            added_files = 0    # 添加的文件数量
            added_folders = 0  # 从文件夹中添加的文件数量

            # 遍历所有拖放的文件和文件夹
            for path in files:
                if os.path.isfile(path):
                    # 处理单个文件
                    if self.file_handler.add_file(path):
                        added_files += 1
                        # 如果启用了文件监控，添加监控
                        if self.watch_enabled:
                            self.file_watcher.add_file(path)
                elif os.path.isdir(path):
                    # 处理文件夹，递归添加所有支持的文件
                    count = self.file_handler.add_folder(path)
                    added_folders += count
                    # 为文件夹中的所有文件添加监控
                    if self.watch_enabled:
                        for file_info in self.file_handler.files[-count:]:
                            self.file_watcher.add_file(file_info.path)

            # UI更新必须在主线程执行
            self.after(0, lambda: self._on_drop_complete(added_files, added_folders))

        # 启动后台处理线程
        threading.Thread(target=process, daemon=True).start()
    
    def _on_drop_complete(self, added_files, added_folders):
        """
        拖放处理完成回调

        功能说明：
        - 更新文件列表显示
        - 刷新统计信息
        - 向用户显示处理结果

        用户体验设计：
        - 提供清晰的成功/失败反馈
        - 显示具体的处理数量
        - 使用StatusBar通知避免打断用户操作

        参数说明：
        - added_files: 成功添加的文件数量
        - added_folders: 从文件夹中添加的文件数量
        """
        # 刷新文件列表显示
        self.file_panel.refresh()

        # 构建用户反馈消息
        messages = []
        if added_files > 0:
            messages.append(f"{added_files} 个文件")
        if added_folders > 0:
            messages.append(f"文件夹中的 {added_folders} 个文件")

        # 显示处理结果
        if messages:
            msg = f"已添加: {', '.join(messages)}"
            self._show_toast(msg, 'success')
        else:
            self._show_toast("没有找到支持的文件", 'warning')
    
    def _parse_drop_files(self, data):
        if data.startswith('{'):
            files = []
            current = ""
            in_braces = False
            
            for char in data:
                if char == '{':
                    in_braces = True
                elif char == '}':
                    in_braces = False
                    if current:
                        files.append(current)
                        current = ""
                elif in_braces:
                    current += char
            
            return files
        else:
            return data.split()
    
    def _on_file_changed(self, event_type: str, file_path: str):
        # 使用状态栏显示文件变化消息，替代复杂的通知栏
        if event_type == 'modified':
            self.status_bar.show_message(MSG_FILE_MODIFIED.format(filename=os.path.basename(file_path)), 3000)
        elif event_type == 'deleted':
            self.status_bar.show_message(MSG_FILE_DELETED.format(filename=os.path.basename(file_path)), 3000)

    def _refresh_changed_files(self):
        try:
            # 从FileWatcher获取状态管理器中的变化
            changes = self.file_watcher.file_state_manager.get_and_clear_changes()

            if not changes:
                self.status_bar.show_message(MSG_NO_CHANGES, 2000)
                return

            modified_count = 0
            deleted_count = 0

            # 处理每个文件变化
            for change in changes:
                if change.change_type == 'deleted':
                    # 从文件处理器中移除已删除的文件
                    self.file_handler.remove_file(change.path)
                    self.file_watcher.remove_file(change.path)
                    deleted_count += 1
                elif change.change_type == 'modified':
                    # 更新已修改文件的缓存
                    for file_info in self.file_handler.files:
                        if file_info.path == change.path:
                            file_info.update_cache()
                            modified_count += 1
                            break

            # 刷新文件列表面板
            self.file_panel.refresh()

            # 显示刷新结果
            if modified_count > 0 or deleted_count > 0:
                msg = MSG_REFRESH_COMPLETE.format(modified=modified_count, deleted=deleted_count)
                self.status_bar.show_message(msg, 3000)

        except Exception as e:
            self.status_bar.show_message(MSG_REFRESH_FAILED.format(error=str(e)), 3000)
    
        
        
        
    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)  # 为StatusBar预留空间
        
        self.file_panel = FileListPanel(self, self.file_handler)
        self.file_panel.grid(row=0, column=0, sticky='nsew', 
                           padx=(MD.PAD_M, MD.PAD_S), 
                           pady=MD.PAD_M)
        
        self.control_panel = ControlPanel(self, self.file_handler)
        self.control_panel.grid(row=0, column=1, sticky='nsew',
                              padx=(MD.PAD_S, MD.PAD_M),
                              pady=MD.PAD_M)
        
        self.file_panel.set_update_callback(self._on_file_update)
        self.file_panel.set_file_add_callback(self._on_files_added_to_list)
        self.control_panel.set_preview_callback(self._on_preview)
        self.control_panel.set_convert_callback(self._on_convert)
        
        # 创建StatusBar组件
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=1, column=0, columnspan=2, sticky='ew',
                           padx=MD.PAD_M, pady=(0, MD.PAD_M))
        
        # 注册拖放（延迟到UI构建完成后）
        if DRAG_DROP_AVAILABLE:
            self.after(100, self._setup_drag_drop)
    
    def _on_files_added_to_list(self, file_paths: list):
        if not self.watch_enabled:
            return
        
        for file_path in file_paths:
            self.file_watcher.add_file(file_path)
    
    def _on_window_configure(self, event):
        if event.widget != self:
            return
        
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        
        self._resize_after_id = self.after(UI_UPDATE_DEBOUNCE, self._handle_resize)
    
    def _handle_resize(self):
        self._resize_after_id = None
        self.update_idletasks()
    
    def _on_file_update(self, message: str, type: str = 'info'):
        # 使用防抖机制更新状态栏，避免频繁更新
        if self._status_update_after_id:
            self.after_cancel(self._status_update_after_id)

        self._status_update_after_id = self.after(UI_UPDATE_DEBOUNCE,
                                                   lambda: self._debounced_status_update(message, type))

    def _debounced_status_update(self, message: str, type: str = 'info'):
        self._status_update_after_id = None
        self._update_status_bar_stats()
        self._show_toast(message, type)
    
    def _update_status_bar_stats(self):
        stats = self.file_handler.get_processing_statistics()
        self.status_bar.update_stats(
            stats['marked'],
            stats['total'],
            stats['size'],
            stats['languages']
        )
    
    def _on_preview(self, preview_type: str, data):
        if preview_type == 'template':
            TemplatePreviewDialog(self, data)
        
        elif preview_type == 'conversion':
            template = self.control_panel.get_template()
            max_files = self.settings.get('preview_max_files', 5)
            ConversionPreviewDialog(self, data, template, max_files)
        
        elif preview_type == 'warning':
            self._show_toast(f"警告: {data}", 'warning')
    
    def _on_convert(self, action: str, data):
        if action == 'warning':
            self._show_toast(f"警告: {data}", 'warning')
            return
        
        if action == 'start':
            self._perform_conversion(data)
    
    def _perform_conversion(self, files):
        output_file = filedialog.asksaveasfilename(
            title="保存 Markdown 文件",
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if not output_file:
            return
        
        self.control_panel.show_progress()
        
        template = self.control_panel.get_template()
        self.converter.set_markdown_template(template)
        
        # 异步转换
        import threading
        
        def convert_thread():
            def progress_callback(current, total, filename):
                self.after(0, lambda: self.control_panel.update_progress(current, total, filename))
            
            result = self.converter.convert_files(files, output_file, progress_callback)
            self.after(0, lambda: self._on_conversion_complete(result, output_file))
        
        threading.Thread(target=convert_thread, daemon=True).start()
    
    def _on_conversion_complete(self, result, output_file):
        self.after(1000, self.control_panel.hide_progress)
        
        if result['success']:
            self._show_toast(f"成功: {result['message']}", 'success')
            messagebox.showinfo(
                "转换完成",
                f"{result['message']}\n\n保存位置: {output_file}"
            )
        else:
            self._show_toast(f"错误: {result['message']}", 'error')
            messagebox.showerror("转换失败", result['message'])
    
    def _show_toast(self, message: str, type: str = 'info'):
        self.status_bar.show_message(message, type)
    
    def _load_saved_state(self):
        recent_files = self.settings.get('recent_files', [])
        for file_path in recent_files:
            if os.path.exists(file_path):
                self.file_handler.add_file(file_path)
                if self.watch_enabled:
                    self.file_watcher.add_file(file_path)

        self.file_panel.refresh()
        self._update_status_bar_stats()
    
    def _save_state(self):
        geometry = self.geometry().split('+')[0]
        width, height = map(int, geometry.split('x'))
        
        self.settings.set('window', {
            'width': width,
            'height': height,
            'min_width': 1000,
            'min_height': 600
        })
        
        max_recent = self.settings.get('max_recent_files', 50)
        recent_files = [f.path for f in self.file_handler.files[:max_recent]]
        self.settings.set('recent_files', recent_files)
        
        self.settings.set('template', self.control_panel.get_template())
        
        self.settings.save()
    
    def _on_closing(self):
        if self.watch_enabled:
            self.file_watcher.stop()
        
        # 清理StatusBar定时器
        if hasattr(self, 'status_bar'):
            self.status_bar.cleanup()
        
        if self.settings.get('auto_save_config', True):
            self._save_state()
        
        self.destroy()