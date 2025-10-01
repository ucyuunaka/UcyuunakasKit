"""
Code2Markdown 现代化UI版本
使用 CustomTkinter 构建的现代化界面
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import time
import json

# 导入核心逻辑
from code2markdown_core import (
    get_language_from_extension,
    format_file_size,
    get_all_supported_files_in_folder,
    format_file_content,
    SUPPORTED_EXTENSIONS,
    TEMPLATES
)

# 全局变量
selected_code_files_global = []

# 现代配色
COLORS = {
    "bg": "#1e1e1e",
    "surface": "#252526",
    "surface_hover": "#2d2d30",
    "border": "#3e3e42",
    "text": "#d4d4d4",
    "text_secondary": "#969696",
    "accent": "#007acc",
    "accent_hover": "#1177dd",
    "success": "#89d185",
    "warning": "#ffcc66",
    "error": "#f48771",
}

# 字体
FONT_TITLE = ("SF Pro Display", 16, "bold")
FONT_BODY = ("SF Pro Text", 11)
FONT_MONO = ("SF Mono", 10)

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Code → Markdown")
        self.geometry("1200x700")
        self.minsize(900, 600)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 配置文件路径
        self.config_file = os.path.join(os.path.dirname(__file__), "code2markdown_config.json")

        # 布局
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 左侧文件列表
        self.left = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        self.left.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)

        # 右侧控制区
        self.right = ctk.CTkFrame(self, fg_color=COLORS["surface"])
        self.right.grid(row=0, column=1, sticky="nsew", padx=(0, 12), pady=12)

        self.build_left()
        self.build_right()
        self.load_config()
        self.refresh_file_list()

        # 绑定关闭事件
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def build_left(self):
        """构建左侧文件列表面板"""
        self.left.grid_rowconfigure(1, weight=1)

        # 标题栏
        title_frame = ctk.CTkFrame(self.left, fg_color="transparent")
        title_frame.pack(fill="x", padx=16, pady=12)

        ctk.CTkLabel(title_frame, text="📁 文件管理", font=FONT_TITLE).pack(side="left")

        # 搜索栏
        search_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        search_frame.pack(side="right")

        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_files)

        search_entry = ctk.CTkEntry(search_frame, textvariable=self.search_var,
                                   placeholder_text="搜索文件...", width=200)
        search_entry.pack(side="left", padx=(8, 0))

        self.filter_var = tk.StringVar(value="全部语言")
        self.filter_var.trace('w', self.filter_files)

        self.filter_combo = ctk.CTkComboBox(search_frame,
                                           values=["全部语言"] + list(SUPPORTED_EXTENSIONS.keys()),
                                           variable=self.filter_var,
                                           state="readonly", width=120)
        self.filter_combo.pack(side="left", padx=(8, 0))

        # 操作按钮栏
        btn_bar = ctk.CTkFrame(self.left, fg_color="transparent")
        btn_bar.pack(fill="x", padx=16, pady=(0, 12))

        button_frame = ctk.CTkFrame(btn_bar, fg_color="transparent")
        button_frame.pack(fill="x")

        ctk.CTkButton(button_frame, text="📂 添加文件", command=self.add_files,
                     fg_color=COLORS["accent"], width=120).pack(side="left", padx=(0, 8))

        ctk.CTkButton(button_frame, text="📁 添加文件夹", command=self.add_folder,
                     fg_color=COLORS["success"], width=120).pack(side="left", padx=(0, 8))

        ctk.CTkButton(button_frame, text="🗑️ 清空", command=self.clear_files,
                     fg_color=COLORS["error"], width=80).pack(side="left", padx=(0, 8))

        ctk.CTkButton(button_frame, text="✓ 全选", command=self.select_all,
                     fg_color=COLORS["surface_hover"], width=80).pack(side="right", padx=(8, 0))

        ctk.CTkButton(button_frame, text="✗ 全不选", command=self.deselect_all,
                     fg_color=COLORS["surface_hover"], width=80).pack(side="right")

        # 文件列表
        self.file_textbox = ctk.CTkTextbox(self.left, font=FONT_MONO, activate_scrollbars=True)
        self.file_textbox.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # 绑定点击事件
        self.file_textbox.bind("<Button-1>", self.on_file_click)
        self.file_textbox.bind("<space>", self.toggle_mark)

        # 统计信息
        self.stats_frame = ctk.CTkFrame(self.left, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=16, pady=(0, 16))

        self.file_count_label = ctk.CTkLabel(self.stats_frame, text="0 个文件",
                                            font=FONT_BODY, fg_color="transparent")
        self.file_count_label.pack()

    def build_right(self):
        """构建右侧控制面板"""
        ctk.CTkLabel(self.right, text="⚙️ 转换设置", font=FONT_TITLE).pack(anchor="w", padx=16, pady=12)

        # 模板选择
        template_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        template_frame.pack(fill="x", padx=16, pady=(0, 12))

        ctk.CTkLabel(template_frame, text="模板样式", font=FONT_BODY).pack(anchor="w", pady=(0, 8))

        self.template_var = tk.StringVar(value="默认")
        self.template_combo = ctk.CTkComboBox(template_frame, values=list(TEMPLATES.keys()),
                                             variable=self.template_var, state="readonly")
        self.template_combo.pack(fill="x")

        # 模板预览按钮
        ctk.CTkButton(template_frame, text="👁️ 预览模板", command=self.preview_template,
                     fg_color=COLORS["surface_hover"]).pack(fill="x", pady=(8, 0))

        # 统计卡片
        stats_card = ctk.CTkFrame(self.right, fg_color=COLORS["surface_hover"])
        stats_card.pack(fill="x", padx=16, pady=(12, 8))

        ctk.CTkLabel(stats_card, text="📊 统计信息", font=FONT_BODY).pack(anchor="w", padx=12, pady=(8, 8))

        self.stats_widgets = {}

        stats_grid = ctk.CTkFrame(stats_card, fg_color="transparent")
        stats_grid.pack(fill="x", padx=12, pady=(0, 8))

        stats_data = [
            ("📄", "总文件数", "total_files", "0"),
            ("✅", "已标记", "marked_files", "0"),
            ("💾", "总大小", "total_size", "0KB"),
            ("🗂️", "语言种类", "language_count", "0")
        ]

        for i, (icon, label, key, value) in enumerate(stats_data):
            stat_frame = ctk.CTkFrame(stats_grid, fg_color="transparent")
            stat_frame.grid(row=i//2, column=i%2, sticky="ew", padx=(0, 8) if i%2 == 0 else (8, 0), pady=(0, 8))

            icon_label = ctk.CTkLabel(stat_frame, text=icon, font=("Segoe UI Emoji", 16))
            icon_label.pack(anchor="w")

            text_frame = ctk.CTkFrame(stat_frame, fg_color="transparent")
            text_frame.pack(anchor="w")

            ctk.CTkLabel(text_frame, text=label, font=("Segoe UI", 9),
                        text_color=COLORS["text_secondary"]).pack(anchor="w")

            value_label = ctk.CTkLabel(text_frame, text=value, font=FONT_BODY)
            value_label.pack(anchor="w")

            self.stats_widgets[key] = value_label

        # 操作按钮
        action_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        action_frame.pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(action_frame, text="👁️ 预览结果", command=self.preview_conversion,
                     fg_color=COLORS["accent"]).pack(fill="x", pady=(0, 8))

        ctk.CTkButton(action_frame, text="🚀 开始转换", command=self.perform_conversion,
                     fg_color=COLORS["success"]).pack(fill="x")

        # 进度显示
        self.progress_frame = ctk.CTkFrame(self.right, fg_color="transparent")
        self.progress_frame.pack(fill="x", padx=16, pady=(12, 0))

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self.progress_frame, text="",
                                        font=("Segoe UI", 10), text_color=COLORS["text_secondary"])
        self.status_label.pack()

    # 文件操作方法
    def add_files(self):
        """添加文件"""
        filetypes = [("所有支持的文件", " ".join(f"*{ext}" for exts in SUPPORTED_EXTENSIONS.values() for ext in exts))]
        filetypes.append(("所有文件", "*.*"))

        files = filedialog.askopenfilenames(title="选择代码文件", filetypes=filetypes)

        if files:
            added = 0
            for file_path in files:
                if not any(item["path"] == file_path for item in selected_code_files_global):
                    selected_code_files_global.append({"path": file_path, "marked": True})
                    added += 1

            self.refresh_file_list()
            self.toast(f"✅ 添加了 {added} 个文件", COLORS["success"])

    def add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")

        if folder:
            files = get_all_supported_files_in_folder(folder)
            added = 0

            for file_path in files:
                if not any(item["path"] == file_path for item in selected_code_files_global):
                    selected_code_files_global.append({"path": file_path, "marked": True})
                    added += 1

            self.refresh_file_list()
            self.toast(f"✅ 从文件夹添加了 {added} 个文件", COLORS["success"])

    def clear_files(self):
        """清空文件列表"""
        if selected_code_files_global and messagebox.askyesno("确认", "确定要清空所有文件吗？"):
            selected_code_files_global.clear()
            self.refresh_file_list()
            self.toast("🗑️ 已清空文件列表", COLORS["error"])

    def select_all(self):
        """全选"""
        for item in selected_code_files_global:
            item["marked"] = True
        self.refresh_file_list()
        self.toast("✅ 已全选所有文件", COLORS["success"])

    def deselect_all(self):
        """全不选"""
        for item in selected_code_files_global:
            item["marked"] = False
        self.refresh_file_list()
        self.toast("⬜ 已取消全选", COLORS["success"])

    def toggle_mark(self, event=None):
        """切换标记状态"""
        # 获取光标位置的行
        cursor_pos = self.file_textbox.index(tk.INSERT)
        line_start = cursor_pos.split('.')[0] + '.0'
        line_end = cursor_pos.split('.')[0] + '.end'

        try:
            line_content = self.file_textbox.get(line_start, line_end)
            # 解析文件名
            parts = line_content.strip().split('  ·  ')
            if len(parts) >= 1:
                filename = parts[0].lstrip('✓ ').lstrip('⬜ ')

                for file_item in selected_code_files_global:
                    if os.path.basename(file_item["path"]) == filename:
                        file_item["marked"] = not file_item["marked"]
                        break

                self.refresh_file_list()
        except:
            pass

    def on_file_click(self, event):
        """处理文件点击事件"""
        # 这里可以添加双击显示文件信息等功能
        pass

    def refresh_file_list(self):
        """刷新文件列表显示"""
        self.file_textbox.delete("1.0", "end")

        for file_item in selected_code_files_global:
            icon = "✓" if file_item["marked"] else "⬜"
            filename = os.path.basename(file_item["path"])
            language = get_language_from_extension(file_item["path"])

            try:
                size = format_file_size(os.path.getsize(file_item["path"]))
            except:
                size = "-"

            line = f"{icon} {filename}  ·  {language}  ·  {size}\n"
            self.file_textbox.insert("end", line)

        # 更新统计
        self.update_stats()

    def update_stats(self):
        """更新统计信息"""
        total = len(selected_code_files_global)
        marked = sum(1 for item in selected_code_files_global if item["marked"])

        # 计算总大小
        total_size = 0
        for item in selected_code_files_global:
            try:
                total_size += os.path.getsize(item["path"])
            except:
                pass

        # 统计语言种类
        languages = set()
        for item in selected_code_files_global:
            lang = get_language_from_extension(item["path"])
            languages.add(lang)

        # 更新显示
        self.stats_widgets['total_files'].configure(text=str(total))
        self.stats_widgets['marked_files'].configure(text=str(marked))
        self.stats_widgets['total_size'].configure(text=format_file_size(total_size))
        self.stats_widgets['language_count'].configure(text=str(len(languages)))

        self.file_count_label.configure(text=f"{marked}/{total} 个文件")

    def filter_files(self, *args):
        """筛选文件"""
        search_term = self.search_var.get().lower()
        language_filter = self.filter_var.get()

        self.file_textbox.delete("1.0", "end")

        for file_item in selected_code_files_global:
            filename = os.path.basename(file_item["path"]).lower()
            language = get_language_from_extension(file_item["path"])

            # 应用筛选条件
            if search_term and search_term not in filename:
                continue

            if language_filter != "全部语言" and language != language_filter:
                continue

            # 显示文件
            icon = "✓" if file_item["marked"] else "⬜"

            try:
                size = format_file_size(os.path.getsize(file_item["path"]))
            except:
                size = "-"

            line = f"{icon} {os.path.basename(file_item['path'])}  ·  {language}  ·  {size}\n"
            self.file_textbox.insert("end", line)

    def preview_template(self):
        """预览模板"""
        template_name = self.template_var.get()
        template_content = TEMPLATES[template_name]

        # 创建预览窗口
        preview = ctk.CTkToplevel(self)
        preview.title(f"模板预览 - {template_name}")
        preview.geometry("700x500")
        preview.configure(fg_color=COLORS["surface"])

        # 标题
        title_label = ctk.CTkLabel(preview, text=f"📋 {template_name} 模板",
                                  font=FONT_TITLE)
        title_label.pack(padx=20, pady=20, anchor="w")

        # 内容
        content_frame = ctk.CTkFrame(preview, fg_color=COLORS["bg"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        text_widget = ctk.CTkTextbox(content_frame, font=FONT_MONO,
                                    fg_color=COLORS["bg"])
        text_widget.pack(fill="both", expand=True, padx=16, pady=16)

        text_widget.insert('1.0', template_content)
        text_widget.configure(state='disabled')

        # 关闭按钮
        ctk.CTkButton(preview, text="关闭", command=preview.destroy,
                     fg_color=COLORS["error"]).pack(pady=(0, 20))

    def preview_conversion(self):
        """预览转换结果"""
        marked_files = [item for item in selected_code_files_global if item["marked"]]

        if not marked_files:
            self.toast("⚠️ 请先标记要预览的文件", COLORS["warning"])
            return

        template_name = self.template_var.get()

        # 创建预览窗口
        preview = ctk.CTkToplevel(self)
        preview.title(f"转换预览 - {template_name} 模板")
        preview.geometry("900x700")
        preview.configure(fg_color=COLORS["surface"])

        # 标题
        title_frame = ctk.CTkFrame(preview, fg_color="transparent")
        title_frame.pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(title_frame, text=f"👁️ 转换预览 ({len(marked_files)} 个文件)",
                    font=FONT_TITLE).pack(anchor="w")

        ctk.CTkLabel(title_frame, text=f"使用模板: {template_name}",
                    font=FONT_BODY, text_color=COLORS["text_secondary"]).pack(anchor="w", pady=(4, 0))

        # 内容
        content_frame = ctk.CTkFrame(preview, fg_color=COLORS["bg"])
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        text_widget = ctk.CTkTextbox(content_frame, font=FONT_MONO,
                                    fg_color=COLORS["bg"])
        text_widget.pack(side="left", fill="both", expand=True)

        scrollbar = ctk.CTkScrollbar(content_frame, command=text_widget.yview)
        scrollbar.pack(side="right", fill="y")
        text_widget.configure(yscrollcommand=scrollbar.set)

        # 生成预览内容
        preview_content = []
        for file_item in marked_files[:5]:  # 只预览前5个文件，避免卡顿
            formatted = format_file_content(file_item["path"], template_name)
            preview_content.append(formatted)

        if len(marked_files) > 5:
            preview_content.append(f"\n\n... 还有 {len(marked_files) - 5} 个文件未显示 ...\n")

        text_widget.insert('1.0', "".join(preview_content))
        text_widget.configure(state='disabled')

        # 关闭按钮
        ctk.CTkButton(preview, text="关闭预览", command=preview.destroy,
                     fg_color=COLORS["accent"]).pack(pady=(0, 20))

    def perform_conversion(self):
        """执行转换"""
        marked_files = [item for item in selected_code_files_global if item["marked"]]

        if not marked_files:
            self.toast("⚠️ 请先标记要转换的文件", COLORS["warning"])
            return

        # 选择保存文件
        output_file = filedialog.asksaveasfilename(
            title="保存 Markdown 文件",
            defaultextension=".md",
            filetypes=[("Markdown 文件", "*.md"), ("所有文件", "*.*")]
        )

        if not output_file:
            return

        template_name = self.template_var.get()

        # 显示进度条
        self.progress_bar.pack(fill="x", pady=(0, 8))
        self.status_label.pack()
        self.progress_var.set(0)

        success_count = 0
        total = len(marked_files)

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for i, file_item in enumerate(marked_files):
                    try:
                        formatted = format_file_content(file_item["path"], template_name)
                        f.write(formatted)
                        success_count += 1

                        # 更新进度
                        progress = ((i + 1) / total) * 100
                        self.progress_var.set(progress)
                        self.status_label.configure(
                            text=f"正在处理: {os.path.basename(file_item['path'])} ({i+1}/{total})"
                        )
                        self.update_idletasks()

                    except Exception as e:
                        print(f"处理文件出错 {file_item['path']}: {str(e)}")

            # 完成
            self.toast(f"✅ 成功转换 {success_count} 个文件", COLORS["success"])
            messagebox.showinfo("完成",
                              f"成功转换 {success_count} 个文件！\n\n保存位置: {output_file}")

        except Exception as e:
            messagebox.showerror("错误", f"转换失败: {str(e)}")
            self.toast("❌ 转换失败", COLORS["error"])

        finally:
            # 隐藏进度条
            self.after(2000, lambda: self.progress_bar.pack_forget())
            self.after(2000, lambda: self.status_label.pack_forget())

    def toast(self, msg, color=COLORS["success"]):
        """显示提示消息"""
        lbl = ctk.CTkLabel(self, text=msg, fg_color=color, text_color=COLORS["text"],
                          corner_radius=6, font=FONT_BODY)
        lbl.place(relx=0.5, rely=0.9, anchor="center")
        self.after(2000, lbl.destroy)

    def save_config(self):
        """保存配置"""
        config = {
            'window_geometry': self.geometry(),
            'template': self.template_var.get(),
            'recent_files': [item["path"] for item in selected_code_files_global],
            'marked_files': [item["path"] for item in selected_code_files_global if item["marked"]]
        }

        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {str(e)}")

    def load_config(self):
        """加载配置"""
        if not os.path.exists(self.config_file):
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            if 'window_geometry' in config:
                self.geometry(config['window_geometry'])

            if 'template' in config:
                self.template_var.set(config['template'])

            if 'recent_files' in config:
                marked_set = set(config.get('marked_files', []))
                for file_path in config['recent_files']:
                    if os.path.exists(file_path):
                        selected_code_files_global.append({
                            "path": file_path,
                            "marked": file_path in marked_set
                        })

                self.refresh_file_list()

        except Exception as e:
            print(f"加载配置失败: {str(e)}")

    def on_closing(self):
        """关闭窗口"""
        self.save_config()
        self.destroy()

if __name__ == "__main__":
    ModernApp().mainloop()
