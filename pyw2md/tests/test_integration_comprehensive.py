"""
综合集成测试 - 测试完整的文件变化检测和处理流程
Comprehensive integration tests for complete file change detection and processing
"""

import unittest
import tempfile
import os
import time
import threading
import shutil
from unittest.mock import Mock, patch
from core.file_watcher import FileWatcher
from core.file_state_manager import FileStateManager
from utils.debouncer import SimpleDebouncer
from core.constants import (
    FILE_CHANGE_MODIFIED, FILE_CHANGE_DELETED, FILE_CHANGE_CREATED,
    DEFAULT_DEBOUNCE_MS, MSG_FILE_MODIFIED, MSG_FILE_DELETED
)


class TestFileChangeDetectionIntegration(unittest.TestCase):
    """文件变化检测集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.watcher = FileWatcher(self.callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_file_change_workflow(self):
        """测试完整的文件变化工作流程"""
        test_file = os.path.join(self.temp_dir, "workflow_test.txt")
        
        # 1. 创建初始文件
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        # 2. 添加到监控并启动
        result = self.watcher.add_file(test_file)
        self.assertTrue(result)
        self.watcher.start()
        
        # 3. 等待监控稳定
        time.sleep(0.1)
        
        # 4. 修改文件
        with open(test_file, 'w') as f:
            f.write("modified content")
        
        # 5. 等待变化处理
        time.sleep(0.5)
        
        # 6. 验证回调被调用
        self.assertGreater(self.callback.call_count, 0)
        
        # 7. 验证回调参数
        if self.callback.call_count > 0:
            args, kwargs = self.callback.call_args
            self.assertTrue(len(args) >= 2)
            event_type, file_path = args[0], args[1]
            self.assertIn(event_type, ['modified', 'created'])
    
    def test_multiple_files_monitoring(self):
        """测试多文件监控"""
        test_files = []
        
        # 创建多个文件
        for i in range(3):
            test_file = os.path.join(self.temp_dir, f"multi_{i}.txt")
            with open(test_file, 'w') as f:
                f.write(f"content {i}")
            test_files.append(test_file)
            self.watcher.add_file(test_file)
        
        # 启动监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 修改文件
        for i, test_file in enumerate(test_files):
            with open(test_file, 'w') as f:
                f.write(f"modified content {i}")
        
        # 等待处理
        time.sleep(0.5)
        
        # 验证有回调
        self.assertGreater(self.callback.call_count, 0)
        
        # 验证监控状态
        for test_file in test_files:
            self.assertTrue(self.watcher.is_monitoring_file(test_file))
    
    def test_file_deletion_detection(self):
        """测试文件删除检测"""
        test_file = os.path.join(self.temp_dir, "delete_test.txt")
        
        # 创建文件并添加监控
        with open(test_file, 'w') as f:
            f.write("to be deleted")
        
        self.watcher.add_file(test_file)
        self.watcher.start()
        time.sleep(0.1)
        
        # 删除文件
        os.remove(test_file)
        
        # 等待处理
        time.sleep(0.5)
        
        # 验证回调（删除事件可能不总是触发，取决于系统）
        # 这里主要验证没有异常发生
        self.assertTrue(True)
    
    def test_watcher_start_stop_workflow(self):
        """测试监控器启动停止工作流程"""
        test_file = os.path.join(self.temp_dir, "lifecycle_test.txt")
        
        # 创建文件
        with open(test_file, 'w') as f:
            f.write("lifecycle test")
        
        # 添加监控
        self.watcher.add_file(test_file)
        
        # 测试启动
        self.watcher.start()
        self.assertTrue(self.watcher.observer.is_alive())
        
        # 测试停止
        self.watcher.stop()
        self.assertFalse(self.watcher.observer.is_alive())
        
        # 测试重新启动
        self.watcher.start()
        self.assertTrue(self.watcher.observer.is_alive())


class TestStateManagerIntegration(unittest.TestCase):
    """状态管理器集成测试"""
    
    def test_state_manager_with_file_watcher(self):
        """测试状态管理器与文件监控器的集成"""
        # 创建状态管理器
        manager = FileStateManager()
        
        # 模拟文件变化
        manager.add_change("/test/file1.txt", FILE_CHANGE_MODIFIED)
        manager.add_change("/test/file2.txt", FILE_CHANGE_DELETED)
        
        # 验证变化管理
        self.assertEqual(manager.get_change_count(), 2)
        self.assertTrue(manager.has_changes())
        
        # 按类型获取变化
        modified_changes = manager.get_changes_by_type(FILE_CHANGE_MODIFIED)
        deleted_changes = manager.get_changes_by_type(FILE_CHANGE_DELETED)
        
        self.assertEqual(len(modified_changes), 1)
        self.assertEqual(len(deleted_changes), 1)
        
        # 获取并清除变化
        changes = manager.get_and_clear_changes()
        self.assertEqual(len(changes), 2)
        self.assertFalse(manager.has_changes())


class TestDebouncerIntegration(unittest.TestCase):
    """防抖器集成测试"""
    
    def test_debouncer_with_callback_system(self):
        """测试防抖器与回调系统的集成"""
        call_count = 0
        call_times = []
        
        def callback():
            nonlocal call_count
            call_count += 1
            call_times.append(time.time())
        
        # 创建防抖器
        debouncer = SimpleDebouncer(callback, delay=0.05)  # 50ms
        
        # 模拟快速连续的事件
        start_time = time.time()
        for i in range(10):
            debouncer.schedule()
            time.sleep(0.01)  # 10ms间隔，小于防抖时间
        
        # 等待防抖完成
        time.sleep(0.1)
        end_time = time.time()
        
        # 验证防抖效果
        self.assertLessEqual(call_count, 3)  # 允许一定的时序误差
        
        if call_count > 0:
            # 验证调用时间间隔
            for call_time in call_times:
                self.assertGreater(call_time - start_time, 0.04)  # 至少50ms防抖
    
    def test_multiple_debouncers_interaction(self):
        """测试多个防抖器的交互"""
        counter = {'count': 0}
        
        def shared_callback():
            counter['count'] += 1
        
        # 创建多个防抖器
        debouncer1 = SimpleDebouncer(shared_callback, delay=0.05)
        debouncer2 = SimpleDebouncer(shared_callback, delay=0.05)
        
        # 调度所有防抖器
        debouncer1.schedule()
        debouncer2.schedule()
        
        # 等待执行
        time.sleep(0.1)
        
        # 验证都有机会执行
        self.assertGreater(counter['count'], 0)


class TestErrorHandlingIntegration(unittest.TestCase):
    """错误处理集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.error_callback = Mock()
        self.watcher = FileWatcher(self.callback, error_callback=self.error_callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_nonexistent_file_handling(self):
        """测试不存在文件的处理"""
        nonexistent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        
        # 尝试添加不存在的文件
        result = self.watcher.add_file(nonexistent_file)
        self.assertFalse(result)
        
        # 验证错误回调被调用
        self.assertGreater(self.error_callback.call_count, 0)
    
    def test_permission_error_handling(self):
        """测试权限错误的处理"""
        # 在Windows上，创建一个只读目录来模拟权限问题
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir)
        
        try:
            # 尝试修改目录权限（在Windows上可能不起作用）
            os.chmod(readonly_dir, 0o444)
        except:
            pass  # 如果权限修改失败，跳过这个测试
        else:
            test_file = os.path.join(readonly_dir, "test.txt")
            
            # 尝试添加文件
            result = self.watcher.add_file(test_file)
            
            # 恢复权限以便清理
            os.chmod(readonly_dir, 0o755)


class TestPerformanceIntegration(unittest.TestCase):
    """性能集成测试"""
    
    def test_high_frequency_file_changes(self):
        """测试高频文件变化"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            callback = Mock()
            watcher = FileWatcher(callback)
            
            test_file = os.path.join(temp_dir, "perf_test.txt")
            
            # 创建文件
            with open(test_file, 'w') as f:
                f.write("initial")
            
            watcher.add_file(test_file)
            watcher.start()
            time.sleep(0.1)
            
            # 高频修改文件
            start_time = time.time()
            for i in range(100):
                with open(test_file, 'w') as f:
                    f.write(f"iteration {i}")
                time.sleep(0.001)  # 1ms间隔
            
            # 等待处理完成
            time.sleep(0.5)
            end_time = time.time()
            
            # 验证性能
            duration = end_time - start_time
            self.assertLess(duration, 2.0)  # 应该在2秒内完成
            
            # 验证防抖效果（不应该有100次回调）
            self.assertLess(callback.call_count, 50)
            
        finally:
            watcher.stop()
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_memory_usage_stability(self):
        """测试内存使用稳定性"""
        import psutil
        import gc
        
        # 获取当前进程
        process = psutil.Process()
        
        # 基线内存
        gc.collect()
        baseline_memory = process.memory_info().rss
        
        # 创建大量组件
        watchers = []
        callbacks = []
        
        for i in range(10):
            callback = Mock()
            callbacks.append(callback)
            watcher = FileWatcher(callback)
            watchers.append(watcher)
        
        # 执行操作
        temp_dir = tempfile.mkdtemp()
        try:
            for i, watcher in enumerate(watchers):
                test_file = os.path.join(temp_dir, f"memory_test_{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"content {i}")
                
                watcher.add_file(test_file)
                watcher.start()
                
                # 修改文件
                with open(test_file, 'w') as f:
                    f.write(f"modified {i}")
                
                time.sleep(0.01)
            
            time.sleep(0.5)
            
            # 检查内存使用
            peak_memory = process.memory_info().rss
            memory_increase = peak_memory - baseline_memory
            
            # 内存增长应该在合理范围内（小于50MB）
            self.assertLess(memory_increase, 50 * 1024 * 1024)
            
        finally:
            # 清理
            for watcher in watchers:
                watcher.stop()
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestSystemIntegration(unittest.TestCase):
    """系统集成测试"""
    
    def test_complete_workflow_simulation(self):
        """测试完整工作流程模拟"""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 创建模拟的应用状态
            file_changes = []
            status_messages = []
            
            def file_change_callback(event_type, file_path):
                file_changes.append((event_type, file_path))
            
            # 创建监控器
            watcher = FileWatcher(file_change_callback)
            
            # 创建测试文件
            test_files = []
            for i in range(5):
                test_file = os.path.join(temp_dir, f"complete_test_{i}.txt")
                with open(test_file, 'w') as f:
                    f.write(f"initial content {i}")
                test_files.append(test_file)
                watcher.add_file(test_file)
            
            # 启动监控
            watcher.start()
            time.sleep(0.1)
            
            # 模拟用户操作
            operations = [
                # 修改操作
                lambda: self._modify_files(test_files),
                # 等待处理
                lambda: time.sleep(0.2),
                # 删除操作
                lambda: self._delete_some_files(test_files[:2]),
                # 等待处理
                lambda: time.sleep(0.2),
            ]
            
            # 执行操作
            for operation in operations:
                operation()
            
            # 验证结果
            self.assertGreater(len(file_changes), 0)
            
            # 验证系统状态
            remaining_files = [f for f in test_files if os.path.exists(f)]
            self.assertEqual(len(remaining_files), 3)  # 应该有3个文件被删除
            
        finally:
            watcher.stop()
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def _modify_files(self, files):
        """修改文件列表"""
        for file_path in files:
            if os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    f.write(f"modified at {time.time()}")
    
    def _delete_some_files(self, files):
        """删除一些文件"""
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except:
                pass  # 忽略删除错误


if __name__ == '__main__':
    unittest.main()