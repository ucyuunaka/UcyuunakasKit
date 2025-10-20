"""
代码转Markdown工具 - 极简版
没有过度设计，只有实用功能。
"""

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinter import ttk
import os
import json
from pathlib import Path
import threading
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class SimpleWatcher(FileSystemEventHandler):
    """简单的文件监控 - 20行解决问题"""
    
    def __init__(self, callback):
        self.callback = callback
        self.last_time = {}
    
    def on_modified(self, event):
        if not event.is_directory:
            path = os.path.abspath(event.src_path)
            now = time.time()
            # 简单防抖：1秒内只处理一次
            if path not in self.last_time or now - self.last_time[path] > 1:
                self.last_time[path] = now
                self.callback(path)


class SimpleApp:
    """简单应用 - 没有企业级架构"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("代码转Markdown - 极简版")
        self.root.geometry("900x700")
        self.root.configure(bg='#f5f5f5')
        
        # 设置ttk主题
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义样式
        style.configure('Title.TLabel', background='#f5f5f5', foreground='#333333', font=('Arial', 12, 'bold'))
        style.configure('Modern.TFrame', background='#f5f5f5')
        style.configure('Card.TFrame', background='white', relief='raised', borderwidth=1)
        style.configure('Modern.TButton', font=('Arial', 10), padding=10)
        style.map('Modern.TButton',
                 background=[('active', '#e0e0e0'), ('!active', 'white')],
                 foreground=[('active', 'black'), ('!active', 'black')])
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'), padding=10)
        style.map('Primary.TButton',
                 background=[('active', '#007acc'), ('!active', '#0084ff')],
                 foreground=[('active', 'white'), ('!active', 'white')])
        style.configure('Status.TLabel', background='#e8e8e8', foreground='#555555', relief='sunken', padding=5)
        
        # 数据结构：一个列表就够了，不需要状态管理器
        self.files = []
        self.observer = None
        
        self._build_ui()
        self._load_config()
        
    def _build_ui(self):
        """构建界面 - 现代化UI设计"""
        # 主容器
        main_container = ttk.Frame(self.root, style='Modern.TFrame')
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(main_container, text="代码转Markdown工具", style='Title.TLabel')
        title_label.pack(pady=(0, 15))
        
        # 按钮区域 - 卡片样式
        btn_card = ttk.Frame(main_container, style='Card.TFrame')
        btn_card.pack(fill='x', pady=(0, 10))
        
        btn_frame = ttk.Frame(btn_card, style='Modern.TFrame')
        btn_frame.pack(fill='x', padx=15, pady=15)
        
        ttk.Button(btn_frame, text="添加文件", command=self._add_files, style='Modern.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="添加文件夹", command=self._add_folder, style='Modern.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="清空", command=self._clear, style='Modern.TButton').pack(side='left', padx=(0, 10))
        ttk.Button(btn_frame, text="转换", command=self._convert, style='Primary.TButton').pack(side='right')
        
        # 文件列表区域 - 卡片样式
        list_card = ttk.Frame(main_container, style='Card.TFrame')
        list_card.pack(fill='both', expand=True, pady=(0, 10))
        
        list_label = ttk.Label(list_card, text="文件列表", style='Title.TLabel')
        list_label.pack(padx=15, pady=(15, 5))
        
        list_frame = ttk.Frame(list_card, style='Modern.TFrame')
        list_frame.pack(fill='both', expand=True, padx=15, pady=(0, 15))
        
        # 使用ttk的Treeview替代Listbox，更现代
        self.listbox = ttk.Treeview(list_frame, columns=('name',), show='tree headings')
        self.listbox.heading('#0', text='文件名')
        self.listbox.column('#0', width=200)
        self.listbox.pack(fill='both', expand=True)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.listbox.yview)
        scrollbar.pack(side='right', fill='y')
        self.listbox.configure(yscrollcommand=scrollbar.set)
        
        # 状态栏
        self.status = ttk.Label(main_container, text="就绪", style='Status.TLabel')
        self.status.pack(fill='x', pady=(0, 0))
        
    def _add_files(self):
        """添加文件"""
        files = filedialog.askopenfilenames(
            title="选择代码文件",
            filetypes=[
                ("Python文件", "*.py"),
                ("JavaScript文件", "*.js"),
                ("TypeScript文件", "*.ts"),
                ("Java文件", "*.java"),
                ("C/C++文件", "*.cpp *.c"),
                ("头文件", "*.h"),
                ("TeX文件", "*.tex"),
                ("所有文件", "*.*")
            ]
        )
        for f in files:
            self._add_file(f)
            
    def _add_folder(self):
        """添加文件夹"""
        folder = filedialog.askdirectory(title="选择文件夹")
        if folder:
            for root, dirs, files in os.walk(folder):
                for f in files:
                    if f.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.tex')):
                        self._add_file(os.path.join(root, f))
                        
    def _add_file(self, path):
        """添加单个文件"""
        path = os.path.abspath(path)
        if path not in self.files and os.path.exists(path):
            self.files.append(path)
            self.listbox.insert('', 'end', text=os.path.basename(path), values=(path,))
            self._start_watching()
            
    def _clear(self):
        """清空列表"""
        self.files.clear()
        for item in self.listbox.get_children():
            self.listbox.delete(item)
        self._stop_watching()
        
    def _start_watching(self):
        """开始监控 - 不需要错误计数和自动禁用"""
        if self.observer:
            return
            
        self.observer = Observer()
        handler = SimpleWatcher(self._on_file_changed)
        
        # 监控所有文件的父目录
        dirs = set()
        for f in self.files:
            dirs.add(os.path.dirname(f))
            
        for d in dirs:
            self.observer.schedule(handler, d, recursive=False)
            
        self.observer.start()
        
    def _stop_watching(self):
        """停止监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            
    def _on_file_changed(self, path):
        """文件变化回调"""
        if path in self.files:
            self.root.after(0, lambda: self.status.config(text=f"文件已更新: {os.path.basename(path)}"))
            
    def _convert(self):
        """转换文件 - 没有进度条和复杂回调"""
        if not self.files:
            messagebox.showwarning("警告", "请先添加文件")
            return
            
        output = filedialog.asksaveasfilename(
            title="保存Markdown文件",
            defaultextension=".md",
            filetypes=[("Markdown文件", "*.md")]
        )
        
        if not output:
            return
            
        # 简单的转换逻辑
        def convert_thread():
            try:
                with open(output, 'w', encoding='utf-8') as out:
                    out.write("# 代码文件汇总\n\n")
                    
                    for f in self.files:
                        if not os.path.exists(f):
                            continue
                            
                        out.write(f"## {os.path.basename(f)}\n\n")
                        out.write("```" + self._get_lang(f) + "\n")
                        
                        with open(f, 'r', encoding='utf-8') as infile:
                            out.write(infile.read())
                            
                        out.write("\n```\n\n")
                        
                self.root.after(0, lambda: (
                    self.status.config(text=f"转换完成: {len(self.files)} 个文件"),
                    messagebox.showinfo("完成", f"已转换 {len(self.files)} 个文件")
                ))
                
            except Exception as e:
                self.root.after(0, lambda: (
                    self.status.config(text=f"转换失败: {e}"),
                    messagebox.showerror("错误", f"转换失败: {e}")
                ))
                
        threading.Thread(target=convert_thread, daemon=True).start()
        self.status.config(text="正在转换...")
        
    def _get_lang(self, path):
        """获取语言标识"""
        ext = Path(path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.tex': 'tex'
        }
        return lang_map.get(ext, '')
        
    def _load_config(self):
        """加载配置 - 没有复杂的配置系统"""
        config_file = os.path.join(os.path.dirname(__file__), 'simple_config.json')
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    if 'files' in config:
                        for f in config['files']:
                            if os.path.exists(f):
                                self._add_file(f)
        except:
            pass
            
    def _save_config(self):
        """保存配置"""
        config_file = os.path.join(os.path.dirname(__file__), 'simple_config.json')
        try:
            with open(config_file, 'w') as f:
                json.dump({'files': self.files}, f)
        except:
            pass
            
    def run(self):
        """运行应用"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.root.mainloop()
        
    def _on_closing(self):
        """关闭应用"""
        self._stop_watching()
        self._save_config()
        self.root.destroy()


if __name__ == '__main__':
    app = SimpleApp()
    app.run()