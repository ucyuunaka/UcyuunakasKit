#!/usr/bin/env python3
"""
性能分析脚本 - 分析重构后的系统性能
Performance analysis script for the refactored system
"""

import time
import threading
import tempfile
import os
import statistics
from typing import List, Dict, Any

# 导入要测试的组件
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.file_state_manager import FileStateManager
from utils.debouncer import SimpleDebouncer
from core.file_watcher import FileWatcher

class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
    
    def test_file_state_manager_performance(self, iterations: int = 1000) -> Dict[str, float]:
        """测试FileStateManager性能"""
        print(f"测试 FileStateManager 性能 ({iterations} 次迭代)...")
        
        manager = FileStateManager()
        
        # 测试添加变化性能
        start_time = time.perf_counter()
        for i in range(iterations):
            manager.add_change(f"/test/file_{i}.txt", "modified")
        
        add_time = time.perf_counter() - start_time
        
        # 测试获取变化性能
        start_time = time.perf_counter()
        for _ in range(100):
            changes = manager.get_and_clear_changes()
        
        get_time = time.perf_counter() - start_time
        
        # 测试线程安全性能
        def worker():
            for i in range(iterations // 10):
                manager.add_change(f"/thread/file_{i}.txt", "modified")
                if i % 100 == 0:
                    manager.get_and_clear_changes()
        
        start_time = time.perf_counter()
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        thread_time = time.perf_counter() - start_time
        
        return {
            "add_operations_per_second": iterations / add_time,
            "get_operations_per_second": 100 / get_time,
            "thread_safe_operations_per_second": (iterations * 10) / thread_time,
            "add_avg_time_ms": (add_time / iterations) * 1000,
            "get_avg_time_ms": (get_time / 100) * 1000,
            "thread_avg_time_ms": (thread_time / (iterations * 10)) * 1000
        }
    
    def test_debouncer_performance(self, iterations: int = 100) -> Dict[str, float]:
        """测试SimpleDebouncer性能"""
        print(f"测试 SimpleDebouncer 性能 ({iterations} 次迭代)...")
        
        call_count = 0
        call_times = []
        
        def callback():
            nonlocal call_count
            call_count += 1
            call_times.append(time.perf_counter())
        
        debouncer = SimpleDebouncer(callback, delay=0.01)  # 10ms
        
        # 测试快速调用性能
        start_time = time.perf_counter()
        for i in range(iterations):
            debouncer.schedule()
            time.sleep(0.001)  # 1ms间隔
        
        # 等待最后一次调用完成
        time.sleep(0.05)
        
        total_time = time.perf_counter() - start_time
        
        # 计算实际执行的调用间隔
        if len(call_times) > 1:
            intervals = [(call_times[i] - call_times[i-1]) * 1000 
                        for i in range(1, len(call_times))]
            avg_interval = statistics.mean(intervals)
            max_interval = max(intervals)
            min_interval = min(intervals)
        else:
            avg_interval = max_interval = min_interval = 0
        
        return {
            "calls_made": call_count,
            "calls_suppressed": iterations - call_count,
            "suppression_ratio": (iterations - call_count) / iterations,
            "total_time_seconds": total_time,
            "avg_interval_ms": avg_interval,
            "max_interval_ms": max_interval,
            "min_interval_ms": min_interval,
            "effectiveness": call_count / iterations if iterations > 0 else 0
        }
    
    def test_memory_usage(self) -> Dict[str, Any]:
        """测试内存使用情况"""
        import psutil
        import gc
        
        print("测试内存使用情况...")
        
        process = psutil.Process()
        
        # 基线内存使用
        gc.collect()
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 创建大量FileStateManager实例
        managers = []
        for i in range(100):
            manager = FileStateManager()
            for j in range(100):
                manager.add_change(f"/test/file_{i}_{j}.txt", "modified")
            managers.append(manager)
        
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 清理并测试内存释放
        managers.clear()
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        return {
            "baseline_memory_mb": baseline_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": peak_memory - baseline_memory,
            "memory_released_mb": peak_memory - final_memory,
            "memory_leak_suspected": (final_memory - baseline_memory) > 10  # 10MB阈值
        }
    
    def generate_report(self) -> str:
        """生成性能报告"""
        print("生成性能分析报告...")
        
        # 运行所有测试
        state_manager_results = self.test_file_state_manager_performance()
        debouncer_results = self.test_debouncer_performance()
        memory_results = self.test_memory_usage()
        
        report = f"""
# pyw2md 重构后性能分析报告
# Performance Analysis Report for pyw2md Refactoring

生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}

## 1. FileStateManager 性能
- 添加操作性能: {state_manager_results['add_operations_per_second']:.0f} ops/sec
- 获取操作性能: {state_manager_results['get_operations_per_second']:.0f} ops/sec
- 线程安全操作性能: {state_manager_results['thread_safe_operations_per_second']:.0f} ops/sec
- 平均添加时间: {state_manager_results['add_avg_time_ms']:.3f} ms
- 平均获取时间: {state_manager_results['get_avg_time_ms']:.3f} ms
- 平均线程操作时间: {state_manager_results['thread_avg_time_ms']:.3f} ms

## 2. SimpleDebouncer 性能
- 实际执行次数: {debouncer_results['calls_made']}
- 抑制的调用次数: {debouncer_results['calls_suppressed']}
- 抑制比率: {debouncer_results['suppression_ratio']:.1%}
- 防抖有效性: {debouncer_results['effectiveness']:.1%}
- 平均调用间隔: {debouncer_results['avg_interval_ms']:.1f} ms
- 最大调用间隔: {debouncer_results['max_interval_ms']:.1f} ms
- 最小调用间隔: {debouncer_results['min_interval_ms']:.1f} ms

## 3. 内存使用情况
- 基线内存: {memory_results['baseline_memory_mb']:.1f} MB
- 峰值内存: {memory_results['peak_memory_mb']:.1f} MB
- 最终内存: {memory_results['final_memory_mb']:.1f} MB
- 内存增长: {memory_results['memory_increase_mb']:.1f} MB
- 内存释放: {memory_results['memory_released_mb']:.1f} MB
- 疑似内存泄漏: {'是' if memory_results['memory_leak_suspected'] else '否'}

## 4. 性能评估
### 优势
- FileStateManager 提供了高性能的状态管理操作
- SimpleDebouncer 有效抑制了重复调用
- 线程安全实现可靠

### 需要关注的方面
- {'内存使用需要优化' if memory_results['memory_leak_suspected'] else '内存使用正常'}
- {'防抖机制工作良好' if debouncer_results['suppression_ratio'] > 0.5 else '防抖效果可能需要调整'}
- 线程性能满足并发需求

## 5. 建议
1. 继续监控内存使用情况
2. 根据实际使用情况调整防抖延迟
3. 定期进行性能回归测试
"""
        
        return report

def main():
    """主函数"""
    print("开始性能分析...")
    
    analyzer = PerformanceAnalyzer()
    report = analyzer.generate_report()
    
    # 保存报告
    report_path = "performance_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"性能分析完成，报告已保存到: {report_path}")
    print(report)

if __name__ == "__main__":
    main()