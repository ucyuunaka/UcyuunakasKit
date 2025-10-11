"""
对话框组件
"""

import customtkinter as ctk
from config.theme import MD
from ui.widgets.material_card import Btn
from core.converter import preview_template, Converter
from core.file_handler import FileInfo

class PreviewDialog(ctk.CTkToplevel):
    """预览对话框基类"""
    
    def __init__(self, parent, title: str, width: int = 800, height: int = 600):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.configure(fg_color=MD.BG_MAIN)
        
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
        header.pack(fill='x', padx=MD.PAD_M, pady=MD.PAD_M)
        header.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header, fg_color='transparent')
        header_content.pack(fill='both', expand=True, padx=MD.PAD_M, pady=MD.PAD_M)
        
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
        content.pack(fill='both', expand=True, padx=MD.PAD_M, pady=(0, MD.PAD_M))
        
        textbox = ctk.CTkTextbox(
            content,
            font=MD.FONT_MONO,
            fg_color=MD.SURFACE,
            text_color=MD.ON_SURFACE,
            wrap='none'
        )
        textbox.pack(fill='both', expand=True, padx=MD.PAD_M, pady=MD.PAD_M)
        
        return textbox
    
    def _build_footer(self):
        """构建底部按钮"""
        footer = ctk.CTkFrame(self, fg_color='transparent')
        footer.pack(fill='x', padx=MD.PAD_M, pady=(0, MD.PAD_M))
        
        Btn(
            footer,
            kind='normal',
            text="关闭",
            command=self.destroy,
            width=120
        ).pack(side='right')
        
        return footer

class TemplatePreviewDialog(PreviewDialog):
    """模板预览对话框"""
    
    def __init__(self, parent, template_name: str):
        super().__init__(parent, f"模板预览 - {template_name}", 700, 500)
        
        self._build_header(
            f"{template_name} 模板",
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