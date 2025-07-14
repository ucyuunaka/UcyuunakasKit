# 提示词启动器 (Prompt Launcher)

一个轻量级的 Windows 桌面效率工具，通过系统托盘快速访问和复制预设的提示词。

## 功能特点

- 🖱️ 系统托盘图标，右键显示分类菜单
- 📋 一键复制提示词到剪贴板
- ✨ 复制成功时的视觉反馈（图标短暂变色）
- 🔧 通过 JSON 配置文件自定义提示词和分类
- 💻 独立 exe 文件，无需安装 Python 环境

## 使用方法

1. 运行 `main.exe`
2. 在系统托盘区域找到程序图标
3. 右键点击图标查看提示词菜单
4. 点击任意提示词即可复制到剪贴板
5. 选择"退出"关闭程序

## 配置说明

编辑 `config.json` 文件来自定义提示词：

```json
{
  "enable_feedback": true, // 是否启用复制成功的视觉反馈
  "categories": [
    {
      "category_name": "分类名称",
      "prompts": [
        {
          "title": "在菜单中显示的标题",
          "content": "实际复制到剪贴板的内容"
        }
      ]
    }
  ]
}
```

## 文件说明

- `main.exe` - 主程序
- `config.json` - 配置文件（必须与 exe 在同一目录）
- `icon.png` - 默认托盘图标
- `icon_success.png` - 成功反馈图标

## 开发信息

基于开发文档中的技术方案实现：

- Python + pystray (系统托盘)
- pyperclip (剪贴板操作)
- Pillow (图像处理)
- PyInstaller (打包)

---

_按照开发文档逐步完成的 Windows 桌面效率工具_
