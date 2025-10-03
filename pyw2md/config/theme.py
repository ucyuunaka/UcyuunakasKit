"""
Material Design 3 主题配置
基于 Material You 设计系统
"""

class MaterialTheme:
    """Material Design 3 颜色系统"""

    # 主色调 - 紫蓝色系
    PRIMARY = "#6750A4"
    PRIMARY_CONTAINER = "#EADDFF"
    ON_PRIMARY = "#FFFFFF"
    ON_PRIMARY_CONTAINER = "#21005E"

    # 次要色 - 粉紫色系
    SECONDARY = "#625B71"
    SECONDARY_CONTAINER = "#E8DEF8"
    ON_SECONDARY = "#FFFFFF"
    ON_SECONDARY_CONTAINER = "#1E192B"

    # 第三色 - 暖红色系
    TERTIARY = "#7D5260"
    TERTIARY_CONTAINER = "#FFD8E4"
    ON_TERTIARY = "#FFFFFF"
    ON_TERTIARY_CONTAINER = "#370B1E"

    # 错误色
    ERROR = "#BA1A1A"
    ERROR_CONTAINER = "#FFDAD6"
    ON_ERROR = "#FFFFFF"
    ON_ERROR_CONTAINER = "#410002"

    # 背景色 - 深色主题
    BACKGROUND = "#1C1B1F"
    ON_BACKGROUND = "#E6E1E5"

    # 表面色
    SURFACE = "#1C1B1F"
    SURFACE_1 = "#2B2930"  # 高程1
    SURFACE_2 = "#322F37"  # 高程2
    SURFACE_3 = "#38353E"  # 高程3
    SURFACE_4 = "#3A3740"  # 高程4
    SURFACE_5 = "#403D46"  # 高程5

    ON_SURFACE = "#E6E1E5"
    ON_SURFACE_VARIANT = "#CAC4D0"

    # 轮廓色
    OUTLINE = "#938F99"
    OUTLINE_VARIANT = "#49454F"

    # 成功色（扩展）
    SUCCESS = "#4CAF50"
    SUCCESS_CONTAINER = "#C8E6C9"

    # 警告色（扩展）
    WARNING = "#FF9800"
    WARNING_CONTAINER = "#FFE0B2"

    # 信息色（扩展）
    INFO = "#2196F3"
    INFO_CONTAINER = "#BBDEFB"

    # 字体
    FONT_FAMILY = "Segoe UI Variable"
    FONT_DISPLAY = (FONT_FAMILY, 28, "bold")
    FONT_HEADLINE = (FONT_FAMILY, 24, "bold")
    FONT_TITLE = (FONT_FAMILY, 16, "bold")
    FONT_BODY_LARGE = (FONT_FAMILY, 14)
    FONT_BODY = (FONT_FAMILY, 12)
    FONT_LABEL = (FONT_FAMILY, 11)
    FONT_MONO = ("Consolas", 11)

    # 圆角
    RADIUS_SMALL = 8
    RADIUS_MEDIUM = 12
    RADIUS_LARGE = 16
    RADIUS_XLARGE = 28

    # 间距
    SPACING_XS = 4
    SPACING_SM = 8
    SPACING_MD = 16
    SPACING_LG = 24
    SPACING_XL = 32

    # 阴影（模拟）
    SHADOW_COLOR = "#00000040"

# 快捷访问
MD = MaterialTheme
