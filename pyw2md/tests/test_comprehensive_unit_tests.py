"""
综合单元测试 - 覆盖所有重构后的核心组件
Comprehensive unit tests for all refactored core components
"""

import unittest
import tempfile
import os
import time
import threading
import shutil
from unittest.mock import Mock, patch
from core.file_state_manager import FileStateManager
from utils.debouncer import SimpleDebouncer, DebouncerGroup
from core.file_watcher import FileWatcher
from core.constants import (
    FILE_CHANGE_MODIFIED, FILE_CHANGE_DELETED, FILE_CHANGE_CREATED,
    DEFAULT_DEBOUNCE_MS, MSG_FILE_MODIFIED, MSG_FILE_DELETED
)


class TestFileStateManagerComprehensive(unittest.TestCase):
    """FileStateManager的全面测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = FileStateManager()
    
    def test_add_and_get_changes(self):
        """测试添加和获取变化"""
        # 添加变化
        self.manager.add_change("/test/file1.txt", FILE_CHANGE_MODIFIED)
        self.manager.add_change("/test/file2.txt", FILE_CHANGE_DELETED)
        
        # 验证变化计数
        self.assertEqual(self.manager.get_change_count(), 2)
        self.assertTrue(self.manager.has_changes())
        
        # 获取变化
        changes = self.manager.get_and_clear_changes()
        
        # 验证变化内容
        self.assertEqual(len(changes), 2)
        self.assertFalse(self.manager.has_changes())
        self.assertEqual(self.manager.get_change_count(), 0)
    
    def test_duplicate_changes(self):
        """测试重复变化的处理"""
        file_path = "/test/duplicate.txt"
        
        # 添加相同路径的变化
        self.manager.add_change(file_path, FILE_CHANGE_MODIFIED)
        self.manager.add_change(file_path, FILE_CHANGE_DELETED)
        
        # 获取变化，应该只有最新的一个
        changes = self.manager.get_and_clear_changes()
        self.assertEqual(len(changes), 1)
        self.assertEqual(changes[0].change_type, FILE_CHANGE_DELETED)
    
    def test_get_changes_by_type(self):
        """测试按类型获取变化"""
        # 添加不同类型的变化
        self.manager.add_change("/test/modified1.txt", FILE_CHANGE_MODIFIED)
        self.manager.add_change("/test/deleted1.txt", FILE_CHANGE_DELETED)
        self.manager.add_change("/test/modified2.txt", FILE_CHANGE_MODIFIED)
        
        # 获取修改类型的变化
        modified_changes = self.manager.get_changes_by_type(FILE_CHANGE_MODIFIED)
        self.assertEqual(len(modified_changes), 2)
        
        # 获取删除类型的变化
        deleted_changes = self.manager.get_changes_by_type(FILE_CHANGE_DELETED)
        self.assertEqual(len(deleted_changes), 1)
    
    def test_cleanup_old_changes(self):
        """测试清理过期变化"""
        import time as time_module
        
        # 添加变化
        self.manager.add_change("/test/old.txt", FILE_CHANGE_MODIFIED)
        
        # 等待一小段时间
        time_module.sleep(0.1)
        
        # 添加新变化
        self.manager.add_change("/test/new.txt", FILE_CHANGE_MODIFIED)
        
        # 清理1秒前的变化
        self.manager.cleanup_old_changes(1)  # 1秒
        
        # 应该还有变化（因为时间间隔很小）
        self.assertGreater(self.manager.get_change_count(), 0)
    
    def test_thread_safety(self):
        """测试线程安全性"""
        def worker(thread_id):
            for i in range(100):
                self.manager.add_change(f"/thread{thread_id}/file{i}.txt", FILE_CHANGE_MODIFIED)
                if i % 10 == 0:
                    self.manager.get_and_clear_changes()
        
        # 创建多个线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证没有异常发生
        self.assertIsInstance(self.manager.get_change_count(), int)


class TestSimpleDebouncerComprehensive(unittest.TestCase):
    """SimpleDebouncer的全面测试"""
    
    def test_basic_debounce_functionality(self):
        """测试基本防抖功能"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = SimpleDebouncer(callback, delay=0.01)  # 10ms
        
        # 快速调用多次
        for _ in range(10):
            debouncer.schedule()
        
        # 等待防抖完成
        time.sleep(0.05)
        
        # 应该只调用一次
        self.assertEqual(call_count, 1)
    
    def test_cancel_debounce(self):
        """测试取消防抖"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = SimpleDebouncer(callback, delay=0.1)  # 100ms
        
        # 调度但立即取消
        debouncer.schedule()
        debouncer.cancel()
        
        # 等待足够时间
        time.sleep(0.2)
        
        # 应该没有调用
        self.assertEqual(call_count, 0)
    
    def test_flush_debounce(self):
        """测试立即执行防抖"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = SimpleDebouncer(callback, delay=0.1)  # 100ms
        
        # 调度
        debouncer.schedule()
        
        # 立即刷新
        debouncer.flush()
        
        # 应该立即调用
        self.assertEqual(call_count, 1)
    
    def test_is_pending(self):
        """测试待执行状态"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = SimpleDebouncer(callback, delay=0.1)  # 100ms
        
        # 初始状态
        self.assertFalse(debouncer.is_pending())
        
        # 调度后
        debouncer.schedule()
        self.assertTrue(debouncer.is_pending())
        
        # 等待执行完成
        time.sleep(0.2)
        self.assertFalse(debouncer.is_pending())
        self.assertEqual(call_count, 1)
    
    def test_thread_safety(self):
        """测试线程安全性"""
        call_count = 0
        lock = threading.Lock()
        
        def callback():
            nonlocal call_count
            with lock:
                call_count += 1
        
        debouncer = SimpleDebouncer(callback, delay=0.01)  # 10ms
        
        def worker():
            for _ in range(50):
                debouncer.schedule()
                time.sleep(0.001)  # 1ms间隔
        
        # 创建多个线程
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 等待最后的防抖执行
        time.sleep(0.05)
        
        # 验证至少有一次调用
        self.assertGreater(call_count, 0)


class TestDebouncerGroupComprehensive(unittest.TestCase):
    """DebouncerGroup的全面测试"""
    
    def test_create_and_manage_debouncers(self):
        """测试创建和管理防抖器"""
        group = DebouncerGroup()
        
        # 创建防抖器
        debouncer1 = group.create_debouncer("test1", lambda: None, delay=0.01)
        debouncer2 = group.create_debouncer("test2", lambda: None, delay=0.01)
        
        # 验证防抖器创建
        self.assertIsNotNone(debouncer1)
        self.assertIsNotNone(debouncer2)
        
        # 获取防抖器
        retrieved1 = group.get_debouncer("test1")
        retrieved2 = group.get_debouncer("test2")
        
        self.assertEqual(debouncer1, retrieved1)
        self.assertEqual(debouncer2, retrieved2)
    
    def test_flush_all_debouncers(self):
        """测试刷新所有防抖器"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        group = DebouncerGroup()
        debouncer1 = group.create_debouncer("test1", callback, delay=0.1)
        debouncer2 = group.create_debouncer("test2", callback, delay=0.1)
        
        # 调度所有防抖器
        debouncer1.schedule()
        debouncer2.schedule()
        
        # 刷新所有
        group.flush_all()
        
        # 应该立即执行所有
        self.assertEqual(call_count, 2)
    
    def test_cancel_all_debouncers(self):
        """测试取消所有防抖器"""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        group = DebouncerGroup()
        debouncer1 = group.create_debouncer("test1", callback, delay=0.1)
        debouncer2 = group.create_debouncer("test2", callback, delay=0.1)
        
        # 调度所有防抖器
        debouncer1.schedule()
        debouncer2.schedule()
        
        # 取消所有
        group.cancel_all()
        
        # 等待足够时间
        time.sleep(0.2)
        
        # 应该没有调用
        self.assertEqual(call_count, 0)


class TestConstantsAndMessages(unittest.TestCase):
    """常量和消息的测试"""
    
    def test_message_formatting(self):
        """测试消息格式化"""
        filename = "test.txt"
        
        # 测试文件修改消息
        modified_msg = MSG_FILE_MODIFIED.format(filename=filename)
        self.assertIn(filename, modified_msg)
        self.assertIn("修改", modified_msg)
        
        # 测试文件删除消息
        deleted_msg = MSG_FILE_DELETED.format(filename=filename)
        self.assertIn(filename, deleted_msg)
        self.assertIn("删除", deleted_msg)
    
    def test_constant_values(self):
        """测试常量值"""
        # 测试文件变化类型
        self.assertEqual(FILE_CHANGE_MODIFIED, "modified")
        self.assertEqual(FILE_CHANGE_DELETED, "deleted")
        self.assertEqual(FILE_CHANGE_CREATED, "created")
        
        # 测试防抖时间
        self.assertEqual(DEFAULT_DEBOUNCE_MS, 300)


if __name__ == '__main__':
    unittest.main()