#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试配置文件功能
"""

from photo2pdf import Photo2PDF
from photo2pdf_gui import Photo2PDFGUI
import tkinter as tk

def test_photo2pdf_config():
    """测试命令行版本的配置加载"""
    print("测试 Photo2PDF 配置加载...")
    converter = Photo2PDF()
    
    print(f"质量设置: {converter.config['quality']}")
    print(f"优化设置: {converter.config['optimize']}")
    print(f"背景颜色: {converter.config['background_color']}")
    print(f"最大图像尺寸: {converter.config['max_image_size']}")
    print(f"默认输出目录: {converter.config['default_output_dir']}")
    print()

def test_gui_config():
    """测试GUI版本的配置加载"""
    print("测试 Photo2PDFGUI 配置加载...")
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    gui = Photo2PDFGUI(root)
    
    print(f"质量设置: {gui.config['quality']}")
    print(f"优化设置: {gui.config['optimize']}")
    print(f"背景颜色: {gui.config['background_color']}")
    print(f"窗口宽度: {gui.config['window_width']}")
    print(f"窗口高度: {gui.config['window_height']}")
    print(f"列表框高度: {gui.config['listbox_height']}")
    print(f"结果文本高度: {gui.config['result_text_height']}")
    
    root.destroy()
    print()

if __name__ == "__main__":
    print("=" * 50)
    print("配置文件功能测试")
    print("=" * 50)
    
    test_photo2pdf_config()
    test_gui_config()
    
    print("测试完成！")
    print("\n现在您可以通过修改 config.ini 文件来自定义以下设置:")
    print("- quality: PDF质量 (1-100)")
    print("- optimize: 是否启用PDF优化 (true/false)")
    print("- background_color: 透明背景替换颜色 (R, G, B)")
    print("- window_width/height: GUI窗口大小")
    print("- listbox_height: 文件列表高度")
    print("- result_text_height: 结果显示区域高度")
