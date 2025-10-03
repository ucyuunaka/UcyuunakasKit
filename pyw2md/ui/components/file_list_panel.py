"""
文件列表面板组件 - 虚拟化渲染优化版
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, ttk
from config.theme import MD
from ui.widgets.material_card import MaterialCard, MaterialButton, MaterialEntry
from core.file_handler import FileHandler, get_all_languages, format_size
import os
from pathlib import Path
import threading

class FileListPanel(MaterialCard):
    """文件列表面板 - 性能优化版"""
    
    # 渲染优化参数
    BATCH_SIZE = 100  # 每批渲染的节点数
    RENDER_DELAY = 10  # 批次间延迟（毫秒）
    
    def __init__(self, master, file_handler: FileHandler, **kwargs):
        super().__init__(master, elevation=1, **kwargs)

        self.file_handler = file_handler
        self.on_update_callback = None
        self.on_file_add_callback = None
        self._refresh_pending = False
        self._loading = False
        self._loading_animation_id = None
        self._update_lock = False
        self._render_queue = []  # 渲染队列
        self._render_job_id = None  # 渲染任务ID

        self._build_ui()
    
    def _build_ui(self):
        """构建UI"""
        container = ctk.CTkFrame(self, fg_color='transparent')
        container.pack(fill='both', expand=True, padx=MD.SPACING_MD, pady=MD.SPACING_MD)
        
        self._build_header(container)
        self._build_search_bar(container)
        self._build_action_bar(container)
        self._build_file_list(container)
        self._build_footer(container)
    
    def _build_header(self, parent):
        """构建标题栏"""
        header = ctk.CTkFrame(parent, fg_color='transparent')
        header.pack(fill='x', pady=(0, MD.SPACING_MD))
        
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
        
        # 加载指示器
        self.loading_container = ctk.CTkFrame(header, fg_color=MD.SURFACE_2, corner_radius=MD.RADIUS_MEDIUM)
        
        self.loading_progress = ctk.CTkProgressBar(
            self.loading_container,
            height=6,
            corner_radius=3,
            fg_color=MD.SURFACE,
            progress_color=MD.PRIMARY,
            mode='indeterminate'
        )
        self.loading_progress.pack(padx=MD.SPACING_MD, pady=(MD.SPACING_SM, MD.SPACING_XS))
        
        self.loading_label = ctk.CTkLabel(
            self.loading_container,
            text="加载中...",
            font=MD.FONT_BODY,
            text_color=MD.PRIMARY
        )
        self.loading_label.pack(padx=MD.SPACING_MD, pady=(0, MD.SPACING_SM))
    
    def _build_search_bar(self, parent):
        """构建搜索栏"""
        search_bar = ctk.CTkFrame(parent, fg_color='transparent')
        search_bar.pack(fill='x', pady=(0, MD.SPACING_MD))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._schedule_refresh())
        
        search_entry = MaterialEntry(
            search_bar,
            textvariable=self.search_var,
            placeholder_text="🔍 搜索文件名...",
            width=300
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, MD.SPACING_SM))
        
        self.language_var = tk.StringVar(value="全部语言")
        self.language_var.trace('w', lambda *args: self._schedule_refresh())
        
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
        
        action_bar.grid_columnconfigure(0, weight=1)
        action_bar.grid_columnconfigure(1, weight=0)
        
        left_buttons = ctk.CTkFrame(action_bar, fg_color='transparent')
        left_buttons.grid(row=0, column=0, sticky='w', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            left_buttons,
            text="➕ 文件",
            command=self._add_files,
            style='filled',
            width=100
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            left_buttons,
            text="📁 文件夹",
            command=self._add_folder,
            style='tonal',
            width=100
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            left_buttons,
            text="🔄",
            command=self._refresh_files,
            style='outlined',
            width=50
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            left_buttons,
            text="🗑️",
            command=self._clear_files,
            style='error',
            width=50
        ).pack(side='left')
        
        right_buttons = ctk.CTkFrame(action_bar, fg_color='transparent')
        right_buttons.grid(row=0, column=1, sticky='e')
        
        MaterialButton(
            right_buttons,
            text="全选",
            command=lambda: self._mark_all(True),
            style='outlined',
            width=60
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            right_buttons,
            text="全不选",
            command=lambda: self._mark_all(False),
            style='outlined',
            width=70
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            right_buttons,
            text="展开",
            command=self._expand_all,
            style='outlined',
            width=60
        ).pack(side='left', padx=(0, MD.SPACING_SM))
        
        MaterialButton(
            right_buttons,
            text="折叠",
            command=self._collapse_all,
            style='outlined',
            width=60
        ).pack(side='left')
    
    def _build_file_list(self, parent):
        """构建文件列表（树状视图）"""
        list_container = ctk.CTkFrame(parent, fg_color=MD.SURFACE)
        list_container.pack(fill='both', expand=True, pady=(0, MD.SPACING_MD))
        
        style = ttk.Style()
        style.theme_use('clam')
        
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
        
        style.map(
            "Material.Treeview",
            background=[('selected', MD.PRIMARY_CONTAINER)],
            foreground=[('selected', MD.ON_PRIMARY_CONTAINER)]
        )
        
        columns = ('status', 'language', 'size')
        self.file_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show='tree headings',
            style="Material.Treeview",
            selectmode='browse'
        )
        
        self.file_tree.column('#0', width=400, minwidth=200, stretch=True)
        self.file_tree.column('status', width=80, minwidth=60, anchor='center', stretch=False)
        self.file_tree.column('language', width=120, minwidth=80, anchor='center', stretch=False)
        self.file_tree.column('size', width=100, minwidth=80, anchor='e', stretch=False)
        
        self.file_tree.heading('#0', text='📁 文件路径', anchor='w')
        self.file_tree.heading('status', text='状态', anchor='center')
        self.file_tree.heading('language', text='语言', anchor='center')
        self.file_tree.heading('size', text='大小', anchor='e')
        
        vsb = ttk.Scrollbar(list_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=vsb.set)
        
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        self.file_tree.bind('<Double-Button-1>', self._on_item_double_click)
        self.file_tree.bind('<space>', self._on_space_press)
        self.file_tree.bind('<Button-1>', self._on_item_click)
        
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
    
    def _add_files(self):
        """添加文件"""
        filetypes = [
            ("所有支持的文件", "*.py *.js *.java *.cpp *.html *.css"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(title="选择代码文件", filetypes=filetypes)
        
        if files:
            self._show_loading(True)
            def add_files_thread():
                count = self.file_handler.add_files(list(files))
                self.after(0, lambda: self._on_files_added(count))
            
            thread = threading.Thread(target=add_files_thread, daemon=True)
            thread.start()
    
    def _on_files_added(self, count):
        """文件添加完成回调"""
        self._show_loading(False)
        self.refresh()

        if self.on_file_add_callback:
            added_files = [f.path for f in self.file_handler.files[-count:]] if count > 0 else []
            self.on_file_add_callback(added_files)

        if self.on_update_callback:
            self.on_update_callback(f"✅ 成功添加了 {count} 个文件", 'success')
    
    def _add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            self._show_loading(True)
            def add_folder_thread():
                count = self.file_handler.add_folder(folder)
                self.after(0, lambda: self._on_folder_added(count))
            
            thread = threading.Thread(target=add_folder_thread, daemon=True)
            thread.start()
    
    def _on_folder_added(self, count):
        """文件夹添加完成回调"""
        self._show_loading(False)
        self.refresh()

        if self.on_file_add_callback:
            added_files = [f.path for f in self.file_handler.files[-count:]] if count > 0 else []
            self.on_file_add_callback(added_files)

        if self.on_update_callback:
            self.on_update_callback(f"✅ 成功从文件夹添加了 {count} 个文件", 'success')
    
    def _refresh_files(self):
        """刷新文件列表"""
        if self._loading:
            return
        
        self._show_loading(True)
        
        def refresh_thread():
            result = self.file_handler.refresh_files()
            self.after(0, lambda: self._on_files_refreshed(result))
        
        thread = threading.Thread(target=refresh_thread, daemon=True)
        thread.start()
    
    def _on_files_refreshed(self, result):
        """文件刷新完成回调"""
        self._show_loading(False)
        self.refresh()
        
        removed_count = result['removed_count']
        modified_count = result['modified_count']
        
        messages = []
        if removed_count > 0:
            messages.append(f"移除了 {removed_count} 个不存在的文件")
        if modified_count > 0:
            messages.append(f"检测到 {modified_count} 个文件已修改")
        
        if messages:
            message = "🔄 刷新完成: " + ", ".join(messages)
        else:
            message = "🔄 刷新完成，所有文件都是最新的"
        
        if self.on_update_callback:
            self.on_update_callback(message, 'success')
    
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
    
    def _schedule_refresh(self):
        """延迟刷新（防抖）"""
        if self._refresh_pending:
            return
        
        self._refresh_pending = True
        self.after(500, self._execute_refresh)
    
    def _execute_refresh(self):
        """执行刷新"""
        self._refresh_pending = False
        self._filter_files()
    
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
            file_path = self.item_to_path[item]
            self._toggle_mark(file_path)
    
    def _on_item_double_click(self, event):
        """双击项目"""
        item = self.file_tree.selection()
        if item:
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
        tree_dict = {}
        
        for file_info in files:
            path = Path(file_info.path)
            parts = path.parts
            
            current = tree_dict
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            filename = parts[-1]
            current[filename] = file_info
        
        return tree_dict
    
    def _insert_tree_recursive(self, parent_item, tree_dict, prefix=""):
        """递归插入树节点 - 收集到队列而非立即插入"""
        for name, value in sorted(tree_dict.items()):
            if isinstance(value, dict):
                # 文件夹节点 - 添加文件夹占位符
                folder_index = len(self._render_queue)
                folder_node = {
                    'type': 'folder',
                    'parent': parent_item,
                    'name': name,
                    'prefix': prefix + name + os.sep,
                    'item_id': None  # 将在渲染时设置
                }
                self._render_queue.append(folder_node)
                
                # 递归处理子节点 - 使用索引引用父节点
                self._insert_tree_recursive(folder_index, value, prefix + name + os.sep)
            else:
                # 文件节点
                file_info = value
                icon = "✅" if file_info.marked else "⬜"
                
                self._render_queue.append({
                    'type': 'file',
                    'parent': parent_item,
                    'name': name,
                    'icon': icon,
                    'file_info': file_info
                })
    
    def _display_files(self, files):
        """显示文件列表 - 分批渲染优化版"""
        if self._update_lock:
            return
        
        self._update_lock = True
        
        # 取消之前的渲染任务
        if self._render_job_id:
            self.after_cancel(self._render_job_id)
            self._render_job_id = None
        
        # 清空现有内容
        self.file_tree.configure(selectmode='none')
        children = self.file_tree.get_children()
        if children:
            self.file_tree.delete(*children)
        
        self.item_to_path.clear()
        self.path_to_item.clear()
        self._render_queue.clear()
        
        if not files:
            self.file_tree.insert(
                '',
                'end',
                text='  暂无文件 - 点击上方按钮添加文件或文件夹',
                values=('', '', '')
            )
            self._restore_tree_state()
            return
        
        # 构建渲染队列 - 一次性构建完整的队列
        tree_structure = self._build_tree_structure(files)
        self._insert_tree_recursive('', tree_structure)
        
        # 开始分批渲染
        self._render_next_batch(0)
    
    def _render_next_batch(self, start_index):
        """渲染下一批节点"""
        end_index = min(start_index + self.BATCH_SIZE, len(self._render_queue))
        
        # 渲染当前批次
        for i in range(start_index, end_index):
            item_data = self._render_queue[i]
            
            # 解析父节点引用
            parent = item_data['parent']
            if isinstance(parent, int):
                # 如果parent是索引,获取对应的item_id
                if parent < len(self._render_queue) and self._render_queue[parent].get('item_id'):
                    parent = self._render_queue[parent]['item_id']
                else:
                    parent = ''
            
            if item_data['type'] == 'folder':
                folder_item = self.file_tree.insert(
                    parent,
                    'end',
                    text=f"📁 {item_data['name']}",
                    values=('', '', ''),
                    open=True
                )
                # 保存文件夹项目ID,以便子节点使用
                item_data['item_id'] = folder_item
            
            elif item_data['type'] == 'file':
                file_info = item_data['file_info']
                file_item = self.file_tree.insert(
                    parent,
                    'end',
                    text=f"📄 {item_data['name']}",
                    values=(item_data['icon'], file_info.language, format_size(file_info.size)),
                    tags=('file',)
                )
                
                self.item_to_path[file_item] = file_info.path
                self.path_to_item[file_info.path] = file_item
        
        # 如果还有未渲染的节点，继续下一批
        if end_index < len(self._render_queue):
            self._render_job_id = self.after(
                self.RENDER_DELAY,
                lambda: self._render_next_batch(end_index)
            )
        else:
            # 渲染完成
            self._render_queue.clear()
            self._restore_tree_state()
    
    def _restore_tree_state(self):
        """恢复树状态"""
        self.file_tree.configure(selectmode='browse')
        self._update_lock = False
    
    def _animate_loading(self):
        """加载动画"""
        if self._loading:
            current = self.loading_progress.get()
            if current >= 1.0:
                self.loading_progress.set(0)
            else:
                self.loading_progress.set(current + 0.05)
            
            self._loading_animation_id = self.after(50, self._animate_loading)
    
    def _show_loading(self, show: bool):
        """显示/隐藏加载指示器"""
        self._loading = show
        
        if show:
            self.loading_container.pack(side='right', padx=MD.SPACING_MD)
            self.loading_progress.set(0)
            self._animate_loading()
        else:
            if self._loading_animation_id:
                self.after_cancel(self._loading_animation_id)
                self._loading_animation_id = None
            self.loading_container.pack_forget()
    
    def refresh(self):
        """刷新显示"""
        self._filter_files()
        
        stats = self.file_handler.get_stats()
        self.stats_label.configure(
            text=f"📊 {stats['marked']}/{stats['total']} 个文件已选中  •  "
                 f"💾 共 {format_size(stats['size'])}  •  "
                 f"🔤 {stats['languages']} 种语言"
        )
    
    def set_update_callback(self, callback):
        """设置更新回调"""
        self.on_update_callback = callback

    def set_file_add_callback(self, callback):
        """设置文件添加回调"""
        self.on_file_add_callback = callback