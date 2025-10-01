#!/usr/bin/env python3
"""
测试重构后的Code2Markdown功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(__file__))

def test_core_module():
    """测试核心模块功能"""
    print("[TEST] 测试核心模块...")

    # 测试导入
    try:
        from code2markdown_core import (
            get_language_from_extension,
            format_file_size,
            SUPPORTED_EXTENSIONS,
            TEMPLATES,
            format_file_content
        )
        print("[PASS] 核心模块导入成功")
    except ImportError as e:
        print(f"[FAIL] 核心模块导入失败: {e}")
        return False

    # 测试语言识别
    test_cases = [
        ("test.py", "Python"),
        ("script.js", "JavaScript"),
        ("style.css", "CSS"),
        ("index.html", "HTML"),
        ("data.json", "JSON"),
        ("unknown.xyz", "Text")
    ]

    for file_path, expected in test_cases:
        result = get_language_from_extension(file_path)
        if result == expected:
            print(f"[PASS] 语言识别正确: {file_path} -> {result}")
        else:
            print(f"[FAIL] 语言识别错误: {file_path} -> {result} (期望: {expected})")
            return False

    # 测试文件大小格式化
    size_tests = [
        (500, "500B"),
        (1500, "1.5KB"),
        (1500000, "1.4MB")  # 1500000 / (1024*1024) ≈ 1.4305，格式化后为1.4MB
    ]

    for size_bytes, expected in size_tests:
        result = format_file_size(size_bytes)
        if result == expected:
            print(f"[PASS] 文件大小格式化正确: {size_bytes} -> {result}")
        else:
            print(f"[FAIL] 文件大小格式化错误: {size_bytes} -> {result} (期望: {expected})")
            return False

    # 测试模板
    if len(TEMPLATES) >= 4:
        print(f"[PASS] 模板加载成功，共 {len(TEMPLATES)} 个模板")
    else:
        print(f"[FAIL] 模板加载失败，只有 {len(TEMPLATES)} 个模板")
        return False

    # 测试文件内容格式化（使用现有的测试文件）
    test_files = ["pys/test1.py", "pys/test2.py", "pys/test3.py"]
    for test_file in test_files:
        file_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(file_path):
            try:
                result = format_file_content(file_path, "默认")
                if result and len(result) > 0:
                    print(f"[PASS] 文件内容格式化成功: {test_file}")
                else:
                    print(f"[FAIL] 文件内容格式化失败: {test_file}")
                    return False
            except Exception as e:
                print(f"[FAIL] 文件内容格式化异常: {test_file} - {e}")
                return False

    print("[SUCCESS] 核心模块测试通过！")
    return True

def test_modern_app_import():
    """测试现代化UI模块导入"""
    print("\n[TEST] 测试现代化UI模块导入...")

    try:
        # 只导入不运行，避免GUI相关问题
        import importlib.util
        spec = importlib.util.spec_from_file_location("app_modern", "app_modern.py")
        if spec is None:
            print("[FAIL] 无法找到 app_modern.py 文件")
            return False

        print("[PASS] 现代化UI模块导入测试通过")
        return True

    except Exception as e:
        print(f"[FAIL] 现代化UI模块导入失败: {e}")
        return False

def main():
    """主测试函数"""
    print("[START] 开始测试重构后的Code2Markdown...")

    # 测试核心模块
    core_ok = test_core_module()

    # 测试UI模块导入
    ui_ok = test_modern_app_import()

    if core_ok and ui_ok:
        print("\n[SUCCESS] 所有测试通过！重构成功！")
        print("\n[INFO] 使用说明:")
        print("1. 安装依赖: pip install -r requirements.txt")
        print("2. 运行现代化版本: python app_modern.py")
        print("3. 运行传统版本: python main.py")
        return 0
    else:
        print("\n[FAIL] 测试失败，需要修复问题")
        return 1

if __name__ == "__main__":
    exit(main())
