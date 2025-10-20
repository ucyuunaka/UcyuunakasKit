"""
pyw2md 核心接口定义
Core interfaces for pyw2md to reduce component coupling
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum

# 导入常量
from .constants import (
    FILE_CHANGE_MODIFIED, 
    FILE_CHANGE_DELETED, 
    FILE_CHANGE_CREATED
)

class FileChangeType(Enum):
    """文件变化类型枚举"""
    MODIFIED = FILE_CHANGE_MODIFIED
    DELETED = FILE_CHANGE_DELETED
    CREATED = FILE_CHANGE_CREATED

@dataclass
class FileChange:
    """文件变化记录"""
    path: str
    change_type: FileChangeType
    timestamp: float

class IMessageDisplay(ABC):
    """消息显示接口"""
    
    @abstractmethod
    def show_message(self, message: str, duration_ms: int = 3000, msg_type: str = "info") -> None:
        """显示消息"""
        pass

    @abstractmethod
    def clear_message(self) -> None:
        """清除消息"""
        pass

class IFileChangeHandler(ABC):
    """文件变化处理接口"""
    
    @abstractmethod
    def on_file_changed(self, change: FileChange) -> None:
        """文件变化回调"""
        pass

    @abstractmethod
    def on_batch_changes(self, changes: List[FileChange]) -> None:
        """批量文件变化回调"""
        pass

class IFileWatcher(ABC):
    """文件监控接口"""
    
    @abstractmethod
    def start_watching(self, paths: List[str]) -> bool:
        """开始监控指定路径"""
        pass

    @abstractmethod
    def stop_watching(self) -> None:
        """停止监控"""
        pass

    @abstractmethod
    def is_watching(self) -> bool:
        """检查是否正在监控"""
        pass

    @abstractmethod
    def set_change_handler(self, handler: IFileChangeHandler) -> None:
        """设置变化处理器"""
        pass

class IStateManager(ABC):
    """状态管理接口"""
    
    @abstractmethod
    def add_change(self, change: FileChange) -> None:
        """添加变化记录"""
        pass

    @abstractmethod
    def get_and_clear_changes(self) -> List[FileChange]:
        """获取并清除所有变化"""
        pass

    @abstractmethod
    def has_changes(self) -> bool:
        """检查是否有待处理变化"""
        pass

    @abstractmethod
    def get_change_count(self) -> int:
        """获取变化数量"""
        pass

class IRefreshHandler(ABC):
    """刷新处理接口"""
    
    @abstractmethod
    def refresh_changed_files(self, changes: List[FileChange]) -> bool:
        """刷新变化的文件"""
        pass

    @abstractmethod
    def can_refresh(self) -> bool:
        """检查是否可以执行刷新"""
        pass