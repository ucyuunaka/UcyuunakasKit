import customtkinter as ctk
from config.theme import MD
from core.file_handler import format_size


class StatusBar(ctk.CTkFrame):
    
    def __init__(self, parent):
        super().__init__(
            parent, 
            fg_color=MD.BG_SURFACE,
            height=48,
            corner_radius=0
        )

        self._timer_id = None
        self._stats_data = {
            'marked': 0,
            'total': 0,
            'size': 0,
            'languages': 0
        }

        self._label = ctk.CTkLabel(
            self,
            text="",
            font=MD.get_font_body(),
            anchor='w',
            padx=MD.PAD_M
        )
        self._label.pack(fill='x', expand=True, padx=MD.PAD_M, pady=MD.PAD_S)

        self.show_default()
    
    def show_message(self, message: str, type: str = 'info', duration: int = 3000):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

        colors = {
            'success': MD.SUCCESS,
            'error': MD.ERROR,
            'warning': MD.WARNING,
            'info': MD.INFO
        }

        color = colors.get(type, MD.INFO)

        self.configure(fg_color=color)
        self._label.configure(
            text=message,
            text_color=MD.ON_PRIMARY
        )

        self._timer_id = self.after(duration, self.show_default)
    
    def show_default(self):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

        self.configure(fg_color=MD.BG_SURFACE)

        stats = self._stats_data
        text = (
            f"{stats['marked']}/{stats['total']} 文件  •  "
            f"{format_size(stats['size'])}  •  "
            f"{stats['languages']} 语言"
        )

        self._label.configure(
            text=text,
            text_color=MD.TEXT_SECONDARY
        )
    
    def update_stats(self, marked: int, total: int, size: int, languages: int):
        self._stats_data = {
            'marked': marked,
            'total': total,
            'size': size,
            'languages': languages
        }

        if self._timer_id is None:
            self.show_default()

    def cleanup(self):
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None
