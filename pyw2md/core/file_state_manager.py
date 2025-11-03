import time
from typing import Dict, List, Tuple, Set
from threading import Lock, RLock
from dataclasses import dataclass


@dataclass
class FileChange:
    path: str
    change_type: str  # 'modified', 'deleted'
    timestamp: float


class FileStateManager:
    def __init__(self):
        self._changes: Dict[str, FileChange] = {}
        self._lock = RLock()
        self._last_cleared_time = 0.0
    
    def add_change(self, path: str, change_type: str) -> bool:
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
        with self._lock:
            changes = list(self._changes.values())
            self._changes.clear()
            self._last_cleared_time = time.time()
            return changes
    
    def get_changes(self) -> List[FileChange]:
        with self._lock:
            return list(self._changes.values())
    
    def has_changes(self) -> bool:
        with self._lock:
            return len(self._changes) > 0
    
    def get_change_count(self) -> int:
        with self._lock:
            return len(self._changes)
    
    def get_changes_by_type(self, change_type: str) -> List[FileChange]:
        with self._lock:
            return [change for change in self._changes.values() 
                   if change.change_type == change_type]
    
    def remove_change(self, path: str) -> bool:
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
        with self._lock:
            if path in self._changes:
                return self._changes[path].change_type
            return 'normal'
    
    def get_last_cleared_time(self) -> float:
        with self._lock:
            return self._last_cleared_time
    
    def cleanup_old_changes(self, max_age_seconds: float = 300.0):
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