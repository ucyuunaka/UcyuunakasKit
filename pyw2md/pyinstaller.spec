# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置文件

功能：
- 配置PyInstaller打包参数
- 包含必要的依赖和数据文件
- 优化打包结果
- 处理tkinterdnd2等特殊依赖
"""

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# 获取当前目录
block_cipher = None

# 基础配置
a = Analysis(
    ['main.py'],
    pathex=[os.path.dirname(os.path.abspath(__file__))],
    binaries=[],
    datas=[
        # 包含配置文件
        ('config.json', '.'),
        # 包含主题文件（如果有）
        ('config/theme.py', 'config'),
        # 包含图标文件（如果有）
        # ('assets/icon.ico', 'assets'),
    ],
    hiddenimports=[
        # 确保所有子模块都被包含
        'customtkinter',
        'tkinter',
        'tkinter.filedialog',
        'tkinter.messagebox',
        'concurrent.futures',
        'threading',
        'json',
        'os',
        'sys',
        # 文件监控依赖
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        # 核心模块
        'core.converter',
        'core.file_handler',
        'core.file_watcher',
        'config.settings',
        'config.theme',
        'ui.app',
        'ui.components.control_panel',
        'ui.components.file_list_panel',
        'ui.components.dialogs',
        'ui.widgets.material_card',
        'utils.helpers',
        'utils.packaging',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 排除不需要的模块，减小打包体积
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'PyQt5',
        'PySide2',
        'test',
        'unittest',
        'distutils',
        'setuptools',
        'pkg_resources',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# 尝试包含tkinterdnd2
try:
    import tkinterdnd2
    # 获取tkinterdnd2的路径
    tkdnd_path = os.path.dirname(tkinterdnd2.__file__)

    # 添加tkinterdnd2的数据文件
    tkdnd_datas = []

    # 查找DLL文件
    for root, dirs, files in os.walk(tkdnd_path):
        for file in files:
            if file.endswith(('.dll', '.tcl', '.so')):
                source_path = os.path.join(root, file)
                # 计算相对路径
                rel_path = os.path.relpath(root, tkdnd_path)
                if rel_path == '.':
                    dest_path = 'tkinterdnd2'
                else:
                    dest_path = os.path.join('tkinterdnd2', rel_path)

                tkdnd_datas.append((source_path, dest_path))
                print(f"包含tkinterdnd2文件: {source_path} -> {dest_path}")

    # 添加到datas
    a.datas.extend(tkdnd_datas)

    # 添加隐藏的导入
    a.hiddenimports.extend([
        'tkinterdnd2',
        'tkinterdnd2.TkinterDnD',
        'tkinterdnd2.dnd',
    ])

    print(f"成功配置tkinterdnd2，包含 {len(tkdnd_datas)} 个文件")

except ImportError:
    print("警告: tkinterdnd2未安装，拖放功能将不可用")

# 确保包含config.json的默认配置
default_config = {
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
    "auto_watch_files": True,
    "watch_debounce_time": 1.0
}

# 如果config.json不存在，创建一个默认的
if not os.path.exists('config.json'):
    import json
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=2, ensure_ascii=False)
    print("创建默认配置文件")

# PyInstaller配置
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='pyw2md',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # 设置为True以便查看调试信息，稳定后可改为False
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加图标文件 'assets/icon.ico'
)

# 收集依赖信息
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='pyw2md',
)

print("=" * 60)
print("PyInstaller配置完成")
print("=" * 60)
print("打包命令:")
print("pyinstaller pyinstaller.spec")
print("\n或者使用:")
print("pyinstaller --clean -y pyinstaller.spec")
print("=" * 60)