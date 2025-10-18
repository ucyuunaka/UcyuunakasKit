"""
文件列表面板组件 - 性能优化版本
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, ttk
from config.theme import MD
from ui.widgets.material_card import Card, Btn
from core.file_handler import FileHandler, get_all_languages, format_size
import os
from pathlib import Path
import threading
from typing import List
from utils.dpi_helper import DPIHelper
from config.settings import Settings

class FileListPanel(Card):
    """文件列表面板"""
    
    def __init__(self, master, file_handler: FileHandler, **kwargs):
        super().__init__(master, **kwargs)
        
        self.file_handler = file_handler
        self.on_update_callback = None
        self.on_file_add_callback = None
        self._refresh_pending = False
        self._loading = False
        self._loading_animation_id = None
        self._update_lock = False  # 添加更新锁

        # 初始化配置管理器
        self.settings = Settings()

        self._build_ui()
    
    def _build_ui(self):
        """构建UI"""
        # 主容器
        container = ctk.CTkFrame(self, fg_color='transparent')
        container.pack(fill='both', expand=True, padx=MD.PAD_M, pady=MD.PAD_M)
        
        # 标题栏
        self._build_header(container)
        
        # 搜索和筛选栏
        self._build_search_bar(container)
        
        # 操作按钮栏
        self._build_action_bar(container)
        
        # 文件列表（树状视图）
        self._build_file_list(container)
        
    
    def _build_header(self, parent):
        """构建标题栏"""
        header = ctk.CTkFrame(parent, fg_color='transparent')
        header.pack(fill='x', pady=(0, MD.PAD_M))
        
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
            text="📂",
            font=("Segoe UI Emoji", 16)
        ).pack(side='left', padx=(MD.PAD_S, 0))
        
        # 加载指示器容器
        self.loading_container = ctk.CTkFrame(header, fg_color=MD.BG_SURFACE, corner_radius=MD.RADIUS)
        
        # 加载进度条（不确定模式）
        self.loading_progress = ctk.CTkProgressBar(
            self.loading_container,
            height=6,
            corner_radius=3,
            fg_color=MD.SURFACE,
            progress_color=MD.PRIMARY,
            mode='indeterminate'
        )
        self.loading_progress.pack(padx=MD.PAD_M, pady=(MD.PAD_S, MD.PAD_S))
        
        # 加载文本
        self.loading_label = ctk.CTkLabel(
            self.loading_container,
            text="加载中...",
            font=MD.FONT_BODY,
            text_color=MD.PRIMARY
        )
        self.loading_label.pack(padx=MD.PAD_M, pady=(0, MD.PAD_S))
    
    def _build_search_bar(self, parent):
        """构建搜索栏"""
        search_bar = ctk.CTkFrame(parent, fg_color='transparent')
        search_bar.pack(fill='x', pady=(0, MD.PAD_M))
        
        # 搜索框
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._schedule_refresh())
        
        search_entry = ctk.CTkEntry(
            search_bar,
            textvariable=self.search_var,
            placeholder_text="🔍 搜索文件名...",
            width=300,
            fg_color=MD.BG_SURFACE,
            border_color=MD.BORDER,
            corner_radius=MD.RADIUS
        )
        search_entry.pack(side='left', fill='x', expand=True, padx=(0, MD.PAD_S))
        
        # 语言筛选
        self.language_var = tk.StringVar(value="全部语言")
        self.language_var.trace('w', lambda *args: self._schedule_refresh())
        
        languages = ["全部语言"] + get_all_languages()
        language_combo = ctk.CTkComboBox(
            search_bar,
            values=languages,
            variable=self.language_var,
            state='readonly',
            width=150,
            fg_color=MD.BG_SURFACE,
            button_color=MD.PRIMARY,
            border_color=MD.OUTLINE,
            font=MD.FONT_BODY
        )
        language_combo.pack(side='left')
    
    def _build_action_bar(self, parent):
        """构建操作按钮栏"""
        action_bar = ctk.CTkFrame(parent, fg_color='transparent')
        action_bar.pack(fill='x', pady=(0, MD.PAD_M))
        
        action_bar.grid_columnconfigure(0, weight=1)
        action_bar.grid_columnconfigure(1, weight=0)
        
        # 左侧按钮容器
        left_buttons = ctk.CTkFrame(action_bar, fg_color='transparent')
        left_buttons.grid(row=0, column=0, sticky='w', padx=(0, MD.PAD_S))
        
        Btn(
            left_buttons,
            kind='primary',
            text="➕ 文件",
            command=self._add_files,
            width=100
        ).pack(side='left', padx=(0, MD.PAD_S))
        
        Btn(
            left_buttons,
            kind='primary',
            text="文件夹",
            command=self._add_folder,
            width=100
        ).pack(side='left', padx=(0, MD.PAD_S))
        
        Btn(
            left_buttons,
            kind='normal',
            text="刷新",
            command=self._refresh_files,
            width=50
        ).pack(side='left', padx=(0, MD.PAD_S))
        
        Btn(
            left_buttons,
            kind='danger',
            text="清除所有",
            command=self._clear_files,
            width=50
        ).pack(side='left')
        
        # 右侧按钮容器
        right_buttons = ctk.CTkFrame(action_bar, fg_color='transparent')
        right_buttons.grid(row=0, column=1, sticky='e')
        
        Btn(
            right_buttons,
            kind='normal',
            text="全选",
            command=lambda: self._mark_all(True),
            width=60
        ).pack(side='left', padx=(0, MD.PAD_S))
        
        Btn(
            right_buttons,
            kind='normal',
            text="全不选",
            command=lambda: self._mark_all(False),
            width=70
        ).pack(side='left', padx=(0, MD.PAD_S))
        
        Btn(
            right_buttons,
            kind='normal',
            text="展开",
            command=self._expand_all,
            width=60
        ).pack(side='left', padx=(0, MD.PAD_S))
        
        Btn(
            right_buttons,
            kind='normal',
            text="折叠",
            command=self._collapse_all,
            width=60
        ).pack(side='left')
    
    def _build_file_list(self, parent):
        """构建文件列表（树状视图）- 性能优化版"""

        # ========== 调试代码开始 ==========
        import tkinter as tk
        scaling_factor = DPIHelper.get_scaling_factor()
        font_config = MD.get_font_ui(scaling_factor)
        
        print("=" * 60)
        print("DPI诊断信息")
        print("=" * 60)
        print(f"系统DPI: {DPIHelper.get_system_dpi()}")
        print(f"缩放因子: {scaling_factor}")
        print(f"字体配置: {font_config}")
        print(f"基础行高: 18")
        print(f"计算后行高: {DPIHelper.scale_value(18, scaling_factor)}")
        print(f"字体高度: {font_config[1]}")
        print(f"最小行高: {int(font_config[1] * 1.5)}")
        
        # 测试tkinter实际如��渲染字体
        test_font = tk.font.Font(family=font_config[0], size=font_config[1])
        actual_height = test_font.metrics('linespace')
        print(f"Tkinter实际字体行高: {actual_height} 像素")
        print("=" * 60)

        # 列表容器
        list_container = ctk.CTkFrame(parent, fg_color=MD.SURFACE)
        list_container.pack(fill='both', expand=True, pady=(0, MD.PAD_M))

        # 创建样式
        style = ttk.Style()
        style.theme_use('clam')

        # 根据DPI缩放因子计算合适的行高
        scaling_factor = DPIHelper.get_scaling_factor()

        # 获取实际字体行高（关键修复）
        font_config = MD.get_font_ui(scaling_factor)
        ui_font = tk.font.Font(family=font_config[0], size=font_config[1])
        actual_line_height = ui_font.metrics('linespace')

        # 计算最终行高（实际行高 + 20%间距）
        final_rowheight = int(actual_line_height * 1.2)

        # 配置 Treeview 样式
        style.configure(
            "Compact.Treeview",
            background=MD.BG_SURFACE,
            foreground=MD.TEXT_PRIMARY,
            fieldbackground=MD.BG_SURFACE,
            borderwidth=0,
            font=MD.get_font_ui(scaling_factor),
            rowheight=final_rowheight
        )
        
        style.configure(
            "Compact.Treeview.Heading",
            background=MD.BG_ELEVATED,
            foreground=MD.TEXT_PRIMARY,
            borderwidth=1,
            relief="flat",
            font=MD.get_font_title(scaling_factor)
        )

        style.map(
            "Compact.Treeview",
            background=[('selected', MD.BG_ELEVATED)],
            foreground=[('selected', MD.TEXT_PRIMARY)]
        )

        # 创建 Treeview
        columns = ('status', 'language', 'size')
        self.file_tree = ttk.Treeview(
            list_container,
            columns=columns,
            show='tree headings',
            style="Compact.Treeview",
            selectmode='browse'
        )
        
        # 配置列 - 启用所有列的宽度调整功能
        column_widths = self.settings.get('column_widths', {})
        self.file_tree.column('#0', width=column_widths.get('path', 400), minwidth=180, stretch=True)
        self.file_tree.column('status', width=column_widths.get('status', 50), minwidth=50, anchor='center', stretch=True)
        self.file_tree.column('language', width=column_widths.get('language', 80), minwidth=70, anchor='center', stretch=True)
        self.file_tree.column('size', width=column_widths.get('size', 70), minwidth=70, anchor='e', stretch=True)

        # 设置列标题
        self.file_tree.heading('#0', text='[+] 文件路径', anchor='w')
        self.file_tree.heading('status', text='状态', anchor='center')
        self.file_tree.heading('language', text='语言', anchor='center')
        self.file_tree.heading('size', text='大小', anchor='e')
        
        # 滚动条
        vsb = ttk.Scrollbar(list_container, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=vsb.set)
        
        # 布局
        self.file_tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)
        
        # 绑定事件
        self.file_tree.bind('<Double-Button-1>', self._on_item_double_click)
        self.file_tree.bind('<space>', self._on_space_press)
        self.file_tree.bind('<Button-1>', self._on_item_click)

        # 绑定列宽调整事件
        self.file_tree.bind('<ButtonRelease-1>', self._on_column_resize)
        
        # 存储节点映射
        self.item_to_path = {}
        self.path_to_item = {}
    
    
    # 事件处理
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

        # 调用文件添加回调，传递新添加的文件路径
        if self.on_file_add_callback and count > 0:
            added_files = [f.path for f in self.file_handler.files[-count:]]
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

        # 调用文件添加回调，传递新添加的文件路径
        if self.on_file_add_callback and count > 0:
            added_files = [f.path for f in self.file_handler.files[-count:]]
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
        """延迟刷新（防抖）- 优化版"""
        if self._refresh_pending:
            return
        
        self._refresh_pending = True
        # 增加延迟时间，减少刷新频率
        self.after(500, self._execute_refresh)  # 从300ms改为500ms
    
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
            path_info = self.item_to_path[item]
            
            # 检查是否是文件夹节点
            if path_info.startswith("FOLDER:"):
                # 文件夹批量操作
                self._toggle_folder_mark(item)
            else:
                # 单个文件操作
                self._toggle_mark(path_info)
    
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
    def _toggle_folder_mark(self, folder_item):
        """切换文件夹下所有文件的标记状态"""
        # 收集文件夹下所有文件
        file_paths = self._collect_files_in_folder(folder_item)
        
        if not file_paths:
            return
        
        # 确定新状态：基于第一个文件的当前状态
        first_file_path = file_paths[0]
        first_file = None
        for file in self.file_handler.files:
            if file.path == first_file_path:
                first_file = file
                break
        
        if first_file:
            new_state = not first_file.marked
            # 批量设置状态
            count = self.file_handler.set_marks_batch(file_paths, new_state)
            self.refresh()
            
            if self.on_update_callback:
                action = "选中" if new_state else "取消选中"
                self.on_update_callback(f"✅ 已{action}文件夹中的 {count} 个文件", 'info')
    
    def _collect_files_in_folder(self, folder_item) -> List[str]:
        """递归收集文件夹下的所有文件路径"""
        file_paths = []
        
        def collect_recursive(item):
            children = self.file_tree.get_children(item)
            for child in children:
                if child in self.item_to_path:
                    # 这是一个文件节点
                    file_paths.append(self.item_to_path[child])
                else:
                    # 这是一个文件夹节点，递归处理
                    collect_recursive(child)
        
        collect_recursive(folder_item)
        return file_paths
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
        """递归插入树节点"""
        for name, value in sorted(tree_dict.items()):
            if isinstance(value, dict):
                folder_path = prefix + name + os.sep
                folder_item = self.file_tree.insert(
                    parent_item,
                    'end',
                    text=f"[+] {name}",
                    values=('', '', ''),
                    open=True
                )
                # 为文件夹节点添加映射，使用特殊前缀标识
                self.item_to_path[folder_item] = f"FOLDER:{folder_path}"
                self.path_to_item[f"FOLDER:{folder_path}"] = folder_item
                self._insert_tree_recursive(folder_item, value, prefix + name + os.sep)
            else:
                file_info = value
                icon = "[x]" if file_info.marked else "[ ]"

                file_item = self.file_tree.insert(
                    parent_item,
                    'end',
                    text=f" {name}",
                    values=(icon, file_info.language, format_size(file_info.size)),
                    tags=('file',)
                )
                
                self.item_to_path[file_item] = file_info.path
                self.path_to_item[file_info.path] = file_item
    
    def _display_files(self, files):
        """显示文件列表 - 性能优化版（消除撕裂）"""
        # 防止重复更新
        if self._update_lock:
            return
        
        self._update_lock = True
        
        try:
            # 1. 暂停UI更新
            self.file_tree.configure(selectmode='none')
            
            # 2. 批量删除（使用detach而非delete可以更快）
            children = self.file_tree.get_children()
            if children:
                self.file_tree.delete(*children)  # 批量删除
            
            self.item_to_path.clear()
            self.path_to_item.clear()
            
            if not files:
                # 空状态
                self.file_tree.insert(
                    '',
                    'end',
                    text='  暂无文件 - 点击上方按钮添加文件或文件夹',
                    values=('', '', '')
                )
            else:
                # 3. 构建并批量插入
                tree_structure = self._build_tree_structure(files)
                self._insert_tree_recursive('', tree_structure)
            
            # 4. 强制更新一次UI
            self.file_tree.update_idletasks()
            
        finally:
            # 5. 延迟恢复选择模式，确保UI完全更新
            self.after(10, self._restore_tree_state)
    
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
            self.loading_container.pack(side='right', padx=MD.PAD_M)
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
        
        # 统计信息现在由StatusBar统一显示，这里不需要重复更新
    
    def set_update_callback(self, callback):
        """设置更新回调"""
        self.on_update_callback = callback

    def _on_column_resize(self, event):
        """列宽调整事件处理"""
        # 检查是否是列标题区域
        region = self.file_tree.identify_region(event.x, event.y)
        if region == 'heading':
            # 获取当前列宽
            column_widths = {
                'path': self.file_tree.column('#0', 'width'),
                'status': self.file_tree.column('status', 'width'),
                'language': self.file_tree.column('language', 'width'),
                'size': self.file_tree.column('size', 'width')
            }

            # 保存到配置
            self.settings.set('column_widths', column_widths)
            if self.settings.get('auto_save_config', True):
                self.settings.save()

    def set_file_add_callback(self, callback):
        """设置文件添加回调"""
        self.on_file_add_callback = callback