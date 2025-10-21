# pyw2md - 文件监控和转换工具

上次更新时间：2025-10-21 代码注释重构优化

## 1. TODO List

- [ ] 完善GUI界面设计
- [ ] 添加更多文件格式支持
- [ ] 优化文件监控性能
- [ ] 增加批量转换功能
- [ ] 添加配置文件导入/导出

## 2. 定期更新速查表

| 日期 | 版本 | 更新内容 | 维护者 |
|------|------|----------|--------|
| 2025-10-21 | 1.0.3 | 代码注释重构优化 | AI助手 |
| 2025-10-21 | 1.0.2 | 完成自动化构建系统 | AI助手 |
| 2025-10-20 | 1.0.1 | 重构文件监控模块 | AI助手 |
| 2025-10-18 | 1.0.0 | 项目初始化 | 人类开发者 |

## 3. 文献调研

### 核心技术文献
- PyInstaller官方文档: Python应用程序打包最佳实践
- watchdog库文档: 跨平台文件系统监控
- customtkinter文档: 现代化tkinter界面设计
- tkinterdnd2文档: Python拖放功能实现

### 参考项目
- PyInstaller样例项目
- watchdog官方示例
- 文件监控工具设计模式

## 4. 项目基本信息

pyw2md是一个Python文件监控和转换工具，支持自动检测文件变化并转换为Markdown格式。项目采用模块化设计，具备强大的错误处理和用户友好的界面。

### 核心功能
- **文件监控**: 实时监控指定目录的文件变化
- **格式转换**: 自动将各种格式文件转换为Markdown
- **拖放支持**: 支持文件拖放操作
- **配置管理**: 灵活的配置文件系统
- **错误处理**: 完善的错误处理和用户反馈

### 技术特点
- 基于Python 3.13+开发
- 使用customtkinter提供现代化UI
- watchdog提供跨平台文件监控
- PyInstaller支持一键打包
- 模块化架构设计

## 5. 全面的项目工具列表

### 开发工具
- **IDE**: VS Code
- **版本控制**: Git
- **包管理**: pip + requirements.txt
- **测试框架**: pytest
- **打包工具**: PyInstaller

### 核心依赖
- `customtkinter>=5.2.0` - UI框架
- `watchdog>=3.0.0` - 文件监控
- `tkinterdnd2>=0.3.0` - 拖放功能
- `setuptools>=65.0.0` - 兼容性支持

### 构建工具
- `build.py` - 主构建脚本
- `pyw2md.spec` - PyInstaller配置
- `utils/build_helper.py` - 构建辅助工具
- `utils/version_manager.py` - 版本管理

### 项目结构
```
pyw2md/
├── core/                    # 核心功能模块
├── ui/                      # 用户界面模块
├── utils/                   # 工具模块
├── config/                  # 配置文件
├── tests/                   # 测试模块
├── openspec/               # OpenSpec规范
├── main.py                 # 主程序入口
├── build.py                # 构建脚本
├── requirements.txt        # 依赖列表
└── BUILD.md               # 构建指南
```

## 6. 变量表 (简写与符号)

| 变量/符号 | 含义 | 用途 |
|-----------|------|------|
| `vm` | VersionManager | 版本管理器实例 |
| `fh` | FileHandler | 文件处理器 |
| `fw` | FileWatcher | 文件监控器 |
| `ctk` | customtkinter | UI框架 |
| `dnd` | drag and drop | 拖放功能 |
| `spec` | specification | PyInstaller配置文件 |

## 7. 项目进展记录

### 当前状态: 重构刷新和自动检测系统的重大改进

#### 已完成功能
1. **核心文件监控模块** (已完成)
   - 重构了FileWatcher类，使用统一的状态管理
   - 集成了SimpleDebouncer提供300ms防抖
   - 增强了错误处理和用户反馈机制

2. **统一状态管理** (已完成)
   - 实现了FileStateManager类
   - 提供线程安全的状态操作
   - 支持变更分类统计和过期清理

3. **防抖机制优化** (已完成)
   - 创建了SimpleDebouncer类
   - 支持可配置的防抖延迟
   - 提供防抖器组统一管理

4. **自动化构建系统** (已完成)
   - 完整的build.py构建脚本
   - PyInstaller配置文件
   - 版本管理集成
   - 详细的构建报告生成

5. **测试覆盖** (进行中)
   - 单元测试: 37/45 通过 (82.2%)
   - 需要修复的错误处理测试: 8个
   - 集成测试和重构测试基本完成

#### 技术债务
- utils/debouncer_broken.py 需要清理
- 部分测试用例需要修复
- GUI模块需要进一步重构

#### 下一步计划
- 完成测试用例修复
- 开始GUI模块重构
- 优化用户界面体验
- 添加更多文件格式支持

### 成果展示 (由用户填写)

*这里将由用户添加实际使用成果和反馈*

---

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行程序
```bash
python main.py
```

### 构建exe文件
```bash
python build.py --clean
```

详细构建说明请参考 [BUILD.md](BUILD.md)

## 技术文档

- [构建指南](BUILD.md) - 详细的构建和打包说明
- [技术文档](CLAUDE.md) - 项目架构和API文档
- [OpenSpec规范](openspec/) - 标准化变更管理

## 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。

## 贡献指南

欢迎提交Issue和Pull Request。请确保：
1. 遵循现有的代码风格
2. 添加适当的测试
3. 更新相关文档

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交GitHub Issue
- 发送邮件至项目维护者

---

**注意**: 本项目正在积极开发中，某些功能可能还不稳定。建议在生产环境使用前进行充分测试。