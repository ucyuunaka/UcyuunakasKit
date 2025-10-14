"""
代码转Markdown工具 - 应用主入口

设计思路：
- 采用CustomTkinter框架构建现代化UI界面
- 统一设置深色主题和蓝色配色方案，提供一致的用户体验
- 通过MaterialApp类封装所有UI逻辑，保持主函数简洁
- 遵循单一职责原则，主函数只负责初始化和启动应用

技术特点：
- 使用customtkinter替代标准tkinter，获得更好的视觉效果
- 预设主题配置，确保应用启动即呈现统一的视觉风格
- 通过main函数封装应用启动逻辑，便于测试和维护
"""

import customtkinter as ctk
from ui.app import MaterialApp

def main():
    """
    应用入口函数

    功能说明：
    - 配置CustomTkinter的主题和外观模式
    - 创建MaterialApp应用实例
    - 启动应用主循环

    设计考量：
    - 将UI配置集中在此处，便于统一管理
    - 使用深色模式减少眼部疲劳，适合长时间编码工作
    - 蓝色主题提供专业的开发环境氛围
    """
    # 设置应用外观模式为深色，提供舒适的编码环境
    ctk.set_appearance_mode("dark")

    # 设置默认颜色主题为蓝色，营造专业的开发氛围
    ctk.set_default_color_theme("blue")

    # 创建应用主窗口实例
    app = MaterialApp()

    # 启动应用主循环，开始处理用户交互
    app.mainloop()

if __name__ == "__main__":
    # 当脚本直接运行时启动应用
    # 使用此模式便于开发调试和打包部署
    main()
