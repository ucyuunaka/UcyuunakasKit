"""
代码转Markdown工具
"""

import customtkinter as ctk
from ui.app import MaterialApp

def main():
    """应用入口"""
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = MaterialApp()
    app.mainloop()

if __name__ == "__main__":
    main()
