"""
文件监控模块 - 自动检测文件变化（增强版）
"""

import os
import logging
from typing import Callable, Dict, Set, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileDeletedEvent
from .file_state_manager import FileStateManager
from utils.debouncer import SimpleDebouncer
from .constants import (
    DEFAULT_DEBOUNCE_MS, MAX_WATCH_ERRORS, MSG_WATCH_FAILED, MSG_WATCH_RESTARTED,
    FILE_CHANGE_MODIFIED, FILE_CHANGE_DELETED
)

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
    
    def __init__(self, file_state_manager: FileStateManager, callback: Callable, watched_files: Set[str], error_callback: Callable):
        super().__init__()
        self.file_state_manager = file_state_manager
        self.callback = callback
        self.watched_files = watched_files
        self.error_callback = error_callback
  
        self.debouncer = SimpleDebouncer(self._process_changes, delay=0.3)
    
    def _process_changes(self):
        """处理累积的文件变化"""
        try:
            changes = self.file_state_manager.get_and_clear_changes()
            if changes:
                for change in changes:
                    self.callback(change.change_type, change.path)
        except Exception as e:
            self.error_callback(f"处理文件变化时发生错误: {e}", "change_processing_error", e)
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        try:
            file_path = os.path.abspath(event.src_path)
            
            
            if file_path not in self.watched_files:
                return
            
  
            self.file_state_manager.add_change(file_path, 'modified')
            
  
            self.debouncer.schedule()
            
        except Exception as e:
            self.error_callback(f"处理文件修改事件时发生错误: {e}", "file_modified_error", e)
    
    def on_deleted(self, event):
        if event.is_directory:
            return
        
        try:
            file_path = os.path.abspath(event.src_path)
            
            
            if file_path not in self.watched_files:
                return
            
  
            self.file_state_manager.add_change(file_path, 'deleted')
            
  
            self.debouncer.schedule()
            
        except Exception as e:
            self.error_callback(f"处理文件删除事件时发生错误: {e}", "file_deleted_error", e)


class FileWatcher:
    """文件监控器"""
    
    def __init__(self, callback: Callable, error_callback: Optional[Callable] = None):
        """
        初始化文件监控器
        
        Args:
            callback: 回调函数 callback(event_type, file_path)
                     event_type: 'modified' 或 'deleted'
            error_callback: 错误回调函数 callback(error_message, error_type, exception=None)
                           error_type: 'directory_watch_failed', 'observer_start_failed', 
                                       'observer_stop_failed', 'monitoring_disabled' 等
        """
        self.callback = callback
        self.error_callback = error_callback or self._default_error_callback
        self.observer = Observer()
        self.watched_files: Set[str] = set()
        self.watched_dirs: Dict[str, Set[str]] = {}  # 目录 -> 该目录下监控的文件集合
        self.handler = None
        self.is_running = False
        self.monitoring_enabled = True  # 监控功能启用状态
        self.error_count = 0  # 错误计数
        self.max_errors = 10  # 最大错误次数
  
        self.file_state_manager = FileStateManager()
    
    def _default_error_callback(self, error_message: str, error_type: str, exception: Optional[Exception] = None):
        """默认错误回调函数"""
        logger.error(f"文件监控错误 [{error_type}]: {error_message}")
        # 这里可以替换为用户可见的消息显示
        print(f"文件监控错误: {error_message}")
    
    def _handle_error(self, error_message: str, error_type: str, exception: Optional[Exception] = None):
        """处理错误"""
        self.error_count += 1
        
  
        logger.error(f"文件监控错误 [{error_type}]: {error_message}")
        if exception:
            logger.exception(f"异常详情: {exception}")
        
  
        self.error_callback(error_message, error_type, exception)
        
    
        if self.error_count >= self.max_errors:
            self.monitoring_enabled = False
            error_msg = f"文件监控错误次数过多({self.error_count})，已自动禁用监控功能"
            self.error_callback(error_msg, "monitoring_disabled", None)
            logger.critical(error_msg)
    
    def start(self):
        if not self.monitoring_enabled:
            self._handle_error("监控功能已被禁用", "monitoring_disabled")
            return False
        
        if self.is_running:
            return True
        
        try:
            self.handler = FileChangeHandler(
                self.file_state_manager, 
                self.callback, 
                self.watched_files,
                self.error_callback
            )
            self.observer.start()
            self.is_running = True
            logger.info("文件监控器启动成功")
            return True
            
        except Exception as e:
            error_msg = f"启动文件监控器失败: {e}"
            self._handle_error(error_msg, "observer_start_failed", e)
            return False
    
    def stop(self):
        if not self.is_running:
            return True
        
        try:
            if self.handler:
                self.handler.debouncer.cancel()
            self.observer.stop()
            self.observer.join(timeout=5)
            
            if self.observer.is_alive():
                logger.warning("文件监控器停止超时")
                self._handle_error("文件监控器停止超时", "observer_stop_timeout")
            
            self.is_running = False
            logger.info("文件监控器停止成功")
            return True
            
        except Exception as e:
            error_msg = f"停止文件监控器失败: {e}"
            self._handle_error(error_msg, "observer_stop_failed", e)
            return False
    
    def add_file(self, file_path: str):
        if not self.monitoring_enabled:
            self._handle_error(f"无法添加文件监控 {file_path}，监控功能已被禁用", "monitoring_disabled")
            return False
        
        if not os.path.exists(file_path):
            error_msg = f"文件不存在，无法添加到监控: {file_path}"
            self._handle_error(error_msg, "file_not_found")
            return False
        
        try:
            file_path = os.path.abspath(file_path)
            dir_path = os.path.dirname(file_path)
            
  
            self.watched_files.add(file_path)
            
  
            if dir_path not in self.watched_dirs:
                self.watched_dirs[dir_path] = set()
  
                if self.handler is None:
                    self.handler = FileChangeHandler(
                        self.file_state_manager, 
                        self.callback, 
                        self.watched_files,
                        self.error_callback
                    )
                
                try:
                    self.observer.schedule(self.handler, dir_path, recursive=False)
                    logger.info(f"开始监控目录: {dir_path}")
                except Exception as e:
                    error_msg = f"监控目录失败 {dir_path}: {e}"
                    self._handle_error(error_msg, "directory_watch_failed", e)
  
                    self.watched_files.discard(file_path)
                    self.watched_dirs.pop(dir_path, None)
                    return False
            
    
            self.watched_dirs[dir_path].add(file_path)
            logger.debug(f"添加文件到监控: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"添加文件到监控失败 {file_path}: {e}"
            self._handle_error(error_msg, "add_file_failed", e)
            return False
    
    def remove_file(self, file_path: str):
        try:
            file_path = os.path.abspath(file_path)
            dir_path = os.path.dirname(file_path)
            
    
            self.watched_files.discard(file_path)
            
      
            if dir_path in self.watched_dirs:
                self.watched_dirs[dir_path].discard(file_path)
                
  
                if not self.watched_dirs[dir_path]:
                    del self.watched_dirs[dir_path]
                    logger.info(f"停止监控目录: {dir_path}")
    
                    
            logger.debug(f"从监控中移除文件: {file_path}")
            return True
            
        except Exception as e:
            error_msg = f"从监控移除文件失败 {file_path}: {e}"
            self._handle_error(error_msg, "remove_file_failed", e)
            return False
    
    def clear(self):
        try:
            self.watched_files.clear()
            self.watched_dirs.clear()
            
            if self.is_running:
                self.stop()
                self.observer = Observer()
                self.handler = FileChangeHandler(
                    self.file_state_manager, 
                    self.callback, 
                    self.watched_files,
                    self.error_callback
                )
                self.start()
            
            logger.info("已清空所有监控")
            return True
            
        except Exception as e:
            error_msg = f"清空监控失败: {e}"
            self._handle_error(error_msg, "clear_monitoring_failed", e)
            return False
    
    def get_watched_count(self) -> int:
        return len(self.watched_files)
    
    def get_pending_changes_count(self) -> int:
        return self.file_state_manager.get_change_count()
    
    def flush_pending_changes(self):
        try:
            if self.handler:
                self.handler.debouncer.flush()
                return True
            return False
        except Exception as e:
            error_msg = f"刷新待处理变化失败: {e}"
            self._handle_error(error_msg, "flush_changes_failed", e)
            return False
    
    def is_monitoring_file(self, file_path: str) -> bool:
        file_path = os.path.abspath(file_path)
        return file_path in self.watched_files
    
    def get_watched_directories(self) -> Set[str]:
        return set(self.watched_dirs.keys())
    
    def get_monitored_files_in_directory(self, dir_path: str) -> Set[str]:
        dir_path = os.path.abspath(dir_path)
        return self.watched_dirs.get(dir_path, set())
    
    def get_monitoring_status(self) -> Dict[str, any]:
        return {
            'is_running': self.is_running,
            'monitoring_enabled': self.monitoring_enabled,
            'error_count': self.error_count,
            'max_errors': self.max_errors,
            'watched_files_count': len(self.watched_files),
            'watched_directories_count': len(self.watched_dirs),
            'pending_changes_count': self.get_pending_changes_count()
        }
    
    def reset_error_count(self):
        self.error_count = 0
        logger.info("已重置错误计数")
    
    def enable_monitoring(self):
        if not self.monitoring_enabled:
            self.monitoring_enabled = True
            self.reset_error_count()
            logger.info("已启用监控功能")
            return True
        return False
    
    def disable_monitoring(self):
        if self.monitoring_enabled:
            self.monitoring_enabled = False
            self.stop()  # 停止当前监控
            logger.info("已禁用监控功能")
            return True
        return False
    
    def restart_monitoring(self) -> bool:
        try:
            was_running = self.is_running
            if was_running:
                self.stop()
            
  
            self.reset_error_count()
            
            if was_running:
                return self.start()
            
            return True
            
        except Exception as e:
            error_msg = f"重启监控失败: {e}"
            self._handle_error(error_msg, "restart_monitoring_failed", e)
            return False