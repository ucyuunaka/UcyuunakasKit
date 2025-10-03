"""
Material Design 卡片组件
"""

import customtkinter as ctk
from config.theme import MD

class MaterialCard(ctk.CTkFrame):
    """Material Design 卡片"""
    
    def __init__(self, master, elevation=1, **kwargs):
        # 根据高程选择背景色
        surface_colors = {
            0: MD.SURFACE,
            1: MD.SURFACE_1,
            2: MD.SURFACE_2,
            3: MD.SURFACE_3,
            4: MD.SURFACE_4,
            5: MD.SURFACE_5
        }
        
        fg_color = kwargs.pop('fg_color', surface_colors.get(elevation, MD.SURFACE_1))
        corner_radius = kwargs.pop('corner_radius', MD.RADIUS_MEDIUM)
        
        super().__init__(
            master,
            fg_color=fg_color,
            corner_radius=corner_radius,
            **kwargs
        )
        
        self.elevation = elevation

class MaterialButton(ctk.CTkButton):
    """Material Design 按钮"""
    
    STYLES = {
        'filled': {
            'fg_color': MD.PRIMARY,
            'hover_color': MD.PRIMARY_CONTAINER,
            'text_color': MD.ON_PRIMARY
        },
        'tonal': {
            'fg_color': MD.SECONDARY_CONTAINER,
            'hover_color': MD.SECONDARY,
            'text_color': MD.ON_SECONDARY_CONTAINER
        },
        'outlined': {
            'fg_color': 'transparent',
            'hover_color': MD.SURFACE_2,
            'text_color': MD.PRIMARY,
            'border_width': 1,
            'border_color': MD.OUTLINE
        },
        'text': {
            'fg_color': 'transparent',
            'hover_color': MD.SURFACE_2,
            'text_color': MD.PRIMARY
        },
        'error': {
            'fg_color': MD.ERROR,
            'hover_color': MD.ERROR_CONTAINER,
            'text_color': MD.ON_ERROR
        },
        'success': {
            'fg_color': MD.SUCCESS,
            'hover_color': MD.SUCCESS_CONTAINER,
            'text_color': MD.ON_PRIMARY
        }
    }
    
    def __init__(self, master, style='filled', **kwargs):
        style_props = self.STYLES.get(style, self.STYLES['filled']).copy()
        
        # 合并样式属性和用户属性
        for key, value in style_props.items():
            kwargs.setdefault(key, value)
        
        kwargs.setdefault('corner_radius', MD.RADIUS_LARGE)
        kwargs.setdefault('font', MD.FONT_LABEL)
        kwargs.setdefault('height', 40)
        
        super().__init__(master, **kwargs)

class MaterialEntry(ctk.CTkEntry):
    """Material Design 输入框"""
    
    def __init__(self, master, **kwargs):
        kwargs.setdefault('fg_color', MD.SURFACE_2)
        kwargs.setdefault('border_color', MD.OUTLINE)
        kwargs.setdefault('text_color', MD.ON_SURFACE)
        kwargs.setdefault('placeholder_text_color', MD.ON_SURFACE_VARIANT)
        kwargs.setdefault('corner_radius', MD.RADIUS_SMALL)
        kwargs.setdefault('font', MD.FONT_BODY)
        kwargs.setdefault('height', 40)
        
        super().__init__(master, **kwargs)

class StatCard(MaterialCard):
    """统计卡片组件"""
    
    def __init__(self, master, icon: str, label: str, value: str = "0", **kwargs):
        super().__init__(master, elevation=0, **kwargs)
        
        self.configure(fg_color=MD.SURFACE_2)
        
        # 内边距容器
        container = ctk.CTkFrame(self, fg_color='transparent')
        container.pack(fill='both', expand=True, padx=MD.SPACING_SM, pady=MD.SPACING_SM)
        
        # 图标
        self.icon_label = ctk.CTkLabel(
            container,
            text=icon,
            font=("Segoe UI Emoji", 20),
            text_color=MD.PRIMARY
        )
        self.icon_label.pack(anchor='w')
        
        # 数值
        self.value_label = ctk.CTkLabel(
            container,
            text=value,
            font=MD.FONT_TITLE,
            text_color=MD.ON_SURFACE
        )
        self.value_label.pack(anchor='w', pady=(MD.SPACING_XS, 0))
        
        # 标签
        self.label_label = ctk.CTkLabel(
            container,
            text=label,
            font=MD.FONT_LABEL,
            text_color=MD.ON_SURFACE_VARIANT
        )
        self.label_label.pack(anchor='w')
    
    def update_value(self, value: str):
        """更新数值"""
        self.value_label.configure(text=value)