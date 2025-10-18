"""
控制面板组件 - 使用可滚动容器避免按钮消失
"""

import customtkinter as ctk
import tkinter as tk
from config.theme import MD
from ui.widgets.material_card import Card, Btn
from core.converter import get_template_names, Converter
from core.file_handler import FileHandler, format_size

class ControlPanel(Card):
    """控制面板"""

    def __init__(self, master, file_handler: FileHandler, **kwargs):
        super().__init__(master, **kwargs)
        
        self.file_handler = file_handler
        self.converter = Converter()
        
        self.on_preview_callback = None
        self.on_convert_callback = None
        
        self._build_ui()
    
    def _build_ui(self):
        """构建UI - 使用可滚动框架"""
        # 创建可滚动容器以避免内容被遮挡
        scrollable_container = ctk.CTkScrollableFrame(
            self,
            fg_color='transparent'
        )
        scrollable_container.pack(fill='both', expand=True, padx=MD.PAD_M, pady=MD.PAD_M)
        
        # 标题
        self._build_header(scrollable_container)
        
        # 模板选择
        self._build_template_section(scrollable_container)
        
        
        # 操作按钮（放在可滚动区域内，确保始终可访问）
        self._build_actions(scrollable_container)
        
        # 进度显示（固定在底部）
        self._build_progress()
    
    def _build_header(self, parent):
        """构建标题"""
        header = ctk.CTkFrame(parent, fg_color='transparent')
        header.pack(fill='x', pady=(0, MD.PAD_M))
        
        title_container = ctk.CTkFrame(header, fg_color='transparent')
        title_container.pack(anchor='w')
        
        ctk.CTkLabel(
            title_container,
            text="转换设置",
            font=MD.FONT_HEADLINE,
            text_color=MD.ON_SURFACE
        ).pack(side='left')
        
        ctk.CTkLabel(
            title_container,
            text="⚙️",
            font=("Segoe UI Emoji", 24)
        ).pack(side='left', padx=(MD.PAD_S, 0))
    
    def _build_template_section(self, parent):
        """构建模板选择区域"""
        section = Card(parent, fg_color=MD.BG_SURFACE)
        section.pack(fill='x', pady=(0, MD.PAD_M))
        
        section_container = ctk.CTkFrame(section, fg_color='transparent')
        section_container.pack(fill='both', padx=MD.PAD_M, pady=MD.PAD_M)
        
        # 标题
        ctk.CTkLabel(
            section_container,
            text="Markdown 模板",
            font=MD.FONT_TITLE,
            text_color=MD.TEXT_PRIMARY,
            anchor='w'
        ).pack(fill='x', pady=(0, MD.PAD_S))
        
        # 模板选择下拉框
        self.template_var = tk.StringVar(value="默认")
        template_combo = ctk.CTkComboBox(
            section_container,
            values=get_template_names(),
            variable=self.template_var,
            state='readonly',
            fg_color=MD.BG_SURFACE,
            button_color=MD.ACCENT_BLUE,
            border_color=MD.BORDER,
            font=MD.FONT_UI,
            command=self._on_template_changed
        )
        template_combo.pack(fill='x', pady=(0, MD.PAD_S))
        
        # 预览按钮
        Btn(
            section_container,
            text="预览模板",
            command=self._preview_template,
            kind='normal',
            width=200
        ).pack(fill='x')
    
    
    def _build_actions(self, parent):
        """构建操作按钮 - 现在在滚动区域内"""
        actions = ctk.CTkFrame(parent, fg_color='transparent')
        actions.pack(fill='x', pady=(MD.PAD_M, MD.PAD_M))
        
        Btn(
            actions,
            text="预览转换结果",
            command=self._preview_conversion,
            kind='normal',
            height=48
        ).pack(fill='x', pady=(0, MD.PAD_M))

        Btn(
            actions,
            text="开始转换",
            command=self._start_conversion,
            kind='primary',
            height=56,
            font=MD.FONT_UI
        ).pack(fill='x')
        
        # 添加一些底部空间，确保按钮不会紧贴底部
        ctk.CTkFrame(parent, fg_color='transparent', height=20).pack()
    
    def _build_progress(self):
        """构建进度显示 - 固定在窗口底部"""
        # 在主卡片底部创建固定的进度容器
        self.progress_container = ctk.CTkFrame(self, fg_color=MD.BG_SURFACE, height=60)
        
        progress_content = ctk.CTkFrame(self.progress_container, fg_color='transparent')
        progress_content.pack(fill='both', expand=True, padx=MD.PAD_M, pady=MD.PAD_S)
        
        self.progress_bar = ctk.CTkProgressBar(
            progress_content,
            height=8,
            corner_radius=4,
            fg_color=MD.BG_SURFACE,
            progress_color=MD.ACCENT_BLUE
        )
        self.progress_bar.pack(fill='x', pady=(0, MD.PAD_S))
        
        self.progress_label = ctk.CTkLabel(
            progress_content,
            text="",
            font=MD.FONT_UI,
            text_color=MD.TEXT_SECONDARY
        )
        self.progress_label.pack()
        
        # 初始隐藏
        self.hide_progress()
    
    # 事件处理
    def _on_template_changed(self, template_name):
        """模板改变事件"""
        self.converter.set_template(template_name)
    
    def _preview_template(self):
        """预览模板"""
        if self.on_preview_callback:
            self.on_preview_callback('template', self.template_var.get())
    
    def _preview_conversion(self):
        """预览转换"""
        marked_files = self.file_handler.get_marked_files()
        
        if not marked_files:
            if self.on_preview_callback:
                self.on_preview_callback('warning', '请先选择要预览的文件')
            return
        
        if self.on_preview_callback:
            self.on_preview_callback('conversion', marked_files)
    
    def _start_conversion(self):
        """开始转换"""
        marked_files = self.file_handler.get_marked_files()
        
        if not marked_files:
            if self.on_convert_callback:
                self.on_convert_callback('warning', '请先选择要转换的文件')
            return
        
        if self.on_convert_callback:
            self.on_convert_callback('start', marked_files)
    
    def update_stats(self):
        """更新统计信息 - 现在只更新StatusBar"""
        # 统计信息现在由StatusBar统一显示，这里不需要重复更新
        pass
    
    def show_progress(self):
        """显示进度条"""
        self.progress_container.pack(side='bottom', fill='x', padx=MD.PAD_M, pady=(0, MD.PAD_M))
        self.progress_bar.set(0)
    
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_container.pack_forget()
    
    def update_progress(self, current: int, total: int, filename: str = ""):
        """更新进度"""
        progress = current / total if total > 0 else 0
        self.progress_bar.set(progress)
        
        # 截断过长的文件名
        if len(filename) > 30:
            filename = "..." + filename[-27:]
        
        self.progress_label.configure(
            text=f"正在处理: {filename} ({current}/{total})"
        )
    
    def set_preview_callback(self, callback):
        """设置预览回调"""
        self.on_preview_callback = callback
    
    def set_convert_callback(self, callback):
        """设置转换回调"""
        self.on_convert_callback = callback
    
    def get_template(self) -> str:
        """获取当前模板"""
        return self.template_var.get()