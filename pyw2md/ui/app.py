"""
主应用窗口 - 优化版（拖放降级 + 性能优化）
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

# 导入拖放支持
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
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
from ui.components.dialogs import TemplatePreviewDialog, ConversionPreviewDialog


# ============ 优雅降级基类 ============
class DragDropMixin:
    """拖放功能混合类 - 提供安全的降级处理"""
    
    def drop_target_register(self, *args, **kwargs):
        """安全的拖放注册"""
        if DRAG_DROP_AVAILABLE and hasattr(super(), 'drop_target_register'):
            return super().drop_target_register(*args, **kwargs)
        return None
    
    def dnd_bind(self, *args, **kwargs):
        """安全的拖放绑定"""
        if DRAG_DROP_AVAILABLE and hasattr(super(), 'dnd_bind'):
            return super().dnd_bind(*args, **kwargs)
        return None


if DRAG_DROP_AVAILABLE:
    class AppBase(DragDropMixin, TkinterDnD.Tk):
        """支持拖放的基类"""
        def __init__(self):
            TkinterDnD.Tk.__init__(self)
else:
    class AppBase(DragDropMixin, ctk.CTk):
        """不支持拖放的降级基类"""
        def __init__(self):
            ctk.CTk.__init__(self)


class MaterialApp(AppBase):
    """主应用程序 - 性能优化版"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化
        self.settings = Settings()
        self.file_handler = FileHandler()
        self.converter = Converter()
        
        # 文件监控器
        self.file_watcher = FileWatcher(self._on_file_changed)
        self.watch_enabled = self.settings.get('auto_watch_files', True)
        
        # 修改文件跟踪
        self.modified_files = set()
        self.deleted_files = set()
        
        # 窗口调整防抖
        self._resize_after_id = None
        
        self._setup_window()
        self._build_ui()
        self._setup_drag_drop()
        self._load_saved_state()
        
        # 启动文件监控
        if self.watch_enabled:
            self.file_watcher.start()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.bind('<Configure>', self._on_window_configure)
    
    def _setup_window(self):
        """设置窗口"""
        self.title("代码转Markdown工具 - 性能优化版")
        
        width = self.settings.get('window', {}).get('width', 1280)
        height = self.settings.get('window', {}).get('height', 800)
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        min_width = self.settings.get('window', {}).get('min_width', 1000)
        min_height = self.settings.get('window', {}).get('min_height', 600)
        self.minsize(min_width, min_height)
        
        # 统一背景色设置
        self._set_background_color()
    
    def _set_background_color(self):
        """设置背景色 - 兼容不同父类"""
        try:
            if DRAG_DROP_AVAILABLE:
                self.configure(bg=MD.BACKGROUND)
            else:
                self.configure(fg_color=MD.BACKGROUND)
        except Exception as e:
            print(f"设置背景色失败: {e}")
    
    def _setup_drag_drop(self):
        """设置拖放功能 - 安全降级"""
        if not DRAG_DROP_AVAILABLE:
            print("拖放功能不可用，已降级为文件选择模式")
            self._show_drag_drop_hint()
            return
        
        try:
            # 为主窗口注册拖放
            self.drop_target_register(DND_FILES)
            self.dnd_bind('<<Drop>>', self._on_drop)
            
            # 为文件列表面板注册拖放
            if hasattr(self, 'file_panel'):
                self.file_panel.drop_target_register(DND_FILES)
                self.file_panel.dnd_bind('<<Drop>>', self._on_drop)
            
            print("拖放功能已启用")
        except Exception as e:
            print(f"警告: 拖放功能初始化失败: {e}")
    
    def _show_drag_drop_hint(self):
        """显示拖放功能提示"""
        hint = ctk.CTkLabel(
            self,
            text="💡 提示: 安装 tkinterdnd2 启用拖放功能",
            font=MD.FONT_LABEL,
            text_color=MD.WARNING
        )
        hint.pack(side='top', pady=MD.SPACING_SM)
        self.after(5000, hint.destroy)
    
    def _on_drop(self, event):
        """处理拖放事件"""
        files = self._parse_drop_files(event.data)
        
        if not files:
            return
        
        # 异步处理拖放文件
        self._process_dropped_files_async(files)
    
    def _process_dropped_files_async(self, files):
        """异步处理拖放的文件"""
        import threading
        
        def process():
            added_files = 0
            added_folders = 0
            
            for path in files:
                if os.path.isfile(path):
                    if self.file_handler.add_file(path):
                        added_files += 1
                        if self.watch_enabled:
                            self.file_watcher.add_file(path)
                elif os.path.isdir(path):
                    count = self.file_handler.add_folder(path)
                    added_folders += count
                    if self.watch_enabled:
                        for file_info in self.file_handler.files[-count:]:
                            self.file_watcher.add_file(file_info.path)
            
            # UI更新必须在主线程
            self.after(0, lambda: self._on_drop_complete(added_files, added_folders))
        
        threading.Thread(target=process, daemon=True).start()
    
    def _on_drop_complete(self, added_files, added_folders):
        """拖放完成回调"""
        self.file_panel.refresh()
        self.control_panel.update_stats()
        
        messages = []
        if added_files > 0:
            messages.append(f"{added_files} 个文件")
        if added_folders > 0:
            messages.append(f"文件夹中的 {added_folders} 个文件")
        
        if messages:
            msg = f"已添加: {', '.join(messages)}"
            self._show_toast(msg, 'success')
        else:
            self._show_toast("没有找到支持的文件", 'warning')
    
    def _parse_drop_files(self, data):
        """解析拖放的文件路径"""
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
        """文件变化回调"""
        if event_type == 'modified':
            self.modified_files.add(file_path)
            self._show_file_change_notification()
        elif event_type == 'deleted':
            self.deleted_files.add(file_path)
            self._show_file_change_notification()
    
    def _show_file_change_notification(self):
        """显示文件变化通知"""
        modified_count = len(self.modified_files)
        deleted_count = len(self.deleted_files)
        
        messages = []
        if modified_count > 0:
            messages.append(f"{modified_count} 个文件已修改")
        if deleted_count > 0:
            messages.append(f"{deleted_count} 个文件已删除")
        
        if messages:
            msg = "检测到文件变化: " + ", ".join(messages)
            
            if not hasattr(self, 'notification_bar') or not self.notification_bar.winfo_exists():
                self._create_notification_bar(msg)
            else:
                self.notification_label.configure(text=msg)
    
    def _create_notification_bar(self, message: str):
        """创建通知栏"""
        self.notification_bar = ctk.CTkFrame(
            self,
            fg_color=MD.WARNING_CONTAINER,
            height=50
        )
        self.notification_bar.pack(side='top', fill='x', padx=MD.SPACING_LG, pady=(MD.SPACING_LG, 0))
        
        content = ctk.CTkFrame(self.notification_bar, fg_color='transparent')
        content.pack(fill='both', expand=True, padx=MD.SPACING_MD, pady=MD.SPACING_SM)
        
        self.notification_label = ctk.CTkLabel(
            content,
            text=message,
            font=MD.FONT_BODY,
            text_color=MD.ON_SURFACE
        )
        self.notification_label.pack(side='left', padx=(0, MD.SPACING_MD))
        
        button_frame = ctk.CTkFrame(content, fg_color='transparent')
        button_frame.pack(side='right')
        
        ctk.CTkButton(
            button_frame,
            text="刷新",
            command=self._refresh_changed_files,
            fg_color=MD.PRIMARY,
            hover_color=MD.PRIMARY_CONTAINER,
            width=80,
            height=32
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        ctk.CTkButton(
            button_frame,
            text="关闭",
            command=self._close_notification,
            fg_color='transparent',
            hover_color=MD.SURFACE_2,
            width=32,
            height=32
        ).pack(side='left')
    
    def _refresh_changed_files(self):
        """刷新变化的文件"""
        for file_path in self.deleted_files:
            self.file_handler.remove_file(file_path)
            self.file_watcher.remove_file(file_path)
        
        for file_path in self.modified_files:
            for file_info in self.file_handler.files:
                if file_info.path == file_path:
                    file_info.update_cache()
                    break
        
        self.file_panel.refresh()
        self.control_panel.update_stats()
        
        modified_count = len(self.modified_files)
        deleted_count = len(self.deleted_files)
        self.modified_files.clear()
        self.deleted_files.clear()
        
        self._close_notification()
        
        msg = f"已刷新: {modified_count} 个修改, {deleted_count} 个删除"
        self._show_toast(msg, 'success')
    
    def _close_notification(self):
        """关闭通知栏"""
        if hasattr(self, 'notification_bar') and self.notification_bar.winfo_exists():
            self.notification_bar.destroy()
        
        self.modified_files.clear()
        self.deleted_files.clear()
    
    def _build_ui(self):
        """构建UI"""
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.file_panel = FileListPanel(self, self.file_handler)
        self.file_panel.grid(row=0, column=0, sticky='nsew', 
                           padx=(MD.SPACING_LG, MD.SPACING_SM), 
                           pady=MD.SPACING_LG)
        
        self.control_panel = ControlPanel(self, self.file_handler)
        self.control_panel.grid(row=0, column=1, sticky='nsew',
                              padx=(MD.SPACING_SM, MD.SPACING_LG),
                              pady=MD.SPACING_LG)
        
        self.file_panel.set_update_callback(self._on_file_update)
        self.file_panel.set_file_add_callback(self._on_files_added_to_list)
        self.control_panel.set_preview_callback(self._on_preview)
        self.control_panel.set_convert_callback(self._on_convert)
        
        # 注册拖放（延迟到UI构建完成后）
        if DRAG_DROP_AVAILABLE:
            self.after(100, self._setup_drag_drop)
        
        self.toast_label = None
    
    def _on_files_added_to_list(self, file_paths: list):
        """文件添加到列表的回调"""
        if not self.watch_enabled:
            return
        
        for file_path in file_paths:
            self.file_watcher.add_file(file_path)
    
    def _on_window_configure(self, event):
        """窗口调整事件"""
        if event.widget != self:
            return
        
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        
        self._resize_after_id = self.after(100, self._handle_resize)
    
    def _handle_resize(self):
        """处理窗口调整"""
        self._resize_after_id = None
        self.update_idletasks()
    
    def _on_file_update(self, message: str, type: str = 'info'):
        """文件更新回调"""
        self.control_panel.update_stats()
        self._show_toast(message, type)
    
    def _on_preview(self, preview_type: str, data):
        """预览回调"""
        if preview_type == 'template':
            TemplatePreviewDialog(self, data)
        
        elif preview_type == 'conversion':
            template = self.control_panel.get_template()
            max_files = self.settings.get('preview_max_files', 5)
            ConversionPreviewDialog(self, data, template, max_files)
        
        elif preview_type == 'warning':
            self._show_toast(f"警告: {data}", 'warning')
    
    def _on_convert(self, action: str, data):
        """转换回调"""
        if action == 'warning':
            self._show_toast(f"警告: {data}", 'warning')
            return
        
        if action == 'start':
            self._perform_conversion(data)
    
    def _perform_conversion(self, files):
        """执行转换 - 异步优化"""
        output_file = filedialog.asksaveasfilename(
            title="保存 Markdown 文件",
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if not output_file:
            return
        
        self.control_panel.show_progress()
        
        template = self.control_panel.get_template()
        self.converter.set_template(template)
        
        # 异步转换
        import threading
        
        def convert_thread():
            def progress_callback(current, total, filename):
                self.after(0, lambda: self.control_panel.update_progress(current, total, filename))
            
            result = self.converter.convert_files(files, output_file, progress_callback)
            self.after(0, lambda: self._on_conversion_complete(result, output_file))
        
        threading.Thread(target=convert_thread, daemon=True).start()
    
    def _on_conversion_complete(self, result, output_file):
        """转换完成回调"""
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
        """显示通知消息"""
        colors = {
            'success': MD.SUCCESS,
            'error': MD.ERROR,
            'warning': MD.WARNING,
            'info': MD.INFO
        }
        
        color = colors.get(type, MD.INFO)
        
        if self.toast_label:
            self.toast_label.destroy()
        
        self.toast_label = ctk.CTkLabel(
            self,
            text=message,
            font=MD.FONT_BODY,
            fg_color=color,
            text_color=MD.ON_PRIMARY,
            corner_radius=MD.RADIUS_MEDIUM,
            height=48
        )
        
        self.toast_label.place(relx=0.5, rely=0.92, anchor='center')
        
        self.after(3000, lambda: self.toast_label.destroy() if self.toast_label else None)
    
    def _load_saved_state(self):
        """加载保存的状态"""
        recent_files = self.settings.get('recent_files', [])
        for file_path in recent_files:
            if os.path.exists(file_path):
                self.file_handler.add_file(file_path)
                if self.watch_enabled:
                    self.file_watcher.add_file(file_path)
        
        self.file_panel.refresh()
        self.control_panel.update_stats()
    
    def _save_state(self):
        """保存状态"""
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
        """关闭窗口"""
        if self.watch_enabled:
            self.file_watcher.stop()
        
        if self.settings.get('auto_save_config', True):
            self._save_state()
        
        self.destroy()