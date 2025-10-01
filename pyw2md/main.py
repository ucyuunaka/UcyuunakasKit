import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import json

# 尝试导入拖拽功能
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "code2markdown_config.json")

# 全局变量
selected_code_files_global = []

# 支持的编程语言
SUPPORTED_EXTENSIONS = {
    'Python': ['.py', '.pyw'],
    'JavaScript': ['.js', '.jsx', '.ts', '.tsx'],
    'Java': ['.java'],
    'C/C++': ['.c', '.cpp', '.h', '.hpp'],
    'C#': ['.cs'],
    'PHP': ['.php'],
    'Ruby': ['.rb'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass', '.less'],
    'SQL': ['.sql'],
    'Shell': ['.sh', '.bash', '.zsh'],
    'YAML': ['.yml', '.yaml'],
    'JSON': ['.json'],
    'XML': ['.xml'],
    'Markdown': ['.md'],
    'Text': ['.txt']
}

# Markdown 模板
TEMPLATES = {
    "默认": "# {relative_path}\n```{language}\n{content}\n```\n\n",
    "带注释": """# 文件: {relative_path}

**语言**: {language}  
**大小**: {size} 字节  
**最后修改**: {mtime}

```{language}
{content}
```

---

""",
    "GitHub风格": """## {basename}

```{language}
{content}
```

<details>
<summary>文件信息</summary>

- **路径**: `{relative_path}`
- **语言**: {language}
- **大小**: {size} 字节

</details>

---
""",
    "简洁": """```{language}
// {relative_path}
{content}
```

"""
}

def get_language_from_extension(file_path):
    """根据文件扩展名获取编程语言"""
    _, ext = os.path.splitext(file_path.lower())
    for language, extensions in SUPPORTED_EXTENSIONS.items():
        if ext in extensions:
            return language
    return "Text"

def format_file_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/(1024*1024):.1f}MB"

def get_all_supported_files_in_folder(folder_path):
    """递归获取文件夹中所有支持的代码文件"""
    supported_files = []
    all_extensions = [ext for exts in SUPPORTED_EXTENSIONS.values() for ext in exts]
    
    for root_dir, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root_dir, file)
            _, ext = os.path.splitext(file_path.lower())
            if ext in all_extensions:
                supported_files.append(file_path)
    
    return supported_files

def format_file_content(file_path, template_name):
    """使用指定模板格式化文件内容"""
    try:
        current_dir = os.getcwd()
        basename = os.path.basename(file_path)
        language = get_language_from_extension(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        file_size = os.path.getsize(file_path)
        mtime = os.path.getmtime(file_path)
        
        try:
            relative_path = os.path.relpath(file_path, current_dir)
        except ValueError:
            relative_path = file_path
        
        template = TEMPLATES[template_name]
        formatted = template.format(
            relative_path=relative_path,
            basename=basename,
            language=language,
            size=file_size,
            mtime=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime)),
            content=content
        )
        
        return formatted
    
    except Exception as e:
        return f"<!-- 错误处理文件 {file_path}: {str(e)} -->\n"

class ModernUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Code2Markdown Pro")
        self.root.geometry("1200x700")
        self.root.minsize(800, 500)
        
        # 现代配色方案 - 提高对比度以改善清晰度
        self.colors = {
            'bg_dark': '#0F1419',
            'bg_medium': '#1A1F2E',
            'bg_card': '#242938',
            'bg_card_hover': '#2F3647',
            'accent_primary': '#7C3AED',
            'accent_secondary': '#9D5BFF',
            'accent_success': '#10B981',
            'accent_warning': '#F59E0B',
            'accent_error': '#EF4444',
            'accent_info': '#06B6D4',
            'text_primary': '#F8FAFC',
            'text_secondary': '#CBD5E1',
            'text_muted': '#94A3B8',
            'border': '#334155',
            'gradient_start': '#7C3AED',
            'gradient_end': '#9D5BFF'
        }
        
        self.setup_styles()
        self.create_ui()
        self.load_config()
        
        # 绑定关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        
        # 设置拖拽
        if HAS_DND:
            self.setup_drag_drop()
    
    def setup_styles(self):
        """设置样式"""
        self.root.configure(bg=self.colors['bg_dark'])
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # 树视图样式 - 改善清晰度
        style.configure("Modern.Treeview",
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_card'],
                       borderwidth=0,
                       font=("Segoe UI", 9, "normal"),
                       rowheight=28)
        
        style.configure("Modern.Treeview.Heading",
                       background=self.colors['bg_medium'],
                       foreground=self.colors['text_secondary'],
                       borderwidth=0,
                       font=("Segoe UI", 9, "bold"))
        
        style.map("Modern.Treeview",
                 background=[("selected", self.colors['accent_primary'])],
                 foreground=[("selected", self.colors['text_primary'])])
        
        # 进度条样式
        style.configure("Modern.Horizontal.TProgressbar",
                       background=self.colors['accent_success'],
                       troughcolor=self.colors['bg_medium'],
                       borderwidth=0,
                       thickness=6)
        
        # 下拉框样式
        style.configure("Modern.TCombobox",
                       background=self.colors['bg_card'],
                       foreground=self.colors['text_primary'],
                       fieldbackground=self.colors['bg_card'],
                       borderwidth=0,
                       arrowcolor=self.colors['text_secondary'])
    
    def create_gradient_frame(self, parent, height=4):
        """创建渐变装饰条"""
        canvas = tk.Canvas(parent, height=height, bg=self.colors['bg_dark'],
                          highlightthickness=0)
        canvas.pack(fill=tk.X)

        # 创建渐变效果 - 使用动态宽度
        def update_gradient(event=None):
            canvas.delete("gradient")
            width = canvas.winfo_width()
            if width <= 1:  # 避免除零错误
                width = 1400
            for i in range(width):
                ratio = i / width
                color = self.interpolate_color(
                    self.colors['gradient_start'],
                    self.colors['gradient_end'],
                    ratio)
                canvas.create_line(i, 0, i, height, fill=color, tags="gradient")

        update_gradient()
        canvas.bind("<Configure>", update_gradient)
        return canvas
    
    def interpolate_color(self, color1, color2, ratio):
        """颜色插值"""
        c1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
        c2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
        c3 = tuple(int(c1[i] + (c2[i] - c1[i]) * ratio) for i in range(3))
        return f'#{c3[0]:02x}{c3[1]:02x}{c3[2]:02x}'
    
    def create_ui(self):
        """创建UI"""
        # 顶部标题栏
        self.create_header()

        # 渐变装饰条
        self.create_gradient_frame(self.root, 3)

        # 主容器 - 使用更大的边距但确保响应式
        main_container = tk.Frame(self.root, bg=self.colors['bg_dark'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # 创建两栏布局，使用grid布局确保响应式
        main_container.grid_columnconfigure(0, weight=3)  # 左侧占3份
        main_container.grid_columnconfigure(1, weight=1)  # 右侧占1份
        main_container.grid_rowconfigure(0, weight=1)     # 填充高度

        # 左侧：文件列表
        left_panel = self.create_left_panel(main_container)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # 右侧：控制面板和统计
        right_panel = self.create_right_panel(main_container)
        right_panel.grid(row=0, column=1, sticky="ns", padx=(8, 0))
    
    def create_header(self):
        """创建顶部标题栏"""
        header = tk.Frame(self.root, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, padx=20, pady=(16, 8))
        header.pack_propagate(False)
        
        # Logo和标题
        title_frame = tk.Frame(header, bg=self.colors['bg_dark'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # 使用更现代的emoji组合
        logo = tk.Label(title_frame, text="⚡", font=("Segoe UI Emoji", 42), 
                       bg=self.colors['bg_dark'], fg=self.colors['accent_primary'])
        logo.pack(side=tk.LEFT, padx=(0, 16))
        
        text_frame = tk.Frame(title_frame, bg=self.colors['bg_dark'])
        text_frame.pack(side=tk.LEFT, fill=tk.Y, pady=10)
        
        title = tk.Label(text_frame, text="Code2Markdown",
                        font=("Segoe UI", 20, "bold"),
                        bg=self.colors['bg_dark'], fg=self.colors['text_primary'])
        title.pack(anchor="w")

        subtitle = tk.Label(text_frame, text="专业代码转 Markdown 工具 • 支持 20+ 编程语言",
                           font=("Segoe UI", 10),
                           bg=self.colors['bg_dark'], fg=self.colors['text_secondary'])
        subtitle.pack(anchor="w")
        
        # 版本信息
        version_frame = tk.Frame(header, bg=self.colors['bg_dark'])
        version_frame.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
        version_badge = tk.Frame(version_frame, bg=self.colors['accent_primary'])
        version_badge.pack(anchor="e", pady=(0, 8))
        
        version = tk.Label(version_badge, text=" v2.0 Pro ", 
                          font=("Segoe UI", 10, "bold"),
                          bg=self.colors['accent_primary'], 
                          fg=self.colors['text_primary'])
        version.pack(padx=12, pady=4)
        
        stats = tk.Label(version_frame, text="🚀 快速 • 高效 • 专业", 
                        font=("Segoe UI", 10),
                        bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        stats.pack(anchor="e")
    
    def create_card(self, parent, title=None, icon=None):
        """创建卡片容器"""
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        
        if title:
            header = tk.Frame(card, bg=self.colors['bg_card'])
            header.pack(fill=tk.X, padx=20, pady=(20, 16))
            
            if icon:
                icon_label = tk.Label(header, text=icon, font=("Segoe UI Emoji", 16),
                                     bg=self.colors['bg_card'], 
                                     fg=self.colors['accent_primary'])
                icon_label.pack(side=tk.LEFT, padx=(0, 12))
            
            title_label = tk.Label(header, text=title,
                                  font=("Segoe UI", 14, "bold"),
                                  bg=self.colors['bg_card'],
                                  fg=self.colors['text_primary'])
            title_label.pack(side=tk.LEFT)
        
        return card
    
    def create_left_panel(self, parent):
        """创建左侧文件管理面板"""
        panel = tk.Frame(parent, bg=self.colors['bg_dark'])
        
        # 文件列表卡片
        files_card = self.create_card(panel, "文件管理", "📁")
        files_card.pack(fill=tk.BOTH, expand=True)
        
        # 操作按钮组
        actions_frame = tk.Frame(files_card, bg=self.colors['bg_card'])
        actions_frame.pack(fill=tk.X, padx=20, pady=(0, 16))
        
        btn_frame = tk.Frame(actions_frame, bg=self.colors['bg_card'])
        btn_frame.pack(fill=tk.X)
        
        # 添加文件按钮
        self.create_button(btn_frame, "📂 添加文件", self.add_files, 
                          style='primary').pack(side=tk.LEFT, padx=(0, 8))
        
        # 添加文件夹按钮
        self.create_button(btn_frame, "📁 添加文件夹", self.add_folder, 
                          style='success').pack(side=tk.LEFT, padx=(0, 8))
        
        # 清空按钮
        self.create_button(btn_frame, "🗑️", self.clear_files, 
                          style='danger', width=40).pack(side=tk.RIGHT)
        
        # 搜索栏
        search_frame = tk.Frame(files_card, bg=self.colors['bg_medium'])
        search_frame.pack(fill=tk.X, padx=20, pady=(0, 16))
        
        search_icon = tk.Label(search_frame, text="🔍", 
                              font=("Segoe UI Emoji", 12),
                              bg=self.colors['bg_medium'], 
                              fg=self.colors['text_muted'])
        search_icon.pack(side=tk.LEFT, padx=(12, 8))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)
        
        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               font=("Segoe UI", 10),
                               bg=self.colors['bg_medium'],
                               fg=self.colors['text_primary'],
                               insertbackground=self.colors['text_primary'],
                               relief="flat", bd=0)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8)
        
        # 语言筛选
        self.filter_var = tk.StringVar(value="全部语言")
        self.filter_var.trace('w', self.filter_files)
        
        filter_combo = ttk.Combobox(search_frame, 
                                   textvariable=self.filter_var,
                                   values=["全部语言"] + list(SUPPORTED_EXTENSIONS.keys()),
                                   state="readonly",
                                   width=12,
                                   font=("Segoe UI", 9),
                                   style="Modern.TCombobox")
        filter_combo.pack(side=tk.RIGHT, padx=12)
        
        # 文件树
        tree_container = tk.Frame(files_card, bg=self.colors['bg_card'])
        tree_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        self.file_tree = ttk.Treeview(tree_container,
                                      columns=('language', 'size', 'status'),
                                      show='tree headings',
                                      style="Modern.Treeview",
                                      selectmode='extended')
        
        self.file_tree.heading('#0', text='文件名')
        self.file_tree.heading('language', text='语言')
        self.file_tree.heading('size', text='大小')
        self.file_tree.heading('status', text='状态')
        
        self.file_tree.column('#0', width=350)
        self.file_tree.column('language', width=100)
        self.file_tree.column('size', width=80)
        self.file_tree.column('status', width=80)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 滚动条
        scrollbar = tk.Scrollbar(tree_container, orient="vertical",
                                command=self.file_tree.yview,
                                bg=self.colors['bg_card'])
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_tree.config(yscrollcommand=scrollbar.set)
        
        # 绑定事件
        self.file_tree.bind('<space>', lambda e: self.toggle_mark())
        self.file_tree.bind('<Double-1>', lambda e: self.show_file_info())
        self.file_tree.bind('<Button-3>', self.show_context_menu)
        
        # 底部快捷操作
        quick_actions = tk.Frame(files_card, bg=self.colors['bg_card'])
        quick_actions.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_button(quick_actions, "✓ 全选", self.select_all, 
                          style='secondary', width=80).pack(side=tk.LEFT, padx=(0, 8))
        
        self.create_button(quick_actions, "✗ 全不选", self.deselect_all, 
                          style='secondary', width=80).pack(side=tk.LEFT)
        
        # 文件统计
        self.file_count_label = tk.Label(quick_actions,
                                         text="0 个文件",
                                         font=("Segoe UI", 10),
                                         bg=self.colors['bg_card'],
                                         fg=self.colors['text_muted'])
        self.file_count_label.pack(side=tk.RIGHT)
        
        return panel
    
    def create_right_panel(self, parent):
        """创建右侧控制面板"""
        panel = tk.Frame(parent, bg=self.colors['bg_dark'])
        panel.grid_propagate(False)  # 防止子组件改变面板大小
        
        # 统计卡片
        stats_card = self.create_card(panel, "统计信息", "📊")
        stats_card.pack(fill=tk.X, pady=(0, 16))
        
        stats_content = tk.Frame(stats_card, bg=self.colors['bg_card'])
        stats_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 统计项
        self.stats_widgets = {}
        stats_data = [
            ("📄", "总文件数", "total_files", "0"),
            ("✅", "已标记", "marked_files", "0"),
            ("💾", "总大小", "total_size", "0KB"),
            ("🗂️", "语言种类", "language_count", "0")
        ]
        
        for i, (icon, label, key, value) in enumerate(stats_data):
            stat_frame = tk.Frame(stats_content, bg=self.colors['bg_medium'])
            stat_frame.pack(fill=tk.X, pady=(0, 8))
            
            icon_label = tk.Label(stat_frame, text=icon, 
                                 font=("Segoe UI Emoji", 18),
                                 bg=self.colors['bg_medium'],
                                 fg=self.colors['accent_primary'])
            icon_label.pack(side=tk.LEFT, padx=16, pady=12)
            
            text_frame = tk.Frame(stat_frame, bg=self.colors['bg_medium'])
            text_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=12)
            
            tk.Label(text_frame, text=label,
                    font=("Segoe UI", 8),
                    bg=self.colors['bg_medium'],
                    fg=self.colors['text_muted']).pack(anchor="w")

            value_label = tk.Label(text_frame, text=value,
                                  font=("Segoe UI", 14, "bold"),
                                  bg=self.colors['bg_medium'],
                                  fg=self.colors['text_primary'])
            value_label.pack(anchor="w")
            
            self.stats_widgets[key] = value_label
        
        # 模板选择卡片
        template_card = self.create_card(panel, "输出模板", "🎨")
        template_card.pack(fill=tk.X, pady=(0, 16))
        
        template_content = tk.Frame(template_card, bg=self.colors['bg_card'])
        template_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        tk.Label(template_content, text="选择模板样式",
                font=("Segoe UI", 10),
                bg=self.colors['bg_card'],
                fg=self.colors['text_secondary']).pack(anchor="w", pady=(0, 8))
        
        self.template_var = tk.StringVar(value="默认")
        
        template_combo = ttk.Combobox(template_content,
                                     textvariable=self.template_var,
                                     values=list(TEMPLATES.keys()),
                                     state="readonly",
                                     font=("Segoe UI", 10),
                                     style="Modern.TCombobox")
        template_combo.pack(fill=tk.X, pady=(0, 12))
        
        self.create_button(template_content, "👁️ 预览模板", 
                          self.preview_template,
                          style='secondary').pack(fill=tk.X)
        
        # 操作卡片
        action_card = self.create_card(panel, "转换操作", "⚡")
        action_card.pack(fill=tk.X, pady=(0, 16))
        
        action_content = tk.Frame(action_card, bg=self.colors['bg_card'])
        action_content.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        self.create_button(action_content, "👁️ 预览结果", 
                          self.preview_conversion,
                          style='info').pack(fill=tk.X, pady=(0, 12))
        
        self.create_button(action_content, "🚀 开始转换", 
                          self.perform_conversion,
                          style='success',
                          height=48).pack(fill=tk.X)
        
        # 进度显示
        progress_frame = tk.Frame(action_content, bg=self.colors['bg_card'])
        progress_frame.pack(fill=tk.X, pady=(12, 0))
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           style="Modern.Horizontal.TProgressbar")
        
        # 状态标签
        self.status_label = tk.Label(progress_frame,
                                     text="",
                                     font=("Segoe UI", 9),
                                     bg=self.colors['bg_card'],
                                     fg=self.colors['text_muted'])
        
        
        return panel
    
    def create_button(self, parent, text, command, style='primary', width=None, height=36):
        """创建现代化按钮"""
        style_config = {
            'primary': {
                'bg': self.colors['accent_primary'],
                'hover': self.colors['accent_secondary'],
                'fg': self.colors['text_primary']
            },
            'success': {
                'bg': self.colors['accent_success'],
                'hover': '#0DA574',
                'fg': self.colors['text_primary']
            },
            'danger': {
                'bg': self.colors['accent_error'],
                'hover': '#FF5252',
                'fg': self.colors['text_primary']
            },
            'secondary': {
                'bg': self.colors['bg_medium'],
                'hover': self.colors['bg_card_hover'],
                'fg': self.colors['text_secondary']
            },
            'info': {
                'bg': self.colors['accent_info'],
                'hover': '#45C0B8',
                'fg': self.colors['text_primary']
            }
        }
        
        config = style_config.get(style, style_config['primary'])
        
        btn = tk.Button(parent, text=text, command=command,
                       font=("Segoe UI", 9, "bold"),
                       bg=config['bg'],
                       fg=config['fg'],
                       relief="flat",
                       bd=0,
                       cursor="hand2",
                       height=height//20 if not width else 1)
        
        if width:
            btn.config(width=width//8)
        
        # Hover效果
        def on_enter(e):
            btn.config(bg=config['hover'])
        
        def on_leave(e):
            btn.config(bg=config['bg'])
        
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        
        return btn
    
    def refresh_file_list(self):
        """刷新文件列表显示"""
        # 清空树
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 添加文件
        for file_item in selected_code_files_global:
            file_path = file_item["path"]
            filename = os.path.basename(file_path)
            language = get_language_from_extension(file_path)
            
            try:
                size = os.path.getsize(file_path)
                size_str = format_file_size(size)
            except:
                size_str = "-"
            
            status = "✅" if file_item["marked"] else "⬜"
            icon = "✓ " if file_item["marked"] else "  "
            
            self.file_tree.insert('', 'end',
                                 text=f"{icon}{filename}",
                                 values=(language, size_str, status))
        
        # 更新统计
        self.update_stats()
    
    def update_stats(self):
        """更新统计信息"""
        total = len(selected_code_files_global)
        marked = sum(1 for item in selected_code_files_global if item["marked"])
        
        # 计算总大小
        total_size = 0
        for item in selected_code_files_global:
            try:
                total_size += os.path.getsize(item["path"])
            except:
                pass
        
        # 统计语言种类
        languages = set()
        for item in selected_code_files_global:
            lang = get_language_from_extension(item["path"])
            languages.add(lang)
        
        # 更新显示
        self.stats_widgets['total_files'].config(text=str(total))
        self.stats_widgets['marked_files'].config(text=str(marked))
        self.stats_widgets['total_size'].config(text=format_file_size(total_size))
        self.stats_widgets['language_count'].config(text=str(len(languages)))
        
        self.file_count_label.config(text=f"{marked}/{total} 个文件")
    
    def filter_files(self, *args):
        """筛选文件"""
        search_term = self.search_var.get().lower()
        language_filter = self.filter_var.get()
        
        # 清空树
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # 筛选并显示
        for file_item in selected_code_files_global:
            file_path = file_item["path"]
            filename = os.path.basename(file_path).lower()
            language = get_language_from_extension(file_path)
            
            # 应用筛选条件
            if search_term and search_term not in filename:
                continue
            
            if language_filter != "全部语言" and language != language_filter:
                continue
            
            # 显示文件
            try:
                size = os.path.getsize(file_path)
                size_str = format_file_size(size)
            except:
                size_str = "-"
            
            status = "✅" if file_item["marked"] else "⬜"
            icon = "✓ " if file_item["marked"] else "  "
            
            self.file_tree.insert('', 'end',
                                 text=f"{icon}{os.path.basename(file_path)}",
                                 values=(language, size_str, status))
    
    # 文件操作方法
    def add_files(self):
        """添加文件"""
        filetypes = [("所有支持的文件", " ".join(f"*{ext}" for exts in SUPPORTED_EXTENSIONS.values() for ext in exts))]
        filetypes.append(("所有文件", "*.*"))
        
        files = filedialog.askopenfilenames(title="选择代码文件", filetypes=filetypes)
        
        if files:
            added = 0
            for file_path in files:
                if not any(item["path"] == file_path for item in selected_code_files_global):
                    selected_code_files_global.append({"path": file_path, "marked": True})
                    added += 1
            
            self.refresh_file_list()
            self.show_status(f"✅ 添加了 {added} 个文件", 'success')
    
    def add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        
        if folder:
            files = get_all_supported_files_in_folder(folder)
            added = 0
            
            for file_path in files:
                if not any(item["path"] == file_path for item in selected_code_files_global):
                    selected_code_files_global.append({"path": file_path, "marked": True})
                    added += 1
            
            self.refresh_file_list()
            self.show_status(f"✅ 从文件夹添加了 {added} 个文件", 'success')
    
    def clear_files(self):
        """清空文件列表"""
        if selected_code_files_global and messagebox.askyesno("确认", "确定要清空所有文件吗？"):
            selected_code_files_global.clear()
            self.refresh_file_list()
            self.show_status("🗑️ 已清空文件列表", 'info')
    
    def select_all(self):
        """全选"""
        for item in selected_code_files_global:
            item["marked"] = True
        self.refresh_file_list()
        self.show_status("✅ 已全选所有文件", 'success')
    
    def deselect_all(self):
        """全不选"""
        for item in selected_code_files_global:
            item["marked"] = False
        self.refresh_file_list()
        self.show_status("⬜ 已取消全选", 'info')
    
    def toggle_mark(self):
        """切换标记状态"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        for item_id in selection:
            item_text = self.file_tree.item(item_id, 'text')
            filename = item_text.strip().lstrip('✓ ')
            
            for file_item in selected_code_files_global:
                if os.path.basename(file_item["path"]) == filename:
                    file_item["marked"] = not file_item["marked"]
                    break
        
        self.refresh_file_list()
    
    def show_file_info(self):
        """显示文件信息"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item_text = self.file_tree.item(item_id, 'text')
        filename = item_text.strip().lstrip('✓ ')
        
        for file_item in selected_code_files_global:
            if os.path.basename(file_item["path"]) == filename:
                file_path = file_item["path"]
                
                try:
                    size = os.path.getsize(file_path)
                    mtime = time.strftime("%Y-%m-%d %H:%M:%S", 
                                        time.localtime(os.path.getmtime(file_path)))
                    
                    info = f"""文件名: {os.path.basename(file_path)}
路径: {file_path}
大小: {format_file_size(size)}
修改时间: {mtime}
语言: {get_language_from_extension(file_path)}
状态: {'已标记 ✅' if file_item["marked"] else '未标记 ⬜'}"""
                    
                    messagebox.showinfo("文件信息", info)
                except Exception as e:
                    messagebox.showerror("错误", f"无法获取文件信息: {str(e)}")
                
                break
    
    def show_context_menu(self, event):
        """显示右键菜单"""
        menu = tk.Menu(self.root, tearoff=0,
                      bg=self.colors['bg_card'],
                      fg=self.colors['text_primary'],
                      activebackground=self.colors['accent_primary'],
                      activeforeground=self.colors['text_primary'])
        
        menu.add_command(label="✓ 标记", command=self.mark_selected)
        menu.add_command(label="✗ 取消标记", command=self.unmark_selected)
        menu.add_separator()
        menu.add_command(label="ℹ️ 文件信息", command=self.show_file_info)
        menu.add_command(label="🗑️ 移除", command=self.remove_selected)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def mark_selected(self):
        """标记选中的文件"""
        selection = self.file_tree.selection()
        for item_id in selection:
            item_text = self.file_tree.item(item_id, 'text')
            filename = item_text.strip().lstrip('✓ ')
            
            for file_item in selected_code_files_global:
                if os.path.basename(file_item["path"]) == filename:
                    file_item["marked"] = True
                    break
        
        self.refresh_file_list()
    
    def unmark_selected(self):
        """取消标记选中的文件"""
        selection = self.file_tree.selection()
        for item_id in selection:
            item_text = self.file_tree.item(item_id, 'text')
            filename = item_text.strip().lstrip('✓ ')
            
            for file_item in selected_code_files_global:
                if os.path.basename(file_item["path"]) == filename:
                    file_item["marked"] = False
                    break
        
        self.refresh_file_list()
    
    def remove_selected(self):
        """移除选中的文件"""
        selection = self.file_tree.selection()
        if not selection:
            return
        
        files_to_remove = []
        for item_id in selection:
            item_text = self.file_tree.item(item_id, 'text')
            filename = item_text.strip().lstrip('✓ ')
            files_to_remove.append(filename)
        
        selected_code_files_global[:] = [
            item for item in selected_code_files_global
            if os.path.basename(item["path"]) not in files_to_remove
        ]
        
        self.refresh_file_list()
        self.show_status(f"🗑️ 已移除 {len(files_to_remove)} 个文件", 'info')
    
    def preview_template(self):
        """预览模板"""
        template_name = self.template_var.get()
        template_content = TEMPLATES[template_name]
        
        # 创建预览窗口
        preview = tk.Toplevel(self.root)
        preview.title(f"模板预览 - {template_name}")
        preview.geometry("700x500")
        preview.configure(bg=self.colors['bg_dark'])
        
        # 标题
        header = tk.Frame(preview, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, padx=24, pady=24)
        
        tk.Label(header, text=f"📋 {template_name} 模板",
                font=("Segoe UI", 18, "bold"),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_primary']).pack(anchor="w")
        
        # 内容
        content_frame = tk.Frame(preview, bg=self.colors['bg_card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        text_widget = tk.Text(content_frame,
                             font=("Consolas", 10),
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_primary'],
                             wrap=tk.WORD,
                             padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        text_widget.insert('1.0', template_content)
        text_widget.config(state='disabled')
        
        # 关闭按钮
        self.create_button(preview, "关闭", preview.destroy,
                          style='primary').pack(pady=(0, 24))
    
    def preview_conversion(self):
        """预览转换结果"""
        marked_files = [item for item in selected_code_files_global if item["marked"]]
        
        if not marked_files:
            messagebox.showwarning("警告", "请先标记要预览的文件！")
            return
        
        template_name = self.template_var.get()
        
        # 创建预览窗口
        preview = tk.Toplevel(self.root)
        preview.title(f"转换预览 - {template_name} 模板")
        preview.geometry("900x700")
        preview.configure(bg=self.colors['bg_dark'])
        
        # 标题
        header = tk.Frame(preview, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, padx=24, pady=24)
        
        tk.Label(header, text=f"👁️ 转换预览 ({len(marked_files)} 个文件)",
                font=("Segoe UI", 18, "bold"),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_primary']).pack(anchor="w")
        
        tk.Label(header, text=f"使用模板: {template_name}",
                font=("Segoe UI", 10),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_secondary']).pack(anchor="w", pady=(4, 0))
        
        # 内容
        content_frame = tk.Frame(preview, bg=self.colors['bg_card'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        text_widget = tk.Text(content_frame,
                             font=("Consolas", 9),
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_primary'],
                             wrap=tk.WORD,
                             padx=20, pady=20)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(content_frame, orient="vertical",
                                command=text_widget.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.config(yscrollcommand=scrollbar.set)
        
        # 生成预览内容
        preview_content = []
        for file_item in marked_files:
            formatted = format_file_content(file_item["path"], template_name)
            preview_content.append(formatted)
        
        text_widget.insert('1.0', "".join(preview_content))
        text_widget.config(state='disabled')
        
        # 关闭按钮
        self.create_button(preview, "关闭预览", preview.destroy,
                          style='primary').pack(pady=(0, 24))
    
    def perform_conversion(self):
        """执行转换"""
        marked_files = [item for item in selected_code_files_global if item["marked"]]
        
        if not marked_files:
            messagebox.showwarning("警告", "请先标记要转换的文件！")
            return
        
        # 选择保存文件
        output_file = filedialog.asksaveasfilename(
            title="保存 Markdown 文件",
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if not output_file:
            return
        
        template_name = self.template_var.get()
        
        # 显示进度条
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))
        self.status_label.pack()
        self.progress_var.set(0)
        
        success_count = 0
        total = len(marked_files)
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, file_item in enumerate(marked_files):
                    try:
                        formatted = format_file_content(file_item["path"], template_name)
                        f.write(formatted)
                        success_count += 1
                        
                        # 更新进度
                        progress = ((i + 1) / total) * 100
                        self.progress_var.set(progress)
                        self.status_label.config(
                            text=f"正在处理: {os.path.basename(file_item['path'])} ({i+1}/{total})"
                        )
                        self.root.update_idletasks()
                        
                    except Exception as e:
                        print(f"处理文件出错 {file_item['path']}: {str(e)}")
            
            # 完成
            self.show_status(f"✅ 成功转换 {success_count} 个文件", 'success')
            messagebox.showinfo("完成", 
                              f"成功转换 {success_count} 个文件！\n\n保存位置: {output_file}")
            
        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            self.show_status(f"❌ 转换失败", 'error')
        
        finally:
            # 隐藏进度条
            self.root.after(2000, lambda: self.progress_bar.pack_forget())
            self.root.after(2000, lambda: self.status_label.pack_forget())
    
    def show_status(self, message, status_type='info'):
        """显示状态消息"""
        colors_map = {
            'success': self.colors['accent_success'],
            'error': self.colors['accent_error'],
            'warning': self.colors['accent_warning'],
            'info': self.colors['accent_info']
        }
        
        self.status_label.config(text=message, 
                                fg=colors_map.get(status_type, self.colors['text_muted']))
        self.status_label.pack(pady=(8, 0))
        
        # 3秒后清除消息
        self.root.after(3000, lambda: self.status_label.pack_forget())
    
    
    def show_help(self):
        """显示帮助"""
        help_window = tk.Toplevel(self.root)
        help_window.title("帮助")
        help_window.geometry("600x500")
        help_window.configure(bg=self.colors['bg_dark'])
        
        # 标题
        header = tk.Frame(help_window, bg=self.colors['bg_dark'])
        header.pack(fill=tk.X, padx=24, pady=24)
        
        tk.Label(header, text="❓ 帮助文档",
                font=("Segoe UI", 18, "bold"),
                bg=self.colors['bg_dark'],
                fg=self.colors['text_primary']).pack(anchor="w")
        
        # 内容
        content = tk.Frame(help_window, bg=self.colors['bg_card'])
        content.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))
        
        help_text = """
Code2Markdown Pro 使用指南

基本操作：
1. 点击「添加文件」或「添加文件夹」选择要转换的代码文件
2. 在文件列表中标记需要转换的文件（空格键切换）
3. 选择输出模板样式
4. 点击「预览结果」查看转换效果
5. 点击「开始转换」生成 Markdown 文件

高级功能：
• 搜索和筛选：使用搜索框快速查找文件
• 拖拽添加：直接拖拽文件或文件夹到窗口
• 批量操作：右键菜单提供批量标记等功能
• 自动保存：配置和文件列表会自动保存

支持的语言：
Python, JavaScript, Java, C/C++, C#, PHP, Ruby, Go, Rust,
HTML, CSS, SQL, Shell, YAML, JSON, XML, Markdown 等20+种语言

问题反馈：
如有问题或建议，欢迎反馈！
        """
        
        text_widget = tk.Text(content,
                             font=("Segoe UI", 10),
                             bg=self.colors['bg_card'],
                             fg=self.colors['text_primary'],
                             wrap=tk.WORD,
                             padx=20, pady=20)
        text_widget.pack(fill=tk.BOTH, expand=True)
        text_widget.insert('1.0', help_text.strip())
        text_widget.config(state='disabled')
        
        # 关闭按钮
        self.create_button(help_window, "关闭", help_window.destroy,
                          style='primary').pack(pady=(0, 24))
    
    def setup_drag_drop(self):
        """设置拖拽功能"""
        def on_drop(event):
            files = self.root.tk.splitlist(event.data)
            added = 0
            
            for file_path in files:
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file_path.lower())
                    all_exts = [e for exts in SUPPORTED_EXTENSIONS.values() for e in exts]
                    
                    if ext in all_exts:
                        if not any(item["path"] == file_path for item in selected_code_files_global):
                            selected_code_files_global.append({"path": file_path, "marked": True})
                            added += 1
                
                elif os.path.isdir(file_path):
                    folder_files = get_all_supported_files_in_folder(file_path)
                    for f in folder_files:
                        if not any(item["path"] == f for item in selected_code_files_global):
                            selected_code_files_global.append({"path": f, "marked": True})
                            added += 1
            
            if added > 0:
                self.refresh_file_list()
                self.show_status(f"✅ 拖拽添加了 {added} 个文件", 'success')
        
        self.file_tree.drop_target_register(DND_FILES)
        self.file_tree.dnd_bind('<<Drop>>', on_drop)
    
    def save_config(self):
        """保存配置"""
        config = {
            'window_geometry': self.root.geometry(),
            'template': self.template_var.get(),
            'recent_files': [item["path"] for item in selected_code_files_global],
            'marked_files': [item["path"] for item in selected_code_files_global if item["marked"]]
        }
        
        try:
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
    
    def load_config(self):
        """加载配置"""
        if not os.path.exists(CONFIG_FILE):
            return
        
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'window_geometry' in config:
                self.root.geometry(config['window_geometry'])
            
            if 'template' in config:
                self.template_var.set(config['template'])
            
            if 'recent_files' in config:
                marked_set = set(config.get('marked_files', []))
                for file_path in config['recent_files']:
                    if os.path.exists(file_path):
                        selected_code_files_global.append({
                            "path": file_path,
                            "marked": file_path in marked_set
                        })
                
                self.refresh_file_list()
        
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
    
    def on_closing(self):
        """关闭窗口"""
        self.save_config()
        self.root.destroy()

# 主程序
if __name__ == "__main__":
    if HAS_DND:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    
    app = ModernUI(root)
    root.mainloop()
