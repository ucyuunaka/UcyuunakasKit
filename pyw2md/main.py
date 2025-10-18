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
    - 设置DPI感知，确保在高DPI显示器上清晰显示
    - 创建MaterialApp应用实例
    - 启动应用主循环

    设计考量：
    - 将UI配置集中在此处，便于统一管理
    - 使用深色模式减少眼部疲劳，适合长时间编码工作
    - 蓝色主题提供专业的开发环境氛围
    - DPI感知设置必须在任何UI创建之前完成
    """
    # 导入DPI相关模块（在函数内部导入避免循环依赖）
    from utils.dpi_helper import set_dpi_awareness, get_dpi_helper
    from config.settings import Settings
    import logging

    # 配置日志
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # 设置DPI感知（必须在任何UI创建之前调用）
    logger.info("Setting DPI awareness...")
    if set_dpi_awareness():
        logger.info("DPI awareness set successfully")

        # 检测并记录系统DPI信息
        dpi_helper = get_dpi_helper()
        dpi_x, dpi_y = dpi_helper.get_system_dpi()
        scaling_factor = dpi_helper.get_scaling_factor()
        logger.info(f"System DPI: {dpi_x}x{dpi_y}, Scaling factor: {scaling_factor}")
    else:
        logger.warning("Failed to set DPI awareness, continuing with default settings")

    # 加载配置以获取DPI设置
    try:
        settings = Settings()
        dpi_config = settings.get("dpi_scaling", {})

        # 如果禁用自动检测，使用配置的缩放因子
        if not dpi_config.get("auto_detect", True):
            manual_factor = dpi_config.get("scaling_factor", 1.0)
            if manual_factor != 1.0:
                logger.info(f"Using manual DPI scaling factor: {manual_factor}")
                # 更新DPI助手的缩放因子
                dpi_helper = get_dpi_helper()
                dpi_helper._scaling_factor = manual_factor
    except Exception as e:
        logger.error(f"Failed to load DPI settings: {e}")

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
