#!/usr/bin/env python3
"""
简单的tkinter测试脚本
用于验证tkinter打包是否正常工作
"""

import tkinter as tk
from tkinter import messagebox
import sys

def main():
    print("Testing tkinter in packaged environment...")
    print(f"Python executable: {sys.executable}")

    try:
        # 创建基本窗口
        root = tk.Tk()
        root.title("pyw2md Test")
        root.geometry("300x200")

        # 添加标签
        label = tk.Label(root, text="tkinter packaging test successful!", font=("Arial", 12))
        label.pack(pady=50)

        # 添加按钮
        def show_message():
            messagebox.showinfo("Test", "tkinter is working correctly!")

        button = tk.Button(root, text="Click Me", command=show_message)
        button.pack(pady=10)

        # 添加退出按钮
        def quit_app():
            root.quit()
            sys.exit(0)

        quit_button = tk.Button(root, text="Quit", command=quit_app)
        quit_button.pack(pady=5)

        print("Window created successfully")
        root.mainloop()

    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()