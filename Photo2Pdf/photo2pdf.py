#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像转PDF工具
支持将PNG、JPG、JPEG、BMP、TIFF等格式的图像文件转换为PDF格式
"""

from PIL import Image
import os
import sys
import argparse
from pathlib import Path
import glob

class Photo2PDF:
    """图像转PDF转换器"""
    
    # 支持的图像格式
    SUPPORTED_FORMATS = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif', '.webp', '.gif'}
    
    def __init__(self):
        self.processed_count = 0
        self.failed_count = 0
        self.failed_files = []
    
    def image_to_pdf(self, image_path, pdf_path):
        """
        将单个图像文件转换为PDF
        
        Args:
            image_path (str): 输入图像文件路径
            pdf_path (str): 输出PDF文件路径
        
        Returns:
            bool: 转换是否成功
        """
        try:
            # 打开图像文件
            image = Image.open(image_path)
            
            # 处理图像模式
            if image.mode == 'RGBA':
                # 创建白色背景处理透明图像
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为遮罩
                image = background
            elif image.mode == 'P':
                # 处理调色板模式
                image = image.convert('RGB')
            elif image.mode != 'RGB':
                # 其他模式转为RGB
                image = image.convert('RGB')
            
            # 保存为PDF
            image.save(pdf_path, "PDF", quality=95, optimize=True)
            print(f"✓ 成功转换: {os.path.basename(image_path)} -> {os.path.basename(pdf_path)}")
            self.processed_count += 1
            return True
            
        except Exception as e:
            print(f"✗ 转换失败: {os.path.basename(image_path)} - 错误: {str(e)}")
            self.failed_count += 1
            self.failed_files.append(image_path)
            return False
    
    def batch_convert_directory(self, input_dir, output_dir=None, recursive=False):
        """
        批量转换目录中的图像文件
        
        Args:
            input_dir (str): 输入目录路径
            output_dir (str): 输出目录路径，如果为None则使用输入目录
            recursive (bool): 是否递归处理子目录
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            print(f"错误: 输入目录不存在 - {input_dir}")
            return
        
        if output_dir is None:
            output_path = input_path
        else:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        # 获取所有支持的图像文件
        pattern = "**/*" if recursive else "*"
        image_files = []
        
        for ext in self.SUPPORTED_FORMATS:
            image_files.extend(input_path.glob(f"{pattern}{ext}"))
            image_files.extend(input_path.glob(f"{pattern}{ext.upper()}"))
        
        if not image_files:
            print(f"在目录 {input_dir} 中未找到支持的图像文件")
            return
        
        print(f"找到 {len(image_files)} 个图像文件")
        print("开始批量转换...")
        
        for image_file in image_files:
            # 生成PDF文件路径
            if output_dir is None:
                pdf_file = image_file.with_suffix('.pdf')
            else:
                # 保持相对目录结构
                rel_path = image_file.relative_to(input_path)
                pdf_file = output_path / rel_path.with_suffix('.pdf')
                pdf_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.image_to_pdf(str(image_file), str(pdf_file))
    
    def batch_convert_files(self, file_list, output_dir=None):
        """
        批量转换指定的文件列表
        
        Args:
            file_list (list): 图像文件路径列表
            output_dir (str): 输出目录路径
        """
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"开始转换 {len(file_list)} 个文件...")
        
        for image_file in file_list:
            image_path = Path(image_file)
            if not image_path.exists():
                print(f"✗ 文件不存在: {image_file}")
                self.failed_count += 1
                continue
            
            if output_dir:
                pdf_file = output_path / f"{image_path.stem}.pdf"
            else:
                pdf_file = image_path.with_suffix('.pdf')
            
            self.image_to_pdf(str(image_path), str(pdf_file))
    
    def merge_images_to_pdf(self, image_list, pdf_path):
        """
        将多个图像合并为一个PDF文件
        
        Args:
            image_list (list): 图像文件路径列表
            pdf_path (str): 输出PDF文件路径
        """
        try:
            images = []
            
            for image_path in image_list:
                if not os.path.exists(image_path):
                    print(f"警告: 文件不存在 - {image_path}")
                    continue
                
                image = Image.open(image_path)
                
                # 处理图像模式
                if image.mode == 'RGBA':
                    background = Image.new('RGB', image.size, (255, 255, 255))
                    background.paste(image, mask=image.split()[-1])
                    image = background
                elif image.mode != 'RGB':
                    image = image.convert('RGB')
                
                images.append(image)
            
            if not images:
                print("错误: 没有有效的图像文件")
                return False
            
            # 保存合并的PDF
            images[0].save(pdf_path, "PDF", save_all=True, append_images=images[1:], quality=95, optimize=True)
            print(f"✓ 成功合并 {len(images)} 个图像到: {os.path.basename(pdf_path)}")
            return True
            
        except Exception as e:
            print(f"✗ 合并失败: {str(e)}")
            return False
    
    def print_summary(self):
        """打印转换结果摘要"""
        print("\n" + "="*50)
        print("转换完成！")
        print(f"成功转换: {self.processed_count} 个文件")
        print(f"转换失败: {self.failed_count} 个文件")
        
        if self.failed_files:
            print("\n失败的文件:")
            for file in self.failed_files:
                print(f"  - {file}")
        print("="*50)


def main():
    """主函数 - 命令行界面"""
    parser = argparse.ArgumentParser(description='图像转PDF工具')
    parser.add_argument('input', nargs='?', help='输入文件或目录路径')
    parser.add_argument('-o', '--output', help='输出目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    parser.add_argument('-m', '--merge', action='store_true', help='将所有图像合并为一个PDF文件')
    parser.add_argument('--merge-output', help='合并PDF的输出文件名')
    
    args = parser.parse_args()
    
    converter = Photo2PDF()
    
    # 如果没有提供输入参数，使用当前目录
    if not args.input:
        args.input = '.'
    
    input_path = Path(args.input)
    
    try:
        if input_path.is_file():
            # 单个文件转换
            if args.merge:
                print("警告: 单个文件无法使用合并模式")
            converter.batch_convert_files([str(input_path)], args.output)
        
        elif input_path.is_dir():
            if args.merge:
                # 合并模式：将目录中所有图像合并为一个PDF
                pattern = "**/*" if args.recursive else "*"
                image_files = []
                
                for ext in converter.SUPPORTED_FORMATS:
                    image_files.extend(input_path.glob(f"{pattern}{ext}"))
                    image_files.extend(input_path.glob(f"{pattern}{ext.upper()}"))
                
                if not image_files:
                    print(f"在目录 {args.input} 中未找到支持的图像文件")
                    return
                
                # 按文件名排序
                image_files.sort()
                
                # 确定输出文件名
                if args.merge_output:
                    output_pdf = args.merge_output
                elif args.output:
                    output_pdf = os.path.join(args.output, f"{input_path.name}_merged.pdf")
                else:
                    output_pdf = f"{input_path.name}_merged.pdf"
                
                converter.merge_images_to_pdf([str(f) for f in image_files], output_pdf)
            else:
                # 批量转换模式
                converter.batch_convert_directory(str(input_path), args.output, args.recursive)
        
        else:
            print(f"错误: 输入路径不存在 - {args.input}")
            return
        
        converter.print_summary()
        
    except KeyboardInterrupt:
        print("\n操作被用户中断")
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()
