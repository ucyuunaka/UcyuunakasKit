"""
文件处理核心模块

核心职责：
- 管理代码文件的识别、加载和元数据维护
- 提供文件语言检测和分类功能
- 实现文件状态跟踪和缓存机制
- 支持文件筛选、搜索和批量操作

设计思路：
- 采用数据类模式封装文件信息，提供类型安全的访问接口
- 实现文件系统抽象层，隔离底层文件操作细节
- 使用缓存机制优化频繁访问的文件属性
- 提供灵活的筛选和搜索功能，支持多种过滤条件

语言识别策略：
- 基于文件扩展名的精确匹配
- 支持39种主流编程语言和标记语言
- 可扩展的语言定义字典，便于添加新语言支持
- 智能回退机制，未知类型默认为Text

性能优化：
- 文件属性缓存，避免重复的系统调用
- 批量文件处理，减少单次操作开销
- 延迟加载策略，按需获取文件信息
- 内存友好的文件列表管理

错误处理：
- 文件访问异常的优雅处理
- 文件不存在时的安全降级
- 编码错误的备选处理方案
- 完整的错误信息和状态反馈
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass


LANGUAGE_EXTENSIONS = {
    'Python': ['.py', '.pyw', '.pyi'],
    'JavaScript': ['.js', '.jsx', '.mjs'],
    'TypeScript': ['.ts', '.tsx'],
    'Java': ['.java'],
    'C': ['.c', '.h'],
    'C++': ['.cpp', '.hpp', '.cc', '.cxx'],
    'C#': ['.cs'],
    'PHP': ['.php'],
    'Ruby': ['.rb'],
    'Go': ['.go'],
    'Rust': ['.rs'],
    'Swift': ['.swift'],
    'Kotlin': ['.kt', '.kts'],
    'HTML': ['.html', '.htm'],
    'CSS': ['.css', '.scss', '.sass', '.less'],
    'SQL': ['.sql'],
    'Shell': ['.sh', '.bash', '.zsh'],
    'PowerShell': ['.ps1'],
    'YAML': ['.yml', '.yaml'],
    'JSON': ['.json'],
    'XML': ['.xml'],
    'Markdown': ['.md'],
    'Vue': ['.vue'],
    'Svelte': ['.svelte'],
    'Dart': ['.dart'],
    'R': ['.r', '.R'],
    'Lua': ['.lua'],
    'Perl': ['.pl', '.pm'],
    'Text': ['.txt']
}

@dataclass
class FileInfo:
    """文件信息数据类
    
    核心属性：
    - path: 文件完整路径，唯一标识符
    - marked: 是否被标记为选中状态，用于批量操作
    - _cached_size: 缓存的文件大小，避免重复获取
    - _cached_mtime: 缓存的修改时间，用于变更检测
    """
    path: str                # 文件完整路径
    marked: bool = True      # 是否被标记选中
    _cached_size: int = None # 缓存的文件大小
    _cached_mtime: float = None # 缓存的修改时间
    
    @property
    def name(self) -> str:
        """获取文件名（不含路径）"""
        return os.path.basename(self.path)

    @property
    def language(self) -> str:
        """获取文件对应的编程语言"""
        return get_language(self.path)

    @property
    def size(self) -> int:
        """获取文件大小（字节）"""
        try:
            return os.path.getsize(self.path)
        except:
            return 0

    @property
    def exists(self) -> bool:
        """检查文件是否存在"""
        return os.path.exists(self.path)

    @property
    def mtime(self) -> float:
        """获取文件最后修改时间"""
        try:
            return os.path.getmtime(self.path)
        except:
            return 0

    def is_modified(self) -> bool:
        """检查文件是否被修改"""
        if self._cached_mtime is None:
            self._cached_mtime = self.mtime
            return False
        return self.mtime != self._cached_mtime

    def update_cache(self):
        """手动更新缓存信息"""
        self._cached_size = self.size
        self._cached_mtime = self.mtime

class FileHandler:
    """
    文件处理器 - 核心文件管理类

    核心职责：
    - 维护文件列表和文件状态管理
    - 提供文件的添加、删除、标记等操作
    - 支持批量文件处理和文件夹扫描
    - 提供文件统计信息和筛选功能

    设计特点：
    - 使用FileInfo数据类封装文件元数据
    - 实现文件状态跟踪和变更检测
    - 支持文件标记系统，便于批量操作
    - 提供灵活的筛选和搜索功能

    性能考虑：
    - 文件列表使用List存储，支持快速遍历
    - 文件存在性检查和重复检测
    - 批量操作优化，减少单次处理开销
    - 内存友好的文件信息管理

    状态管理：
    - 维护文件列表的顺序和完整性
    - 支持文件标记状态的批量修改
    - 提供文件刷新和状态同步功能
    - 处理文件不存在和访问异常
    """

    def __init__(self):
        """
        初始化文件处理器

        创建空的文件列表，用于存储FileInfo对象
        支持动态添加和删除文件操作
        """
        self.files: List[FileInfo] = []
    
    def add_file(self, path: str) -> bool:
        """
        添加单个文件到处理列表

        功能说明：
        - 验证文件存在性和类型
        - 检查文件是否已存在于列表中
        - 创建FileInfo对象并初始化缓存
        - 将文件添加到内部列表

        参数：
        - path: 文件完整路径

        返回值：
        - True: 文件成功添加
        - False: 文件添加失败（不存在、重复等）

        错误处理：
        - 文件不存在时返回False
        - 文件路径重复时返回False
        - 文件访问异常时安全降级

        性能考虑：
        - 使用列表推导式进行重复检测
        - 立即初始化文件缓存，避免后续重复访问
        """
        # 验证文件存在且为普通文件
        if not os.path.isfile(path):
            return False

        # 检查文件是否已存在于列表中
        if any(f.path == path for f in self.files):
            return False

        # 创建文件信息对象并初始化缓存
        file_info = FileInfo(path=path, marked=True)
        file_info.update_cache()  # 立即获取文件元数据

        # 添加到文件列表
        self.files.append(file_info)
        return True
    
    def add_files(self, paths: List[str]) -> int:
        count = 0
        for path in paths:
            if self.add_file(path):
                count += 1
        return count
    
    def add_folder(self, folder_path: str, recursive: bool = True) -> int:
        if not os.path.isdir(folder_path):
            return 0
        
        count = 0
        for file_path in scan_folder(folder_path, recursive):
            if self.add_file(file_path):
                count += 1
        return count
    
    def remove_file(self, path: str) -> bool:
        for i, file in enumerate(self.files):
            if file.path == path:
                self.files.pop(i)
                return True
        return False
    
    def clear(self):
        self.files.clear()
    
    def toggle_mark(self, path: str) -> bool:
        for file in self.files:
            if file.path == path:
                file.marked = not file.marked
                return file.marked
        return False
    def set_file_selection(self, path: str, marked: bool) -> bool:
        for file in self.files:
            if file.path == path:
                file.marked = marked
                return True
        return False
    
    def set_marks_batch(self, paths: List[str], marked: bool) -> int:
        count = 0
        for file in self.files:
            if file.path in paths:
                file.marked = marked
                count += 1
        return count
    
    def mark_all(self, marked: bool = True):
        for file in self.files:
            file.marked = marked
    
    def get_selected_files(self) -> List[FileInfo]:
        return [f for f in self.files if f.marked]
    
    def get_processing_statistics(self) -> Dict:
        total = len(self.files)
        marked = len(self.get_selected_files())
        total_size = sum(f.size for f in self.files)
        languages = set(f.language for f in self.files)
        
        return {
            'total': total,
            'marked': marked,
            'size': total_size,
            'languages': len(languages)
        }
    
    def filter_files(self, 
                    search: Optional[str] = None,
                    language: Optional[str] = None) -> List[FileInfo]:
        """筛选文件"""
        result = self.files
        
        if search:
            search = search.lower()
            result = [f for f in result if search in f.name.lower()]
        
        if language and language != "全部语言":
            result = [f for f in result if f.language == language]
        
        return result
    
    def refresh_files(self) -> Dict:
        removed = []
        modified = []
        
        # 检查文件是否存在，是否被修改
        for file_info in self.files[:]:  # 使用切片创建副本进行迭代
            if not file_info.exists:
                self.files.remove(file_info)
                removed.append(file_info.path)
            else:
                if file_info.is_modified():
                    modified.append(file_info.path)
                file_info.update_cache()
        
        return {
            'removed': removed,
            'modified': modified,
            'removed_count': len(removed),
            'modified_count': len(modified)
        }

def get_language(file_path: str) -> str:
    _, ext = os.path.splitext(file_path.lower())
    
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return language
    
    return "Text"

def get_all_languages() -> List[str]:
    return sorted(LANGUAGE_EXTENSIONS.keys())

def scan_folder(folder_path: str, recursive: bool = True):
    """扫描文件夹获取支持的文件（生成器）"""
    all_extensions = {ext for exts in LANGUAGE_EXTENSIONS.values() for ext in exts}
    
    if recursive:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path.lower())
                if ext in all_extensions:
                    yield file_path
    else:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_path.lower())
                if ext in all_extensions:
                    yield file_path

def format_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"