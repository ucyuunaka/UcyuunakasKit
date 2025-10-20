"""
FileWatcher错误处理测试
"""

import unittest
import tempfile
import os
import time
import threading
import logging
from unittest.mock import Mock, patch
from core.file_watcher import FileWatcher, FileWatcherError, MonitoringError


class TestFileWatcherErrorHandling(unittest.TestCase):
    """FileWatcher错误处理测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.error_callback = Mock()
        self.watcher = FileWatcher(self.callback, self.error_callback)
        
        # 配置日志
        logging.basicConfig(level=logging.DEBUG)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_default_error_callback(self):
        """测试默认错误回调"""
        # 创建一个没有自定义错误回调的监控器
        watcher_no_callback = FileWatcher(self.callback)
        
        # 触发错误
        watcher_no_callback._handle_error("测试错误", "test_error")
        
        # 验证错误计数增加
        self.assertEqual(watcher_no_callback.error_count, 1)
    
    def test_custom_error_callback(self):
        """测试自定义错误回调"""
        # 触发错误
        self.watcher._handle_error("测试错误", "test_error")
        
        # 验证错误回调被调用
        self.error_callback.assert_called_once_with("测试错误", "test_error", None)
        
        # 验证错误计数增加
        self.assertEqual(self.watcher.error_count, 1)
    
    def test_error_callback_with_exception(self):
        """测试带异常的错误回调"""
        exception = ValueError("测试异常")
        
        # 触发错误
        self.watcher._handle_error("测试错误", "test_error", exception)
        
        # 验证错误回调被调用
        self.error_callback.assert_called_once_with("测试错误", "test_error", exception)
    
    def test_monitoring_disabled_after_max_errors(self):
        """测试达到最大错误次数后禁用监控"""
        # 设置较小的最大错误次数用于测试
        self.watcher.max_errors = 3
        
        # 触发多次错误
        for i in range(3):
            self.watcher._handle_error(f"错误 {i+1}", "test_error")
        
        # 验证监控被禁用
        self.assertFalse(self.watcher.monitoring_enabled)
        self.assertEqual(self.watcher.error_count, 3)
        
        # 验证禁用监控的错误回调被调用
        error_calls = [call[0] for call in self.error_callback.call_args_list]
        disable_call = [call for call in error_calls if "已自动禁用监控功能" in call[0]]
        self.assertTrue(len(disable_call) > 0)
    
    def test_add_nonexistent_file(self):
        """测试添加不存在的文件"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        
        # 尝试添加不存在的文件
        result = self.watcher.add_file(nonexistent_file)
        
        # 验证添加失败
        self.assertFalse(result)
        
        # 验证错误回调被调用
        self.error_callback.assert_called()
        error_args = self.error_callback.call_args[0]
        self.assertEqual(error_args[1], "file_not_found")
        self.assertIn("文件不存在", error_args[0])
    
    def test_add_file_when_monitoring_disabled(self):
        """测试监控禁用时添加文件"""
        # 禁用监控
        self.watcher.monitoring_enabled = False
        
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # 尝试添加文件
        result = self.watcher.add_file(test_file)
        
        # 验证添加失败
        self.assertFalse(result)
        
        # 验证错误回调被调用
        self.error_callback.assert_called()
        error_args = self.error_callback.call_args[0]
        self.assertEqual(error_args[1], "monitoring_disabled")
    
    def test_get_monitoring_status(self):
        """测试获取监控状态"""
        status = self.watcher.get_monitoring_status()
        
        # 验证状态信息
        expected_keys = [
            'is_running', 'monitoring_enabled', 'error_count',
            'max_errors', 'watched_files_count', 'watched_directories_count',
            'pending_changes_count'
        ]
        for key in expected_keys:
            self.assertIn(key, status)
        
        # 验证初始状态
        self.assertFalse(status['is_running'])
        self.assertTrue(status['monitoring_enabled'])
        self.assertEqual(status['error_count'], 0)
        self.assertEqual(status['watched_files_count'], 0)
    
    def test_reset_error_count(self):
        """测试重置错误计数"""
        # 增加错误计数
        self.watcher._handle_error("测试错误", "test_error")
        self.assertEqual(self.watcher.error_count, 1)
        
        # 重置错误计数
        self.watcher.reset_error_count()
        self.assertEqual(self.watcher.error_count, 0)
    
    def test_enable_disable_monitoring(self):
        """测试启用/禁用监控"""
        # 初始状态应该是启用的
        self.assertTrue(self.watcher.monitoring_enabled)
        
        # 禁用监控
        result = self.watcher.disable_monitoring()
        self.assertTrue(result)
        self.assertFalse(self.watcher.monitoring_enabled)
        
        # 再次禁用应该返回False
        result = self.watcher.disable_monitoring()
        self.assertFalse(result)
        
        # 启用监控
        result = self.watcher.enable_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.watcher.monitoring_enabled)
        
        # 再次启用应该返回False
        result = self.watcher.enable_monitoring()
        self.assertFalse(result)
    
    def test_restart_monitoring(self):
        """测试重启监控"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "restart_test.txt")
        with open(test_file, 'w') as f:
            f.write("test")
        
        # 添加文件并启动监控
        self.watcher.add_file(test_file)
        self.watcher.start()
        self.assertTrue(self.watcher.is_running)
        
        # 重启监控
        result = self.watcher.restart_monitoring()
        self.assertTrue(result)
        self.assertTrue(self.watcher.is_running)
        
        # 验证错误计数被重置
        self.assertEqual(self.watcher.error_count, 0)
    
    def test_flush_pending_changes_error_handling(self):
        """测试刷新待处理变化的错误处理"""
        # 模拟handler存在但debouncer出错的情况
        self.watcher.handler = Mock()
        self.watcher.handler.debouncer = Mock()
        self.watcher.handler.debouncer.flush.side_effect = Exception("刷新失败")
        
        # 尝试刷新
        result = self.watcher.flush_pending_changes()
        
        # 验证返回False
        self.assertFalse(result)
        
        # 验证错误回调被调用
        self.error_callback.assert_called()
        error_args = self.error_callback.call_args[0]
        self.assertEqual(error_args[1], "flush_changes_failed")
    
    @patch('core.file_watcher.Observer')
    def test_observer_start_failure(self, mock_observer):
        """测试Observer启动失败"""
        # 模拟Observer启动失败
        mock_observer.return_value.start.side_effect = Exception("启动失败")
        
        # 创建新的监控器
        watcher = FileWatcher(self.callback, self.error_callback)
        
        # 尝试启动
        result = watcher.start()
        
        # 验证启动失败
        self.assertFalse(result)
        
        # 验证错误回调被调用
        self.error_callback.assert_called()
        error_args = self.error_callback.call_args[0]
        self.assertEqual(error_args[1], "observer_start_failed")
        
        # 清理
        watcher.stop()
    
    def test_clear_monitoring_error_handling(self):
        """测试清空监控的错误处理"""
        # 模拟清空过程中的错误
        with patch.object(self.watcher, 'stop', side_effect=Exception("停止失败")):
            # 尝试清空
            result = self.watcher.clear()
            
            # 验证返回False
            self.assertFalse(result)
            
            # 验证错误回调被调用
            self.error_callback.assert_called()
            error_args = self.error_callback.call_args[0]
            self.assertEqual(error_args[1], "clear_monitoring_failed")


class TestFileWatcherErrorIntegration(unittest.TestCase):
    """FileWatcher错误处理集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.errors_received = []
        self.error_lock = threading.Lock()
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def error_callback(self, error_message: str, error_type: str, exception=None):
        """错误回调函数"""
        with self.error_lock:
            self.errors_received.append({
                'message': error_message,
                'type': error_type,
                'exception': exception
            })
    
    def file_change_callback(self, event_type: str, file_path: str):
        """文件变化回调"""
        pass  # 不需要处理文件变化
    
    def test_real_error_scenarios(self):
        """测试真实错误场景"""
        watcher = FileWatcher(self.file_change_callback, self.error_callback)
        
        try:
            # 测试添加不存在的文件
            nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
            result = watcher.add_file(nonexistent_file)
            self.assertFalse(result)
            
            # 测试启动监控时的错误处理
            watcher.monitoring_enabled = False
            result = watcher.start()
            self.assertFalse(result)
            
            # 验证错误被记录
            with self.error_lock:
                self.assertGreater(len(self.errors_received), 0)
                
                error_types = [error['type'] for error in self.errors_received]
                self.assertIn('file_not_found', error_types)
                self.assertIn('monitoring_disabled', error_types)
        
        finally:
            watcher.stop()
    
    def test_error_recovery(self):
        """测试错误恢复"""
        watcher = FileWatcher(self.file_change_callback, self.error_callback)
        
        try:
            # 触发一些错误
            for i in range(3):
                watcher._handle_error(f"错误 {i+1}", "test_error")
            
            # 验证监控被禁用
            self.assertFalse(watcher.monitoring_enabled)
            
            # 重新启用监控
            result = watcher.enable_monitoring()
            self.assertTrue(result)
            self.assertTrue(watcher.monitoring_enabled)
            
            # 验证错误计数被重置
            self.assertEqual(watcher.error_count, 0)
        
        finally:
            watcher.stop()


if __name__ == '__main__':
    unittest.main()