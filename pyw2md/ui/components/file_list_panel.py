"""
文件列表面板组件
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, ttk
from config.theme import MD
from ui.widgets.material_card import MaterialCard, MaterialButton, MaterialEntry
from core.file_handler import FileHandler, get_all_languages, format_size
import os
from pathlib import Path

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
        
        # 文件列表（树状视图）
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
            text="➕ 添加文件",
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
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            right_buttons,
            text="🔄 展开全部",
            command=self._expand_all,
            style='outlined',
            width=100
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            right_buttons,
            text="📁 折叠全部",
            command=self._collapse_all,
            style='outlined',
            width=100
        ).pack(side='left')
    
    def _build_file_list(self, parent):
        """构建文件列表（树状视图）"""
        # 列表容器
        list_container = ctk.CTkFrame(parent, fg_color=MD.SURFACE)
        list_container.pack(fill='both', expand=True, pady=(0, MD.SPACING_MD))
        
        # 创建样式
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置 Treeview 样式以匹配 Material Design
        style.configure(
            "Material.Treeview",
            background=MD.SURFACE,
            foreground=MD.ON_SURFACE,
            fieldbackground=MD.SURFACE,
            borderwidth=0,
            font=MD.FONT_BODY,
            rowheight=32
        )
        
        style.configure(
            "Material.Treeview.Heading",
            background=MD.SURFACE_2,
            foreground=MD.ON_SURFACE,
            borderwidth=1,
            relief="flat",
            font=MD.FONT_TITLE
        )
        
        # 配置选中和悬停样式
        style.map(
            "Material.Treeview",
            background=[('selected', MD.PRIMARY_CONTAINER)],
            foreground=[('selected', MD.ON_PRIMARY_CONTAINER)]
        )
        
        # 创建 Treeview
        columns = ('status', 'language', 'size')
        self.file_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show='tree headings',
            style="Material.Treeview",
            selectmode='browse'
        )
        
        # 配置列
        self.file_tree.column('#0', width=400, minwidth=200, stretch=True)
        self.file_tree.column('status', width=80, minwidth=60, anchor='center', stretch=False)
        self.file_tree.column('language', width=120, minwidth=80, anchor='center', stretch=False)
        self.file_tree.column('size', width=100, minwidth=80, anchor='e', stretch=False)
        
        # 设置列标题
        self.file_tree.heading('#0', text='📁 文件路径', anchor='w')
        self.file_tree.heading('status', text='状态', anchor='center')
        self.file_tree.heading('language', text='语言', anchor='center')
        self.file_tree.heading('size', text='大小', anchor='e')
        
        # 添加滚动条
        vsb = ttk.Scrollbar(list_container, orient="vertical", command=self.file_tree.yview)
        hsb = ttk.Scrollbar(list_container, orient="horizontal", command=self.file_tree.xview)
        self.file_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 布局
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.file_tree.bind('<Double-Button-1>', self._on_item_double_click)
        self.file_tree.bind('<space>', self._on_space_press)
        self.file_tree.bind('<Button-1>', self._on_item_click)
        
        # 存储节点到文件路径的映射
        self.item_to_path = {}
        self.path_to_item = {}
    
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
                self.on_update_callback(f"✅ 成功添加了 {count} 个文件", 'success')
    
    def _add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            count = self.file_handler.add_folder(folder)
            self.refresh()
            
            if self.on_update_callback:
                self.on_update_callback(f"✅ 成功从文件夹添加了 {count} 个文件", 'success')
    
    def _clear_files(self):
        """清空文件"""
        if not self.file_handler.files:
            return
        
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
    
    def _expand_all(self):
        """展开所有节点"""
        def expand_recursive(item):
            self.file_tree.item(item, open=True)
            for child in self.file_tree.get_children(item):
                expand_recursive(child)
        
        for item in self.file_tree.get_children():
            expand_recursive(item)
    
    def _collapse_all(self):
        """折叠所有节点"""
        def collapse_recursive(item):
            self.file_tree.item(item, open=False)
            for child in self.file_tree.get_children(item):
                collapse_recursive(child)
        
        for item in self.file_tree.get_children():
            collapse_recursive(item)
    
    def _filter_files(self):
        """筛选文件"""
        search = self.search_var.get()
        language = self.language_var.get()
        
        filtered = self.file_handler.filter_files(
            search=search if search else None,
            language=language if language != "全部语言" else None
        )
        
        self._display_files(filtered)
    
    def _on_item_click(self, event):
        """单击项目"""
        item = self.file_tree.identify('item', event.x, event.y)
        if item and item in self.item_to_path:
            # 只处理文件节点
            file_path = self.item_to_path[item]
            self._toggle_mark(file_path)
    
    def _on_item_double_click(self, event):
        """双击项目"""
        item = self.file_tree.selection()
        if item:
            # 展开/折叠文件夹
            if self.file_tree.get_children(item[0]):
                current_state = self.file_tree.item(item[0], 'open')
                self.file_tree.item(item[0], open=not current_state)
    
    def _on_space_press(self, event):
        """空格键切换标记"""
        item = self.file_tree.selection()
        if item and item[0] in self.item_to_path:
            file_path = self.item_to_path[item[0]]
            self._toggle_mark(file_path)
    
    def _toggle_mark(self, file_path: str):
        """切换文件标记状态"""
        self.file_handler.toggle_mark(file_path)
        self.refresh()
    
    def _build_tree_structure(self, files):
        """构建树状结构"""
        # 按路径组织文件
        tree_dict = {}
        
        for file_info in files:
            path = Path(file_info.path)
            parts = path.parts
            
            # 构建树状字典
            current = tree_dict
            for i, part in enumerate(parts[:-1]):  # 除了文件名的所有部分
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # 添加文件
            filename = parts[-1]
            current[filename] = file_info
        
        return tree_dict
    
    def _insert_tree_recursive(self, parent_item, tree_dict, prefix=""):
        """递归插入树节点"""
        for name, value in sorted(tree_dict.items()):
            if isinstance(value, dict):
                # 这是一个文件夹
                folder_item = self.file_tree.insert(
                    parent_item,
                    'end',
                    text=f"📁 {name}",
                    values=('', '', ''),
                    open=True
                )
                # 递归处理子项
                self._insert_tree_recursive(folder_item, value, prefix + name + os.sep)
            else:
                # 这是一个文件
                file_info = value
                icon = "✅" if file_info.marked else "⬜"
                
                file_item = self.file_tree.insert(
                    parent_item,
                    'end',
                    text=f"📄 {name}",
                    values=(icon, file_info.language, format_size(file_info.size)),
                    tags=('file',)
                )
                
                # 存储映射关系
                self.item_to_path[file_item] = file_info.path
                self.path_to_item[file_info.path] = file_item
    
    def _display_files(self, files):
        """显示文件列表（树状结构）"""
        # 清空现有内容
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        self.item_to_path.clear()
        self.path_to_item.clear()
        
        if not files:
            # 显示空状态
            empty_item = self.file_tree.insert(
                '',
                'end',
                text='  暂无文件 - 点击上方按钮添加文件或文件夹',
                values=('', '', '')
            )
            return
        
        # 构建树状结构
        tree_structure = self._build_tree_structure(files)
        
        # 插入树节点
        self._insert_tree_recursive('', tree_structure)
    
    def refresh(self):
        """刷新显示"""
        self._filter_files()
        
        # 更新统计
        stats = self.file_handler.get_stats()
        self.stats_label.configure(
            text=f"📊 {stats['marked']}/{stats['total']} 个文件已选中  •  "
                 f"💾 共 {format_size(stats['size'])}  •  "
                 f"🔤 {stats['languages']} 种语言"
        )
    
    def set_update_callback(self, callback):
        """设置更新回调"""
        self.on_update_callback = callback