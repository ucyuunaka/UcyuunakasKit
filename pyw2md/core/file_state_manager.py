"""
文件状态管理器 - 统一管理所有文件变化状态
"""

import time
from typing import Dict, List, Tuple, Set
from threading import Lock, RLock
from dataclasses import dataclass


@dataclass
class FileChange:
    """文件变化记录"""
    path: str
    change_type: str  # 'modified', 'deleted'
    timestamp: float


class FileStateManager:
    """
    统一的文件状态管理器
    
    负责管理所有文件变化状态，提供线程安全的状态操作接口。
    取代分散在各个组件中的状态管理，确保状态的一致性和可追踪性。
    """
    
    def __init__(self):
        """初始化文件状态管理器"""
        self._changes: Dict[str, FileChange] = {}  # path -> FileChange
        self._lock = RLock()  # 使用可重入锁
        self._last_cleared_time = 0.0
    
    def add_change(self, path: str, change_type: str) -> bool:
        """
        添加文件变化记录
        
        Args:
            path: 文件路径
            change_type: 变化类型 ('modified' 或 'deleted')
            
        Returns:
            bool: 是否成功添加（如果是重复变化则返回False）
        """
        with self._lock:
            current_time = time.time()
            
            # 检查是否是重复变化
            if path in self._changes:
                existing_change = self._changes[path]
                # 相同类型的变化且时间间隔很短，视为重复
                if (existing_change.change_type == change_type and 
                    current_time - existing_change.timestamp < 0.1):
                    return False
            
            # 添加或更新变化记录
            self._changes[path] = FileChange(path, change_type, current_time)
            return True
    
    def get_and_clear_changes(self) -> List[FileChange]:
        """
        获取并清除所有待处理的变化
        
        Returns:
            List[FileChange]: 变化记录列表
        """
        with self._lock:
            changes = list(self._changes.values())
            self._changes.clear()
            self._last_cleared_time = time.time()
            return changes
    
    def get_changes(self) -> List[FileChange]:
        """
        获取当前所有待处理的变化（不清除）
        
        Returns:
            List[FileChange]: 变化记录列表
        """
        with self._lock:
            return list(self._changes.values())
    
    def has_changes(self) -> bool:
        with self._lock:
            return len(self._changes) > 0
    
    def get_change_count(self) -> int:
        with self._lock:
            return len(self._changes)
    
    def get_changes_by_type(self, change_type: str) -> List[FileChange]:
        """
        获取指定类型的变化
        
        Args:
            change_type: 变化类型 ('modified' 或 'deleted')
            
        Returns:
            List[FileChange]: 指定类型的变化记录列表
        """
        with self._lock:
            return [change for change in self._changes.values() 
                   if change.change_type == change_type]
    
    def remove_change(self, path: str) -> bool:
        """
        移除指定文件的变化记录
        
        Args:
            path: 文件路径
            
        Returns:
            bool: 是否成功移除
        """
        with self._lock:
            if path in self._changes:
                del self._changes[path]
                return True
            return False
    
    def clear_changes(self):
        with self._lock:
            self._changes.clear()
            self._last_cleared_time = time.time()
    
    def get_file_status(self, path: str) -> str:
        """
        获取指定文件的状态
        
        Args:
            path: 文件路径
            
        Returns:
            str: 文件状态 ('modified', 'deleted', 'normal')
        """
        with self._lock:
            if path in self._changes:
                return self._changes[path].change_type
            return 'normal'
    
    def get_last_cleared_time(self) -> float:
        with self._lock:
            return self._last_cleared_time
    
    def cleanup_old_changes(self, max_age_seconds: float = 300.0):
        """
        清理过期的变化记录
        
        Args:
            max_age_seconds: 最大保留时间（秒），默认5分钟
        """
        with self._lock:
            current_time = time.time()
            expired_paths = []
            
            for path, change in self._changes.items():
                if current_time - change.timestamp > max_age_seconds:
                    expired_paths.append(path)
            
            for path in expired_paths:
                del self._changes[path]
    
    def get_summary(self) -> Dict[str, int]:
        with self._lock:
            summary = {
                'total': len(self._changes),
                'modified': 0,
                'deleted': 0
            }
            
            for change in self._changes.values():
                if change.change_type in summary:
                    summary[change.change_type] += 1
            
            return summary