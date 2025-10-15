"""
打包环境工具模块

功能：
- 检测当前是否运行在PyInstaller打包环境中
- 提供打包环境下的资源路径解析
- 处理打包环境下的依赖库加载问题
- 为拖放功能提供打包环境优化
"""

import sys
import os
import warnings
from typing import Optional, List, Dict, Any


def is_packaged() -> bool:
    """
    检测是否运行在PyInstaller打包环境中

    Returns:
        bool: True表示运行在打包环境中
    """
    return hasattr(sys, '_MEIPASS')


def get_resource_path(relative_path: str) -> str:
    """
    获取资源文件的绝对路径

    在打包环境中，资源文件会被解压到临时目录，
    本函数负责解析正确的路径。

    Args:
        relative_path: 相对路径

    Returns:
        str: 资源文件的绝对路径
    """
    if is_packaged():
        # 打包环境下，资源在_MEIPASS目录中
        base_path = sys._MEIPASS
    else:
        # 开发环境下，资源在当前目录
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


def check_drag_drop_dependencies() -> Dict[str, Any]:
    """
    检查拖放功能所需的依赖库

    Returns:
        Dict[str, Any]: 包含依赖检查结果的字典
        {
            'tkinterdnd2_available': bool,  # tkinterdnd2是否可用
            'dll_files': List[str],         # 找到的DLL文件列表
            'warnings': List[str],         # 警告信息列表
            'errors': List[str],           # 错误信息列表
            'suggestions': List[str]       # 解决建议列表
        }
    """
    result = {
        'tkinterdnd2_available': False,
        'dll_files': [],
        'warnings': [],
        'errors': [],
        'suggestions': []
    }

    # 检查tkinterdnd2模块
    try:
        import tkinterdnd2
        result['tkinterdnd2_available'] = True
    except ImportError as e:
        result['errors'].append(f"tkinterdnd2导入失败: {str(e)}")
        result['suggestions'].append("请安装tkinterdnd2: pip install tkinterdnd2")

    # 在打包环境中检查DLL文件
    if is_packaged():
        try:
            # 检查常见的tkinterdnd2 DLL文件
            dll_names = ['tkdnd2.8.dll', 'tkdnd2.9.dll', 'tkdnd_unix.tcl', 'tkdnd_windows.tcl']
            meipass_path = sys._MEIPASS

            for dll_name in dll_names:
                dll_path = os.path.join(meipass_path, dll_name)
                if os.path.exists(dll_path):
                    result['dll_files'].append(dll_path)

            if not result['dll_files']:
                result['warnings'].append("在打包环境中未找到tkinterdnd2的DLL文件")
                result['suggestions'].append("确保在打包时包含tkinterdnd2的DLL文件")

        except Exception as e:
            result['errors'].append(f"检查DLL文件时出错: {str(e)}")

    return result


def safe_import_tkinterdnd2() -> tuple[bool, Optional[Exception]]:
    """
    安全地导入tkinterdnd2模块

    Returns:
        tuple[bool, Optional[Exception]]: (是否成功导入, 异常对象)
    """
    try:
        # 在打包环境中，可能需要添加额外的路径
        if is_packaged():
            meipass_path = sys._MEIPASS
            # 将_MEIPASS添加到Python路径，以便找到tkinterdnd2
            if meipass_path not in sys.path:
                sys.path.insert(0, meipass_path)

        from tkinterdnd2 import DND_FILES, TkinterDnD
        return True, None
    except Exception as e:
        return False, e


def get_packaging_info() -> Dict[str, Any]:
    """
    获取当前打包环境的信息

    Returns:
        Dict[str, Any]: 打包环境信息
    """
    info = {
        'is_packaged': is_packaged(),
        'python_version': sys.version,
        'executable': sys.executable,
        'platform': sys.platform,
        'meipass_path': getattr(sys, '_MEIPASS', None),
        'drag_drop_check': check_drag_drop_dependencies()
    }

    return info


def print_packaging_debug_info():
    """打印打包环境的调试信息"""
    info = get_packaging_info()

    print("=" * 60)
    print("打包环境调试信息")
    print("=" * 60)
    print(f"是否打包环境: {info['is_packaged']}")
    print(f"Python版本: {info['python_version']}")
    print(f"可执行文件: {info['executable']}")
    print(f"平台: {info['platform']}")

    if info['meipass_path']:
        print(f"MEIPASS路径: {info['meipass_path']}")

    drag_drop = info['drag_drop_check']
    print(f"tkinterdnd2可用: {drag_drop['tkinterdnd2_available']}")

    if drag_drop['dll_files']:
        print("找到的DLL文件:")
        for dll in drag_drop['dll_files']:
            print(f"  - {dll}")

    if drag_drop['warnings']:
        print("警告:")
        for warning in drag_drop['warnings']:
            print(f"  ! {warning}")

    if drag_drop['errors']:
        print("错误:")
        for error in drag_drop['errors']:
            print(f"  ✗ {error}")

    if drag_drop['suggestions']:
        print("建议:")
        for suggestion in drag_drop['suggestions']:
            print(f"  → {suggestion}")

    print("=" * 60)