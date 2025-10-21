# pyw2md 构建指南

## 概述

pyw2md项目提供了完整的自动化构建系统，使开发者能够通过简单的命令行操作生成可执行的exe文件。

## 系统要求

### 开发环境要求
- **Python版本**: 3.11+ (推荐3.13)
- **操作系统**: Windows 10/11 (64位)
- **内存**: 至少4GB可用RAM
- **磁盘空间**: 至少2GB可用空间

### 必需依赖
```bash
pip install -r requirements.txt
```

主要依赖包括：
- `customtkinter>=5.2.0` - 现代化UI框架
- `watchdog>=3.0.0` - 文件系统监控
- `PyInstaller>=5.0.0` - 打包工具
- `setuptools>=65.0.0` - 兼容性支持
- `tkinterdnd2>=0.3.0` - 拖放功能支持

## 快速开始

### 1. 基本构建
```bash
python build.py
```

### 2. 清理构建
```bash
python build.py --clean
```

### 3. 版本管理构建
```bash
# 递增补丁版本 (1.0.0 -> 1.0.1)
python build.py --version patch

# 递增次版本 (1.0.0 -> 1.1.0)
python build.py --version minor

# 递增主版本 (1.0.0 -> 2.0.0)
python build.py --version major
```

## 命令行选项

| 选项 | 简写 | 描述 | 示例 |
|------|------|------|------|
| `--clean` | `-c` | 构建前清理构建目录 | `python build.py --clean` |
| `--version` | `-v` | 递增版本号 | `python build.py --version patch` |
| `--debug` | `-d` | 启用调试模式 | `python build.py --debug` |
| `--verbose` | `-V` | 详细输出 | `python build.py --verbose` |
| `--no-tag` | - | 不创建Git标签 | `python build.py --no-tag` |
| `--no-upx` | - | 不使用UPX压缩 | `python build.py --no-upx` |

## 构建流程详解

### 阶段1: 环境检查
- Python版本验证
- 平台兼容性检查
- 磁盘空间检查
- 必需依赖验证

### 阶段2: 打包环境验证
- tkinterdnd2可用性检查
- PyInstaller可用性验证
- 打包环境信息收集

### 阶段3: 版本管理
- 读取当前版本号
- 根据参数递增版本
- 更新VERSION文件
- 可选创建Git标签

### 阶段4: 清理准备
- 清理旧的构建目录
- 删除临时文件
- 准备干净构建环境

### 阶段5: PyInstaller构建
- 使用预配置的spec文件
- 包含所有必要依赖
- 处理特殊的DLL文件
- 生成独立可执行文件

### 阶段6: 验证和报告
- 验证exe文件生成
- 检查文件大小
- 生成详细构建报告

## 构建产物

### 主要文件
```
dist/
└── pyw2md/
    ├── pyw2md.exe          # 主可执行文件
    └── _internal/           # 内部依赖文件

build_report.json            # 详细构建报告
```

### 构建报告内容
- **构建信息**: 时间、配置、环境详情
- **版本信息**: 当前版本和构建历史
- **依赖分析**: 完整的依赖关系图
- **问题报告**: 识别的问题和建议
- **环境报告**: 打包环境验证结果

## 常见问题解决

### 1. DLL加载失败
**问题**: `ImportError: DLL load failed while importing _tkinter`

**解决方案**:
```bash
# 确保使用windowed模式构建
python build.py --clean

# 如果仍有问题，检查Anaconda环境
conda install tk
```

### 2. 缺少依赖
**问题**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```bash
# 重新安装所有依赖
pip install -r requirements.txt --upgrade

# 清理后重新构建
python build.py --clean
```

### 3. 版本管理问题
**问题**: 版本号无法更新

**解决方案**:
```bash
# 手动检查VERSION文件
type VERSION

# 强制设置版本
python -c "from utils.version_manager import VersionManager; vm = VersionManager('.'); vm.write_version('1.0.0')"
```

### 4. 构建速度慢
**解决方案**:
```bash
# 禁用UPX压缩（如果不需要）
python build.py --no-upx

# 使用增量构建（不使用--clean）
python build.py
```

## 高级配置

### 自定义构建配置
可以通过修改`build_config.json`来自定义构建选项：

```json
{
    "default_mode": "windowed",
    "compression": true,
    "upx_compress": true,
    "include_debug_info": false,
    "additional_hidden_imports": [],
    "excluded_modules": []
}
```

### spec文件自定义
`pyw2md.spec`文件包含详细的打包配置：
- 隐藏导入列表
- 数据文件包含规则
- 二进制文件处理
- 排除模块配置

### 环境变量
- `PYW2MD_LOG_LEVEL`: 设置日志级别
- `PYW2MD_CONFIG_FILE`: 自定义配置文件路径

## 调试和故障排除

### 调试模式
```bash
python build.py --debug --verbose
```

调试模式会：
- 保留临时文件
- 输出详细日志
- 提供完整错误堆栈
- 生成调试版本的exe

### 查看详细日志
构建日志保存在：
- `build_report.json` - 结构化构建报告
- 控制台输出 - 实时构建信息
- PyInstaller日志 - 打包过程详情

### 常见错误代码
- **退出码1**: 环境检查失败
- **退出码2**: 依赖验证失败
- **退出码3**: PyInstaller构建失败
- **退出码4**: 构建验证失败

## 最佳实践

### 1. 版本管理
- 在每次发布前递增版本号
- 使用Git标签标记重要版本
- 保留构建报告用于追踪

### 2. 构建环境
- 使用干净的虚拟环境
- 定期更新依赖版本
- 备份重要的构建配置

### 3. 测试流程
- 在不同Windows版本上测试
- 验证所有功能正常工作
- 检查文件大小和启动速度

### 4. 发布准备
- 使用`--clean`确保干净构建
- 验证版本号正确性
- 检查构建报告中的问题

## 技术支持

如果遇到构建问题，请提供以下信息：
1. 构建命令和输出
2. `build_report.json`文件
3. Python版本和操作系统信息
4. 错误消息和堆栈跟踪

## 相关文档

- [PyInstaller官方文档](https://pyinstaller.readthedocs.io/)
- [customtkinter文档](https://customtkinter.tomschimansky.com/)
- [项目README.md](README.md)
- [项目技术文档](CLAUDE.md)

---

**最后更新**: 2025-10-21
**维护者**: pyw2md开发团队