"""
集成测试 - 测试FileStateManager和SimpleDebouncer的协作
"""

import unittest
import time
import threading
import tempfile
import os
from core.file_state_manager import FileStateManager
from utils.debouncer import SimpleDebouncer, DebouncerGroup


class TestIntegration(unittest.TestCase):
    """集成测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.file_manager = FileStateManager()
        self.debouncer_group = DebouncerGroup()
        self.processed_changes = []
        self.process_lock = threading.Lock()
    
    def process_changes(self, *args, **kwargs):
        """处理文件变化的回调函数"""
        with self.process_lock:
            changes = self.file_manager.get_and_clear_changes()
            self.processed_changes.extend(changes)
    
    def test_file_change_debouncing_integration(self):
        """测试文件变化与防抖机制的集成"""
        # 创建防抖器
        debouncer = self.debouncer_group.create_debouncer(
            "file_processor", 
            self.process_changes, 
            delay=0.1
        )
        
        # 模拟快速连续的文件变化
        for i in range(10):
            self.file_manager.add_change(f"test_{i}.txt", "modified")
            debouncer.schedule()
        
        # 立即检查应该没有处理变化
        self.assertEqual(len(self.processed_changes), 0)
        
        # 等待防抖延迟
        time.sleep(0.2)
        
        # 检查变化应该被处理
        self.assertGreater(len(self.processed_changes), 0)
        self.assertEqual(self.file_manager.get_change_count(), 0)
    
    def test_concurrent_file_operations(self):
        """测试并发文件操作"""
        def add_file_changes(thread_id):
            for i in range(10):
                self.file_manager.add_change(f"file_{thread_id}_{i}.txt", "modified")
                time.sleep(0.001)  # 短暂延迟
        
        def schedule_processing():
            debouncer = self.debouncer_group.get_debouncer("file_processor")
            if debouncer:
                debouncer.schedule()
        
        # 创建防抖器
        debouncer = self.debouncer_group.create_debouncer(
            "file_processor",
            self.process_changes,
            delay=0.2
        )
        
        # 创建多个线程添加文件变化
        threads = []
        for i in range(3):
            thread = threading.Thread(target=add_file_changes, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 同时调度处理
        for _ in range(10):
            threading.Thread(target=schedule_processing).start()
            time.sleep(0.01)
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 等待防抖延迟
        time.sleep(0.3)
        
        # 验证所有变化都被处理
        self.assertEqual(len(self.processed_changes), 30)  # 3线程 × 10变化
        self.assertEqual(self.file_manager.get_change_count(), 0)
    
    def test_mixed_change_types(self):
        """测试混合变化类型"""
        debouncer = self.debouncer_group.create_debouncer(
            "mixed_processor",
            self.process_changes,
            delay=0.1
        )
        
        # 添加不同类型的变化
        self.file_manager.add_change("test1.txt", "modified")
        self.file_manager.add_change("test2.txt", "deleted")
        self.file_manager.add_change("test3.txt", "modified")
        
        # 调度处理
        debouncer.schedule()
        
        # 等待处理完成
        time.sleep(0.2)
        
        # 验证变化处理
        self.assertEqual(len(self.processed_changes), 3)
        
        # 检查变化类型
        change_types = [change.change_type for change in self.processed_changes]
        self.assertEqual(change_types.count("modified"), 2)
        self.assertEqual(change_types.count("deleted"), 1)
        
        # 验证文件状态已清空
        self.assertEqual(self.file_manager.get_change_count(), 0)
    
    def test_performance_under_load(self):
        """测试高负载下的性能"""
        debouncer = self.debouncer_group.create_debouncer(
            "performance_processor",
            self.process_changes,
            delay=0.1
        )
        
        start_time = time.time()
        
        # 大量文件变化
        for i in range(1000):
            self.file_manager.add_change(f"perf_test_{i}.txt", "modified")
            if i % 10 == 0:  # 每10个变化调度一次处理
                debouncer.schedule()
        
        # 最后调度一次处理剩余的变化
        debouncer.schedule()
        
        # 等待处理完成
        time.sleep(0.2)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 验证所有变化都被处理
        self.assertEqual(len(self.processed_changes), 1000)
        self.assertEqual(self.file_manager.get_change_count(), 0)
        
        # 性能应该在合理范围内（这里设置为5秒）
        self.assertLess(duration, 5.0)
        print(f"处理1000个变化耗时: {duration:.3f}秒")
    
    def test_cleanup_and_resource_management(self):
        """测试清理和资源管理"""
        # 创建多个防抖器
        for i in range(5):
            self.debouncer_group.create_debouncer(
                f"clean_test_{i}",
                lambda: None,
                delay=0.1
            )
        
        # 检查防抖器已创建
        status = self.debouncer_group.get_status()
        self.assertEqual(len(status), 5)
        
        # 清理所有防抖器
        self.debouncer_group.clear_all()
        
        # 检查状态已清空
        status = self.debouncer_group.get_status()
        self.assertEqual(len(status), 0)
        
        # 测试文件管理器清理
        self.file_manager.add_change("cleanup_test.txt", "modified")
        self.assertEqual(self.file_manager.get_change_count(), 1)
        
        self.file_manager.clear_changes()
        self.assertEqual(self.file_manager.get_change_count(), 0)
        
        # 测试过期变化清理
        self.file_manager.add_change("old_test.txt", "modified")
        time.sleep(0.1)
        self.file_manager.cleanup_old_changes(max_age_seconds=0.05)
        self.assertEqual(self.file_manager.get_change_count(), 0)


class TestRealFileScenario(unittest.TestCase):
    """真实文件场景测试"""
    
    def setUp(self):
        """测试前准备"""
        self.temp_dir = tempfile.mkdtemp()
        self.file_manager = FileStateManager()
        self.debouncer = SimpleDebouncer(self.process_file_changes, delay=0.1)
        self.changes_detected = []
    
    def tearDown(self):
        """测试后清理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def process_file_changes(self):
        """处理文件变化的回调"""
        changes = self.file_manager.get_and_clear_changes()
        self.changes_detected.extend(changes)
    
    def test_real_file_operations(self):
        """测试真实文件操作"""
        # 创建测试文件
        test_file = os.path.join(self.temp_dir, "test.txt")
        
        # 模拟文件创建
        with open(test_file, 'w') as f:
            f.write("initial content")
        
        # 记录文件变化
        self.file_manager.add_change(test_file, "modified")
        self.debouncer.schedule()
        
        # 等待处理
        time.sleep(0.2)
        
        # 修改文件
        with open(test_file, 'a') as f:
            f.write("\nmodified content")
        
        self.file_manager.add_change(test_file, "modified")
        self.debouncer.schedule()
        
        # 等待处理
        time.sleep(0.2)
        
        # 删除文件
        os.remove(test_file)
        self.file_manager.add_change(test_file, "deleted")
        self.debouncer.schedule()
        
        # 等待处理
        time.sleep(0.2)
        
        # 验证变化被检测
        self.assertEqual(len(self.changes_detected), 3)
        
        # 验证变化类型
        change_types = [change.change_type for change in self.changes_detected]
        self.assertEqual(change_types, ["modified", "modified", "deleted"])


if __name__ == '__main__':
    unittest.main()