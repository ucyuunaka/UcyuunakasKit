"""
防抖器模块 - 统一的防抖机制
"""

import threading
import time
from typing import Callable, Optional, Any
from weakref import WeakMethod


class SimpleDebouncer:
    """
    统一的防抖器实现
    
    提供可配置的防抖机制，用于合并频繁的操作调用，
    避免过多的计算和UI更新。
    """
    
    def __init__(self, callback: Callable, delay: float = 0.3):
        """
        初始化防抖器
        
        Args:
            callback: 回调函数
            delay: 防抖延迟时间（秒），默认300ms
        """
        self.callback = callback
        self.delay = delay
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._last_call_time = 0.0
        self._call_count = 0
        self._is_running = False
        
        # 使用弱引用避免循环引用问题
        if hasattr(callback, '__self__') and hasattr(callback, '__func__'):
            try:
                self.callback = WeakMethod(callback)
            except TypeError:
                # 如果不是绑定方法，直接使用原始回调
                self.callback = callback
    
    def schedule(self, *args, **kwargs) -> bool:
        """
        调度执行回调函数
        
        Args:
            *args: 传递给回调函数的位置参数
            **kwargs: 传递给回调函数的关键字参数
            
        Returns:
            bool: 是否成功调度（如果是重复调度则返回False）
        """
        with self._lock:
            current_time = time.time()
            
            # 如果距离上次调用时间太短，忽略此次调用
            if current_time - self._last_call_time < 0.01:  # 10ms内的重复调用
                return False
            
            # 取消已存在的定时器
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            
            # 创建新的定时器
            self._timer = threading.Timer(self.delay, self._execute, args, kwargs)
            self._timer.start()
            self._last_call_time = current_time
            self._call_count += 1
            self._is_running = True
            
            return True
    
    def _execute(self, *args, **kwargs):
        """执行回调函数"""
        try:
            with self._lock:
                self._timer = None
                self._is_running = False
            
            # 调用回调函数
            if callable(self.callback):
                if isinstance(self.callback, WeakMethod):
                    callback = self.callback()
                    if callback is not None:
                        callback(*args, **kwargs)
                else:
                    self.callback(*args, **kwargs)
        except Exception as e:
            # 防抖器执行失败不应该影响主程序
            print(f"Debouncer callback error: {e}")
    
    def cancel(self) -> bool:
        """
        取消当前待执行的定时器
        
        Returns:
            bool: 是否成功取消
        """
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
                self._is_running = False
                return True
            return False
    
    def is_pending(self) -> bool:
        """
        检查是否有待执行的回调
        
        Returns:
            bool: 是否有待执行的回调
        """
        with self._lock:
            return self._timer is not None
    
    def is_running(self) -> bool:
        """
        检查防抖器是否正在运行
        
        Returns:
            bool: 是否正在运行
        """
        with self._lock:
            return self._is_running
    
    def flush(self) -> bool:
        """
        立即执行待执行的回调（如果有）
        
        Returns:
            bool: 是否执行了回调
        """
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
                self._is_running = False
                # 在锁外执行回调，避免死锁
                threading.Thread(target=self._execute).start()
                return True
            return False
    
    def get_call_count(self) -> int:
        """
        获取总调用次数
        
        Returns:
            int: 总调用次数
        """
        with self._lock:
            return self._call_count
    
    def get_last_call_time(self) -> float:
        """
        获取上次调用时间
        
        Returns:
            float: 上次调用时间戳
        """
        with self._lock:
            return self._last_call_time
    
    def reset(self):
        """重置防抖器状态"""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._is_running = False
            self._last_call_time = 0.0
            self._call_count = 0
    
    def __del__(self):
        """析构函数，确保清理定时器"""
        self.cancel()


class DebouncerGroup:
    """
    防抖器组管理器
    
    用于管理多个相关的防抖器，提供统一的控制接口。
    """
    
    def __init__(self):
        """初始化防抖器组"""
        self._debouncers: dict[str, SimpleDebouncer] = {}
        self._lock = threading.Lock()
    
    def create_debouncer(self, name: str, callback: Callable, delay: float = 0.3) -> SimpleDebouncer:
        """
        创建或获取防抖器
        
        Args:
            name: 防抖器名称
            callback: 回调函数
            delay: 防抖延迟时间
            
        Returns:
            SimpleDebouncer: 防抖器实例
        """
        with self._lock:
            if name in self._debouncers:
                return self._debouncers[name]
            
            debouncer = SimpleDebouncer(callback, delay)
            self._debouncers[name] = debouncer
            return debouncer
    
    def get_debouncer(self, name: str) -> Optional[SimpleDebouncer]:
        """
        获取防抖器
        
        Args:
            name: 防抖器名称
            
        Returns:
            Optional[SimpleDebouncer]: 防抖器实例，如果不存在则返回None
        """
        with self._lock:
            return self._debouncers.get(name)
    
    def cancel_all(self):
        """取消所有防抖器"""
        with self._lock:
            for debouncer in self._debouncers.values():
                debouncer.cancel()
    
    def flush_all(self):
        """立即执行所有待执行的回调"""
        with self._lock:
            for debouncer in self._debouncers.values():
                debouncer.flush()
    
    def remove_debouncer(self, name: str) -> bool:
        """
        移除防抖器
        
        Args:
            name: 防抖器名称
            
        Returns:
            bool: 是否成功移除
        """
        with self._lock:
            if name in self._debouncers:
                self._debouncers[name].cancel()
                del self._debouncers[name]
                return True
            return False
    
    def clear_all(self):
        """清除所有防抖器"""
        with self._lock:
            for debouncer in self._debouncers.values():
                debouncer.cancel()
            self._debouncers.clear()
    
    def get_status(self) -> dict[str, dict]:
        """
        获取所有防抖器的状态
        
        Returns:
            dict[str, dict]: 防抖器状态信息
        """
        with self._lock:
            status = {}
            for name, debouncer in self._debouncers.items():
                status[name] = {
                    'is_pending': debouncer.is_pending(),
                    'is_running': debouncer.is_running(),
                    'call_count': debouncer.get_call_count(),
                    'last_call_time': debouncer.get_last_call_time()
                }
            return status