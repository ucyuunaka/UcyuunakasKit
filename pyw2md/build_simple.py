#!/usr/bin/env python3
"""
简化版构建脚本 - 用于测试
"""

import os
import sys
import subprocess
from pathlib import Path

def simple_build():
    """简单构建测试"""
    print("=== pyw2md 简化构建测试 ===")

    project_root = Path(__file__).parent
    print(f"项目目录: {project_root}")

    # 检查基本文件
    required_files = [
        "main.py",
        "pyw2md.spec",
        "requirements.txt",
        "VERSION"
    ]

    print("\n检查必需文件:")
    for file_name in required_files:
        file_path = project_root / file_name
        if file_path.exists():
            print(f"  [OK] {file_name}")
        else:
            print(f"  [ERROR] {file_name} 不存在")
            return False

    # 检查Python环境
    print(f"\nPython版本: {sys.version}")
    print(f"Python路径: {sys.executable}")

    # 检查必需的包
    print("\n检查必需的包:")
    required_packages = ['customtkinter', 'watchdog', 'PyInstaller']
    for package in required_packages:
        try:
            __import__(package)
            print(f"  [OK] {package}")
        except ImportError:
            print(f"  [ERROR] {package} 未安装")
            return False

    # 运行PyInstaller
    print("\n运行PyInstaller...")
    spec_file = project_root / "pyw2md_simple.spec"
    cmd = [sys.executable, "-m", "PyInstaller", str(spec_file), "--log-level=INFO"]

    print(f"执行命令: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("[OK] PyInstaller构建成功")

            # 检查输出文件
            dist_dir = project_root / "dist"

            # 首先检查是否是目录形式的打包
            pyw2md_dir = dist_dir / "pyw2md"
            if pyw2md_dir.exists():
                exe_files = list(pyw2md_dir.glob("*.exe"))
                if exe_files:
                    exe_file = exe_files[0]
                    size_mb = exe_file.stat().st_size // (1024 * 1024)
                    print(f"[OK] 生成exe文件: pyw2md/{exe_file.name} ({size_mb}MB)")
                    print(f"[OK] 完整应用目录: {pyw2md_dir}")
                    return True

            # 然后检查是否是单文件exe
            exe_files = list(dist_dir.glob("*.exe"))
            if exe_files:
                exe_file = exe_files[0]
                size_mb = exe_file.stat().st_size // (1024 * 1024)
                print(f"[OK] 生成exe文件: {exe_file.name} ({size_mb}MB)")
                return True

            print("[ERROR] 未找到生成的exe文件")
            return False
        else:
            print(f"[ERROR] PyInstaller构建失败 (退出码: {result.returncode})")
            if result.stdout:
                print("输出:")
                print(result.stdout[:1000])  # 只显示前1000字符
            if result.stderr:
                print("错误:")
                print(result.stderr[:1000])
            return False

    except Exception as e:
        print(f"[ERROR] 执行PyInstaller时出错: {e}")
        return False

if __name__ == "__main__":
    success = simple_build()
    print(f"\n构建结果: {'成功' if success else '失败'}")
    sys.exit(0 if success else 1)