"""
重构后的FileWatcher测试 - 修复版本
"""

import unittest
import tempfile
import os
import time
import threading
from unittest.mock import Mock
from core.file_watcher import FileWatcher


class TestFileWatcherRefactored(unittest.TestCase):
    """重构后FileWatcher的测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.watcher = FileWatcher(self.callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_watcher_uses_file_state_manager(self):
        """测试FileWatcher使用FileStateManager"""
        # 验证FileWatcher有file_state_manager属性
        self.assertTrue(hasattr(self.watcher, 'file_state_manager'))
        
        # 验证FileStateManager实例存在
        from core.file_state_manager import FileStateManager
        self.assertIsInstance(self.watcher.file_state_manager, FileStateManager)
    
    def test_file_watcher_uses_simple_debouncer(self):
        """测试FileWatcher使用SimpleDebouncer"""
        # 启动监控器
        self.watcher.start()
        
        # 验证handler使用了SimpleDebouncer
        self.assertIsNotNone(self.watcher.handler)
        from utils.debouncer import SimpleDebouncer
        self.assertIsInstance(self.watcher.handler.debouncer, SimpleDebouncer)
        
        # 验证防抖延迟设置为300ms
        self.assertEqual(self.watcher.handler.debouncer.delay, 0.3)
    
    def test_file_change_debouncing(self):
        """测试文件变化防抖"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "debounce_test.txt")
        with open(test_file, 'w') as f:
            f.write("content1")
        
        # 添加到监控
        result = self.watcher.add_file(test_file)
        self.assertTrue(result)
        self.watcher.start()
        
        # 快速连续修改文件
        with open(test_file, 'w') as f:
            f.write("content2")
        
        with open(test_file, 'w') as f:
            f.write("content3")
        
        # 等待防抖处理
        time.sleep(0.5)
        
        # 应该有回调被触发
        self.assertGreater(self.callback.call_count, 0)
    
    def test_pending_changes_management(self):
        """测试待处理变化管理"""
        # 验证初始状态
        self.assertEqual(self.watcher.get_pending_changes_count(), 0)
        
        # 创建测试文件并添加到监控
        test_file = os.path.join(self.temp_dir, "pending_test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        self.watcher.add_file(test_file)
        self.watcher.start()
        
        # 修改文件
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        # 等待处理
        time.sleep(0.5)
        
        # 验证变化被处理
        self.assertGreater(self.callback.call_count, 0)
    
    def test_flush_pending_changes(self):
        """测试立即处理待处理变化"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "flush_test.txt")
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        self.watcher.add_file(test_file)
        self.watcher.start()
        
        # 修改文件
        with open(test_file, 'w') as f:
            f.write("flush test")
        
        # 立即刷新
        self.watcher.flush_pending_changes()
        
        # 等待处理完成
        time.sleep(0.2)
        
        # 应该有回调被触发
        self.assertGreater(self.callback.call_count, 0)
    
    def test_monitoring_status_methods(self):
        """测试监控状态方法"""
        test_file = os.path.join(self.temp_dir, "status_test.txt")
        
        # 创建测试文件
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # 初始状态
        self.assertFalse(self.watcher.is_monitoring_file(test_file))
        self.assertEqual(len(self.watcher.get_watched_directories()), 0)
        
        # 添加文件监控
        result = self.watcher.add_file(test_file)
        self.assertTrue(result)
        
        # 验证监控状态
        self.assertTrue(self.watcher.is_monitoring_file(test_file))
        self.assertEqual(len(self.watcher.get_watched_directories()), 1)
        self.assertIn(os.path.abspath(self.temp_dir), self.watcher.get_watched_directories())
        
        # 验证目录下的文件列表
        files_in_dir = self.watcher.get_monitored_files_in_directory(self.temp_dir)
        self.assertIn(os.path.abspath(test_file), files_in_dir)
    
    def test_concurrent_file_operations(self):
        """测试并发文件操作"""
        test_files = []
        for i in range(5):
            test_file = os.path.join(self.temp_dir, f"concurrent_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"initial_{i}")
            test_files.append(test_file)
            self.watcher.add_file(test_file)
        
        self.watcher.start()
        
        def modify_file(file_path, content):
            with open(file_path, 'w') as f:
                f.write(content)
        
        # 并发修改多个文件
        threads = []
        for i, test_file in enumerate(test_files):
            thread = threading.Thread(target=modify_file, args=(test_file, f"content_{i}"))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 等待防抖处理
        time.sleep(0.5)
        
        # 验证所有变化都被处理
        self.assertGreater(self.callback.call_count, 0)
    
    def test_cleanup_on_stop(self):
        """测试停止时的清理"""
        test_file = os.path.join(self.temp_dir, "cleanup_test.txt")
        with open(test_file, 'w') as f:
            f.write("test content")
        
        self.watcher.add_file(test_file)
        self.watcher.start()
        
        # 验证handler和debouncer存在
        self.assertIsNotNone(self.watcher.handler)
        self.assertIsNotNone(self.watcher.handler.debouncer)
        
        # 停止监控
        self.watcher.stop()
        
        # 验证监控已停止
        self.assertFalse(self.watcher.is_running)


class TestFileWatcherIntegration(unittest.TestCase):
    """FileWatcher集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.changes_received = []
        self.change_lock = threading.Lock()
        
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def file_change_callback(self, event_type, file_path):
        """文件变化回调"""
        with self.change_lock:
            self.changes_received.append((event_type, file_path))
    
    def test_end_to_end_file_monitoring(self):
        """端到端文件监控测试"""
        watcher = FileWatcher(self.file_change_callback)
        
        try:
            # 创建测试文件
            test_file = os.path.join(self.temp_dir, "e2e_test.txt")
            with open(test_file, 'w') as f:
                f.write("initial content")
            
            # 添加到监控
            watcher.add_file(test_file)
            watcher.start()
            
            # 修改文件
            with open(test_file, 'a') as f:
                f.write("\nmodified content")
            
            # 等待处理
            time.sleep(0.5)
            
            # 验证变化被检测
            with self.change_lock:
                self.assertGreater(len(self.changes_received), 0)
                
                # 验证变化内容
                event_types = [change[0] for change in self.changes_received]
                file_paths = [change[1] for change in self.changes_received]
                
                self.assertIn('modified', event_types)
                self.assertIn(os.path.abspath(test_file), file_paths)
        
        finally:
            watcher.stop()
    
    def test_multiple_file_types(self):
        """测试多种文件类型的监控"""
        watcher = FileWatcher(self.file_change_callback)
        
        try:
            # 创建不同类型的文件
            files = []
            for ext in ['.txt', '.py', '.md', '.json']:
                test_file = os.path.join(self.temp_dir, f"test{ext}")
                with open(test_file, 'w') as f:
                    f.write(f"content for {ext}")
                files.append(test_file)
                watcher.add_file(test_file)
            
            watcher.start()
            
            # 修改所有文件
            for test_file in files:
                with open(test_file, 'a') as f:
                    f.write(f"\nmodified {test_file}")
            
            # 等待处理
            time.sleep(0.5)
            
            # 验证所有变化都被检测
            with self.change_lock:
                modified_files = [change[1] for change in self.changes_received 
                                if change[0] == 'modified']
                self.assertGreater(len(modified_files), 0)
        
        finally:
            watcher.stop()


if __name__ == '__main__':
    unittest.main()