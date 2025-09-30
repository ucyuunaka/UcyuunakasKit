import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import sys

# 全局变量，用于存储所有选定的代码文件路径和标记状态
# 每个元素是一个字典: {"path": 文件路径, "marked": 是否标记}
selected_code_files_global = []
# 支持的编程语言扩展名
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
    'CSS': ['.css'],
    'SQL': ['.sql'],
    'Shell': ['.sh', '.bash', '.zsh'],
    'YAML': ['.yml', '.yaml'],
    'JSON': ['.json'],
    'XML': ['.xml'],
    'Markdown': ['.md'],
    'Text': ['.txt']
}

# 预定义的 Markdown 模板
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

*文件路径*: `{relative_path}`
*语言*: {language}
*大小*: {size} 字节

---
""",
    "简洁": """```{language}
// {relative_path}
{content}
```"""
}

def get_language_from_extension(file_path):
    """
    根据文件扩展名获取编程语言名称。
    """
    _, ext = os.path.splitext(file_path.lower())
    for language, extensions in SUPPORTED_EXTENSIONS.items():
        if ext in extensions:
            return language
    return "Unknown"

def build_file_tree():
    """
    根据文件路径构建树状结构数据。
    返回: 树结构字典 {路径: {'children': {}, 'marked': bool, 'language': str, 'is_file': bool}}
    """
    tree_data = {}

    for file_item in selected_code_files_global:
        file_path = file_item["path"]
        is_marked = file_item["marked"]
        language = get_language_from_extension(file_path)

        # 标准化路径分隔符
        path_parts = file_path.replace('\\', '/').split('/')
        current_dict = tree_data

        # 构建树结构
        for i, part in enumerate(path_parts[:-1]):  # 除了文件名外的所有路径部分
            if part not in current_dict:
                current_dict[part] = {
                    'children': {},
                    'marked': False,
                    'language': '文件夹',
                    'is_file': False
                }
            current_dict = current_dict[part]['children']

        # 添加文件
        filename = path_parts[-1]
        current_dict[filename] = {
            'children': {},
            'marked': is_marked,
            'language': language,
            'is_file': True
        }

    return tree_data

def add_code_files():
    """
    通过 GUI 界面选择代码文件，并将其路径添加到全局列表和列表框中。
    """
    global selected_code_files_global

    # 构建文件类型过滤器
    filetypes = []
    all_extensions = []
    for language, extensions in SUPPORTED_EXTENSIONS.items():
        filetypes.append((f"{language} files", " ".join(f"*{ext}" for ext in extensions)))
        all_extensions.extend(extensions)

    # 添加"所有支持的文件"选项
    filetypes.append(("所有支持的文件", " ".join(f"*{ext}" for ext in all_extensions)))
    filetypes.append(("所有文件", "*.*"))

    code_files_paths = filedialog.askopenfilenames(
        title="选择要添加的代码文件",
        filetypes=filetypes
    )
    if not code_files_paths:
        return # 用户取消选择

    added_count = 0
    for code_file_path in code_files_paths:
        # 检查文件是否已经存在
        existing_file = next((item for item in selected_code_files_global if item["path"] == code_file_path), None)
        if not existing_file:
            # 添加新文件，默认标记为True
            selected_code_files_global.append({"path": code_file_path, "marked": True})
            added_count += 1

    # 刷新显示
    refresh_all_tree_items()
    root.update_idletasks()

    # 更新状态
    if added_count > 0:
        status_label.config(text=f"✅ 成功添加 {added_count} 个文件")
    else:
        status_label.config(text="ℹ️ 未添加新文件（可能已存在）")

def get_all_supported_files_in_folder(folder_path):
    """
    递归获取文件夹及其子文件夹中所有支持的代码文件。
    """
    supported_files = []
    all_extensions = []
    for extensions in SUPPORTED_EXTENSIONS.values():
        all_extensions.extend(extensions)

    for root_dir, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root_dir, file)
            _, ext = os.path.splitext(file_path.lower())
            if ext in all_extensions:
                supported_files.append(file_path)

    return supported_files

def add_folder():
    """
    通过 GUI 界面选择文件夹，并递归添加其中所有支持的代码文件。
    """
    global selected_code_files_global

    folder_path = filedialog.askdirectory(title="选择要添加的文件夹")
    if not folder_path:
        return # 用户取消选择

    # 获取文件夹中的所有支持文件
    supported_files = get_all_supported_files_in_folder(folder_path)

    if not supported_files:
        status_label.config(text=f"文件夹 '{os.path.basename(folder_path)}' 中未找到支持的代码文件。")
        return

    added_count = 0
    for file_path in supported_files:
        # 检查文件是否已经存在
        existing_file = next((item for item in selected_code_files_global if item["path"] == file_path), None)
        if not existing_file:
            # 添加新文件，默认标记为True
            selected_code_files_global.append({"path": file_path, "marked": True})
            # 文件已添加到全局列表，通过刷新函数更新显示
            added_count += 1

    # 刷新显示
    refresh_all_tree_items()
    root.update_idletasks()

    # 更新状态
    if added_count > 0:
        folder_name = os.path.basename(folder_path)
        status_label.config(text=f"✅ 成功添加文件夹 '{folder_name}' 中的 {added_count} 个文件")
    else:
        status_label.config(text="ℹ️ 文件夹中未找到新文件（可能已存在）")

def format_file_content(file_path, template_name):
    """
    使用指定模板格式化文件内容。
    """
    try:
        current_dir = os.getcwd()
        basename = os.path.basename(file_path)
        language = get_language_from_extension(file_path)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 获取文件信息
        file_size = os.path.getsize(file_path)
        mtime = os.path.getmtime(file_path)

        # 处理相对路径，避免跨盘符问题
        try:
            relative_path = os.path.relpath(file_path, current_dir)
        except ValueError:
            # 如果路径在不同盘符上，回退到使用相对于驱动器根目录的路径
            drive, tail = os.path.splitdrive(file_path)
            if drive:
                relative_path = f"{drive}/.../{os.path.basename(file_path)}"
            else:
                relative_path = os.path.basename(file_path)

        # 格式化模板
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

def preview_conversion():
    """
    预览转换后的 Markdown 内容。只预览标记的文件。
    """
    global selected_code_files_global

    # 获取标记的文件
    marked_files = [item for item in selected_code_files_global if item["marked"]]

    if not selected_code_files_global:
        messagebox.showwarning("警告", "请先添加代码文件！")
        return

    if not marked_files:
        messagebox.showwarning("警告", "没有标记的文件需要预览！请标记要预览的文件。")
        return

    # 获取选择的模板
    template_name = template_var.get()

    # 创建预览内容
    preview_content = []

    for file_item in marked_files:
        code_file_path = file_item["path"]
        formatted_content = format_file_content(code_file_path, template_name)
        preview_content.append(formatted_content)

    # 创建预览窗口
    preview_window = tk.Toplevel(root)
    preview_window.title(f"预览转换结果 - 使用 {template_name} 模板")
    preview_window.geometry("900x700")
    preview_window.configure(bg=colors['bg_primary'])

    # 主容器
    main_container = tk.Frame(preview_window, bg=colors['bg_primary'])
    main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

    # 标题区域
    header_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    header_frame.pack(fill=tk.X, pady=(0, 20))

    title_icon = tk.Label(header_frame, text="👁️", font=("Segoe UI", 20), bg=colors['bg_primary'], fg=colors['accent_primary'])
    title_icon.pack(side=tk.LEFT)

    title_label = tk.Label(header_frame, text=f"预览转换结果", font=("Segoe UI", 18, "bold"), bg=colors['bg_primary'], fg=colors['text_primary'])
    title_label.pack(side=tk.LEFT, padx=(12, 0))

    template_info = tk.Label(header_frame, text=f"使用 {template_name} 模板", font=("Segoe UI", 10), bg=colors['bg_primary'], fg=colors['text_secondary'])
    template_info.pack(side=tk.RIGHT)

    # 内容显示区域
    content_frame = tk.Frame(main_container, bg=colors['bg_card'], padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # 创建文本区域显示预览内容
    text_area = tk.Text(content_frame,
                       font=("Consolas", 10),
                       bg=colors['bg_card'],
                       fg=colors['text_primary'],
                       wrap=tk.WORD,
                       padx=16,
                       pady=16,
                       insertbackground=colors['text_primary'],
                       selectbackground=colors['accent_primary'],
                       selectforeground=colors['text_primary'])
    text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # 添加现代化滚动条
    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=text_area.yview, bg=colors['bg_card'], width=16)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.config(yscrollcommand=scrollbar.set)

    # 插入预览内容
    preview_text = "".join(preview_content)
    text_area.insert(tk.END, preview_text)

    # 禁止编辑
    text_area.config(state=tk.DISABLED)

    # 底部按钮区域
    button_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    button_frame.pack(fill=tk.X)

    close_button = tk.Button(button_frame,
                           text="关闭预览",
                           command=preview_window.destroy,
                           font=("Segoe UI", 11, "bold"),
                           bg=colors['accent_primary'],
                           fg=colors['text_primary'],
                           relief="flat",
                           padx=24,
                           pady=10,
                           height=2)
    close_button.pack()

def select_all_files():
    """全选所有文件"""
    global selected_code_files_global
    for file_item in selected_code_files_global:
        file_item["marked"] = True
    refresh_all_tree_items()
    update_file_count()

def deselect_all_files():
    """取消全选所有文件"""
    global selected_code_files_global
    for file_item in selected_code_files_global:
        file_item["marked"] = False
    refresh_all_tree_items()
    update_file_count()

def update_file_count():
    """更新文件计数显示"""
    marked_count = sum(1 for item in selected_code_files_global if item["marked"])
    total_count = len(selected_code_files_global)
    file_count_label.config(text=f"已选择: {marked_count}/{total_count} 个文件")

def clear_selected_files():
    """
    清空已选择的代码文件列表和树状结构。
    """
    global selected_code_files_global
    selected_code_files_global.clear()
    # 清空树状结构
    for item in selected_files_tree.get_children():
        selected_files_tree.delete(item)
    status_label.config(text="✅ 文件列表已清空")
    file_count_label.config(text="已选择: 0 个文件")

def toggle_file_mark(event):
    """
    切换选中文件的标记状态。
    """
    global selected_code_files_global

    # 获取选中的项目
    selection = selected_files_tree.selection()
    if not selection:
        return

    # 获取选中项目的ID
    selected_item = selection[0]
    item_text = selected_files_tree.item(selected_item, 'text')
    item_values = selected_files_tree.item(selected_item, 'values')

    # 检查是否为文件（不是文件夹）
    if item_text.startswith('📁'):
        return  # 跳过文件夹

    # 提取文件名（去掉标记符号）
    filename = item_text[2:] if item_text.startswith(('✓ ', '✗ ')) else item_text

    # 查找对应的文件项
    for file_item in selected_code_files_global:
        if os.path.basename(file_item["path"]) == filename:
            # 切换标记状态
            file_item["marked"] = not file_item["marked"]
            break

    # 刷新树显示
    refresh_all_tree_items()

# 不再需要此函数，已被树状结构替代

def refresh_all_tree_items():
    """
    刷新树状结构中所有项目的显示。
    """
    global selected_code_files_global

    # 清空现有树内容
    for item in selected_files_tree.get_children():
        selected_files_tree.delete(item)

    # 构建树结构数据
    tree_data = build_file_tree()

    # 递归添加树节点
    def add_tree_nodes(parent_id, parent_dict, parent_path=""):
        for name, node_data in parent_dict.items():
            current_path = os.path.join(parent_path, name) if parent_path else name

            # 根据标记状态设置文本和图标
            if node_data['is_file']:
                if node_data['marked']:
                    display_text = f"✓ {name}"
                    status_text = "已标记"
                else:
                    display_text = f"✗ {name}"
                    status_text = "未标记"

                # 获取文件大小（如果是文件）
                file_size = "-"
                if node_data['is_file']:
                    try:
                        size_bytes = os.path.getsize(os.path.join(parent_path, name) if parent_path else name)
                        if size_bytes < 1024:
                            file_size = f"{size_bytes}B"
                        elif size_bytes < 1024 * 1024:
                            file_size = f"{size_bytes//1024}KB"
                        else:
                            file_size = f"{size_bytes//(1024*1024)}MB"
                    except:
                        file_size = "-"
            else:
                display_text = f"📁 {name}"
                status_text = "-"
                file_size = "-"

            # 插入节点
            item_id = selected_files_tree.insert(
                parent_id, 'end',
                text=display_text,
                values=(node_data['language'], status_text, file_size)
            )

            # 如果有子节点，递归添加
            if node_data['children']:
                add_tree_nodes(item_id, node_data['children'], current_path)

    # 添加根节点
    add_tree_nodes('', tree_data)

    # 展开所有节点
    def expand_all_nodes(parent_id):
        children = selected_files_tree.get_children(parent_id)
        for child_id in children:
            selected_files_tree.item(child_id, open=True)
            expand_all_nodes(child_id)

    expand_all_nodes('')

    # 更新文件计数
    update_file_count()

def perform_conversion():
    """
    使用全局列表中的代码文件进行转换，并将代码内容写入 Markdown 文件。
    只处理已标记的文件。
    """
    global selected_code_files_global

    # 获取标记的文件
    marked_files = [item for item in selected_code_files_global if item["marked"]]

    if not selected_code_files_global:
        messagebox.showwarning("警告", "请先添加代码文件！")
        return

    if not marked_files:
        messagebox.showwarning("警告", "没有标记的文件需要转换！请标记要转换的文件。")
        return

    # 获取选择的模板
    template_name = template_var.get()

    # 选择或创建 Markdown 文件
    md_file_path = filedialog.asksaveasfilename(
        title="选择或创建要写入的 Markdown 文件",
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.*")]
    )
    if not md_file_path:
        return # 用户取消选择

    success_count = 0
    error_files = []

    # 初始化进度条
    progress_var.set(0)
    total_files = len(marked_files)

    try:
        with open(md_file_path, 'a', encoding='utf-8') as md_file:
            for i, file_item in enumerate(marked_files):
                code_file_path = file_item["path"]
                try:
                    # 更新状态标签，显示当前正在处理的文件
                    status_label.config(text=f"正在处理文件 ({i+1}/{total_files}): {os.path.basename(code_file_path)}")
                    root.update_idletasks() # 强制 GUI 更新

                    # 使用模板格式化文件内容
                    formatted_content = format_file_content(code_file_path, template_name)
                    md_file.write(formatted_content)
                    success_count += 1

                    # 更新进度条
                    progress = ((i + 1) / total_files) * 100
                    progress_var.set(progress)
                    root.update_idletasks()

                except UnicodeDecodeError:
                    error_msg = f"文件编码错误: {os.path.basename(code_file_path)}"
                    error_files.append(error_msg)
                    error_content = format_file_content(code_file_path, template_name)
                    md_file.write(error_content)
                except IOError as e:
                    error_msg = f"文件读取错误 {os.path.basename(code_file_path)}: {str(e)}"
                    error_files.append(error_msg)
                    error_content = format_file_content(code_file_path, template_name)
                    md_file.write(error_content)
                except Exception as e:
                    error_msg = f"处理文件错误 {os.path.basename(code_file_path)}: {str(e)}"
                    error_files.append(error_msg)
                    error_content = format_file_content(code_file_path, template_name)
                    md_file.write(error_content)

        # 显示处理结果
        result_msg = f"转换完成！成功处理 {success_count} 个文件"
        if error_files:
            result_msg += f"，{len(error_files)} 个文件出现错误"
            messagebox.showwarning("转换完成（有错误）", f"{result_msg}\n\n错误文件:\n" + "\n".join(error_files))
        else:
            messagebox.showinfo("成功", f"{result_msg}\n\n所有文件已写入到: {md_file_path}\n使用模板: {template_name}")

        status_label.config(text=f"转换完成！使用 {template_name} 模板")
        # 隐藏进度条
        progress_bar.pack_forget()
        # 不清空列表，让用户可以继续使用
        root.after(3000, lambda: status_label.config(text="")) # 3秒后清空状态标签

    except IOError as e:
        messagebox.showerror("错误", f"无法写入目标文件: {str(e)}")
        status_label.config(text=f"写入错误: {str(e)}")
    except Exception as e:
        messagebox.showerror("错误", f"处理文件时发生未知错误: {str(e)}")
        status_label.config(text=f"未知错误: {str(e)}")

def create_rounded_rectangle(canvas, x1, y1, x2, y2, radius=25, **kwargs):
    """创建圆角矩形"""
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1
    ]

    return canvas.create_polygon(points, smooth=True, **kwargs)

def setup_modern_theme():
    """设置现代化主题样式"""
    style = ttk.Style()

    # 现代深色主题配色方案
    bg_primary = "#0F0F0F"  # 主背景，更深
    bg_secondary = "#1A1A1A"  # 次要背景
    bg_card = "#242424"  # 卡片背景
    surface_color = "#2D2D2D"  # 表面色

    # 现代色彩方案
    accent_primary = "#6366F1"  # 现代紫蓝色
    accent_secondary = "#8B5CF6"  # 紫色
    accent_success = "#10B981"  # 绿色
    accent_warning = "#F59E0B"  # 橙黄色
    accent_error = "#EF4444"  # 红色

    # 文字颜色
    text_primary = "#FFFFFF"
    text_secondary = "#B3B3B3"
    text_muted = "#888888"

    # 边框和分割线
    border_color = "#3A3A3A"
    border_light = "#4A4A4A"

    # 配置主窗口样式
    root.configure(bg=bg_primary)

    # 创建自定义样式
    style.configure("Card.TFrame", background=bg_card, relief="flat")
    style.configure("Surface.TFrame", background=surface_color, relief="flat")

    # 标题样式
    style.configure("Hero.TLabel",
                   background=bg_primary,
                   foreground=text_primary,
                   font=("Segoe UI", 18, "bold"))

    style.configure("Title.TLabel",
                   background=bg_primary,
                   foreground=text_primary,
                   font=("Segoe UI", 14, "bold"))

    style.configure("Subtitle.TLabel",
                   background=bg_primary,
                   foreground=text_secondary,
                   font=("Segoe UI", 10))

    style.configure("Body.TLabel",
                   background=bg_primary,
                   foreground=text_primary,
                   font=("Segoe UI", 10))

    style.configure("Caption.TLabel",
                   background=bg_primary,
                   foreground=text_muted,
                   font=("Segoe UI", 9))

    # 现代化按钮样式
    style.configure("Primary.TButton",
                   background=accent_primary,
                   foreground=text_primary,
                   font=("Segoe UI", 10, "bold"),
                   relief="flat",
                   borderwidth=0,
                   padding=(16, 8))
    style.map("Primary.TButton",
             background=[("active", "#4F46E5"),
                        ("pressed", "#3730A3")],
             relief=[("pressed", "sunken")])

    style.configure("Secondary.TButton",
                   background=bg_secondary,
                   foreground=text_primary,
                   font=("Segoe UI", 10),
                   relief="flat",
                   borderwidth=1,
                   bordercolor=border_color,
                   padding=(14, 7))
    style.map("Secondary.TButton",
             background=[("active", surface_color),
                        ("pressed", "#333333")])

    style.configure("Success.TButton",
                   background=accent_success,
                   foreground=text_primary,
                   font=("Segoe UI", 10, "bold"),
                   relief="flat",
                   borderwidth=0,
                   padding=(16, 8))
    style.map("Success.TButton",
             background=[("active", "#059669"),
                        ("pressed", "#047857")])

    style.configure("Warning.TButton",
                   background=accent_warning,
                   foreground="#1F2937",
                   font=("Segoe UI", 10, "bold"),
                   relief="flat",
                   borderwidth=0,
                   padding=(14, 7))
    style.map("Warning.TButton",
             background=[("active", "#D97706"),
                        ("pressed", "#B45309")])

    style.configure("Danger.TButton",
                   background=accent_error,
                   foreground=text_primary,
                   font=("Segoe UI", 10, "bold"),
                   relief="flat",
                   borderwidth=0,
                   padding=(14, 7))
    style.map("Danger.TButton",
             background=[("active", "#DC2626"),
                        ("pressed", "#B91C1C")])

    # 树状结构现代化样式
    style.configure("Modern.Treeview",
                   background=bg_card,
                   foreground=text_primary,
                   fieldbackground=bg_card,
                   borderwidth=0,
                   font=("Segoe UI", 9),
                   rowheight=28)
    style.configure("Modern.Treeview.Heading",
                   background=bg_secondary,
                   foreground=text_primary,
                   relief="flat",
                   font=("Segoe UI", 10, "bold"),
                   borderwidth=0)
    style.map("Modern.Treeview",
             background=[("selected", accent_primary)],
             foreground=[("selected", text_primary)])

    # 进度条现代化样式
    style.configure("Modern.Horizontal.TProgressbar",
                   background=accent_primary,
                   troughcolor=bg_secondary,
                   borderwidth=0,
                   lightcolor=accent_primary,
                   darkcolor=accent_primary,
                   thickness=8)

    # 下拉框样式
    style.configure("Modern.TCombobox",
                   background=bg_card,
                   foreground=text_primary,
                   fieldbackground=bg_card,
                   borderwidth=1,
                   relief="flat",
                   arrowcolor=text_primary,
                   font=("Segoe UI", 10))

    # 标签框架样式
    style.configure("Card.TLabelframe",
                   background=bg_card,
                   foreground=text_primary,
                   borderwidth=1,
                   relief="groove",
                   font=("Segoe UI", 11, "bold"),
                   labelmargins=10)
    style.configure("Card.TLabelframe.Label",
                   background=accent_primary,
                   foreground=text_primary,
                   font=("Segoe UI", 11, "bold"))

    return {
        'bg_primary': bg_primary,
        'bg_secondary': bg_secondary,
        'bg_card': bg_card,
        'surface': surface_color,
        'accent_primary': accent_primary,
        'accent_secondary': accent_secondary,
        'accent_success': accent_success,
        'accent_warning': accent_warning,
        'accent_error': accent_error,
        'text_primary': text_primary,
        'text_secondary': text_secondary,
        'text_muted': text_muted,
        'border': border_color,
        'border_light': border_light
    }

# 创建主窗口
root = tk.Tk()
root.title("Code2Markdown Pro - 代码转 Markdown 工具")
root.geometry("1200x800")
root.resizable(True, True)
root.minsize(1000, 700)

# 设置现代化主题
colors = setup_modern_theme()

# 创建主容器（使用网格布局）
main_container = tk.Frame(root, bg=colors['bg_primary'])
main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

# 创建顶部标题栏
header_frame = tk.Frame(main_container, bg=colors['bg_primary'], height=80)
header_frame.pack(fill=tk.X, padx=0, pady=0)
header_frame.pack_propagate(False)

# 标题栏内容
header_content = tk.Frame(header_frame, bg=colors['bg_primary'])
header_content.pack(expand=True, padx=24, pady=20)

# 左侧标题区域
title_section = tk.Frame(header_content, bg=colors['bg_primary'])
title_section.pack(side=tk.LEFT)

title_icon = tk.Label(title_section, text="🚀", font=("Segoe UI", 28), bg=colors['bg_primary'], fg=colors['accent_primary'])
title_icon.pack(side=tk.LEFT)

title_text_frame = tk.Frame(title_section, bg=colors['bg_primary'])
title_text_frame.pack(side=tk.LEFT, padx=(16, 0))

title_label = tk.Label(title_text_frame, text="Code2Markdown Pro", font=("Segoe UI", 24, "bold"), bg=colors['bg_primary'], fg=colors['text_primary'])
title_label.pack(anchor="w")

subtitle_label = tk.Label(title_text_frame, text="专业的代码转 Markdown 转换工具", font=("Segoe UI", 11), bg=colors['bg_primary'], fg=colors['text_secondary'])
subtitle_label.pack(anchor="w")

# 右侧信息区域
info_section = tk.Frame(header_content, bg=colors['bg_primary'])
info_section.pack(side=tk.RIGHT)

version_label = tk.Label(info_section, text="v2.0", font=("Segoe UI", 12, "bold"), bg=colors['bg_primary'], fg=colors['accent_primary'])
version_label.pack(anchor="e")

stats_label = tk.Label(info_section, text="支持 20+ 编程语言", font=("Segoe UI", 10), bg=colors['bg_primary'], fg=colors['text_muted'])
stats_label.pack(anchor="e", pady=(4, 0))

# 创建主内容区域
content_frame = tk.Frame(main_container, bg=colors['bg_primary'])
content_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

# 创建左侧面板（文件管理）
left_panel = tk.Frame(content_frame, bg=colors['bg_card'], width=400)
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
left_panel.pack_propagate(False)

# 创建右侧面板（设置和操作）
right_panel = tk.Frame(content_frame, bg=colors['bg_primary'])
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 左侧面板标题
left_title_frame = tk.Frame(left_panel, bg=colors['bg_card'])
left_title_frame.pack(fill=tk.X, padx=20, pady=20)

left_title = tk.Label(left_title_frame, text="📁 文件管理", font=("Segoe UI", 16, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
left_title.pack(anchor="w")

# 说明区域
description_frame = tk.Frame(left_panel, bg=colors['surface'], padx=20, pady=16)
description_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

description_icon = tk.Label(description_frame, text="✨", font=("Segoe UI", 14), bg=colors['surface'], fg=colors['accent_primary'])
description_icon.pack(anchor="w")

description_text = tk.Label(description_frame,
                           text="选择要转换的代码文件或文件夹\n支持递归扫描子目录",
                           font=("Segoe UI", 10),
                           bg=colors['surface'],
                           fg=colors['text_secondary'],
                           justify=tk.LEFT,
                           anchor="w")
description_text.pack(anchor="w", pady=(8, 0))

# 模板选择区域（右侧面板上部）
template_section = tk.Frame(right_panel, bg=colors['bg_card'], pady=24)
template_section.pack(fill=tk.X, padx=20)

# 模板选择标题
template_header = tk.Frame(template_section, bg=colors['bg_card'])
template_header.pack(fill=tk.X, pady=(0, 16))

template_icon = tk.Label(template_header, text="🎨", font=("Segoe UI", 18), bg=colors['bg_card'], fg=colors['accent_primary'])
template_icon.pack(side=tk.LEFT)

template_title = tk.Label(template_header, text="输出模板", font=("Segoe UI", 16, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
template_title.pack(side=tk.LEFT, padx=(12, 0))

# 模板选择控件
template_controls = tk.Frame(template_section, bg=colors['bg_card'])
template_controls.pack(fill=tk.X)

template_label = tk.Label(template_controls, text="选择模板样式:", font=("Segoe UI", 11), bg=colors['bg_card'], fg=colors['text_secondary'])
template_label.pack(anchor="w", pady=(0, 8))

template_combo_frame = tk.Frame(template_controls, bg=colors['bg_card'])
template_combo_frame.pack(fill=tk.X)

template_var = tk.StringVar(value="默认")
template_combo = ttk.Combobox(template_combo_frame,
                             textvariable=template_var,
                             values=list(TEMPLATES.keys()),
                             state="readonly",
                             font=("Segoe UI", 11),
                             style="Modern.TCombobox")
template_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 模板预览按钮
preview_btn_frame = tk.Frame(template_combo_frame, bg=colors['bg_card'])
preview_btn_frame.pack(side=tk.RIGHT, padx=(12, 0))

preview_template_btn = tk.Button(preview_btn_frame,
                               text="👁️ 预览",
                               command=lambda: show_template_preview(template_var.get()),
                               font=("Segoe UI", 10, "bold"),
                               bg=colors['accent_secondary'],
                               fg=colors['text_primary'],
                               relief="flat",
                               padx=16,
                               pady=8,
                               width=10)
preview_template_btn.pack()

def show_template_preview(template_name):
    """显示模板预览窗口"""
    if template_name not in TEMPLATES:
        return

    preview_window = tk.Toplevel(root)
    preview_window.title(f"模板预览 - {template_name}")
    preview_window.geometry("700x500")
    preview_window.configure(bg=colors['bg_primary'])

    # 主容器
    main_container = tk.Frame(preview_window, bg=colors['bg_primary'])
    main_container.pack(fill=tk.BOTH, expand=True, padx=24, pady=24)

    # 标题区域
    header_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    header_frame.pack(fill=tk.X, pady=(0, 20))

    title_icon = tk.Label(header_frame, text="📋", font=("Segoe UI", 20), bg=colors['bg_primary'], fg=colors['accent_primary'])
    title_icon.pack(side=tk.LEFT)

    title_label = tk.Label(header_frame, text=f"{template_name} 模板", font=("Segoe UI", 18, "bold"), bg=colors['bg_primary'], fg=colors['text_primary'])
    title_label.pack(side=tk.LEFT, padx=(12, 0))

    # 模板内容显示
    template_content = TEMPLATES[template_name]
    content_frame = tk.Frame(main_container, bg=colors['bg_card'], padx=20, pady=20)
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    content_label = tk.Text(content_frame,
                           font=("Consolas", 10),
                           bg=colors['bg_card'],
                           fg=colors['text_primary'],
                           wrap=tk.WORD,
                           padx=16,
                           pady=16,
                           insertbackground=colors['text_primary'])
    content_label.pack(fill=tk.BOTH, expand=True)

    # 插入模板内容和说明
    content_label.insert(tk.END, "# 模板内容预览\n\n")
    content_label.insert(tk.END, template_content)
    content_label.insert(tk.END, "\n\n# 使用说明\n")
    content_label.insert(tk.END, get_template_description(template_name))

    content_label.config(state=tk.DISABLED)

    # 底部按钮区域
    button_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    button_frame.pack(fill=tk.X)

    close_btn = tk.Button(button_frame,
                         text="关闭预览",
                         command=preview_window.destroy,
                         font=("Segoe UI", 11, "bold"),
                         bg=colors['accent_primary'],
                         fg=colors['text_primary'],
                         relief="flat",
                         padx=24,
                         pady=10,
                         height=2)
    close_btn.pack()

def get_template_description(template_name):
    """获取模板的描述信息"""
    descriptions = {
        "默认": "简洁的代码块格式，适合快速预览。",
        "带注释": "包含文件元数据（如大小、修改时间）的详细格式。",
        "GitHub风格": "模仿GitHub文件显示的样式，包含文件路径信息。",
        "简洁": "极简格式，只显示代码内容。"
    }
    return descriptions.get(template_name, "无描述信息")

# 状态和进度区域（右侧面板中部）
status_section = tk.Frame(right_panel, bg=colors['bg_card'], pady=24)
status_section.pack(fill=tk.X, padx=20, pady=(20, 0))

# 状态标题
status_header = tk.Frame(status_section, bg=colors['bg_card'])
status_header.pack(fill=tk.X, pady=(0, 16))

status_icon = tk.Label(status_header, text="📊", font=("Segoe UI", 18), bg=colors['bg_card'], fg=colors['accent_primary'])
status_icon.pack(side=tk.LEFT)

status_title = tk.Label(status_header, text="转换状态", font=("Segoe UI", 16, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
status_title.pack(side=tk.LEFT, padx=(12, 0))

# 状态信息区域
status_info_frame = tk.Frame(status_section, bg=colors['bg_card'])
status_info_frame.pack(fill=tk.X, pady=(0, 16))

status_label = tk.Label(status_info_frame,
                       text="就绪",
                       font=("Segoe UI", 12, "bold"),
                       bg=colors['bg_card'],
                       fg=colors['accent_success'],
                       anchor="w")
status_label.pack(fill=tk.X)

# 文件计数显示
file_count_frame = tk.Frame(status_info_frame, bg=colors['bg_card'])
file_count_frame.pack(fill=tk.X, pady=(8, 0))

file_count_label = tk.Label(file_count_frame, text="已选择: 0 个文件", font=("Segoe UI", 10), bg=colors['bg_card'], fg=colors['text_secondary'])
file_count_label.pack(anchor="w")

# 进度区域
progress_container = tk.Frame(status_section, bg=colors['bg_card'])
progress_container.pack(fill=tk.X)

progress_label = tk.Label(progress_container, text="转换进度:", font=("Segoe UI", 11), bg=colors['bg_card'], fg=colors['text_secondary'])
progress_label.pack(anchor="w", pady=(0, 8))

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_container,
                              variable=progress_var,
                              maximum=100,
                              style="Modern.Horizontal.TProgressbar")
progress_bar.pack(fill=tk.X, pady=(0, 8))

# 文件树容器（左侧面板主要内容区域）
files_container = tk.Frame(left_panel, bg=colors['bg_card'])
files_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

# 文件树标题栏
files_header = tk.Frame(files_container, bg=colors['bg_card'])
files_header.pack(fill=tk.X, pady=(0, 16))

files_title = tk.Label(files_header, text="已选择的文件", font=("Segoe UI", 14, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
files_title.pack(side=tk.LEFT)

# 快速操作按钮组
actions_frame = tk.Frame(files_header, bg=colors['bg_card'])
actions_frame.pack(side=tk.RIGHT)

select_all_btn = tk.Button(actions_frame,
                          text="✓ 全选",
                          command=select_all_files,
                          font=("Segoe UI", 9, "bold"),
                          bg=colors['accent_success'],
                          fg=colors['text_primary'],
                          relief="flat",
                          padx=12,
                          pady=6)
select_all_btn.pack(side=tk.LEFT, padx=(0, 8))

deselect_all_btn = tk.Button(actions_frame,
                           text="✗ 全不选",
                           command=deselect_all_files,
                           font=("Segoe UI", 9, "bold"),
                           bg=colors['accent_warning'],
                           fg=colors['text_primary'],
                           relief="flat",
                           padx=12,
                           pady=6)
deselect_all_btn.pack(side=tk.LEFT)

# 文件树框架
tree_frame = tk.Frame(files_container, bg=colors['bg_card'])
tree_frame.pack(fill=tk.BOTH, expand=True)

# 创建现代化树状结构
selected_files_tree = ttk.Treeview(tree_frame,
                                  columns=('language', 'status', 'size'),
                                  show='tree headings',
                                  style="Modern.Treeview")

selected_files_tree.heading('#0', text='📄 文件/文件夹')
selected_files_tree.heading('language', text='💻 语言')
selected_files_tree.heading('status', text='✅ 状态')
selected_files_tree.heading('size', text='📏 大小')

# 设置现代化列宽和样式
selected_files_tree.column('#0', width=280, minwidth=200)
selected_files_tree.column('language', width=90, minwidth=70)
selected_files_tree.column('status', width=80, minwidth=60)
selected_files_tree.column('size', width=80, minwidth=60)

selected_files_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 绑定事件
selected_files_tree.bind('<<TreeviewSelect>>', toggle_file_mark)

# 现代化滚动条
scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=selected_files_tree.yview, bg=colors['bg_card'], width=16)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_files_tree.config(yscrollcommand=scrollbar.set)

# 操作按钮区域（右侧面板底部）
actions_section = tk.Frame(right_panel, bg=colors['bg_card'], pady=24)
actions_section.pack(fill=tk.X, padx=20, pady=(20, 0))

# 操作按钮标题
actions_header = tk.Frame(actions_section, bg=colors['bg_card'])
actions_header.pack(fill=tk.X, pady=(0, 20))

actions_icon = tk.Label(actions_header, text="⚡", font=("Segoe UI", 18), bg=colors['bg_card'], fg=colors['accent_primary'])
actions_icon.pack(side=tk.LEFT)

actions_title = tk.Label(actions_header, text="操作控制", font=("Segoe UI", 16, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
actions_title.pack(side=tk.LEFT, padx=(12, 0))

# 按钮组容器
button_groups = tk.Frame(actions_section, bg=colors['bg_card'])
button_groups.pack(fill=tk.X)

# 文件添加按钮组
add_files_group = tk.Frame(button_groups, bg=colors['bg_card'])
add_files_group.pack(fill=tk.X, pady=(0, 12))

add_files_group_label = tk.Label(add_files_group, text="添加文件:", font=("Segoe UI", 11, "bold"), bg=colors['bg_card'], fg=colors['text_secondary'])
add_files_group_label.pack(anchor="w", pady=(0, 8))

add_files_subgroup = tk.Frame(add_files_group, bg=colors['bg_card'])
add_files_subgroup.pack(fill=tk.X)

add_files_button = tk.Button(add_files_subgroup,
                           text="📂 选择文件",
                           command=add_code_files,
                           font=("Segoe UI", 11, "bold"),
                           bg=colors['accent_primary'],
                           fg=colors['text_primary'],
                           relief="flat",
                           padx=20,
                           pady=12,
                           height=2)
add_files_button.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)

add_folder_button = tk.Button(add_files_subgroup,
                            text="📁 选择文件夹",
                            command=add_folder,
                            font=("Segoe UI", 11, "bold"),
                            bg=colors['accent_success'],
                            fg=colors['text_primary'],
                            relief="flat",
                            padx=20,
                            pady=12,
                            height=2)
add_folder_button.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)

clear_button = tk.Button(add_files_subgroup,
                       text="🗑️ 清空列表",
                       command=clear_selected_files,
                       font=("Segoe UI", 11, "bold"),
                       bg=colors['accent_error'],
                       fg=colors['text_primary'],
                       relief="flat",
                       padx=20,
                       pady=12,
                       height=2)
clear_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 操作执行按钮组
execute_group = tk.Frame(button_groups, bg=colors['bg_card'])
execute_group.pack(fill=tk.X)

execute_group_label = tk.Label(execute_group, text="执行操作:", font=("Segoe UI", 11, "bold"), bg=colors['bg_card'], fg=colors['text_secondary'])
execute_group_label.pack(anchor="w", pady=(0, 8))

execute_subgroup = tk.Frame(execute_group, bg=colors['bg_card'])
execute_subgroup.pack(fill=tk.X)

preview_button = tk.Button(execute_subgroup,
                         text="👁️ 预览转换",
                         command=preview_conversion,
                         font=("Segoe UI", 11, "bold"),
                         bg=colors['accent_secondary'],
                         fg=colors['text_primary'],
                         relief="flat",
                         padx=20,
                         pady=12,
                         height=2)
preview_button.pack(side=tk.LEFT, padx=(0, 12), fill=tk.X, expand=True)

convert_button = tk.Button(execute_subgroup,
                          text="🚀 开始转换",
                          command=perform_conversion,
                          font=("Segoe UI", 11, "bold"),
                          bg=colors['accent_success'],
                          fg=colors['text_primary'],
                          relief="flat",
                          padx=20,
                          pady=12,
                          height=2)
convert_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 运行主循环
root.mainloop()