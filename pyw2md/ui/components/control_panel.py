"""
控制面板组件
"""

import customtkinter as ctk
import tkinter as tk
from config.theme import MD
from ui.widgets.material_card import MaterialCard, MaterialButton, StatCard
from core.converter import get_template_names, Converter
from core.file_handler import FileHandler, format_size

class ControlPanel(MaterialCard):
    """控制面板"""
    
    def __init__(self, master, file_handler: FileHandler, **kwargs):
        super().__init__(master, elevation=1, **kwargs)
        
        self.file_handler = file_handler
        self.converter = Converter()
        
        self.on_preview_callback = None
        self.on_convert_callback = None
        
        self._build_ui()
    
    def _build_ui(self):
        """构建UI"""
        container = ctk.CTkFrame(self, fg_color='transparent')
        container.pack(fill='both', expand=True, padx=MD.SPACING_MD, pady=MD.SPACING_MD)
        
        # 标题
        self._build_header(container)
        
        # 模板选择
        self._build_template_section(container)
        
        # 统计卡片
        self._build_stats_section(container)
        
        # 操作按钮
        self._build_actions(container)
        
        # 进度显示
        self._build_progress(container)
    
    def _build_header(self, parent):
        """构建标题"""
        header = ctk.CTkFrame(parent, fg_color='transparent')
        header.pack(fill='x', pady=(0, MD.SPACING_LG))
        
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
        ).pack(side='left', padx=(MD.SPACING_SM, 0))
    
    def _build_template_section(self, parent):
        """构建模板选择区域"""
        section = MaterialCard(parent, elevation=0, fg_color=MD.SURFACE_2)
        section.pack(fill='x', pady=(0, MD.SPACING_MD))
        
        section_container = ctk.CTkFrame(section, fg_color='transparent')
        section_container.pack(fill='both', padx=MD.SPACING_MD, pady=MD.SPACING_MD)
        
        # 标题
        ctk.CTkLabel(
            section_container,
            text="Markdown 模板",
            font=MD.FONT_TITLE,
            text_color=MD.ON_SURFACE,
            anchor='w'
        ).pack(fill='x', pady=(0, MD.SPACING_SM))
        
        # 模板选择下拉框
        self.template_var = tk.StringVar(value="默认")
        template_combo = ctk.CTkComboBox(
            section_container,
            values=get_template_names(),
            variable=self.template_var,
            state='readonly',
            fg_color=MD.SURFACE,
            button_color=MD.PRIMARY,
            border_color=MD.OUTLINE,
            font=MD.FONT_BODY,
            command=self._on_template_changed
        )
        template_combo.pack(fill='x', pady=(0, MD.SPACING_SM))
        
        # 预览按钮
        MaterialButton(
            section_container,
            text="👁️ 预览模板",
            command=self._preview_template,
            style='outlined',
            width=200
        ).pack(fill='x')
    
    def _build_stats_section(self, parent):
        """构建统计区域"""
        # 区域标题
        ctk.CTkLabel(
            parent,
            text="📊 统计信息",
            font=MD.FONT_TITLE,
            text_color=MD.ON_SURFACE,
            anchor='w'
        ).pack(fill='x', pady=(MD.SPACING_MD, MD.SPACING_SM))
        
        # 统计卡片网格
        stats_grid = ctk.CTkFrame(parent, fg_color='transparent')
        stats_grid.pack(fill='x', pady=(0, MD.SPACING_MD))
        
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        
        # 创建统计卡片
        self.stat_cards = {
            'total': StatCard(stats_grid, "📄", "总文件", "0"),
            'marked': StatCard(stats_grid, "✅", "已选中", "0"),
            'size': StatCard(stats_grid, "💾", "总大小", "0 B"),
            'languages': StatCard(stats_grid, "🏷️", "语言数", "0")
        }
        
        self.stat_cards['total'].grid(row=0, column=0, sticky='ew', padx=(0, MD.SPACING_XS), pady=(0, MD.SPACING_XS))
        self.stat_cards['marked'].grid(row=0, column=1, sticky='ew', padx=(MD.SPACING_XS, 0), pady=(0, MD.SPACING_XS))
        self.stat_cards['size'].grid(row=1, column=0, sticky='ew', padx=(0, MD.SPACING_XS), pady=(MD.SPACING_XS, 0))
        self.stat_cards['languages'].grid(row=1, column=1, sticky='ew', padx=(MD.SPACING_XS, 0), pady=(MD.SPACING_XS, 0))
    
    def _build_actions(self, parent):
        """构建操作按钮"""
        actions = ctk.CTkFrame(parent, fg_color='transparent')
        actions.pack(fill='x', pady=(MD.SPACING_LG, 0))
        
        MaterialButton(
            actions,
            text="👁️ 预览转换结果",
            command=self._preview_conversion,
            style='tonal',
            height=48
        ).pack(fill='x', pady=(0, MD.SPACING_SM))
        
        MaterialButton(
            actions,
            text="🚀 开始转换",
            command=self._start_conversion,
            style='success',
            height=56,
            font=MD.FONT_BODY_LARGE
        ).pack(fill='x')
    
    def _build_progress(self, parent):
        """构建进度显示"""
        self.progress_container = ctk.CTkFrame(parent, fg_color='transparent')
        self.progress_container.pack(fill='x', pady=(MD.SPACING_MD, 0))
        
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_container,
            height=8,
            corner_radius=4,
            fg_color=MD.SURFACE_2,
            progress_color=MD.PRIMARY
        )
        
        self.progress_label = ctk.CTkLabel(
            self.progress_container,
            text="",
            font=MD.FONT_LABEL,
            text_color=MD.ON_SURFACE_VARIANT
        )
        
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
        """更新统计信息"""
        stats = self.file_handler.get_stats()
        
        self.stat_cards['total'].update_value(str(stats['total']))
        self.stat_cards['marked'].update_value(str(stats['marked']))
        self.stat_cards['size'].update_value(format_size(stats['size']))
        self.stat_cards['languages'].update_value(str(stats['languages']))
    
    def show_progress(self):
        """显示进度条"""
        self.progress_bar.pack(fill='x', pady=(0, MD.SPACING_SM))
        self.progress_label.pack()
        self.progress_bar.set(0)
    
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_bar.pack_forget()
        self.progress_label.pack_forget()
    
    def update_progress(self, current: int, total: int, filename: str = ""):
        """更新进度"""
        progress = current / total if total > 0 else 0
        self.progress_bar.set(progress)
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
```

### 9. `ui/components/dialogs.py` - 对话框组件

```python
"""
对话框组件
"""

import customtkinter as ctk
from config.theme import MD
from ui.widgets.material_card import MaterialButton
from core.converter import preview_template, Converter
from core.file_handler import FileInfo

class PreviewDialog(ctk.CTkToplevel):
    """预览对话框基类"""
    
    def __init__(self, parent, title: str, width: int = 800, height: int = 600):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=MD.BACKGROUND)
        
        # 居中显示
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # 模态
        self.transient(parent)
        self.grab_set()
    
    def _build_header(self, title: str, subtitle: str = ""):
        """构建头部"""
        header = ctk.CTkFrame(self, fg_color=MD.SURFACE_1, height=80)
        header.pack(fill='x', padx=MD.SPACING_LG, pady=MD.SPACING_LG)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color='transparent')
        header_content.pack(fill='both', expand=True, padx=MD.SPACING_MD, pady=MD.SPACING_MD)
        
        ctk.CTkLabel(
            header_content,
            text=title,
            font=MD.FONT_HEADLINE,
            text_color=MD.ON_SURFACE
        ).pack(anchor='w')
        
        if subtitle:
            ctk.CTkLabel(
                header_content,
                text=subtitle,
                font=MD.FONT_BODY,
                text_color=MD.ON_SURFACE_VARIANT
            ).pack(anchor='w', pady=(MD.SPACING_XS, 0))
        
        return header
    
    def _build_content_area(self):
        """构建内容区域"""
        content = ctk.CTkFrame(self, fg_color=MD.SURFACE)
        content.pack(fill='both', expand=True, padx=MD.SPACING_LG, pady=(0, MD.SPACING_LG))
        
        textbox = ctk.CTkTextbox(
            content,
            font=MD.FONT_MONO,
            fg_color=MD.SURFACE,
            text_color=MD.ON_SURFACE,
            wrap='none'
        )
        textbox.pack(fill='both', expand=True, padx=MD.SPACING_MD, pady=MD.SPACING_MD)
        
        return textbox
    
    def _build_footer(self):
        """构建底部按钮"""
        footer = ctk.CTkFrame(self, fg_color='transparent')
        footer.pack(fill='x', padx=MD.SPACING_LG, pady=(0, MD.SPACING_LG))
        
        MaterialButton(
            footer,
            text="关闭",
            command=self.destroy,
            style='text',
            width=120
        ).pack(side='right')
        
        return footer

class TemplatePreviewDialog(PreviewDialog):
    """模板预览对话框"""
    
    def __init__(self, parent, template_name: str):
        super().__init__(parent, f"模板预览 - {template_name}", 700, 500)
        
        self._build_header(
            f"📋 {template_name} 模板",
            "查看模板的格式和结构"
        )
        
        textbox = self._build_content_area()
        
        # 显示模板内容
        template_content = preview_template(template_name)
        textbox.insert('1.0', template_content)
        textbox.configure(state='disabled')
        
        self._build_footer()

class ConversionPreviewDialog(PreviewDialog):
    """转换预览对话框"""
    
    def __init__(self, parent, files: list[FileInfo], template: str, max_files: int = 5):
        super().__init__(parent, "转换预览", 900, 700)
        
        self._build_header(
            f"👁️ 转换预览",
            f"使用 {template} 模板  •  预览前 {min(len(files), max_files)} 个文件"
        )
        
        textbox = self._build_content_area()
        
        # 生成预览内容
        converter = Converter(template)
        preview_content = []
        
        for i, file_info in enumerate(files[:max_files]):
            preview_content.append(converter.convert_file(file_info))
        
        if len(files) > max_files:
            preview_content.append(
                f"\n{'='*80}\n"
                f"... 还有 {len(files) - max_files} 个文件未在预览中显示 ...\n"
                f"{'='*80}\n"
            )
        
        textbox.insert('1.0', ''.join(preview_content))
        textbox.configure(state='disabled')
        
        self._build_footer()