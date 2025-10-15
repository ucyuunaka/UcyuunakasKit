#!/usr/bin/env python3
"""
打包构建脚本

功能：
- 自动化执行PyInstaller打包过程
- 检查依赖项
- 清理旧的构建文件
- 生成可执行文件
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_dependencies():
    """检查必要的依赖项"""
    print("检查依赖项...")

    required_packages = [
        'customtkinter',
        'PyInstaller',
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.lower().replace('-', '_'))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"缺少依赖包: {', '.join(missing_packages)}")
        print("请使用以下命令安装:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    # 检查可选依赖
    try:
        import tkinterdnd2
        print("✓ tkinterdnd2已安装，拖放功能可用")
    except ImportError:
        print("⚠ tkinterdnd2未安装，拖放功能将不可用")
        print("  如需启用拖放功能，请运行: pip install tkinterdnd2")

    return True


def clean_build_files():
    """清理旧的构建文件"""
    print("清理旧的构建文件...")

    dirs_to_remove = ['build', 'dist', '__pycache__']
    files_to_remove = ['*.pyc', '*.pyo', '*.pyd', '*.spec']

    # 清理目录
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  删除目录: {dir_name}")

    # 清理Python缓存文件
    for pattern in files_to_remove:
        for path in Path('.').rglob(pattern):
            path.unlink()
            print(f"  删除文件: {path}")

    print("清理完成")


def run_pyinstaller():
    """运行PyInstaller"""
    print("运行PyInstaller...")

    # 使用spec文件进行打包
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',  # 清理临时文件
        '-y',       # 覆盖已存在的文件
        'pyinstaller.spec'
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ 打包成功!")
            print(f"可执行文件位置: dist/pyw2md/pyw2md.exe")
            return True
        else:
            print("✗ 打包失败!")
            print("错误输出:")
            print(result.stderr)
            return False

    except Exception as e:
        print(f"运行PyInstaller时出错: {e}")
        return False


def create_batch_file():
    """创建运行批处理文件"""
    batch_content = """@echo off
echo 正在启动 pyw2md - 代码转Markdown工具...
cd /d "%~dp0"
dist\pyw2md\pyw2md.exe
pause
"""

    with open('run.bat', 'w', encoding='utf-8') as f:
        f.write(batch_content)

    print("创建运行脚本: run.bat")


def main():
    """主函数"""
    print("=" * 60)
    print("pyw2md 打包构建工具")
    print("=" * 60)

    # 检查依赖
    if not check_dependencies():
        return 1

    # 清理旧的构建文件
    clean_build_files()

    # 运行PyInstaller
    if not run_pyinstaller():
        return 1

    # 创建运行脚本
    create_batch_file()

    print("\n" + "=" * 60)
    print("构建完成!")
    print("=" * 60)
    print("使用方法:")
    print("1. 双击 dist/pyw2md/pyw2md.exe 运行程序")
    print("2. 或者双击 run.bat 运行程序")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())