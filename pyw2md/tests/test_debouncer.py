"""
SimpleDebouncer 测试用例
"""

import unittest
import time
import threading
from utils.debouncer import SimpleDebouncer, DebouncerGroup


class TestSimpleDebouncer(unittest.TestCase):
    """SimpleDebouncer 单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.call_count = 0
        self.last_args = None
        self.last_kwargs = None
    
    def callback(self, *args, **kwargs):
        """测试回调函数"""
        self.call_count += 1
        self.last_args = args
        self.last_kwargs = kwargs
    
    def test_basic_debounce(self):
        """测试基本防抖功能"""
        debouncer = SimpleDebouncer(self.callback, delay=0.1)
        
        # 快速多次调用
        debouncer.schedule("test")
        debouncer.schedule("test")
        debouncer.schedule("test")
        
        # 立即检查应该还没有执行
        self.assertEqual(self.call_count, 0)
        
        # 等待防抖延迟后检查
        time.sleep(0.2)
        self.assertEqual(self.call_count, 1)
        self.assertEqual(self.last_args, ("test",))
    
    def test_cancel(self):
        """测试取消功能"""
        debouncer = SimpleDebouncer(self.callback, delay=0.1)
        
        # 调度后立即取消
        debouncer.schedule("test")
        result = debouncer.cancel()
        self.assertTrue(result)
        
        # 等待防抖延迟后检查
        time.sleep(0.2)
        self.assertEqual(self.call_count, 0)
    
    def test_flush(self):
        """测试立即执行功能"""
        debouncer = SimpleDebouncer(self.callback, delay=0.5)
        
        # 调度后立即刷新
        debouncer.schedule("test")
        result = debouncer.flush()
        self.assertTrue(result)
        
        # 短暂等待后应该已经执行
        time.sleep(0.1)
        self.assertEqual(self.call_count, 1)
    
    def test_is_pending(self):
        """测试待执行状态检查"""
        debouncer = SimpleDebouncer(self.callback, delay=0.1)
        
        # 初始状态应该没有待执行
        self.assertFalse(debouncer.is_pending())
        
        # 调度后应该有待执行
        debouncer.schedule("test")
        self.assertTrue(debouncer.is_pending())
        
        # 执行后应该没有待执行
        time.sleep(0.2)
        self.assertFalse(debouncer.is_pending())
    
    def test_duplicate_call_prevention(self):
        """测试重复调用防止"""
        debouncer = SimpleDebouncer(self.callback, delay=0.1)
        
        # 快速连续调用应该被忽略
        result1 = debouncer.schedule("test")
        time.sleep(0.005)  # 5ms间隔
        result2 = debouncer.schedule("test")
        
        self.assertTrue(result1)  # 第一次调用应该成功
        self.assertFalse(result2)  # 第二次调用应该被忽略
        
        # 等待防抖延迟后检查
        time.sleep(0.2)
        self.assertEqual(self.call_count, 1)
    
    def test_reset(self):
        """测试重置功能"""
        debouncer = SimpleDebouncer(self.callback, delay=0.1)
        
        # 调度并获取调用统计
        debouncer.schedule("test")
        initial_count = debouncer.get_call_count()
        self.assertGreater(initial_count, 0)
        
        # 重置后检查状态
        debouncer.reset()
        self.assertEqual(debouncer.get_call_count(), 0)
        self.assertEqual(debouncer.get_last_call_time(), 0.0)
        self.assertFalse(debouncer.is_pending())
    
    def test_thread_safety(self):
        """测试线程安全性"""
        debouncer = SimpleDebouncer(self.callback, delay=0.1)
        call_log = []
        
        def thread_callback(thread_id):
            call_log.append(f"thread_{thread_id}")
        
        def schedule_calls(thread_id):
            for i in range(10):
                debouncer.schedule(thread_id)
        
        # 创建多个线程同时调度
        threads = []
        for i in range(5):
            thread = threading.Thread(target=schedule_calls, args=(i,))
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 等待防抖延迟
        time.sleep(0.2)
        
        # 应该至少执行了一次回调
        self.assertGreaterEqual(self.call_count, 1)


class TestDebouncerGroup(unittest.TestCase):
    """DebouncerGroup 单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.call_count = 0
        self.group = DebouncerGroup()
    
    def callback(self, *args):
        """测试回调函数"""
        self.call_count += 1
    
    def test_create_debouncer(self):
        """测试创建防抖器"""
        # 创建第一个防抖器
        debouncer1 = self.group.create_debouncer("test1", self.callback, 0.1)
        self.assertIsInstance(debouncer1, SimpleDebouncer)
        
        # 重复创建应该返回同一个实例
        debouncer2 = self.group.create_debouncer("test1", self.callback, 0.1)
        self.assertIs(debouncer1, debouncer2)
        
        # 创建不同的防抖器
        debouncer3 = self.group.create_debouncer("test2", self.callback, 0.1)
        self.assertIsNot(debouncer1, debouncer3)
    
    def test_get_debouncer(self):
        """测试获取防抖器"""
        # 获取不存在的防抖器
        debouncer = self.group.get_debouncer("nonexistent")
        self.assertIsNone(debouncer)
        
        # 创建后获取
        self.group.create_debouncer("test", self.callback, 0.1)
        debouncer = self.group.get_debouncer("test")
        self.assertIsInstance(debouncer, SimpleDebouncer)
    
    def test_cancel_all(self):
        """测试取消所有防抖器"""
        # 创建多个防抖器并调度
        debouncer1 = self.group.create_debouncer("test1", self.callback, 0.5)
        debouncer2 = self.group.create_debouncer("test2", self.callback, 0.5)
        
        debouncer1.schedule("test1")
        debouncer2.schedule("test2")
        
        # 确认有待执行的回调
        self.assertTrue(debouncer1.is_pending())
        self.assertTrue(debouncer2.is_pending())
        
        # 取消所有
        self.group.cancel_all()
        
        # 确认没有待执行的回调
        self.assertFalse(debouncer1.is_pending())
        self.assertFalse(debouncer2.is_pending())
        
        # 等待后确认没有执行
        time.sleep(0.6)
        self.assertEqual(self.call_count, 0)
    
    def test_flush_all(self):
        """测试刷新所有防抖器"""
        # 创建多个防抖器并调度
        debouncer1 = self.group.create_debouncer("test1", self.callback, 0.5)
        debouncer2 = self.group.create_debouncer("test2", self.callback, 0.5)
        
        debouncer1.schedule("test1")
        debouncer2.schedule("test2")
        
        # 确认有待执行的回调
        self.assertTrue(debouncer1.is_pending())
        self.assertTrue(debouncer2.is_pending())
        
        # 刷新所有
        self.group.flush_all()
        
        # 短暂等待后应该执行了所有回调
        time.sleep(0.1)
        self.assertEqual(self.call_count, 2)
    
    def test_get_status(self):
        """测试获取状态"""
        # 创建防抖器并调度
        debouncer = self.group.create_debouncer("test", self.callback, 0.1)
        debouncer.schedule("test")
        
        # 获取状态
        status = self.group.get_status()
        self.assertIn("test", status)
        
        test_status = status["test"]
        self.assertTrue(test_status["is_pending"])
        self.assertTrue(test_status["is_running"])
        self.assertGreater(test_status["call_count"], 0)
        self.assertGreater(test_status["last_call_time"], 0)


if __name__ == '__main__':
    unittest.main()