import tkinter as tk
from tkinter import filedialog, messagebox
import os

# 全局变量，用于存储所有选定的 Python 文件路径
selected_py_paths_global = []

def add_py_files():
    """
    通过 GUI 界面选择 Python 文件，并将其路径添加到全局列表和列表框中。
    """
    global selected_py_paths_global
    py_files_paths = filedialog.askopenfilenames(
        title="选择要添加的 Python 文件",
        filetypes=[("Python files", "*.py")]
    )
    if not py_files_paths:
        return # 用户取消选择

    for py_file_path in py_files_paths:
        if py_file_path not in selected_py_paths_global:
            selected_py_paths_global.append(py_file_path)
            selected_files_listbox.insert(tk.END, os.path.basename(py_file_path))
    
    status_label.config(text=f"已添加 {len(py_files_paths)} 个文件。当前共 {len(selected_py_paths_global)} 个文件待转换。")
    root.update_idletasks()

def clear_selected_files():
    """
    清空已选择的 Python 文件列表和列表框。
    """
    global selected_py_paths_global
    selected_py_paths_global.clear()
    selected_files_listbox.delete(0, tk.END)
    status_label.config(text="已清空文件列表。")

def perform_conversion():
    """
    使用全局列表中的 Python 文件进行转换，并将代码内容写入 Markdown 文件。
    """
    global selected_py_paths_global

    if not selected_py_paths_global:
        messagebox.showwarning("警告", "请先添加 Python 文件！")
        return

    # 2. 选择或创建 Markdown 文件
    md_file_path = filedialog.asksaveasfilename(
        title="选择或创建要写入的 Markdown 文件",
        defaultextension=".md",
        filetypes=[("Markdown files", "*.md"), ("All files", "*.* retreats")]
    )
    if not md_file_path:
        return # 用户取消选择

    # 获取当前工作目录，用于计算相对路径
    current_dir = os.getcwd()
    
    try:
        with open(md_file_path, 'a', encoding='utf-8') as md_file:
            for i, py_file_path in enumerate(selected_py_paths_global):
                # 更新状态标签，显示当前正在处理的文件
                status_label.config(text=f"正在处理文件 ({i+1}/{len(selected_py_paths_global)}): {os.path.basename(py_file_path)}")
                root.update_idletasks() # 强制 GUI 更新

                relative_path = os.path.relpath(py_file_path, current_dir)
                
                md_file.write(f"# {relative_path}\n") # 写入相对路径作为标题
                md_file.write("```python\n") # 开始 Python 代码块
                
                with open(py_file_path, 'r', encoding='utf-8') as py_file:
                    md_file.write(py_file.read()) # 写入 Python 文件内容
                
                md_file.write("\n```\n\n") # 结束代码块，并添加两个换行符以便分隔
            
        messagebox.showinfo("成功", f"所有选定的 Python 文件已成功写入到:\n{md_file_path}")
        status_label.config(text="转换完成！")
        # 清空列表，为下一次转换做准备
        clear_selected_files()
        root.after(3000, lambda: status_label.config(text="")) # 3秒后清空状态标签
    except Exception as e:
        messagebox.showerror("错误", f"处理文件时发生错误: {e}")
        status_label.config(text=f"错误: {e}")

# 创建主窗口
root = tk.Tk()
root.title("Python 代码转 Markdown 工具")
root.geometry("500x350") # 增加窗口高度

# 创建说明标签
label = tk.Label(root, text="点击按钮添加 Python 文件，然后点击转换按钮。", wraplength=450)
label.pack(pady=10)

# 创建一个标签用于显示选定的文件路径或处理状态
status_label = tk.Label(root, text="", wraplength=450, fg="blue")
status_label.pack(pady=5)

# 创建一个框架来包含列表框和滚动条
listbox_frame = tk.Frame(root)
listbox_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

# 创建一个列表框来显示选定的文件
selected_files_listbox = tk.Listbox(listbox_frame, height=5, width=60)
selected_files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 为列表框添加滚动条
scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=selected_files_listbox.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
selected_files_listbox.config(yscrollcommand=scrollbar.set)

# 创建按钮框架
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# 创建"添加 Python 文件"按钮
add_files_button = tk.Button(button_frame, text="添加 Python 文件", command=add_py_files)
add_files_button.pack(side=tk.LEFT, padx=5)

# 创建"清空列表"按钮
clear_button = tk.Button(button_frame, text="清空列表", command=clear_selected_files)
clear_button.pack(side=tk.LEFT, padx=5)

# 创建转换按钮
convert_button = tk.Button(button_frame, text="开始转换", command=perform_conversion)
convert_button.pack(side=tk.LEFT, padx=5)

# 运行主循环
root.mainloop()