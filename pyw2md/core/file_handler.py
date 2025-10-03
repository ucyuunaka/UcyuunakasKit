"""
文件处理核心模块
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass

# 支持的语言和扩展名
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
    """文件信息数据类"""
    path: str
    marked: bool = True
    _cached_size: int = None
    _cached_mtime: float = None
    
    @property
    def name(self) -> str:
        return os.path.basename(self.path)
    
    @property
    def language(self) -> str:
        return get_language(self.path)
    
    @property
    def size(self) -> int:
        try:
            return os.path.getsize(self.path)
        except:
            return 0
    
    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)
    
    @property
    def mtime(self) -> float:
        """获取文件修改时间"""
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
        """更新缓存信息"""
        self._cached_size = self.size
        self._cached_mtime = self.mtime

class FileHandler:
    """文件处理器"""
    
    def __init__(self):
        self.files: List[FileInfo] = []
    
    def add_file(self, path: str) -> bool:
        """添加单个文件"""
        if not os.path.isfile(path):
            return False
        
        # 检查是否已存在
        if any(f.path == path for f in self.files):
            return False
        
        file_info = FileInfo(path=path, marked=True)
        file_info.update_cache()
        self.files.append(file_info)
        return True
    
    def add_files(self, paths: List[str]) -> int:
        """批量添加文件"""
        count = 0
        for path in paths:
            if self.add_file(path):
                count += 1
        return count
    
    def add_folder(self, folder_path: str, recursive: bool = True) -> int:
        """添加文件夹中的所有支持文件"""
        if not os.path.isdir(folder_path):
            return 0
        
        files = scan_folder(folder_path, recursive)
        return self.add_files(files)
    
    def remove_file(self, path: str) -> bool:
        """移除文件"""
        for i, file in enumerate(self.files):
            if file.path == path:
                self.files.pop(i)
                return True
        return False
    
    def clear(self):
        """清空所有文件"""
        self.files.clear()
    
    def toggle_mark(self, path: str) -> bool:
        """切换文件标记状态"""
        for file in self.files:
            if file.path == path:
                file.marked = not file.marked
                return file.marked
        return False
    
    def mark_all(self, marked: bool = True):
        """标记/取消标记所有文件"""
        for file in self.files:
            file.marked = marked
    
    def get_marked_files(self) -> List[FileInfo]:
        """获取所有已标记的文件"""
        return [f for f in self.files if f.marked]
    
    def get_stats(self) -> Dict:
        """获取统计信息"""
        total = len(self.files)
        marked = len(self.get_marked_files())
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
        """刷新所有文件，移除不存在的，更新缓存"""
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
    """根据文件扩展名获取编程语言"""
    _, ext = os.path.splitext(file_path.lower())
    
    for language, extensions in LANGUAGE_EXTENSIONS.items():
        if ext in extensions:
            return language
    
    return "Text"

def get_all_languages() -> List[str]:
    """获取所有支持的语言"""
    return sorted(LANGUAGE_EXTENSIONS.keys())

def scan_folder(folder_path: str, recursive: bool = True) -> List[str]:
    """扫描文件夹获取所有支持的文件"""
    supported_files = []
    all_extensions = [ext for exts in LANGUAGE_EXTENSIONS.values() for ext in exts]
    
    if recursive:
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                _, ext = os.path.splitext(file_path.lower())
                if ext in all_extensions:
                    supported_files.append(file_path)
    else:
        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                _, ext = os.path.splitext(file_path.lower())
                if ext in all_extensions:
                    supported_files.append(file_path)
    
    return supported_files

def format_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"