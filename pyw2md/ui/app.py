"""
主应用窗口 - 性能优化版
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import os

from config.theme import MD
from config.settings import Settings
from core.file_handler import FileHandler
from core.converter import Converter
from ui.components.file_list_panel import FileListPanel
from ui.components.control_panel import ControlPanel
from ui.components.dialogs import TemplatePreviewDialog, ConversionPreviewDialog

class MaterialApp(ctk.CTk):
    """主应用程序"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化
        self.settings = Settings()
        self.file_handler = FileHandler()
        self.converter = Converter()
        
        # 窗口调整防抖
        self._resize_after_id = None
        
        self._setup_window()
        self._build_ui()
        self._load_saved_state()
        
        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 绑定窗口调整事件
        self.bind('<Configure>', self._on_window_configure)
    
    def _setup_window(self):
        """设置窗口"""
        self.title("代码转Markdown工具")
        
        # 窗口大小
        width = self.settings.get('window', {}).get('width', 1280)
        height = self.settings.get('window', {}).get('height', 800)
        
        # 居中显示
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # 最小尺寸
        min_width = self.settings.get('window', {}).get('min_width', 1000)
        min_height = self.settings.get('window', {}).get('min_height', 600)
        self.minsize(min_width, min_height)
        
        # 背景色
        self.configure(fg_color=MD.BACKGROUND)
    
    def _build_ui(self):
        """构建UI"""
        # 配置网格
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # 文件列表面板
        self.file_panel = FileListPanel(self, self.file_handler)
        self.file_panel.grid(row=0, column=0, sticky='nsew', 
                           padx=(MD.SPACING_LG, MD.SPACING_SM), 
                           pady=MD.SPACING_LG)
        
        # 控制面板
        self.control_panel = ControlPanel(self, self.file_handler)
        self.control_panel.grid(row=0, column=1, sticky='nsew',
                              padx=(MD.SPACING_SM, MD.SPACING_LG),
                              pady=MD.SPACING_LG)
        
        # 设置回调
        self.file_panel.set_update_callback(self._on_file_update)
        self.control_panel.set_preview_callback(self._on_preview)
        self.control_panel.set_convert_callback(self._on_convert)
        
        # 通知标签
        self.toast_label = None
    
    def _on_window_configure(self, event):
        """窗口调整事件 - 添加防抖"""
        # 只处理主窗口的resize事件
        if event.widget != self:
            return
        
        # 取消之前的延迟调用
        if self._resize_after_id:
            self.after_cancel(self._resize_after_id)
        
        # 延迟处理resize，避免频繁重绘
        self._resize_after_id = self.after(100, self._handle_resize)
    
    def _handle_resize(self):
        """处理窗口调整"""
        self._resize_after_id = None
        # 强制更新布局
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
            self._show_toast(f"⚠️ {data}", 'warning')
    
    def _on_convert(self, action: str, data):
        """转换回调"""
        if action == 'warning':
            self._show_toast(f"⚠️ {data}", 'warning')
            return
        
        if action == 'start':
            self._perform_conversion(data)
    
    def _perform_conversion(self, files):
        """执行转换"""
        output_file = filedialog.asksaveasfilename(
            title="保存 Markdown 文件",
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if not output_file:
            return
        
        # 显示进度
        self.control_panel.show_progress()
        
        # 设置转换器
        template = self.control_panel.get_template()
        self.converter.set_template(template)
        
        # 进度回调
        def progress_callback(current, total, filename):
            self.control_panel.update_progress(current, total, filename)
            self.update_idletasks()
        
        # 执行转换
        result = self.converter.convert_files(files, output_file, progress_callback)
        
        # 隐藏进度
        self.after(1000, self.control_panel.hide_progress)
        
        # 显示结果
        if result['success']:
            self._show_toast(f"成功: {result['message']}", 'success')
            messagebox.showinfo(
                "转换完成",
                f"{result['message']}\n\n保存位置: {output_file}"
            )
        else:
            self._show_toast(f"❌ {result['message']}", 'error')
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
        if self.settings.get('auto_save_config', True):
            self._save_state()
        
        self.destroy()