import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time
import sys
import json

# 尝试导入拖拽功能
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    HAS_DND = True
except ImportError:
    HAS_DND = False
    print("提示：安装 tkinterdnd2 可启用拖拽功能: pip install tkinterdnd2")

# 配置保存
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "code2markdown_config.json")

# 全局变量，用于存储所有选定的代码文件路径和标记状态
# 每个元素是一个字典: {"path": 文件路径, "marked": 是否标记}
selected_code_files_global = []
# 统一的间距系统
SPACING = {
    'xs': 4,
    'sm': 8,
    'md': 12,
    'lg': 16,
    'xl': 20,
    'xxl': 24,
    'xxxl': 32
}

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
    main_container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxl'], pady=SPACING['xxl'])

    # 标题区域
    header_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    header_frame.pack(fill=tk.X, pady=(0, SPACING['xl']))

    title_icon = tk.Label(header_frame, text="👁️", font=("Segoe UI", 20), bg=colors['bg_primary'], fg=colors['accent_primary'])
    title_icon.pack(side=tk.LEFT)

    title_label = tk.Label(header_frame, text=f"预览转换结果", font=("Segoe UI", 18, "bold"), bg=colors['bg_primary'], fg=colors['text_primary'])
    title_label.pack(side=tk.LEFT, padx=(12, 0))

    template_info = tk.Label(header_frame, text=f"使用 {template_name} 模板", font=("Segoe UI", 10), bg=colors['bg_primary'], fg=colors['text_secondary'])
    template_info.pack(side=tk.RIGHT)

    # 内容显示区域
    content_frame = tk.Frame(main_container, bg=colors['bg_card'], padx=SPACING['xl'], pady=SPACING['xl'])
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    # 创建文本区域显示预览内容
    text_area = tk.Text(content_frame,
                       font=("Consolas", 10),
                       bg=colors['bg_card'],
                       fg=colors['text_primary'],
                       wrap=tk.WORD,
    padx=SPACING['lg'],
    pady=SPACING['lg'],
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
                           padx=SPACING['xxl'],
                           pady=SPACING['md'],
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

    # 检查是否为文件夹
    if item_text.startswith('📁'):
        # 提示用户这是文件夹
        status_label.config(
            text="ℹ️ 文件夹不能直接标记，请标记具体文件",
            fg=colors['accent_warning']
        )
        root.after(2000, lambda: status_label.config(text="就绪", fg=colors['accent_success']))
        return

    # 提取文件名（去掉标记符号）
    filename = item_text[2:] if item_text.startswith(('✓ ', '✗ ')) else item_text

    # 查找对应的文件项
    for file_item in selected_code_files_global:
        if os.path.basename(file_item["path"]) == filename:
            # 切换标记状态
            file_item["marked"] = not file_item["marked"]

            # 显示反馈消息
            mark_status = "标记" if file_item["marked"] else "取消标记"
            status_label.config(
                text=f"✓ 已{mark_status}: {filename}",
                fg=colors['accent_success']
            )
            root.after(2000, lambda: status_label.config(text="就绪", fg=colors['accent_success']))
            break

    # 刷新树显示
    refresh_all_tree_items()

def show_file_info(event):
    """双击显示文件详细信息"""
    selection = selected_files_tree.selection()
    if not selection:
        return

    selected_item = selection[0]
    item_text = selected_files_tree.item(selected_item, 'text')

    if item_text.startswith('📁'):
        return  # 文件夹不显示信息

    filename = item_text[2:] if item_text.startswith(('✓ ', '✗ ')) else item_text

    # 查找文件完整路径
    for file_item in selected_code_files_global:
        if os.path.basename(file_item["path"]) == filename:
            file_path = file_item["path"]

            # 获取文件信息
            file_size = os.path.getsize(file_path)
            file_mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(file_path)))

            # 格式化大小
            if file_size < 1024:
                size_str = f"{file_size} B"
            elif file_size < 1024 * 1024:
                size_str = f"{file_size/1024:.2f} KB"
            else:
                size_str = f"{file_size/(1024*1024):.2f} MB"

            # 显示信息对话框
            info_msg = f"""
文件名: {os.path.basename(file_path)}
路径: {file_path}
大小: {size_str}
修改时间: {file_mtime}
语言: {get_language_from_extension(file_path)}
状态: {'已标记 ✓' if file_item["marked"] else '未标记 ✗'}
            """
            messagebox.showinfo("文件信息", info_msg)
            break

# 不再需要此函数，已被树状结构替代

def refresh_all_tree_items():
    """
    刷新树状结构中所有项目的显示。
    """
    global selected_code_files_global

    # 清空现有树内容
    for item in selected_files_tree.get_children():
        selected_files_tree.delete(item)

    # 如果没有文件，显示空状态提示
    if not selected_code_files_global:
        # 创建空状态提示框（覆盖在树上）
        if not hasattr(refresh_all_tree_items, 'empty_state_frame'):
            refresh_all_tree_items.empty_state_frame = tk.Frame(
                tree_frame,
                bg=colors['bg_card']
            )

        empty_frame = refresh_all_tree_items.empty_state_frame
        empty_frame.place(relx=0.5, rely=0.5, anchor='center')

        # 清空之前的内容
        for widget in empty_frame.winfo_children():
            widget.destroy()

        # 空状态图标
        empty_icon = tk.Label(
            empty_frame,
            text="📂",
            font=("Segoe UI", 48),
            bg=colors['bg_card'],
            fg=colors['text_muted']
        )
        empty_icon.pack(pady=(0, SPACING['lg']))

        # 空状态文字
        empty_title = tk.Label(
            empty_frame,
            text="还没有添加文件",
            font=("Segoe UI", 14, "bold"),
            bg=colors['bg_card'],
            fg=colors['text_secondary']
        )
        empty_title.pack()

        empty_hint = tk.Label(
            empty_frame,
            text="点击「选择文件」或「选择文件夹」开始\n支持 20+ 种编程语言",
            font=("Segoe UI", 10),
            bg=colors['bg_card'],
            fg=colors['text_muted'],
            justify=tk.CENTER
        )
        empty_hint.pack(pady=(SPACING['sm'], 0))

        update_file_count()
        return
    else:
        # 如果有文件，隐藏空状态
        if hasattr(refresh_all_tree_items, 'empty_state_frame'):
            refresh_all_tree_items.empty_state_frame.place_forget()

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

def create_modern_button(parent, text, command, style='primary', tooltip=None):
    """创建带 hover 效果的现代化按钮"""

    # 按钮样式配置
    button_styles = {
        'primary': {
            'bg': colors['accent_primary'],
            'hover_bg': '#4F46E5',
            'active_bg': '#3730A3',
            'fg': colors['text_primary']
        },
        'success': {
            'bg': colors['accent_success'],
            'hover_bg': '#059669',
            'active_bg': '#047857',
            'fg': colors['text_primary']
        },
        'danger': {
            'bg': colors['accent_error'],
            'hover_bg': '#DC2626',
            'active_bg': '#B91C1C',
            'fg': colors['text_primary']
        },
        'secondary': {
            'bg': colors['bg_secondary'],
            'hover_bg': colors['surface'],
            'active_bg': '#333333',
            'fg': colors['text_primary']
        }
    }

    style_config = button_styles.get(style, button_styles['primary'])

    btn = tk.Button(
        parent,
        text=text,
        command=command,
        font=("Segoe UI", 11, "bold"),
        bg=style_config['bg'],
        fg=style_config['fg'],
        relief="flat",
        borderwidth=0,
        padx=SPACING['xl'],
        pady=SPACING['md'],
        cursor="hand2"  # 鼠标悬停时显示手型
    )

    # 绑定 hover 效果
    def on_enter(e):
        btn.config(bg=style_config['hover_bg'])

    def on_leave(e):
        btn.config(bg=style_config['bg'])

    def on_click(e):
        btn.config(bg=style_config['active_bg'])
        btn.after(100, lambda: btn.config(bg=style_config['hover_bg']))

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    btn.bind("<Button-1>", on_click)

    # 添加工具提示
    if tooltip:
        ToolTip(btn, tooltip)

    return btn

class ToolTip:
    """创建工具提示"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window or not self.text:
            return

        x = self.widget.winfo_rootx() + self.widget.winfo_width() // 2
        y = self.widget.winfo_rooty() - 30

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(
            tw,
            text=self.text,
            font=("Segoe UI", 9),
            background=colors['surface'],
            foreground=colors['text_primary'],
            relief="solid",
            borderwidth=1,
            padx=SPACING['sm'],
            pady=SPACING['xs']
        )
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# 创建主窗口
if HAS_DND:
    root = TkinterDnD.Tk()
else:
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
header_content.pack(expand=True, padx=SPACING['xxl'], pady=SPACING['xl'])

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
content_frame.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxl'], pady=SPACING['xxl'])

# 创建左侧面板（文件管理）
left_panel = tk.Frame(content_frame, bg=colors['bg_card'], width=400)
left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, SPACING['md']))
left_panel.pack_propagate(False)

# 创建右侧面板（设置和操作）
right_panel = tk.Frame(content_frame, bg=colors['bg_primary'])
right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 左侧面板标题
left_title_frame = tk.Frame(left_panel, bg=colors['bg_card'])
left_title_frame.pack(fill=tk.X, padx=SPACING['xl'], pady=SPACING['xl'])

left_title = tk.Label(left_title_frame, text="📁 文件管理", font=("Segoe UI", 16, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
left_title.pack(anchor="w")

# 说明区域
description_frame = tk.Frame(left_panel, bg=colors['surface'], padx=SPACING['xl'], pady=SPACING['lg'])
description_frame.pack(fill=tk.X, padx=SPACING['xl'], pady=(0, SPACING['xl']))

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
template_section = tk.Frame(right_panel, bg=colors['bg_card'], pady=SPACING['xxl'])
template_section.pack(fill=tk.X, padx=SPACING['xl'])

# 模板选择标题
template_header = tk.Frame(template_section, bg=colors['bg_card'])
template_header.pack(fill=tk.X, pady=(0, SPACING['lg']))

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

preview_template_btn = create_modern_button(preview_btn_frame,
                                          text="👁️ 预览",
                                          command=lambda: show_template_preview(template_var.get()),
                                          style='secondary',
                                          tooltip="查看当前选中模板的格式示例")
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
    main_container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxl'], pady=SPACING['xxl'])

    # 标题区域
    header_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    header_frame.pack(fill=tk.X, pady=(0, SPACING['xl']))

    title_icon = tk.Label(header_frame, text="📋", font=("Segoe UI", 20), bg=colors['bg_primary'], fg=colors['accent_primary'])
    title_icon.pack(side=tk.LEFT)

    title_label = tk.Label(header_frame, text=f"{template_name} 模板", font=("Segoe UI", 18, "bold"), bg=colors['bg_primary'], fg=colors['text_primary'])
    title_label.pack(side=tk.LEFT, padx=(12, 0))

    # 模板内容显示
    template_content = TEMPLATES[template_name]
    content_frame = tk.Frame(main_container, bg=colors['bg_card'], padx=SPACING['xl'], pady=SPACING['xl'])
    content_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))

    content_label = tk.Text(content_frame,
                           font=("Consolas", 10),
                           bg=colors['bg_card'],
                           fg=colors['text_primary'],
                           wrap=tk.WORD,
    padx=SPACING['lg'],
    pady=SPACING['lg'],
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

    close_btn = create_modern_button(button_frame,
                                   text="关闭预览",
                                   command=preview_window.destroy,
                                   style='primary')
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
status_section = tk.Frame(right_panel, bg=colors['bg_card'], pady=SPACING['xxl'])
status_section.pack(fill=tk.X, padx=SPACING['xl'], pady=(SPACING['xl'], 0))

# 状态标题
status_header = tk.Frame(status_section, bg=colors['bg_card'])
status_header.pack(fill=tk.X, pady=(0, SPACING['lg']))

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

def add_search_bar():
    """在文件树上方添加搜索栏"""

    # 搜索容器
    search_container = tk.Frame(files_container, bg=colors['bg_card'])
    search_container.pack(fill=tk.X, pady=(0, SPACING['md']), before=tree_frame)

    # 搜索图标
    search_icon = tk.Label(
        search_container,
        text="🔍",
        font=("Segoe UI", 14),
        bg=colors['bg_card'],
        fg=colors['text_secondary']
    )
    search_icon.pack(side=tk.LEFT, padx=(0, SPACING['sm']))

    # 搜索输入框
    search_var = tk.StringVar()
    search_entry = tk.Entry(
        search_container,
        textvariable=search_var,
        font=("Segoe UI", 10),
        bg=colors['surface'],
        fg=colors['text_primary'],
        insertbackground=colors['text_primary'],
        relief="flat",
        borderwidth=0
    )
    search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, SPACING['sm']), ipady=6)

    # 占位符提示
    def on_focus_in(event):
        if search_entry.get() == '搜索文件...':
            search_entry.delete(0, tk.END)
            search_entry.config(fg=colors['text_primary'])

    def on_focus_out(event):
        if search_entry.get() == '':
            search_entry.insert(0, '搜索文件...')
            search_entry.config(fg=colors['text_muted'])

    search_entry.insert(0, '搜索文件...')
    search_entry.config(fg=colors['text_muted'])
    search_entry.bind('<FocusIn>', on_focus_in)
    search_entry.bind('<FocusOut>', on_focus_out)

    # 语言筛选下拉框
    filter_var = tk.StringVar(value="全部")

    # 获取所有语言类型
    all_languages = ["全部"] + list(SUPPORTED_EXTENSIONS.keys())

    filter_combo = ttk.Combobox(
        search_container,
        textvariable=filter_var,
        values=all_languages,
        state="readonly",
        font=("Segoe UI", 9),
        width=12,
        style="Modern.TCombobox"
    )
    filter_combo.pack(side=tk.LEFT, padx=(0, SPACING['sm']))

    # 清除按钮
    clear_search_btn = create_modern_button(
        search_container,
        text="✕",
        command=lambda: [search_var.set(''), filter_var.set('全部'), filter_files()],
        style='secondary'
    )
    clear_search_btn.pack(side=tk.LEFT)

    def filter_files(*args):
        """根据搜索词和语言筛选文件"""
        search_term = search_var.get().lower()
        if search_term == '搜索文件...':
            search_term = ''

        language_filter = filter_var.get()

        # 清空树
        for item in selected_files_tree.get_children():
            selected_files_tree.delete(item)

        if not selected_code_files_global:
            refresh_all_tree_items()  # 显示空状态
            return

        # 筛选文件
        filtered_files = []
        for file_item in selected_code_files_global:
            file_path = file_item["path"]
            filename = os.path.basename(file_path).lower()
            file_language = get_language_from_extension(file_path)

            # 应用搜索词筛选
            if search_term and search_term not in filename:
                continue

            # 应用语言筛选
            if language_filter != "全部" and file_language != language_filter:
                continue

            filtered_files.append(file_item)

        # 显示筛选结果
        if not filtered_files:
            # 显示"无结果"提示
            no_result_label = tk.Label(
                tree_frame,
                text=f"😔\n\n未找到匹配的文件\n\n搜索词: {search_term if search_term else '无'}\n语言: {language_filter}",
                font=("Segoe UI", 12),
                bg=colors['bg_card'],
                fg=colors['text_muted'],
                justify=tk.CENTER
            )
            no_result_label.place(relx=0.5, rely=0.5, anchor='center')
        else:
            # 显示筛选后的文件（简化版，不构建树结构）
            for file_item in filtered_files:
                file_path = file_item["path"]
                filename = os.path.basename(file_path)
                language = get_language_from_extension(file_path)

                if file_item["marked"]:
                    display_text = f"✓ {filename}"
                    status_text = "已标记"
                else:
                    display_text = f"✗ {filename}"
                    status_text = "未标记"

                # 获取文件大小
                try:
                    size_bytes = os.path.getsize(file_path)
                    if size_bytes < 1024:
                        file_size = f"{size_bytes}B"
                    elif size_bytes < 1024 * 1024:
                        file_size = f"{size_bytes//1024}KB"
                    else:
                        file_size = f"{size_bytes//(1024*1024)}MB"
                except:
                    file_size = "-"

                selected_files_tree.insert(
                    '', 'end',
                    text=display_text,
                    values=(language, status_text, file_size)
                )

        # 更新文件计数
        marked_count = sum(1 for item in filtered_files if item["marked"])
        total_count = len(filtered_files)
        file_count_label.config(text=f"筛选结果: {marked_count}/{total_count} 个文件（共 {len(selected_code_files_global)} 个）")

    # 绑定实时搜索
    search_var.trace('w', filter_files)
    filter_var.trace('w', filter_files)

    return search_var, filter_var

# 文件树容器（左侧面板主要内容区域）
files_container = tk.Frame(left_panel, bg=colors['bg_card'])
files_container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xl'], pady=(0, SPACING['xl']))

# 文件树标题栏
files_header = tk.Frame(files_container, bg=colors['bg_card'])
files_header.pack(fill=tk.X, pady=(0, SPACING['lg']))

files_title = tk.Label(files_header, text="已选择的文件", font=("Segoe UI", 14, "bold"), bg=colors['bg_card'], fg=colors['text_primary'])
files_title.pack(side=tk.LEFT)

# 快速操作按钮组
actions_frame = tk.Frame(files_header, bg=colors['bg_card'])
actions_frame.pack(side=tk.RIGHT)

select_all_btn = create_modern_button(actions_frame,
                                     text="✓ 全选",
                                     command=select_all_files,
                                     style='success',
                                     tooltip="选中所有文件进行转换")
select_all_btn.pack(side=tk.LEFT, padx=(0, SPACING['sm']))

deselect_all_btn = create_modern_button(actions_frame,
                                      text="✗ 全不选",
                                      command=deselect_all_files,
                                      style='secondary',
                                      tooltip="取消选中所有文件")
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

def create_context_menu():
    """创建右键菜单"""
    def show_context_menu(event):
        """显示右键菜单"""
        # 创建弹出菜单
        context_menu = tk.Menu(root, tearoff=0, bg=colors['bg_card'], fg=colors['text_primary'])

        selection = selected_files_tree.selection()
        if selection:
            context_menu.add_command(label="✓ 标记选中", command=lambda: batch_mark(True))
            context_menu.add_command(label="✗ 取消标记", command=lambda: batch_mark(False))
            context_menu.add_separator()
            context_menu.add_command(label="🗑️ 从列表移除", command=remove_selected_files)
            context_menu.add_separator()

        context_menu.add_command(label="📋 标记所有 Python 文件", command=lambda: mark_by_language('Python'))
        context_menu.add_command(label="📋 标记所有 JavaScript 文件", command=lambda: mark_by_language('JavaScript'))
        context_menu.add_separator()
        context_menu.add_command(label="📁 在资源管理器中打开", command=open_in_explorer)

        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()

    def batch_mark(marked_state):
        """批量标记/取消标记"""
        selection = selected_files_tree.selection()
        for selected_item in selection:
            item_text = selected_files_tree.item(selected_item, 'text')
            if not item_text.startswith('📁'):
                filename = item_text[2:] if item_text.startswith(('✓ ', '✗ ')) else item_text
                for file_item in selected_code_files_global:
                    if os.path.basename(file_item["path"]) == filename:
                        file_item["marked"] = marked_state

        refresh_all_tree_items()
        mark_status = "标记" if marked_state else "取消标记"
        status_label.config(text=f"✓ 已批量{mark_status} {len(selection)} 个文件", fg=colors['accent_success'])
        root.after(2000, lambda: status_label.config(text="就绪", fg=colors['accent_success']))

    def mark_by_language(language):
        """按语言类型标记"""
        count = 0
        for file_item in selected_code_files_global:
            if get_language_from_extension(file_item["path"]) == language:
                file_item["marked"] = True
                count += 1

        refresh_all_tree_items()
        status_label.config(text=f"✓ 已标记 {count} 个 {language} 文件", fg=colors['accent_success'])
        root.after(2000, lambda: status_label.config(text="就绪", fg=colors['accent_success']))

    def open_in_explorer():
        """在文件管理器中打开"""
        selection = selected_files_tree.selection()
        if not selection:
            return

        selected_item = selection[0]
        item_text = selected_files_tree.item(selected_item, 'text')
        filename = item_text[2:] if item_text.startswith(('✓ ', '✗ ')) else item_text

        for file_item in selected_code_files_global:
            if os.path.basename(file_item["path"]) == filename:
                import subprocess
                try:
                    subprocess.Popen(f'explorer /select,"{file_item["path"]}"')
                except:
                    # 如果是其他系统，尝试使用通用方法
                    try:
                        subprocess.Popen(['xdg-open', os.path.dirname(file_item["path"])])
                    except:
                        messagebox.showinfo("提示", f"文件位置: {file_item['path']}")
                break

    # 绑定右键菜单
    selected_files_tree.bind('<Button-3>', show_context_menu)

# 绑定事件
selected_files_tree.bind('<<TreeviewSelect>>', toggle_file_mark)
selected_files_tree.bind('<Double-1>', show_file_info)

# 现代化滚动条
scrollbar = tk.Scrollbar(tree_frame, orient="vertical", command=selected_files_tree.yview, bg=colors['bg_card'], width=16)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_files_tree.config(yscrollcommand=scrollbar.set)

# 操作按钮区域（右侧面板底部）
actions_section = tk.Frame(right_panel, bg=colors['bg_card'], pady=SPACING['xxl'])
actions_section.pack(fill=tk.X, padx=SPACING['xl'], pady=(SPACING['xl'], 0))

# 操作按钮标题
actions_header = tk.Frame(actions_section, bg=colors['bg_card'])
actions_header.pack(fill=tk.X, pady=(0, SPACING['xl']))

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

add_files_button = create_modern_button(add_files_subgroup,
                                      text="📂 选择文件",
                                      command=add_code_files,
                                      style='primary',
                                      tooltip="选择单个或多个代码文件\n支持的格式: .py, .js, .java 等")
add_files_button.pack(side=tk.LEFT, padx=(0, SPACING['md']), fill=tk.X, expand=True)

add_folder_button = create_modern_button(add_files_subgroup,
                                       text="📁 选择文件夹",
                                       command=add_folder,
                                       style='success',
                                       tooltip="选择文件夹，自动递归扫描所有支持的代码文件")
add_folder_button.pack(side=tk.LEFT, padx=(0, SPACING['md']), fill=tk.X, expand=True)

clear_button = create_modern_button(add_files_subgroup,
                                 text="🗑️ 清空列表",
                                 command=clear_selected_files,
                                 style='danger',
                                 tooltip="清空当前选择的所有文件")
clear_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

# 操作执行按钮组
execute_group = tk.Frame(button_groups, bg=colors['bg_card'])
execute_group.pack(fill=tk.X)

execute_group_label = tk.Label(execute_group, text="执行操作:", font=("Segoe UI", 11, "bold"), bg=colors['bg_card'], fg=colors['text_secondary'])
execute_group_label.pack(anchor="w", pady=(0, 8))

execute_subgroup = tk.Frame(execute_group, bg=colors['bg_card'])
execute_subgroup.pack(fill=tk.X)

preview_button = create_modern_button(execute_subgroup,
                                    text="👁️ 预览转换",
                                    command=preview_conversion,
                                    style='secondary',
                                    tooltip="预览转换结果，不会生成文件\n快捷键: Ctrl+P")
preview_button.pack(side=tk.LEFT, padx=(0, SPACING['md']), fill=tk.X, expand=True)

convert_button = create_modern_button(execute_subgroup,
                                   text="开始转换",
                                   command=perform_conversion,
                                   style='success',
                                   tooltip="将选中的文件转换为 Markdown 格式\n快捷键: Ctrl+S")
convert_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

def setup_keyboard_shortcuts():
    """设置全局快捷键"""

    # Ctrl+O - 打开文件
    root.bind('<Control-o>', lambda e: add_code_files())

    # Ctrl+Shift+O - 打开文件夹
    root.bind('<Control-Shift-O>', lambda e: add_folder())

    # Ctrl+P - 预览
    root.bind('<Control-p>', lambda e: preview_conversion())

    # Ctrl+S - 开始转换（保存）
    root.bind('<Control-s>', lambda e: perform_conversion())

    # Ctrl+A - 全选文件
    root.bind('<Control-a>', lambda e: select_all_files())

    # Ctrl+D - 取消全选
    root.bind('<Control-d>', lambda e: deselect_all_files())

    # Delete - 删除选中文件
    root.bind('<Delete>', lambda e: remove_selected_files())

    # F1 - 显示帮助
    root.bind('<F1>', lambda e: show_help())

    # Ctrl+Shift+S - 保存配置
    root.bind('<Control-Shift-S>', lambda e: save_config())

    # Escape - 关闭当前弹窗（如果有）
    root.bind('<Escape>', lambda e: close_topmost_window())

def remove_selected_files():
    """删除选中的文件（从列表中移除）"""
    selection = selected_files_tree.selection()
    if not selection:
        messagebox.showwarning("提示", "请先选择要删除的文件")
        return

    # 获取选中的文件名
    files_to_remove = []
    for selected_item in selection:
        item_text = selected_files_tree.item(selected_item, 'text')
        if not item_text.startswith('📁'):  # 不是文件夹
            filename = item_text[2:] if item_text.startswith(('✓ ', '✗ ')) else item_text
            files_to_remove.append(filename)

    if not files_to_remove:
        return

    # 确认删除
    if messagebox.askyesno("确认", f"确定要从列表中移除 {len(files_to_remove)} 个文件吗？"):
        # 从全局列表中移除
        selected_code_files_global[:] = [
            item for item in selected_code_files_global
            if os.path.basename(item["path"]) not in files_to_remove
        ]

        refresh_all_tree_items()
        status_label.config(text=f"✓ 已移除 {len(files_to_remove)} 个文件")

def show_help():
    """显示帮助窗口"""
    help_window = tk.Toplevel(root)
    help_window.title("快捷键帮助")
    help_window.geometry("500x400")
    help_window.configure(bg=colors['bg_primary'])

    # 主容器
    main_container = tk.Frame(help_window, bg=colors['bg_primary'])
    main_container.pack(fill=tk.BOTH, expand=True, padx=SPACING['xxl'], pady=SPACING['xxl'])

    # 标题区域
    header_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    header_frame.pack(fill=tk.X, pady=(0, SPACING['xl']))

    title_icon = tk.Label(header_frame, text="❓", font=("Segoe UI", 20), bg=colors['bg_primary'], fg=colors['accent_primary'])
    title_icon.pack(side=tk.LEFT)

    title_label = tk.Label(header_frame, text="快捷键帮助", font=("Segoe UI", 18, "bold"), bg=colors['bg_primary'], fg=colors['text_primary'])
    title_label.pack(side=tk.LEFT, padx=(SPACING['md'], 0))

    # 帮助内容
    help_content = tk.Frame(main_container, bg=colors['bg_card'], padx=SPACING['xl'], pady=SPACING['xl'])
    help_content.pack(fill=tk.BOTH, expand=True)

    help_text = tk.Text(help_content,
                       font=("Segoe UI", 10),
                       bg=colors['bg_card'],
                       fg=colors['text_primary'],
                       wrap=tk.WORD,
                       padx=SPACING['lg'],
                       pady=SPACING['lg'],
                       insertbackground=colors['text_primary'])
    help_text.pack(fill=tk.BOTH, expand=True)

    # 插入帮助内容
    help_text.insert(tk.END, "文件操作:\n")
    help_text.insert(tk.END, "  Ctrl+O        添加文件\n")
    help_text.insert(tk.END, "  Ctrl+Shift+O  添加文件夹\n")
    help_text.insert(tk.END, "  Ctrl+A        全选文件\n")
    help_text.insert(tk.END, "  Ctrl+D        取消全选\n")
    help_text.insert(tk.END, "  Delete        删除选中文件\n\n")

    help_text.insert(tk.END, "转换操作:\n")
    help_text.insert(tk.END, "  Ctrl+P        预览转换\n")
    help_text.insert(tk.END, "  Ctrl+S        开始转换\n\n")

    help_text.insert(tk.END, "其他:\n")
    help_text.insert(tk.END, "  F1           显示此帮助\n")
    help_text.insert(tk.END, "  Esc          关闭当前窗口\n")

    help_text.config(state=tk.DISABLED)

    # 底部按钮区域
    button_frame = tk.Frame(main_container, bg=colors['bg_primary'])
    button_frame.pack(fill=tk.X)

    close_btn = create_modern_button(button_frame,
                                   text="关闭",
                                   command=help_window.destroy,
                                   style='primary')
    close_btn.pack()

def close_topmost_window():
    """关闭最顶层的窗口"""
    # 获取所有顶级窗口
    top_levels = [w for w in root.winfo_children() if isinstance(w, tk.Toplevel)]
    if top_levels:
        top_levels[-1].destroy()  # 关闭最顶层的窗口

def setup_drag_and_drop():
    """设置拖拽功能"""
    if not HAS_DND:
        return

    def on_drop(event):
        """处理拖拽事件"""
        files = root.tk.splitlist(event.data)

        added_files = 0
        added_folders = 0

        for file_path in files:
            if os.path.isfile(file_path):
                # 检查是否是支持的文件类型
                _, ext = os.path.splitext(file_path.lower())
                all_extensions = [ext for exts in SUPPORTED_EXTENSIONS.values() for ext in exts]

                if ext in all_extensions:
                    if not any(item["path"] == file_path for item in selected_code_files_global):
                        selected_code_files_global.append({"path": file_path, "marked": True})
                        added_files += 1

            elif os.path.isdir(file_path):
                # 递归添加文件夹中的文件
                supported_files = get_all_supported_files_in_folder(file_path)
                for file in supported_files:
                    if not any(item["path"] == file for item in selected_code_files_global):
                        selected_code_files_global.append({"path": file, "marked": True})
                        added_files += 1
                added_folders += 1

        # 刷新显示
        refresh_all_tree_items()

        # 显示反馈
        if added_files > 0:
            msg = f"✓ 拖拽添加 {added_files} 个文件"
            if added_folders > 0:
                msg += f"（来自 {added_folders} 个文件夹）"
            status_label.config(text=msg, fg=colors['accent_success'])
        else:
            status_label.config(text="ℹ️ 未添加新文件", fg=colors['text_muted'])

    # 绑定拖拽事件到文件树区域
    selected_files_tree.drop_target_register(DND_FILES)
    selected_files_tree.dnd_bind('<<Drop>>', on_drop)

# 在主窗口初始化后调用
setup_keyboard_shortcuts()
setup_drag_and_drop()
create_context_menu()

# 添加搜索栏
search_var, filter_var = add_search_bar()

def save_config():
    """保存当前配置"""
    config = {
        'window_geometry': root.geometry(),
        'template': template_var.get(),
        'recent_files': [item["path"] for item in selected_code_files_global],
        'marked_files': [item["path"] for item in selected_code_files_global if item["marked"]]
    }

    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        status_label.config(text="✓ 配置已保存", fg=colors['accent_success'])
        root.after(2000, lambda: status_label.config(text="就绪", fg=colors['accent_success']))
    except Exception as e:
        messagebox.showerror("错误", f"保存配置失败: {str(e)}")

def load_config():
    """加载配置"""
    if not os.path.exists(CONFIG_FILE):
        return

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)

        # 恢复窗口大小和位置
        if 'window_geometry' in config:
            root.geometry(config['window_geometry'])

        # 恢复模板选择
        if 'template' in config:
            template_var.set(config['template'])

        # 恢复文件列表
        if 'recent_files' in config:
            marked_files_set = set(config.get('marked_files', []))
            for file_path in config['recent_files']:
                if os.path.exists(file_path):  # 只添加仍然存在的文件
                    selected_code_files_global.append({
                        "path": file_path,
                        "marked": file_path in marked_files_set
                    })

            refresh_all_tree_items()
            status_label.config(text="✓ 已恢复上次的文件列表", fg=colors['accent_success'])
            root.after(2000, lambda: status_label.config(text="就绪", fg=colors['accent_success']))

    except Exception as e:
        print(f"加载配置失败: {str(e)}")

def on_closing():
    """窗口关闭时自动保存配置"""
    save_config()
    root.destroy()

# 加载配置
load_config()

# 绑定关闭事件
root.protocol("WM_DELETE_WINDOW", on_closing)

# 运行主循环
root.mainloop()