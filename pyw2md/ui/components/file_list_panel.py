"""
文件列表面板组件
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from config.theme import MD
from ui.widgets.material_card import MaterialCard, MaterialButton, MaterialEntry
from core.file_handler import FileHandler, get_all_languages, format_size

class FileListPanel(MaterialCard):
    """文件列表面板"""
    
    def __init__(self, master, file_handler: FileHandler, **kwargs):
        super().__init__(master, elevation=1, **kwargs)
        
        self.file_handler = file_handler
        self.on_update_callback = None
        
        self._build_ui()
    
    def _build_ui(self):
        """构建UI"""
        # 主容器
        container = ctk.CTkFrame(self, fg_color='transparent')
        container.pack(fill='both', expand=True, padx=MD.SPACING_MD, pady=MD.SPACING_MD)
        
        # 标题栏
        self._build_header(container)
        
        # 搜索和筛选栏
        self._build_search_bar(container)
        
        # 操作按钮栏
        self._build_action_bar(container)
        
        # 文件列表
        self._build_file_list(container)
        
        # 底部统计
        self._build_footer(container)
    
    def _build_header(self, parent):
        """构建标题栏"""
        header = ctk.CTkFrame(parent, fg_color='transparent')
        header.pack(fill='x', pady=(0, MD.SPACING_MD))
        
        # 标题
        title_container = ctk.CTkFrame(header, fg_color='transparent')
        title_container.pack(side='left')
        
        ctk.CTkLabel(
            title_container,
            text="文件管理",
            font=MD.FONT_HEADLINE,
            text_color=MD.ON_SURFACE
        ).pack(side='left')
        
        ctk.CTkLabel(
            title_container,
            text="📁",
            font=("Segoe UI Emoji", 24)
        ).pack(side='left', padx=(MD.SPACING_SM, 0))
    
    def _build_search_bar(self, parent):
        """构建搜索栏"""
        search_bar = ctk.CTkFrame(parent, fg_color='transparent')
        search_bar.pack(fill='x', pady=(0, MD.SPACING_MD))
        
        # 搜索框
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._filter_files())
        
        search_entry = MaterialEntry(
            search_bar,
            textvariable=self.search_var,
            placeholder_text="🔍 搜索文件名...",
            width=300
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, MD.SPACING_SM))
        
        # 语言筛选
        self.language_var = tk.StringVar(value="全部语言")
        self.language_var.trace('w', lambda *args: self._filter_files())
        
        languages = ["全部语言"] + get_all_languages()
        language_combo = ctk.CTkComboBox(
            search_bar,
            values=languages,
            variable=self.language_var,
            state='readonly',
            width=150,
            fg_color=MD.SURFACE_2,
            button_color=MD.PRIMARY,
            border_color=MD.OUTLINE,
            font=MD.FONT_BODY
        )
        language_combo.pack(side='left')
    
    def _build_action_bar(self, parent):
        """构建操作按钮栏"""
        action_bar = ctk.CTkFrame(parent, fg_color='transparent')
        action_bar.pack(fill='x', pady=(0, MD.SPACING_MD))
        
        # 左侧按钮
        left_buttons = ctk.CTkFrame(action_bar, fg_color='transparent')
        left_buttons.pack(side='left')
        
        MaterialButton(
            left_buttons,
            text="📄 添加文件",
            command=self._add_files,
            style='filled',
            width=120
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            left_buttons,
            text="📁 添加文件夹",
            command=self._add_folder,
            style='tonal',
            width=120
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            left_buttons,
            text="🗑️ 清空",
            command=self._clear_files,
            style='error',
            width=100
        ).pack(side='left')
        
        # 右侧按钮
        right_buttons = ctk.CTkFrame(action_bar, fg_color='transparent')
        right_buttons.pack(side='right')
        
        MaterialButton(
            right_buttons,
            text="全选",
            command=lambda: self._mark_all(True),
            style='outlined',
            width=80
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            right_buttons,
            text="全不选",
            command=lambda: self._mark_all(False),
            style='outlined',
            width=80
        ).pack(side='left')
    
    def _build_file_list(self, parent):
        """构建文件列表"""
        # 列表容器
        list_container = ctk.CTkFrame(parent, fg_color=MD.SURFACE)
        list_container.pack(fill='both', expand=True, pady=(0, MD.SPACING_MD))
        
        # 文本框
        self.file_textbox = ctk.CTkTextbox(
            list_container,
            font=MD.FONT_MONO,
            fg_color=MD.SURFACE,
            text_color=MD.ON_SURFACE,
            wrap='none'
        )
        self.file_textbox.pack(fill='both', expand=True)
        
        # 绑定事件
        self.file_textbox.bind('<Button-1>', self._on_file_click)
        self.file_textbox.bind('<space>', lambda e: self._toggle_current_mark())
    
    def _build_footer(self, parent):
        """构建底部统计"""
        footer = ctk.CTkFrame(parent, fg_color='transparent')
        footer.pack(fill='x')
        
        self.stats_label = ctk.CTkLabel(
            footer,
            text="0 个文件",
            font=MD.FONT_BODY,
            text_color=MD.ON_SURFACE_VARIANT
        )
        self.stats_label.pack(side='left')
    
    # 事件处理
    def _add_files(self):
        """添加文件"""
        filetypes = [
            ("所有支持的文件", "*.py *.js *.java *.cpp *.html *.css"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(title="选择代码文件", filetypes=filetypes)
        
        if files:
            count = self.file_handler.add_files(list(files))
            self.refresh()
            
            if self.on_update_callback:
                self.on_update_callback(f"✅ 添加了 {count} 个文件", 'success')
    
    def _add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            count = self.file_handler.add_folder(folder)
            self.refresh()
            
            if self.on_update_callback:
                self.on_update_callback(f"✅ 从文件夹添加了 {count} 个文件", 'success')
    
    def _clear_files(self):
        """清空文件"""
        if not self.file_handler.files:
            return
        
        # 简化版确认（可以后续替换为自定义对话框）
        from tkinter import messagebox
        if messagebox.askyesno("确认清空", "确定要清空所有文件吗？"):
            self.file_handler.clear()
            self.refresh()
            
            if self.on_update_callback:
                self.on_update_callback("🗑️ 已清空文件列表", 'info')
    
    def _mark_all(self, marked: bool):
        """全选/全不选"""
        self.file_handler.mark_all(marked)
        self.refresh()
        
        if self.on_update_callback:
            msg = "✅ 已全选" if marked else "⬜ 已取消全选"
            self.on_update_callback(msg, 'info')
    
    def _filter_files(self):
        """筛选文件"""
        search = self.search_var.get()
        language = self.language_var.get()
        
        filtered = self.file_handler.filter_files(
            search=search if search else None,
            language=language if language != "全部语言" else None
        )
        
        self._display_files(filtered)
    
    def _on_file_click(self, event):
        """文件点击事件"""
        # 获取点击位置的行
        index = self.file_textbox.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        
        # 获取该行内容
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_content = self.file_textbox.get(line_start, line_end)
        
        # 解析文件名并切换标记
        if line_content.strip():
            parts = line_content.strip().split('│')
            if len(parts) >= 2:
                filename = parts[1].strip().lstrip('✓ ').lstrip('☐ ')
                
                # 找到对应文件并切换标记
                for file_info in self.file_handler.files:
                    if file_info.name == filename:
                        self.file_handler.toggle_mark(file_info.path)
                        self.refresh()
                        break
    
    def _toggle_current_mark(self):
        """切换当前行的标记状态"""
        cursor_pos = self.file_textbox.index(tk.INSERT)
        line_num = int(cursor_pos.split('.')[0])
        
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        line_content = self.file_textbox.get(line_start, line_end)
        
        if line_content.strip():
            parts = line_content.strip().split('│')
            if len(parts) >= 2:
                filename = parts[1].strip().lstrip('✓ ').lstrip('☐ ')
                
                for file_info in self.file_handler.files:
                    if file_info.name == filename:
                        self.file_handler.toggle_mark(file_info.path)
                        self.refresh()
                        break
    
    def _display_files(self, files):
        """显示文件列表"""
        self.file_textbox.delete('1.0', 'end')
        
        if not files:
            self.file_textbox.insert('end', '\n  暂无文件\n\n  点击上方按钮添加文件或文件夹')
            return
        
        # 表头
        header = f"{'状态':^6}│ {'文件名':<40} │ {'语言':<15} │ {'大小':<10}\n"
        separator = "─" * 80 + "\n"
        
        self.file_textbox.insert('end', header)
        self.file_textbox.insert('end', separator)
        
        # 文件列表
        for file_info in files:
            icon = "✓" if file_info.marked else "☐"
            name = file_info.name[:38] + '..' if len(file_info.name) > 40 else file_info.name
            language = file_info.language
            size = format_size(file_info.size)
            
            line = f"  {icon:^4}│ {name:<40} │ {language:<15} │ {size:<10}\n"
            self.file_textbox.insert('end', line)
    
    def refresh(self):
        """刷新显示"""
        self._filter_files()
        
        # 更新统计
        stats = self.file_handler.get_stats()
        self.stats_label.configure(
            text=f"{stats['marked']}/{stats['total']} 个文件已选中  •  "
                 f"共 {format_size(stats['size'])}  •  "
                 f"{stats['languages']} 种语言"
        )
    
    def set_update_callback(self, callback):
        """设置更新回调"""
        self.on_update_callback = callback