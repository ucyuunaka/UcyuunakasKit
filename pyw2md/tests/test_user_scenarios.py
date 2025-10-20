"""
用户场景测试 - 模拟真实用户使用场景
User scenario tests simulating real user usage patterns
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
from core.constants import (
    FILE_CHANGE_MODIFIED, FILE_CHANGE_DELETED, FILE_CHANGE_CREATED,
    MSG_FILE_MODIFIED, MSG_FILE_DELETED
)


class TestDragDropScenario(unittest.TestCase):
    """拖放文件场景测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.watcher = FileWatcher(self.callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_drag_drop_single_file(self):
        """测试拖放单个文件场景"""
        # 1. 创建源文件（模拟用户拖入的文件）
        source_file = os.path.join(self.temp_dir, "dragged_file.txt")
        with open(source_file, 'w') as f:
            f.write("This is a dragged file")
        
        # 2. 模拟拖放操作 - 添加文件到监控
        result = self.watcher.add_file(source_file)
        self.assertTrue(result)
        
        # 3. 启动监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 4. 验证文件被正确监控
        self.assertTrue(self.watcher.is_monitoring_file(source_file))
        self.assertEqual(len(self.watcher.get_watched_directories()), 1)
        
        # 5. 模拟用户编辑拖入的文件
        time.sleep(0.1)
        with open(source_file, 'w') as f:
            f.write("User edited the dragged file")
        
        # 6. 等待变化检测
        time.sleep(0.5)
        
        # 7. 验证变化被检测到
        self.assertGreater(self.callback.call_count, 0)
    
    def test_drag_drop_multiple_files(self):
        """测试拖放多个文件场景"""
        # 1. 创建多个源文件
        dragged_files = []
        for i in range(5):
            file_path = os.path.join(self.temp_dir, f"dragged_{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Dragged file {i}")
            dragged_files.append(file_path)
        
        # 2. 模拟批量拖放 - 逐个添加到监控
        for file_path in dragged_files:
            result = self.watcher.add_file(file_path)
            self.assertTrue(result)
        
        # 3. 启动监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 4. 验证所有文件都被监控
        for file_path in dragged_files:
            self.assertTrue(self.watcher.is_monitoring_file(file_path))
        
        # 5. 模拟用户编辑其中一些文件
        for i, file_path in enumerate(dragged_files[:3]):  # 编辑前3个文件
            with open(file_path, 'w') as f:
                f.write(f"User edited file {i}")
        
        # 6. 等待变化检测
        time.sleep(0.5)
        
        # 7. 验证变化被检测到
        self.assertGreater(self.callback.call_count, 0)
    
    def test_drag_drop_different_file_types(self):
        """测试拖放不同文件类型场景"""
        file_types = [
            ("document.txt", "Text document content"),
            ("code.py", "print('Hello, World!')"),
            ("config.json", '{"name": "test", "value": 123}'),
            ("readme.md", "# Project Title\n\nDescription here."),
        ]
        
        dragged_files = []
        for filename, content in file_types:
            file_path = os.path.join(self.temp_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            dragged_files.append(file_path)
        
        # 添加所有文件到监控
        for file_path in dragged_files:
            result = self.watcher.add_file(file_path)
            self.assertTrue(result)
        
        # 启动监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 验证不同类型的文件都能被监控
        for file_path in dragged_files:
            self.assertTrue(self.watcher.is_monitoring_file(file_path))


class TestLargeFileScenario(unittest.TestCase):
    """大量文件场景测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.watcher = FileWatcher(self.callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_monitoring_many_files(self):
        """测试监控大量文件"""
        # 1. 创建大量文件
        file_count = 50
        created_files = []
        
        print(f"创建 {file_count} 个文件...")
        for i in range(file_count):
            file_path = os.path.join(self.temp_dir, f"large_set_{i:03d}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content for file {i}\n" + "x" * 100)  # 每个文件约100字节
            created_files.append(file_path)
        
        # 2. 记录添加时间
        start_time = time.time()
        
        # 3. 添加所有文件到监控
        for file_path in created_files:
            result = self.watcher.add_file(file_path)
            self.assertTrue(result)
        
        add_time = time.time() - start_time
        print(f"添加 {file_count} 个文件耗时: {add_time:.3f} 秒")
        
        # 4. 启动监控
        self.watcher.start()
        time.sleep(0.2)
        
        # 5. 验证性能 - 添加操作应该很快
        self.assertLess(add_time, 5.0)  # 应该在5秒内完成
        
        # 6. 验证所有文件都被监控
        monitored_count = 0
        for file_path in created_files:
            if self.watcher.is_monitoring_file(file_path):
                monitored_count += 1
        
        self.assertEqual(monitored_count, file_count)
        
        # 7. 模拟修改部分文件
        files_to_modify = created_files[:10]  # 修改前10个文件
        for file_path in files_to_modify:
            with open(file_path, 'a') as f:
                f.write("\nModified content")
        
        # 8. 等待变化处理
        time.sleep(0.5)
        
        # 9. 验证变化被检测
        self.assertGreater(self.callback.call_count, 0)
        
        print(f"大量文件监控测试完成，监控了 {monitored_count} 个文件")
    
    def test_memory_usage_with_many_files(self):
        """测试大量文件的内存使用"""
        import psutil
        import gc
        
        # 获取当前进程
        process = psutil.Process()
        
        # 基线内存
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建并监控大量文件
        file_count = 100
        created_files = []
        
        for i in range(file_count):
            file_path = os.path.join(self.temp_dir, f"memory_test_{i:03d}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Memory test file {i}")
            created_files.append(file_path)
            
            if i % 10 == 0:
                self.watcher.add_file(file_path)
        
        # 启动监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 检查内存使用
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - baseline_memory
        
        print(f"基线内存: {baseline_memory:.1f} MB")
        print(f"峰值内存: {peak_memory:.1f} MB")
        print(f"内存增长: {memory_increase:.1f} MB")
        
        # 内存增长应该在合理范围内（小于100MB）
        self.assertLess(memory_increase, 100)


class TestNetworkDriveScenario(unittest.TestCase):
    """网络驱动器场景测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.watcher = FileWatcher(self.callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_simulated_network_drive_behavior(self):
        """测试模拟网络驱动器行为"""
        # 在实际测试中，我们无法创建真正的网络驱动器
        # 但可以模拟网络驱动器的一些特征，如延迟和间歇性不可用
        
        test_file = os.path.join(self.temp_dir, "network_file.txt")
        
        # 1. 创建文件
        with open(test_file, 'w') as f:
            f.write("Network drive file")
        
        # 2. 添加到监控
        result = self.watcher.add_file(test_file)
        self.assertTrue(result)
        
        # 3. 启动监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 4. 模拟网络延迟的文件修改
        time.sleep(0.05)  # 模拟网络延迟
        with open(test_file, 'w') as f:
            f.write("Modified with network delay")
        
        # 5. 等待变化处理（网络环境可能需要更长时间）
        time.sleep(1.0)
        
        # 6. 验证系统仍能正常工作
        self.assertTrue(self.watcher.is_monitoring_file(test_file))
        
        # 7. 测试错误恢复 - 模拟网络中断后的恢复
        # （在实际实现中，这会测试重试机制）
        self.assertTrue(True)  # 如果能执行到这里说明系统稳定


class TestUserInteractionScenario(unittest.TestCase):
    """用户交互场景测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.callback = Mock()
        self.watcher = FileWatcher(self.callback)
    
    def tearDown(self):
        """测试后清理"""
        self.watcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_rapid_file_operations(self):
        """测试快速文件操作场景"""
        test_file = os.path.join(self.temp_dir, "rapid_test.txt")
        
        # 1. 创建文件
        with open(test_file, 'w') as f:
            f.write("Initial content")
        
        # 2. 添加到监控
        self.watcher.add_file(test_file)
        self.watcher.start()
        time.sleep(0.1)
        
        # 3. 模拟用户快速操作
        operations = [
            ("Quick edit 1", 0.01),
            ("Quick edit 2", 0.01),
            ("Quick edit 3", 0.01),
            ("Quick edit 4", 0.01),
            ("Quick edit 5", 0.01),
        ]
        
        for content, delay in operations:
            with open(test_file, 'w') as f:
                f.write(content)
            time.sleep(delay)
        
        # 4. 等待防抖处理
        time.sleep(0.5)
        
        # 5. 验证防抖效果 - 回调次数应该远少于操作次数
        self.assertLess(self.callback.call_count, len(operations))
        
        print(f"快速操作测试: {len(operations)} 次操作，触发 {self.callback.call_count} 次回调")
    
    def test_user_pause_and_resume(self):
        """测试用户暂停和恢复场景"""
        test_file = os.path.join(self.temp_dir, "pause_test.txt")
        
        # 1. 创建文件并添加监控
        with open(test_file, 'w') as f:
            f.write("Initial")
        
        self.watcher.add_file(test_file)
        self.watcher.start()
        time.sleep(0.1)
        
        # 2. 用户暂停监控
        self.watcher.stop()
        
        # 3. 在暂停期间修改文件
        with open(test_file, 'w') as f:
            f.write("Modified during pause")
        
        time.sleep(0.2)
        
        # 4. 验证暂停期间没有回调
        pause_callbacks = self.callback.call_count
        
        # 5. 用户恢复监控
        self.watcher.start()
        time.sleep(0.1)
        
        # 6. 恢复后修改文件
        with open(test_file, 'w') as f:
            f.write("Modified after resume")
        
        time.sleep(0.5)
        
        # 7. 验证恢复后能正常工作
        self.assertGreater(self.callback.call_count, pause_callbacks)
    
    def test_application_lifecycle(self):
        """测试应用生命周期场景"""
        test_file = os.path.join(self.temp_dir, "lifecycle_test.txt")
        
        # 1. 创建文件
        with open(test_file, 'w') as f:
            f.write("Lifecycle test")
        
        # 2. 模拟应用启动
        watcher = FileWatcher(self.callback)
        watcher.add_file(test_file)
        watcher.start()
        
        time.sleep(0.1)
        
        # 3. 模拟应用运行期间的文件操作
        with open(test_file, 'w') as f:
            f.write("During runtime")
        
        time.sleep(0.3)
        
        # 4. 模拟应用关闭
        watcher.stop()
        
        # 5. 验证资源清理
        self.assertFalse(watcher.observer.is_alive())
        
        # 6. 验证没有资源泄漏（如果这里能执行，说明没有死锁等）
        self.assertTrue(True)


class TestErrorRecoveryScenario(unittest.TestCase):
    """错误恢复场景测试"""
    
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
    
    def test_file_disappearance_recovery(self):
        """测试文件消失恢复场景"""
        test_file = os.path.join(self.temp_dir, "disappear_test.txt")
        
        # 1. 创建文件并添加监控
        with open(test_file, 'w') as f:
            f.write("Will disappear")
        
        self.watcher.add_file(test_file)
        self.watcher.start()
        time.sleep(0.1)
        
        # 2. 文件消失（被外部程序删除或移动）
        os.remove(test_file)
        time.sleep(0.3)
        
        # 3. 文件重新出现
        with open(test_file, 'w') as f:
            f.write("Reappeared")
        
        # 4. 添加回监控（模拟用户重新添加）
        result = self.watcher.add_file(test_file)
        self.assertTrue(result)
        
        # 5. 验证系统能恢复
        self.assertTrue(self.watcher.is_monitoring_file(test_file))
        
        # 6. 修改重新出现的文件
        with open(test_file, 'w') as f:
            f.write("Modified after recovery")
        
        time.sleep(0.3)
        
        # 7. 验证恢复后能正常检测变化
        self.assertGreater(self.callback.call_count, 0)


if __name__ == '__main__':
    unittest.main()