import time
import random
import math
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.console import Console, Group

# 从我们创建的组件文件中导入 RichDashboard 类
from dashboard_component import RichDashboard

# --- 数据模拟和面板生成函数 (这些都保持不变) ---
def get_mock_data():
    """生成一组模拟的随机数据。"""
    data = {
        "ego_pos": (random.uniform(25.0, 35.0), random.uniform(10.0, 20.0)),
        "ego_speed": 18.0 + random.uniform(-1.0, 1.0),
        "ego_steering": random.uniform(2.0, 3.5),
        "heading": random.uniform(0.0, 360.0),
        "lateral_error": random.uniform(-0.5, 0.5),
        "target_pos": (random.uniform(40.0, 50.0), random.uniform(3.0, 5.0)),
        "repulsive_force": (random.uniform(0.0, 0.5), random.uniform(0.0, 0.5)),
        "other_vehicles": [
            {'id': f'spawn_{random.randint(10,20)}', 'pos': (21.0, random.uniform(60.0, 80.0))},
            {'id': f'spawn_{random.randint(10,20)}', 'pos': (21.0, random.uniform(130.0, 150.0))}
        ],
        "nearest_obstacle_dist": random.uniform(5.0, 15.0),
        "system_status": "正常运行" if random.random() > 0.1 else "警告: 规划紧急制动",
        "apf_calculations": random.randint(100, 200)
    }
    data["rep_force_mag"] = math.hypot(data["repulsive_force"][0], data["repulsive_force"][1])
    data["yaw_rate"] = random.uniform(-0.1, 0.1)
    data["update_id"] = f"{int(time.time() * 1000) % 1000000:06d}" # 把ID生成也放进来
    return data

# (这里省略了 generate_header, generate_status_panel, generate_perception_panel, 
# generate_decision_panel 函数的完整代码，因为它们和你的原始代码完全一样，无需改动)
def generate_header(update_id: str) -> Panel:
    title = Text(f"[Update ID: {update_id}]", justify="center", style="bold magenta")
    return Panel(title, border_style="magenta")

def generate_status_panel(data: dict) -> Panel:
    status_color = "green" if "正常" in data["system_status"] else "bold red"
    grid = Table.grid()
    grid.add_column(ratio=1)
    grid.add_row(Text(f"🧠 路径跟踪: 目标({data['target_pos'][0]:.1f},{data['target_pos'][1]:.1f}) | 力({data['repulsive_force'][0]:.1f},{data['repulsive_force'][1]:.1f})"))
    grid.add_row(Text(f"🎮 速度控制: 当前速度={data['ego_speed']:.2f}m/s, 目标转向={data['ego_steering']:.2f}°"))
    grid.add_row(Text(f"🧭 航向角: {data['heading']:.1f}° | ↔️ 横向误差: {data['lateral_error']:.2f}m"))
    grid.add_row(Text(f"🚨 系统诊断: ") + Text(data['system_status'], style=status_color))
    return Panel(grid, title="[bold cyan]主状态[/]", border_style="cyan")

def generate_perception_panel(data: dict) -> Panel:
    grid = Table.grid()
    grid.add_column()
    grid.add_row(Text(f"✅ 主车位置: ({data['ego_pos'][0]:.2f}, {data['ego_pos'][1]:.2f})"))
    grid.add_row(Text(f"✅ 周围车辆: {len(data['other_vehicles'])} 辆"))
    for vehicle in data['other_vehicles']:
        grid.add_row(Text(f"  - {vehicle['id']} @ ({vehicle['pos'][0]:.1f}, {vehicle['pos'][1]:.1f})"))
    dist_color = "red" if data['nearest_obstacle_dist'] < 8.0 else "green"
    grid.add_row(Text("🔍 最近障碍物:"))
    grid.add_row(Text(f"   距离: ",) + Text(f"{data['nearest_obstacle_dist']:.2f} m", style=dist_color))
    return Panel(grid, title="[bold cyan]感知[/]", border_style="cyan")

def generate_decision_panel(data: dict) -> Panel:
    grid = Table.grid()
    grid.add_column()
    grid.add_row(Text("🎯 路径规划:"))
    grid.add_row(Text(f"   目标点: ({data['target_pos'][0]:.1f}, {data['target_pos'][1]:.1f})"))
    grid.add_row(Text("🌊 人工势场 (APF):"))
    force_color = "red" if data["rep_force_mag"] > 0.4 else "green"
    grid.add_row(Text(f"   斥力大小: ") + Text(f"{data['rep_force_mag']:.2f}", style=force_color))
    grid.add_row(Text(f"   统计: {data['apf_calculations']} 次计算"))
    grid.add_row(Text(f"   偏航率: {data['yaw_rate']:.2f} rad/s"))
    return Panel(grid, title="[bold cyan]决策[/]", border_style="cyan")


# 【核心改动】: 创建一个布局函数
def create_dashboard_layout(data: dict):
    """
    根据传入的数据，构建完整的仪表盘 Rich 可渲染对象。
    这个函数就是告诉 RichDashboard “长什么样”。
    """
    header_panel = generate_header(data['update_id'])
    
    left_content_group = Group(
        generate_status_panel(data),
        generate_perception_panel(data)
    )
    
    decision_panel_content = generate_decision_panel(data)
    
    main_content_grid = Table.grid(expand=True)
    main_content_grid.add_column(ratio=1) # 左侧面板比例
    main_content_grid.add_column(ratio=1) # 右侧面板比例
    main_content_grid.add_row(left_content_group, decision_panel_content)
    
    # 将所有部分组合成一个最终的渲染对象
    full_dashboard_content = Group(
        header_panel,
        main_content_grid
    )
    
    return full_dashboard_content

# --- 主程序 (现在变得非常简洁) ---
if __name__ == "__main__":
    # 1. 实例化仪表盘，并告诉它使用哪个函数来构建布局
    my_dashboard = RichDashboard(layout_function=create_dashboard_layout)
    
    # 2. 运行仪表盘，并告诉它从哪里获取数据
    #    组件会自动处理循环、刷新和退出
    my_dashboard.run(data_provider_func=get_mock_data, refresh_rate=20)