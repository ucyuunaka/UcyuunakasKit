"""
辅助工具函数
"""

import os
from typing import Optional

def get_relative_path(file_path: str, base_path: Optional[str] = None) -> str:
    """获取相对路径"""
    if base_path is None:
        base_path = os.getcwd()
    
    try:
        return os.path.relpath(file_path, base_path)
    except ValueError:
        return file_path

def truncate_string(s: str, max_length: int, suffix: str = '...') -> str:
    """截断字符串"""
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix

def validate_file_path(path: str) -> bool:
    """验证文件路径"""
    return os.path.isfile(path) and os.path.exists(path)
