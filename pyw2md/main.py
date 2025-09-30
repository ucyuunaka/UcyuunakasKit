import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import time

# 全局变量，用于存储所有选定的代码文件路径
selected_code_paths_global = []
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

def add_code_files():
    """
    通过 GUI 界面选择代码文件，并将其路径添加到全局列表和列表框中。
    """
    global selected_code_paths_global

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
        if code_file_path not in selected_code_paths_global:
            selected_code_paths_global.append(code_file_path)
            # 在列表中显示文件名和语言类型
            filename = os.path.basename(code_file_path)
            language = get_language_from_extension(code_file_path)
            selected_files_listbox.insert(tk.END, f"{filename} ({language})")
            added_count += 1

    status_label.config(text=f"已添加 {added_count} 个文件。当前共 {len(selected_code_paths_global)} 个文件待转换。")
    root.update_idletasks()

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
    预览转换后的 Markdown 内容。
    """
    global selected_code_paths_global

    if not selected_code_paths_global:
        messagebox.showwarning("警告", "请先添加代码文件！")
        return

    # 获取选择的模板
    template_name = template_var.get()

    # 创建预览内容
    preview_content = []

    for code_file_path in selected_code_paths_global:
        formatted_content = format_file_content(code_file_path, template_name)
        preview_content.append(formatted_content)

    # 创建预览窗口
    preview_window = tk.Toplevel(root)
    preview_window.title(f"预览转换结果 - 使用 {template_name} 模板")
    preview_window.geometry("800x600")

    # 创建文本区域显示预览内容
    text_area = tk.Text(preview_window, wrap=tk.WORD, padx=10, pady=10)
    text_area.pack(fill=tk.BOTH, expand=True)

    # 添加滚动条
    scrollbar = ttk.Scrollbar(text_area, command=text_area.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_area.config(yscrollcommand=scrollbar.set)

    # 插入预览内容
    preview_text = "".join(preview_content)
    text_area.insert(tk.END, preview_text)

    # 禁止编辑
    text_area.config(state=tk.DISABLED)

    # 添加关闭按钮
    close_button = ttk.Button(preview_window, text="关闭", command=preview_window.destroy)
    close_button.pack(pady=10)

def clear_selected_files():
    """
    清空已选择的代码文件列表和列表框。
    """
    global selected_code_paths_global
    selected_code_paths_global.clear()
    selected_files_listbox.delete(0, tk.END)
    status_label.config(text="已清空文件列表。")

def perform_conversion():
    """
    使用全局列表中的代码文件进行转换，并将代码内容写入 Markdown 文件。
    """
    global selected_code_paths_global

    if not selected_code_paths_global:
        messagebox.showwarning("警告", "请先添加代码文件！")
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
    total_files = len(selected_code_paths_global)

    try:
        with open(md_file_path, 'a', encoding='utf-8') as md_file:
            for i, code_file_path in enumerate(selected_code_paths_global):
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
        # 清空列表，为下一次转换做准备
        clear_selected_files()
        root.after(3000, lambda: status_label.config(text="")) # 3秒后清空状态标签

    except IOError as e:
        messagebox.showerror("错误", f"无法写入目标文件: {str(e)}")
        status_label.config(text=f"写入错误: {str(e)}")
    except Exception as e:
        messagebox.showerror("错误", f"处理文件时发生未知错误: {str(e)}")
        status_label.config(text=f"未知错误: {str(e)}")

# 创建主窗口
root = tk.Tk()
root.title("代码转 Markdown 工具")
root.geometry("600x500") # 调整窗口大小
root.resizable(True, True) # 允许调整窗口大小

# 创建主框架
main_frame = tk.Frame(root, padx=10, pady=10)
main_frame.pack(fill=tk.BOTH, expand=True)

# 创建标题
title_label = tk.Label(main_frame, text="代码转 Markdown 工具", font=("Arial", 14, "bold"))
title_label.pack(pady=(0, 10))

# 创建说明标签
label = tk.Label(main_frame, text="请选择各种编程语言的代码文件，将它们转换为 Markdown 格式。支持 Python、JavaScript、Java、C/C++ 等多种语言。", wraplength=550, justify=tk.CENTER)
label.pack(pady=(0, 10))

# 创建模板选择框架
template_frame = tk.Frame(main_frame)
template_frame.pack(pady=(5, 10))

template_label = tk.Label(template_frame, text="选择模板:")
template_label.pack(side=tk.LEFT)

template_var = tk.StringVar(value="默认")
template_combo = ttk.Combobox(template_frame, textvariable=template_var, values=list(TEMPLATES.keys()), state="readonly", width=15)
template_combo.pack(side=tk.LEFT, padx=(5, 0))

# 创建一个标签用于显示选定的文件路径或处理状态
status_label = tk.Label(main_frame, text="", wraplength=550, fg="blue")
status_label.pack(pady=5)

# 创建进度条
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100, length=550)
progress_bar.pack(pady=5)

# 创建一个框架来包含列表框和滚动条
listbox_frame = tk.Frame(main_frame)
listbox_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

# 创建一个列表框来显示选定的文件
selected_files_listbox = tk.Listbox(listbox_frame, height=5, width=60)
selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 为列表框添加滚动条
scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=selected_files_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_files_listbox.config(yscrollcommand=scrollbar.set)

# 创建按钮框架
button_frame = tk.Frame(main_frame)
button_frame.pack(pady=15, fill=tk.X)

# 创建"添加代码文件"按钮
add_files_button = tk.Button(button_frame, text="添加代码文件", command=add_code_files)
add_files_button.pack(side=tk.LEFT, padx=5)

# 创建"清空列表"按钮
clear_button = tk.Button(button_frame, text="清空列表", command=clear_selected_files)
clear_button.pack(side=tk.LEFT, padx=5)

# 创建预览按钮
preview_button = tk.Button(button_frame, text="预览", command=preview_conversion)
preview_button.pack(side=tk.LEFT, padx=5)

# 创建转换按钮
convert_button = tk.Button(button_frame, text="开始转换", command=perform_conversion)
convert_button.pack(side=tk.LEFT, padx=5)

# 运行主循环
root.mainloop()