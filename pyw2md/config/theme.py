"""
简化主题 - Catppuccin Mocha启发
实用主题 - 高对比度深色
"""

class MD:
    # 背景（3级足够）- 添加向后兼容别名
    BG_MAIN = "#1E1E2E"      # 主背景
    BG_SURFACE = "#2A2A3A"   # 卡片
    BG_ELEVATED = "#363650"  # 高亮/悬停
    BACKGROUND = "#1E1E2E"   # 向后兼容

    # 文字（2级足够）
    TEXT_PRIMARY = "#CDD6F4"   # 主文字
    TEXT_SECONDARY = "#BAC2DE" # 次要文字

    # 强调色（3个足够）
    ACCENT_BLUE = "#89B4FA"    # 主操作
    ACCENT_GREEN = "#A6E3A1"   # 成功
    ACCENT_RED = "#F38BA8"     # 错误/危险
    ACCENT_YELLOW = "#F9E2AF"  # 警告

    # 别名（向后兼容）
    PRIMARY = "#89B4FA"        # 主色
    SUCCESS = "#A6E3A1"        # 成功色
    ERROR = "#F38BA8"          # 错误色

    # 边框
    BORDER = "#45475A"

    # 间距（2个足够）
    PAD_S = 8
    PAD_M = 12

    # 圆角（1个足够）
    RADIUS = 4

    # 字体
    FONT_MONO = ("Cascadia Code", 9)  # 更现代的等宽字体
    FONT_UI = ("Segoe UI", 9)
    FONT_TITLE = ("Segoe UI Semibold", 10)

    # Material Design 向后兼容性 - 添加缺失的颜色常量
    ON_SURFACE = "#CDD6F4"      # 表面文字色
    ON_SURFACE_VARIANT = "#BAC2DE"  # 表面变体文字色
    ON_PRIMARY = "#FFFFFF"      # 主色文字
    SURFACE = "#2A2A3A"         # 表面（通用）
    SURFACE_1 = "#2A2A3A"       # 表面1
    SURFACE_2 = "#363650"       # 表面2
    FONT_HEADLINE = ("Segoe UI Semibold", 12)  # 标题字体
    FONT_BODY = ("Segoe UI", 10)    # 正文字体
    FONT_LABEL = ("Segoe UI", 9)    # 标签字体
    FONT_MONO = ("Cascadia Code", 9)  # 等宽字体

    # 警告颜色
    WARNING = "#FAB387"         # 警告色
    WARNING_CONTAINER = "#7C2D12"  # 警告容器

    # 主色容器
    PRIMARY_CONTAINER = "#1E40AF"   # 主色容器

    # 轮廓色
    OUTLINE = "#797979"         # 轮廓色

    # 信息色
    INFO = "#74C7EC"            # 信息色

    # 圆角大小
    RADIUS_MEDIUM = 8           # 中等圆角

    # 间距常量（向后兼容）
    SPACING_XS = 4              # 极小间距

# 快捷访问保持不变
MD = MD
