#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import threading
from PIL import Image
import configparser

class Photo2PDFGUI:
    """图像转PDF转换器GUI版本"""
    
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    
    def __init__(self, root):
        self.root = root
        self.root.title("图像转PDF工具")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # 变量
        self.selected_files = []
        self.output_directory = tk.StringVar()
        self.conversion_mode = tk.StringVar(value="individual")  # individual 或 merge
        self.processing = False
        
        # 加载配置文件
        self.config = self._load_config()
        
        self.setup_ui()
    
    def _load_config(self):
        """加载配置文件"""
        config = configparser.ConfigParser()
        config_path = Path(__file__).parent / 'config.ini'
        
        # 设置默认值
        defaults = {
            'quality': 95,
            'optimize': True,
            'background_color': (255, 255, 255),
            'max_image_size': 10000,
            'default_output_dir': 'pdf',
            'default_merge_filename': 'merged_images.pdf',
            'overwrite_existing': True,
            'window_width': 600,
            'window_height': 500,
            'listbox_height': 8,
            'result_text_height': 6
        }
        
        if config_path.exists():
            try:
                config.read(config_path, encoding='utf-8')
                
                # 解析配置值
                parsed_config = {}
                
                # 图像处理设置
                if config.has_section('图像处理'):
                    parsed_config['quality'] = config.getint('图像处理', 'quality', fallback=defaults['quality'])
                    parsed_config['optimize'] = config.getboolean('图像处理', 'optimize', fallback=defaults['optimize'])
                    
                    # 解析背景颜色
                    bg_color_str = config.get('图像处理', 'background_color', fallback='255, 255, 255')
                    try:
                        parsed_config['background_color'] = tuple(map(int, bg_color_str.split(',')))
                    except:
                        parsed_config['background_color'] = defaults['background_color']
                    
                    parsed_config['max_image_size'] = config.getint('图像处理', 'max_image_size', fallback=defaults['max_image_size'])
                else:
                    parsed_config.update({k: v for k, v in defaults.items() if k in ['quality', 'optimize', 'background_color', 'max_image_size']})
                
                # 文件处理设置
                if config.has_section('文件处理'):
                    parsed_config['default_output_dir'] = config.get('文件处理', 'default_output_dir', fallback=defaults['default_output_dir'])
                    parsed_config['default_merge_filename'] = config.get('文件处理', 'default_merge_filename', fallback=defaults['default_merge_filename'])
                    parsed_config['overwrite_existing'] = config.getboolean('文件处理', 'overwrite_existing', fallback=defaults['overwrite_existing'])
                else:
                    parsed_config.update({k: v for k, v in defaults.items() if k in ['default_output_dir', 'default_merge_filename', 'overwrite_existing']})
                
                # GUI设置
                if config.has_section('GUI设置'):
                    parsed_config['window_width'] = config.getint('GUI设置', 'window_width', fallback=defaults['window_width'])
                    parsed_config['window_height'] = config.getint('GUI设置', 'window_height', fallback=defaults['window_height'])
                    parsed_config['listbox_height'] = config.getint('GUI设置', 'listbox_height', fallback=defaults['listbox_height'])
                    parsed_config['result_text_height'] = config.getint('GUI设置', 'result_text_height', fallback=defaults['result_text_height'])
                    
                    # 应用窗口大小设置
                    self.root.geometry(f"{parsed_config['window_width']}x{parsed_config['window_height']}")
                else:
                    parsed_config.update({k: v for k, v in defaults.items() if k in ['window_width', 'window_height', 'listbox_height', 'result_text_height']})
                
                return parsed_config
                
            except Exception as e:
                print(f"警告: 读取配置文件失败，使用默认设置: {e}")
                return defaults
        else:
            print("警告: 配置文件不存在，使用默认设置")
            return defaults
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="图像转PDF转换工具", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 文件选择区域
        files_frame = ttk.LabelFrame(main_frame, text="选择图像文件", padding="5")
        files_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        files_frame.rowconfigure(1, weight=1)
        
        # 文件选择按钮
        file_buttons_frame = ttk.Frame(files_frame)
        file_buttons_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(file_buttons_frame, text="选择文件", command=self.select_files).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons_frame, text="选择文件夹", command=self.select_folder).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_buttons_frame, text="清空列表", command=self.clear_files).pack(side=tk.LEFT)
          # 文件列表，使用配置的高度
        self.file_listbox = tk.Listbox(files_frame, height=self.config['listbox_height'])
        self.file_listbox.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.file_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 转换模式选择
        mode_frame = ttk.LabelFrame(main_frame, text="转换模式", padding="5")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="每个图像转换为单独的PDF文件", 
                       variable=self.conversion_mode, value="individual").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="将所有图像合并为一个PDF文件", 
                       variable=self.conversion_mode, value="merge").pack(anchor=tk.W)
        
        # 输出目录选择
        output_frame = ttk.LabelFrame(main_frame, text="输出目录", padding="5")
        output_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_directory, state="readonly").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_frame, text="浏览", command=self.select_output_directory).grid(row=0, column=1)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # 状态标签
        self.status_label = ttk.Label(main_frame, text="准备就绪")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=(0, 10))
        
        self.convert_button = ttk.Button(button_frame, text="开始转换", command=self.start_conversion)
        self.convert_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="退出", command=self.root.quit).pack(side=tk.LEFT)
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="转换结果", padding="5")
        result_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        
        # 结果显示区域，使用配置的高度
        self.result_text = tk.Text(result_frame, height=self.config['result_text_height'], state=tk.DISABLED)
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        result_scrollbar = ttk.Scrollbar(result_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        
        # 配置网格权重
        main_frame.rowconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)
    
    def select_files(self):
        """选择图像文件"""
        file_types = [
            ("所有支持的图像", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff;*.tif;*.webp;*.gif"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg;*.jpeg"),
            ("BMP文件", "*.bmp"),
            ("TIFF文件", "*.tiff;*.tif"),
            ("WebP文件", "*.webp"),
            ("GIF文件", "*.gif"),
            ("所有文件", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="选择图像文件",
            filetypes=file_types
        )
        
        for file in files:
            if file not in self.selected_files:
                self.selected_files.append(file)
                self.file_listbox.insert(tk.END, os.path.basename(file))
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择包含图像的文件夹")
        if folder:
            # 获取文件夹中的所有图像文件
            folder_path = Path(folder)
            image_files = []
            
            for ext in self.SUPPORTED_FORMATS:
                image_files.extend(folder_path.glob(f"*{ext}"))
                image_files.extend(folder_path.glob(f"*{ext.upper()}"))
            
            added_count = 0
            for file in image_files:
                file_str = str(file)
                if file_str not in self.selected_files:
                    self.selected_files.append(file_str)
                    self.file_listbox.insert(tk.END, file.name)
                    added_count += 1
            
            if added_count > 0:
                self.log_result(f"从文件夹添加了 {added_count} 个图像文件")
            else:
                self.log_result("文件夹中没有找到新的图像文件")
    
    def clear_files(self):
        """清空文件列表"""
        self.selected_files.clear()
        self.file_listbox.delete(0, tk.END)
        self.log_result("已清空文件列表")
    
    def select_output_directory(self):
        """选择输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_directory.set(directory)
    
    def log_result(self, message):
        """在结果区域显示消息"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.see(tk.END)
        self.root.update()
    
    def update_status(self, message):
        """更新状态标签"""
        self.status_label.config(text=message)
        self.root.update()
    
    def update_progress(self, current, total):
        """更新进度条"""
        if total > 0:
            progress = (current / total) * 100
            self.progress_var.set(progress)
        self.root.update()
    
    def start_conversion(self):
        """开始转换过程"""
        if self.processing:
            return
        
        if not self.selected_files:
            messagebox.showwarning("警告", "请先选择要转换的图像文件")
            return
        
        if not self.output_directory.get():
            messagebox.showwarning("警告", "请选择输出目录")
            return
        
        # 在新线程中运行转换，避免界面冻结
        self.processing = True
        self.convert_button.config(state=tk.DISABLED)
        
        thread = threading.Thread(target=self.convert_images)
        thread.daemon = True
        thread.start()
    
    def convert_images(self):
        """执行图像转换"""
        try:
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            self.result_text.config(state=tk.DISABLED)
            
            output_dir = Path(self.output_directory.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if self.conversion_mode.get() == "merge":
                # 合并模式
                self.update_status("正在合并图像为PDF...")
                self.merge_images_to_pdf()
            else:
                # 单独转换模式
                self.update_status("正在转换图像...")
                self.convert_individual_images()
            
            self.update_status("转换完成")
            self.progress_var.set(100)
            messagebox.showinfo("完成", "图像转换完成！")
            
        except Exception as e:
            self.log_result(f"转换过程中发生错误: {str(e)}")
            messagebox.showerror("错误", f"转换失败: {str(e)}")
        
        finally:
            self.processing = False
            self.convert_button.config(state=tk.NORMAL)
            self.progress_var.set(0)
    
    def convert_individual_images(self):
        """单独转换每个图像"""
        success_count = 0
        total_files = len(self.selected_files)
        
        for i, image_path in enumerate(self.selected_files):
            try:
                # 生成PDF文件路径
                image_file = Path(image_path)
                pdf_file = Path(self.output_directory.get()) / f"{image_file.stem}.pdf"
                
                # 转换图像
                if self.convert_single_image(image_path, str(pdf_file)):
                    success_count += 1
                    self.log_result(f"✓ {image_file.name} -> {pdf_file.name}")
                else:
                    self.log_result(f"✗ 转换失败: {image_file.name}")
                
                self.update_progress(i + 1, total_files)
                
            except Exception as e:
                self.log_result(f"✗ 转换失败: {Path(image_path).name} - {str(e)}")
        
        self.log_result(f"\n转换完成! 成功: {success_count}/{total_files}")
    
    def merge_images_to_pdf(self):
        """将所有图像合并为一个PDF"""
        try:
            output_file = Path(self.output_directory.get()) / "merged_images.pdf"
            images = []
            
            total_files = len(self.selected_files)
            
            for i, image_path in enumerate(self.selected_files):
                try:
                    image = Image.open(image_path)
                      # 处理图像模式
                    if image.mode == 'RGBA':
                        background = Image.new('RGB', image.size, self.config['background_color'])
                        background.paste(image, mask=image.split()[-1])
                        image = background
                    elif image.mode != 'RGB':
                        image = image.convert('RGB')
                    
                    images.append(image)
                    self.log_result(f"✓ 已加载: {Path(image_path).name}")
                    self.update_progress(i + 1, total_files)
                    
                except Exception as e:
                    self.log_result(f"✗ 加载失败: {Path(image_path).name} - {str(e)}")
            
            if images:                # 保存合并的PDF，使用配置的质量和优化设置
                images[0].save(str(output_file), "PDF", save_all=True, 
                             append_images=images[1:], quality=self.config['quality'], optimize=self.config['optimize'])
                self.log_result(f"\n✓ 成功合并 {len(images)} 个图像到: {output_file.name}")
            else:
                self.log_result("错误: 没有成功加载任何图像")
                
        except Exception as e:
            self.log_result(f"合并失败: {str(e)}")
            raise
    
    def convert_single_image(self, image_path, pdf_path):
        """转换单个图像文件"""
        try:
            image = Image.open(image_path)
              # 处理图像模式
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, self.config['background_color'])
                background.paste(image, mask=image.split()[-1])
                image = background
            elif image.mode == 'P':
                image = image.convert('RGB')
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 保存为PDF，使用配置的质量和优化设置
            image.save(pdf_path, "PDF", quality=self.config['quality'], optimize=self.config['optimize'])
            return True
            
        except Exception:
            return False


def main():
    """主函数"""
    root = tk.Tk()
    app = Photo2PDFGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
