"""
文件监控模块 - 自动检测文件变化
"""

import os
import logging
from typing import Callable, Dict, Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileDeletedEvent
from .file_state_manager import FileStateManager
from utils.debouncer import SimpleDebouncer

# 配置日志
logger = logging.getLogger(__name__)


class FileWatcherError(Exception):
    """文件监控器异常"""
    pass


class MonitoringError(Exception):
    """监控错误异常"""
    pass


class FileChangeHandler(FileSystemEventHandler):
    """文件变化处理器"""
    
    def __init__(self, file_state_manager: FileStateManager, callback: Callable, watched_files: Set[str]):
        super().__init__()
        self.file_state_manager = file_state_manager
        self.callback = callback
        self.watched_files = watched_files
        # 使用统一的防抖机制，设置为300ms
        self.debouncer = SimpleDebouncer(self._process_changes, delay=0.3)
    
    def _process_changes(self):
        """处理累积的文件变化"""
        changes = self.file_state_manager.get_and_clear_changes()
        if changes:
            for change in changes:
                self.callback(change.change_type, change.path)
    
    def on_modified(self, event):
        """文件被修改"""
        if event.is_directory:
            return
        
        file_path = os.path.abspath(event.src_path)
        
        # 只处理监控列表中的文件
        if file_path not in self.watched_files:
            return
        
        # 添加变化到状态管理器
        self.file_state_manager.add_change(file_path, 'modified')
        
        # 调度处理
        self.debouncer.schedule()
    
    def on_deleted(self, event):
        """文件被删除"""
        if event.is_directory:
            return
        
        file_path = os.path.abspath(event.src_path)
        
        # 只处理监控列表中的文件
        if file_path not in self.watched_files:
            return
        
        # 添加变化到状态管理器
        self.file_state_manager.add_change(file_path, 'deleted')
        
        # 调度处理
        self.debouncer.schedule()


class FileWatcher:
    """文件监控器"""
    
    def __init__(self, callback: Callable):
        """
        初始化文件监控器
        
        Args:
            callback: 回调函数 callback(event_type, file_path)
                     event_type: 'modified' 或 'deleted'
        """
        self.callback = callback
        self.observer = Observer()
        self.watched_files: Set[str] = set()
        self.watched_dirs: Dict[str, Set[str]] = {}  # 目录 -> 该目录下监控的文件集合
        self.handler = None
        self.is_running = False
        # 使用统一的状态管理器
        self.file_state_manager = FileStateManager()
    
    def start(self):
        """启动监控"""
        if not self.is_running:
            self.handler = FileChangeHandler(self.file_state_manager, self.callback, self.watched_files)
            self.observer.start()
            self.is_running = True
    
    def stop(self):
        """停止监控"""
        if self.is_running:
            if self.handler:
                self.handler.debouncer.cancel()
            self.observer.stop()
            self.observer.join(timeout=2)
            self.is_running = False
    
    def add_file(self, file_path: str):
        """添加文件到监控列表"""
        if not os.path.exists(file_path):
            return False
        
        file_path = os.path.abspath(file_path)
        dir_path = os.path.dirname(file_path)
        
        # 添加到监控文件集合
        self.watched_files.add(file_path)
        
        # 如果该目录还没有被监控，添加监控
        if dir_path not in self.watched_dirs:
            self.watched_dirs[dir_path] = set()
            # 确保 handler 已初始化
            if self.handler is None:
                self.handler = FileChangeHandler(self.file_state_manager, self.callback, self.watched_files)
            try:
                self.observer.schedule(self.handler, dir_path, recursive=False)
            except Exception as e:
                print(f"监控目录失败 {dir_path}: {e}")
                return False
        
        # 记录该目录下的文件
        self.watched_dirs[dir_path].add(file_path)
        return True
    
    def remove_file(self, file_path: str):
        """从监控列表移除文件"""
        file_path = os.path.abspath(file_path)
        dir_path = os.path.dirname(file_path)
        
        # 从监控文件集合移除
        self.watched_files.discard(file_path)
        
        # 从目录映射中移除
        if dir_path in self.watched_dirs:
            self.watched_dirs[dir_path].discard(file_path)
            
            # 如果该目录下没有其他监控文件了，停止监控该目录
            if not self.watched_dirs[dir_path]:
                del self.watched_dirs[dir_path]
                # 注意: watchdog 不支持直接移除单个监控，需要重启observer
    
    def clear(self):
        """清空所有监控"""
        self.watched_files.clear()
        self.watched_dirs.clear()
        
        if self.is_running:
            self.stop()
            self.observer = Observer()
            self.handler = FileChangeHandler(self.file_state_manager, self.callback, self.watched_files)
            self.start()
    
    def get_watched_count(self) -> int:
        """获取监控文件数量"""
        return len(self.watched_files)
    
    def get_pending_changes_count(self) -> int:
        """获取待处理变化数量"""
        return self.file_state_manager.get_change_count()
    
    def flush_pending_changes(self):
        """立即处理待处理的变化"""
        if self.handler:
            self.handler.debouncer.flush()
    
    def is_monitoring_file(self, file_path: str) -> bool:
        """检查文件是否正在被监控"""
        file_path = os.path.abspath(file_path)
        return file_path in self.watched_files
    
    def get_watched_directories(self) -> Set[str]:
        """获取被监控的目录列表"""
        return set(self.watched_dirs.keys())
    
    def get_monitored_files_in_directory(self, dir_path: str) -> Set[str]:
        """获取指定目录下被监控的文件"""
        dir_path = os.path.abspath(dir_path)
        return self.watched_dirs.get(dir_path, set())