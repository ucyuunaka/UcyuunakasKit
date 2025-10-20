"""
FileStateManager 测试用例
"""

import unittest
import time
import threading
from core.file_state_manager import FileStateManager, FileChange


class TestFileStateManager(unittest.TestCase):
    """FileStateManager 单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = FileStateManager()
    
    def test_add_change(self):
        """测试添加变化"""
        # 添加修改变化
        result = self.manager.add_change("test.txt", "modified")
        self.assertTrue(result)
        self.assertEqual(self.manager.get_change_count(), 1)
        
        # 添加删除变化
        result = self.manager.add_change("test2.txt", "deleted")
        self.assertTrue(result)
        self.assertEqual(self.manager.get_change_count(), 2)
    
    def test_duplicate_change(self):
        """测试重复变化检测"""
        # 添加变化
        result = self.manager.add_change("test.txt", "modified")
        self.assertTrue(result)
        
        # 立即添加相同变化（应该被忽略）
        result = self.manager.add_change("test.txt", "modified")
        self.assertFalse(result)
        self.assertEqual(self.manager.get_change_count(), 1)
        
        # 等待一段时间后添加相同变化
        time.sleep(0.2)
        result = self.manager.add_change("test.txt", "modified")
        self.assertTrue(result)
    
    def test_get_and_clear_changes(self):
        """测试获取并清除变化"""
        # 添加多个变化
        self.manager.add_change("test1.txt", "modified")
        self.manager.add_change("test2.txt", "deleted")
        self.manager.add_change("test3.txt", "modified")
        
        # 获取并清除变化
        changes = self.manager.get_and_clear_changes()
        self.assertEqual(len(changes), 3)
        self.assertEqual(self.manager.get_change_count(), 0)
        
        # 验证变化内容
        paths = [change.path for change in changes]
        self.assertIn("test1.txt", paths)
        self.assertIn("test2.txt", paths)
        self.assertIn("test3.txt", paths)
    
    def test_has_changes(self):
        """测试变化检查"""
        # 初始状态应该没有变化
        self.assertFalse(self.manager.has_changes())
        
        # 添加变化后应该有变化
        self.manager.add_change("test.txt", "modified")
        self.assertTrue(self.manager.has_changes())
        
        # 清除变化后应该没有变化
        self.manager.get_and_clear_changes()
        self.assertFalse(self.manager.has_changes())
    
    def test_get_changes_by_type(self):
        """测试按类型获取变化"""
        # 添加不同类型的变化
        self.manager.add_change("test1.txt", "modified")
        self.manager.add_change("test2.txt", "deleted")
        self.manager.add_change("test3.txt", "modified")
        
        # 获取修改类型的变化
        modified_changes = self.manager.get_changes_by_type("modified")
        self.assertEqual(len(modified_changes), 2)
        
        # 获取删除类型的变化
        deleted_changes = self.manager.get_changes_by_type("deleted")
        self.assertEqual(len(deleted_changes), 1)
    
    def test_remove_change(self):
        """测试移除变化"""
        # 添加变化
        self.manager.add_change("test.txt", "modified")
        self.assertEqual(self.manager.get_change_count(), 1)
        
        # 移除变化
        result = self.manager.remove_change("test.txt")
        self.assertTrue(result)
        self.assertEqual(self.manager.get_change_count(), 0)
        
        # 移除不存在的变化
        result = self.manager.remove_change("nonexistent.txt")
        self.assertFalse(result)
    
    def test_get_file_status(self):
        """测试获取文件状态"""
        # 初始状态
        status = self.manager.get_file_status("test.txt")
        self.assertEqual(status, "normal")
        
        # 添加变化后的状态
        self.manager.add_change("test.txt", "modified")
        status = self.manager.get_file_status("test.txt")
        self.assertEqual(status, "modified")
        
        # 清除变化后的状态
        self.manager.get_and_clear_changes()
        status = self.manager.get_file_status("test.txt")
        self.assertEqual(status, "normal")
    
    def test_get_summary(self):
        """测试获取变化摘要"""
        # 添加多个变化
        self.manager.add_change("test1.txt", "modified")
        self.manager.add_change("test2.txt", "deleted")
        self.manager.add_change("test3.txt", "modified")
        
        # 获取摘要
        summary = self.manager.get_summary()
        self.assertEqual(summary['total'], 3)
        self.assertEqual(summary['modified'], 2)
        self.assertEqual(summary['deleted'], 1)
    
    def test_cleanup_old_changes(self):
        """测试清理过期变化"""
        # 添加变化
        self.manager.add_change("test.txt", "modified")
        self.assertEqual(self.manager.get_change_count(), 1)
        
        # 等待一段时间并清理（使用很短的超时时间进行测试）
        time.sleep(0.1)
        self.manager.cleanup_old_changes(max_age_seconds=0.05)
        self.assertEqual(self.manager.get_change_count(), 0)
    
    def test_thread_safety(self):
        """测试线程安全性"""
        def add_changes(thread_id):
            for i in range(100):
                self.manager.add_change(f"test_{thread_id}_{i}.txt", "modified")
        
        # 创建多个线程同时添加变化
        threads = []
        for i in range(5):
            thread = threading.Thread(target=add_changes, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证所有变化都被正确记录
        changes = self.manager.get_changes()
        self.assertEqual(len(changes), 500)  # 5个线程 × 100个变化


if __name__ == '__main__':
    unittest.main()