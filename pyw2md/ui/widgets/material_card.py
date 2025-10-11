"""
简化卡片组件
"""

import customtkinter as ctk
from config.theme import MD

class Card(ctk.CTkFrame):
    """简化卡片"""

    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', MD.BG_SURFACE)
        kwargs.setdefault('corner_radius', MD.RADIUS)
        super().__init__(master, **kwargs)

class Btn(ctk.CTkButton):
    """简化按钮 - 3种变体"""

    def __init__(self, master, kind='normal', **kwargs):
        # kind: 'primary', 'danger', 'normal'
        if kind == 'primary':
            kwargs.update({
                'fg_color': MD.ACCENT_BLUE,
                'hover_color': MD.BG_ELEVATED,
                'text_color': '#FFFFFF'
            })
        elif kind == 'danger':
            kwargs.update({
                'fg_color': MD.ACCENT_RED,
                'hover_color': MD.BG_ELEVATED,
                'text_color': '#FFFFFF'
            })
        else:  # normal
            kwargs.update({
                'fg_color': 'transparent',
                'border_width': 1,
                'border_color': MD.BORDER,
                'hover_color': MD.BG_ELEVATED,
                'text_color': MD.TEXT_PRIMARY
            })

        kwargs.setdefault('corner_radius', MD.RADIUS)
        kwargs.setdefault('font', MD.FONT_UI)
        kwargs.setdefault('height', 28)

        super().__init__(master, **kwargs)