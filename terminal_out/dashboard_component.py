import time
from rich.console import Console

class RichDashboard:
    """
    一个可复用的、基于 Rich 库的文本仪表盘组件。

    它处理了实时刷新、优雅退出和历史记录等通用功能。
    """
    def __init__(self, layout_function):
        """
        初始化仪表盘。

        Args:
            layout_function (callable): 一个函数，接收一个数据字典作为参数，
                                        并返回一个 Rich 可渲染对象 (e.g., Panel, Group)。
        """
        if not callable(layout_function):
            raise TypeError("layout_function 必须是一个可调用对象 (函数)。")
        
        self.layout_function = layout_function
        self.console = Console()
        self.history_log = []

    def run(self, data_provider_func, refresh_rate: int = 20):
        """
        启动仪表盘的实时显示循环。

        Args:
            data_provider_func (callable): 一个无参数的函数，每次调用时返回最新的数据字典。
            refresh_rate (int, optional): 仪表盘的刷新频率 (Hz). Defaults to 20.
        """
        if not callable(data_provider_func):
            raise TypeError("data_provider_func 必须是一个可调用对象 (函数)。")

        last_time = time.time()
        
        try:
            while True:
                # --- 数据和时间更新 ---
                current_time = time.time()
                data = data_provider_func()
                
                # --- 生成并打印布局 ---
                dashboard_content = self.layout_function(data)
                
                # 使用带记录功能的 Console 捕获输出文本以供历史记录使用
                capture_console = Console(record=True, width=self.console.width)
                capture_console.print(dashboard_content)
                self.history_log.append(capture_console.export_text())

                # 在主控制台实时打印
                self.console.clear()
                self.console.print(dashboard_content)
                
                # --- 控制更新频率 ---
                sleep_time = (1.0 / refresh_rate) - (time.time() - current_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.console.print(f"\n[bold red]发生错误: {e}[/bold red]")
            self.stop()

    def stop(self):
        """
        停止仪表盘并显示历史记录。
        """
        self.console.clear()
        print("--- 📜 历史记录回放 ---")
        if not self.history_log:
            print("没有可回放的历史记录。")
        else:
            for i, frame_text in enumerate(self.history_log):
                print(f"--- Frame {i+1}/{len(self.history_log)} " + "="*60)
                print(frame_text)
        
        print("\n✅ 仪表盘已成功关闭，并已显示所有历史记录。")