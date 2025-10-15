"""
应用配置管理
"""

import json
import os
import sys
from typing import Dict, Any

class Settings:
    """配置管理器"""

    def __init__(self, config_file: str = "config.json"):
        # 检测是否为打包环境
        if hasattr(sys, '_MEIPASS'):
            # 打包环境下，配置文件放在用户数据目录
            self.config_dir = os.path.join(os.path.expanduser('~'), '.pyw2md')
            os.makedirs(self.config_dir, exist_ok=True)
            self.config_file = os.path.join(self.config_dir, config_file)
        else:
            # 开发环境下，配置文件放在当前目录
            self.config_file = config_file

        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """加载配置"""
        if not os.path.exists(self.config_file):
            self.config = self._default_config()
            self.save()
            return

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            self.config = self._default_config()

    def save(self):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置失败: {e}")

    def get(self, key: str, default=None):
        """获取配置项"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """设置配置项"""
        self.config[key] = value

    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            "window": {
                "width": 1280,
                "height": 800,
                "min_width": 1000,
                "min_height": 600
            },
            "template": "默认",
            "recent_files": [],
            "max_recent_files": 50,
            "auto_save_config": True,
            "preview_max_files": 5,
            "auto_watch_files": True,  # 新增：自动监控文件变化
            "watch_debounce_time": 1.0  # 新增：监控防抖时间（秒）
        }
