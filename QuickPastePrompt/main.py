import json
import sys
import os
import threading
import time
from tkinter import messagebox, Tk
import pystray
from pystray import MenuItem, Menu
from PIL import Image
import pyperclip

def resource_path(relative_path):
    """获取资源的绝对路径，兼容开发环境和 PyInstaller 打包环境"""
    try:
        # PyInstaller 创建一个临时文件夹 _MEIPASS 并将路径存储在其中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def load_config():
    """
    加载并解析 config.json 文件。
    如果文件不存在或格式错误，则弹出错误提示并退出程序。
    """
    try:
        with open(resource_path('config.json'), 'r', encoding='utf-8') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        # 使用Tkinter来显示一个没有主窗口的错误弹窗
        root = Tk()
        root.withdraw()  # 隐藏主窗口
        messagebox.showerror("错误", "配置文件 'config.json' 未找到！\n请确保它与程序在同一目录下。")
        sys.exit(1)  # 退出程序
    except json.JSONDecodeError:
        root = Tk()
        root.withdraw()
        messagebox.showerror("错误", "配置文件 'config.json' 格式错误！\n请检查文件内容是否为有效的JSON。")
        sys.exit(1)

def copy_to_clipboard(text):
    """将文本复制到剪贴板，并根据配置触发反馈"""
    try:
        pyperclip.copy(text)
        print(f"已复制: {text[:30]}...")  # 在控制台打印日志，便于调试
        
        # 如果启用了反馈，则执行
        if enable_feedback:
            trigger_feedback()
            
    except Exception as e:
        print(f"复制失败: {e}")

def trigger_feedback():
    """
    通过短暂地切换托盘图标来提供视觉反馈。
    使用线程以避免阻塞主GUI线程。
    """
    def feedback_thread():
        try:
            original_icon = icon.icon
            icon.icon = success_icon  # 切换到成功图标
            time.sleep(0.5)          # 持续0.5秒
            icon.icon = original_icon  # 切换回原始图标
        except Exception as e:
            print(f"反馈动画失败: {e}")

    # 启动一个新线程来执行反馈动画，防止UI卡顿
    threading.Thread(target=feedback_thread, daemon=True).start()

def create_menu_items(categories_data):
    """根据配置数据动态生成菜单项列表"""
    menu_items = []
    
    # 遍历每个分类
    for category in categories_data:
        category_name = category.get('category_name', '未命名分类')
        prompts = category.get('prompts', [])
        
        # 为每个提示词创建子菜单项
        sub_menu_items = []
        for prompt in prompts:
            title = prompt.get('title', '无标题')
            content = prompt.get('content', '')
            
            # 修复：使用 functools.partial 或闭包来正确捕获 content 值
            def make_copy_action(text):
                return lambda icon=None, item=None: copy_to_clipboard(text)
            
            action = make_copy_action(content)
            sub_menu_items.append(MenuItem(title, action))
            
        # 如果子菜单不为空，则创建分类子菜单
        if sub_menu_items:
            menu_items.append(MenuItem(category_name, Menu(*sub_menu_items)))

    # 添加分隔符和退出按钮
    if menu_items:
        menu_items.append(Menu.SEPARATOR)
    menu_items.append(MenuItem('退出', on_exit))
    
    return menu_items

def on_exit(icon, item):
    """退出应用程序"""
    icon.stop()

if __name__ == '__main__':
    # 加载配置
    config_data = load_config()
    enable_feedback = config_data.get('enable_feedback', False)
    categories = config_data.get('categories', [])
    
    # 加载图标
    default_icon = Image.open(resource_path("icon.png"))
    success_icon = Image.open(resource_path("icon_success.png"))
    
    # 创建菜单
    menu = Menu(*create_menu_items(categories))
    
    # 创建托盘图标对象
    icon = pystray.Icon("PromptLauncher", default_icon, "提示词启动器", menu)
    
    print("提示词启动器已启动，请查看系统托盘...")
    
    # 运行托盘图标
    icon.run() 