"""
简化主题 - Catppuccin Mocha启发
实用主题 - 高对比度深色
"""
from typing import Optional, Tuple
from utils.dpi_helper import DPIHelper

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

    # 基础字体大小（未缩放）
    _BASE_FONT_MONO_SIZE = 9
    _BASE_FONT_UI_SIZE = 9
    _BASE_FONT_TITLE_SIZE = 10
    _BASE_FONT_HEADLINE_SIZE = 12
    _BASE_FONT_BODY_SIZE = 10
    _BASE_FONT_LABEL_SIZE = 9

    # Material Design 向后兼容性 - 添加缺失的颜色常量
    ON_SURFACE = "#CDD6F4"      # 表面文字色
    ON_SURFACE_VARIANT = "#BAC2DE"  # 表面变体文字色
    ON_PRIMARY = "#FFFFFF"      # 主色文字
    SURFACE = "#2A2A3A"         # 表面（通用）
    SURFACE_1 = "#2A2A3A"       # 表面1
    SURFACE_2 = "#363650"       # 表面2

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

    @staticmethod
    def get_font_mono(scaling_factor: Optional[float] = None) -> Tuple[str, int]:
        size = DPIHelper.scale_font_size(
            MD._BASE_FONT_MONO_SIZE,
            scaling_factor,
            min_size=8,
            max_size=24
        )
        # 中文字体优先的等宽字体栈
        font_stack = "Cascadia Code Mono, Consolas, 'Microsoft YaHei Mono', 'Courier New', monospace"
        return (font_stack, size)

    @staticmethod
    def get_font_ui(scaling_factor: Optional[float] = None) -> Tuple[str, int]:
        size = DPIHelper.scale_font_size(
            MD._BASE_FONT_UI_SIZE,
            scaling_factor,
            min_size=8,
            max_size=24
        )
        # 中文字体优先的UI字体栈
        font_stack = "Microsoft YaHei UI, Segoe UI, system-ui, -apple-system, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
        return (font_stack, size)

    @staticmethod
    def get_font_title(scaling_factor: Optional[float] = None) -> Tuple[str, int]:
        size = DPIHelper.scale_font_size(
            MD._BASE_FONT_TITLE_SIZE,
            scaling_factor,
            min_size=8,
            max_size=24
        )
        # 中文字体优先的标题字体栈
        font_stack = "Microsoft YaHei UI, Segoe UI Semibold, system-ui, -apple-system, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
        return (font_stack, size)

    @staticmethod
    def get_font_headline(scaling_factor: Optional[float] = None) -> Tuple[str, int]:
        size = DPIHelper.scale_font_size(
            MD._BASE_FONT_HEADLINE_SIZE,
            scaling_factor,
            min_size=10,
            max_size=32
        )
        # 中文字体优先的大标题字体栈
        font_stack = "Microsoft YaHei UI, Segoe UI Semibold, system-ui, -apple-system, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
        return (font_stack, size)

    @staticmethod
    def get_font_body(scaling_factor: Optional[float] = None) -> Tuple[str, int]:
        size = DPIHelper.scale_font_size(
            MD._BASE_FONT_BODY_SIZE,
            scaling_factor,
            min_size=8,
            max_size=24
        )
        # 中文字体优先的正文字体栈
        font_stack = "Microsoft YaHei UI, Segoe UI, system-ui, -apple-system, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
        return (font_stack, size)

    @staticmethod
    def get_font_label(scaling_factor: Optional[float] = None) -> Tuple[str, int]:
        size = DPIHelper.scale_font_size(
            MD._BASE_FONT_LABEL_SIZE,
            scaling_factor,
            min_size=8,
            max_size=24
        )
        # 中文字体优先的标签字体栈
        font_stack = "Microsoft YaHei UI, Segoe UI, system-ui, -apple-system, PingFang SC, Hiragino Sans GB, Microsoft YaHei, sans-serif"
        return (font_stack, size)

    # 向后兼容的静态字体定义（已废弃，建议使用动态方法）
    # 这些常量不支持DPI缩放和中文字体，将在未来版本中移除
    FONT_MONO = ("Cascadia Code", 9)  # ⚠️ 已废弃，使用 get_font_mono()
    FONT_UI = ("Segoe UI", 9)  # ⚠️ 已废弃，使用 get_font_ui()
    FONT_TITLE = ("Segoe UI Semibold", 10)  # ⚠️ 已废弃，使用 get_font_title()
    FONT_HEADLINE = ("Segoe UI Semibold", 12)  # ⚠️ 已废弃，使用 get_font_headline()
    FONT_BODY = ("Segoe UI", 10)  # ⚠️ 已废弃，使用 get_font_body()
    FONT_LABEL = ("Segoe UI", 9)  # ⚠️ 已废弃，使用 get_font_label()

    @staticmethod
    def scale_padding(padding: int, scaling_factor: Optional[float] = None) -> int:
        return DPIHelper.scale_value(padding, scaling_factor)

    @staticmethod
    def scale_radius(radius: int, scaling_factor: Optional[float] = None) -> int:
        return DPIHelper.scale_value(radius, scaling_factor)

    @staticmethod
    def get_treeview_rowheight(scaling_factor: Optional[float] = None) -> int:
        import tkinter.font as tkfont
        font_config = MD.get_font_ui(scaling_factor)

        # 创建临时字体获取实际行高
        temp_font = tkfont.Font(family=font_config[0], size=font_config[1])
        line_height = temp_font.metrics('linespace')

        # 返回实际高度 + 20%间距
        return int(line_height * 1.2)

# 快捷访问保持不变
MD = MD
