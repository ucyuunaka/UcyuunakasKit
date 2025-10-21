#!/usr/bin/env python3
"""
简化版主程序 - 使用标准tkinter而不是customtkinter
用于测试tkinter打包是否正常工作
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from pathlib import Path

def main():
    """简化版主程序"""
    print("启动pyw2md简化版...")
    print(f"Python版本: {sys.version}")
    print(f"当前目录: {os.getcwd()}")

    try:
        # 创建主窗口
        root = tk.Tk()
        root.title("pyw2md - 简化版")
        root.geometry("800x600")

        # 创建菜单栏
        menubar = tk.Menu(root)
        root.config(menu=menubar)

        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开文件", command=lambda: open_file(root))
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=root.quit)

        # 主框架
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="pyw2md - 文件监控和转换工具",
                                font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # 说明文字
        desc_label = ttk.Label(main_frame,
                              text="这是一个简化版本，使用标准tkinter构建。\n"
                                    "用于验证打包功能是否正常工作。",
                              justify=tk.CENTER)
        desc_label.grid(row=1, column=0, columnspan=2, pady=10)

        # 文件列表框架
        list_frame = ttk.LabelFrame(main_frame, text="文件列表", padding="5")
        list_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)

        # 文件列表
        file_listbox = tk.Listbox(list_frame)
        file_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        file_listbox.configure(yscrollcommand=scrollbar.set)

        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # 按钮
        ttk.Button(button_frame, text="添加文件", command=lambda: add_file(file_listbox)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清空列表", command=lambda: file_listbox.delete(0, tk.END)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关于", command=lambda: show_about()).pack(side=tk.LEFT, padx=5)

        # 状态栏
        status_var = tk.StringVar()
        status_var.set("就绪")
        status_bar = ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN)
        status_bar.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # 添加一些示例文件
        sample_files = [
            "README.md",
            "BUILD.md",
            "CLAUDE.md",
            "main.py"
        ]

        for file in sample_files:
            if os.path.exists(file):
                file_listbox.insert(tk.END, file)

        status_var.set(f"简化版已启动 - 找到 {file_listbox.size()} 个文件")

        print("GUI创建成功，启动主循环...")
        root.mainloop()

    except Exception as e:
        print(f"错误: {e}")
        error_msg = f"程序启动失败:\n{str(e)}"
        if 'tkinter' in str(e).lower():
            error_msg += "\n\n这是一个tkinter相关的错误，可能是因为打包时缺少必要的DLL文件。"

        # 尝试显示错误对话框
        try:
            root = tk.Tk()
            root.withdraw()  # 隐藏主窗口
            messagebox.showerror("启动错误", error_msg)
            root.destroy()
        except:
            # 如果连错误对话框都无法显示，打印到控制台
            print("=" * 50)
            print("启动错误:")
            print(error_msg)
            print("=" * 50)
            input("按Enter键退出...")

def open_file(parent):
    """打开文件对话框"""
    filename = filedialog.askopenfilename(
        title="选择文件",
        filetypes=[("所有文件", "*.*"), ("Markdown文件", "*.md"), ("Python文件", "*.py")]
    )
    if filename:
        messagebox.showinfo("文件选择", f"选择了文件:\n{filename}")

def add_file(listbox):
    """添加文件到列表"""
    filename = filedialog.askopenfilename(
        title="选择要添加的文件",
        filetypes=[("所有文件", "*.*")]
    )
    if filename:
        listbox.insert(tk.END, filename)

def show_about():
    """显示关于对话框"""
    about_text = """pyw2md - 文件监控和转换工具

简化版测试程序

版本: 1.0.2
构建时间: 2025-10-21

这个简化版本用于验证tkinter打包功能。"""

    messagebox.showinfo("关于 pyw2md", about_text)

if __name__ == "__main__":
    main()