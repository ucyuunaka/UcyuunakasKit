"""
StatusBar组件 - 底栏状态显示

设计理念:
- 常驻组件,避免动态创建/销毁导致的布局重排
- 双状态模式:默认显示统计信息,临时显示操作反馈
- 平滑状态切换,无视觉闪烁
- 智能定时器管理,防止内存泄漏

状态机设计:
STATE_DEFAULT -> 显示应用统计信息 (文件数、大小、语言数)
STATE_TEMPORARY -> 显示临时消息 + 启动定时器
    ├── 新消息到达 -> 取消旧定时器,重启新定时器
    └── 定时器触发 -> 返回默认状态

技术特点:
- 使用单一Label组件,通过配置切换显示内容和颜色
- 定时器ID追踪机制,确保只有一个活动定时器
- 统计数据缓存,支持实时更新
- 响应式布局,自适应窗口尺寸变化
"""

import customtkinter as ctk
from config.theme import MD
from core.file_handler import format_size


class StatusBar(ctk.CTkFrame):
    """
    StatusBar - 常驻状态栏组件
    
    职责:
    - 显示应用统计信息(默认状态)
    - 显示操作反馈消息(临时状态)
    - 管理状态切换和定时器
    - 提供平滑的用户体验
    
    使用示例:
        status_bar = StatusBar(parent)
        status_bar.grid(row=1, column=0, columnspan=2, sticky='ew')
        
        # 更新统计信息
        status_bar.update_stats(marked=5, total=10, size=1024000, languages=3)
        
        # 显示临时消息
        status_bar.show_message("操作成功", type='success')
        
        # 立即恢复默认状态
        status_bar.show_default()
    """
    
    def __init__(self, parent):
        """
        初始化StatusBar组件
        
        参数:
            parent: 父容器组件
            
        初始化流程:
        1. 创建固定高度的容器Frame
        2. 初始化状态管理变量
        3. 创建内容显示Label
        4. 显示初始默认状态
        """
        super().__init__(
            parent, 
            fg_color=MD.BG_SURFACE,
            height=48,
            corner_radius=0
        )
        
        # 状态管理
        self._timer_id = None  # 当前活动的定时器ID
        self._stats_data = {
            'marked': 0,
            'total': 0,
            'size': 0,
            'languages': 0
        }
        
        # 创建内容显示Label
        self._label = ctk.CTkLabel(
            self,
            text="",
            font=MD.get_font_body(),
            anchor='w',  # 左对齐
            padx=MD.PAD_M
        )
        self._label.pack(fill='x', expand=True, padx=MD.PAD_M, pady=MD.PAD_S)
        
        # 显示初始默认状态
        self.show_default()
    
    def show_message(self, message: str, type: str = 'info', duration: int = 3000):
        """
        显示临时消息
        
        功能说明:
        - 切换到临时状态显示操作反馈消息
        - 自动设置消息类型对应的颜色
        - 启动定时器,指定时间后恢复默认状态
        - 支持消息队列,新消息到达时取消旧定时器
        
        参数:
            message: 要显示的消息文本
            type: 消息类型 ('success'|'error'|'warning'|'info')
            duration: 显示持续时间(毫秒),默认3000ms
            
        状态切换:
            任何状态 -> TEMPORARY -> (duration ms) -> DEFAULT
            
        连续调用处理:
            如果在定时器触发前再次调用,会取消旧定时器并启动新定时器
            确保只显示最新的消息,避免消息堆积
        """
        # 取消现有定时器(如果存在)
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        
        # 消息类型到颜色的映射
        colors = {
            'success': MD.SUCCESS,
            'error': MD.ERROR,
            'warning': MD.WARNING,
            'info': MD.INFO
        }
        
        # 获取对应颜色,默认使用info颜色
        color = colors.get(type, MD.INFO)
        
        # 更新显示:设置背景色和消息文本
        self.configure(fg_color=color)
        self._label.configure(
            text=message,
            text_color=MD.ON_PRIMARY  # 使用高对比度文字颜色
        )
        
        # 启动新定时器,到期后恢复默认状态
        self._timer_id = self.after(duration, self.show_default)
    
    def show_default(self):
        """
        显示默认状态(统计信息)
        
        功能说明:
        - 取消任何活动的定时器
        - 恢复默认背景色
        - 显示当前的统计信息
        - 使用缓存的统计数据格式化显示文本
        
        显示格式:
            "X/Y 文件 • Z KB • N 语言"
            其中:
                X = 已标记文件数
                Y = 总文件数
                Z = 总文件大小(自动格式化)
                N = 编程语言数量
        
        调用时机:
        - 组件初始化时
        - 定时器触发时
        - 外部主动调用时
        """
        # 取消定时器(如果存在)
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
        
        # 恢复默认背景色
        self.configure(fg_color=MD.BG_SURFACE)
        
        # 格式化统计信息
        stats = self._stats_data
        text = (
            f"{stats['marked']}/{stats['total']} 文件  •  "
            f"{format_size(stats['size'])}  •  "
            f"{stats['languages']} 语言"
        )
        
        # 更新显示:设置统计文本和次要文字颜色
        self._label.configure(
            text=text,
            text_color=MD.TEXT_SECONDARY
        )
    
    def update_stats(self, marked: int, total: int, size: int, languages: int):
        """
        更新统计信息
        
        功能说明:
        - 缓存最新的统计数据
        - 如果当前处于默认状态,立即更新显示
        - 如果当前显示临时消息,只更新缓存,等恢复时显示
        
        参数:
            marked: 已标记的文件数
            total: 总文件数
            size: 总文件大小(字节)
            languages: 编程语言数量
            
        智能更新策略:
        - 统计数据始终保持最新
        - 不打断临时消息的显示
        - 临时消息结束后自动显示最新统计
        """
        # 更新缓存的统计数据
        self._stats_data = {
            'marked': marked,
            'total': total,
            'size': size,
            'languages': languages
        }
        
        # 如果当前是默认状态(没有活动定时器),立即更新显示
        if self._timer_id is None:
            self.show_default()
    
    def cleanup(self):
        """
        清理资源
        
        功能说明:
        - 取消所有活动的定时器
        - 防止应用关闭时定时器泄漏
        
        调用时机:
        - 应用关闭时
        - StatusBar销毁前
        
        注意:
            CustomTkinter通常会自动清理定时器
            但显式清理是最佳实践,确保资源正确释放
        """
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
