# 自动化构建系统设计文档

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    自动化构建系统                           │
├─────────────────────────────────────────────────────────────┤
│  build.py (主构建脚本)                                      │
│  ├── 依赖检测和分析                                         │
│  ├── 版本管理                                               │
│  ├── PyInstaller调用                                        │
│  └── 构建验证和报告                                         │
├─────────────────────────────────────────────────────────────┤
│  配置层                                                    │
│  ├── pyw2md.spec (PyInstaller配置)                         │
│  ├── requirements.txt (依赖声明)                            │
│  └── build_config.json (构建配置)                          │
├─────────────────────────────────────────────────────────────┤
│  工具层                                                    │
│  ├── utils/packaging.py (现有打包工具)                      │
│  ├── utils/version_manager.py (版本管理 - 新增)             │
│  └── utils/build_helper.py (构建辅助 - 新增)                │
└─────────────────────────────────────────────────────────────┘
```

## 核心组件设计

### 1. 主构建脚本 (build.py)

**职责**: 协调整个构建流程，提供统一的构建入口

**主要功能**:
- 解析命令行参数
- 执行构建前检查
- 调用PyInstaller执行打包
- 验证构建结果
- 生成构建报告

**接口设计**:
```python
def main():
    """主构建函数"""
    parser = setup_arg_parser()
    args = parser.parse_args()
    
    if args.clean:
        clean_build_artifacts()
    
    if args.version:
        update_version(args.version)
    
    success = build_executable(args)
    
    if success:
        generate_build_report()
        print("✅ 构建成功!")
    else:
        print("❌ 构建失败!")
        sys.exit(1)
```

### 2. PyInstaller配置 (pyw2md.spec)

**职责**: 定义打包的具体参数和包含规则

**关键配置项**:
- `--onefile`: 生成单文件exe
- `--windowed`: 无控制台窗口
- 图标和元数据设置
- 隐藏导入列表
- 数据文件包含规则
- 排除文件规则

### 3. 版本管理器 (utils/version_manager.py)

**职责**: 自动管理应用版本号

**功能特性**:
- 读取当前版本号
- 自动递增版本号
- 版本标记和Git标签
- 版本信息写入代码

**版本格式**: `MAJOR.MINOR.PATCH` (语义化版本)

### 4. 构建辅助工具 (utils/build_helper.py)

**职责**: 提供构建过程中的辅助功能

**功能模块**:
- 依赖分析器
- 资源文件收集器
- 构建环境检查
- 错误诊断工具

## 构建流程设计

### 构建前检查
1. **环境验证**
   - Python版本检查
   - PyInstaller安装检查
   - 必要依赖库检查

2. **项目验证**
   - 项目结构完整性
   - 配置文件有效性
   - 资源文件存在性

3. **版本处理**
   - 读取当前版本
   - 根据参数更新版本
   - 写入版本信息

### 构建执行
1. **依赖收集**
   - 分析import语句
   - 收集隐藏依赖
   - 处理特殊情况(如tkinterdnd2)

2. **资源打包**
   - 配置文件包含
   - 图标和静态资源
   - 数据文件处理

3. **PyInstaller调用**
   - 生成spec文件
   - 执行打包命令
   - 监控构建过程

### 构建后处理
1. **结果验证**
   - 检查exe文件生成
   - 验证文件完整性
   - 测试基本启动

2. **清理工作**
   - 清理临时文件
   - 整理构建产物
   - 更新构建日志

## 技术实现细节

### 依赖处理策略

**自动发现的依赖**:
- 通过ast模块分析Python文件
- 收集所有import语句
- 识别第三方库

**特殊处理**:
- `customtkinter`: 需要包含主题和资源文件
- `tkinterdnd2`: 需要包含DLL文件
- `PIL/Pillow`: 可能需要图像处理插件

### 资源文件管理

**配置文件**:
- `config.json`: 应用配置
- `config/*.json`: 配置目录

**静态资源**:
- 图标文件 (如果存在)
- 主题文件
- 样式表

### 版本管理实现

**版本文件**: `VERSION` 或从 `__init__.py` 读取
```python
# 版本信息格式
__version__ = "1.0.0"
__build_date__ = "2025-10-20"
__git_commit__ = "abc123"
```

**自动更新逻辑**:
```python
def bump_version(version_type='patch'):
    """递增版本号"""
    current = read_version()
    if version_type == 'major':
        new = f"{current.major + 1}.0.0"
    elif version_type == 'minor':
        new = f"{current.major}.{current.minor + 1}.0"
    else:  # patch
        new = f"{current.major}.{current.minor}.{current.patch + 1}"
    
    write_version(new)
    return new
```

## 错误处理和恢复

### 常见错误类型
1. **依赖缺失**: 提供安装命令建议
2. **权限问题**: 指导权限设置
3. **磁盘空间**: 检查可用空间
4. **路径问题**: 使用绝对路径
5. **PyInstaller错误**: 提供具体解决方案

### 错误恢复机制
- 详细的错误日志
- 自动修复尝试
- 用户友好的错误提示
- 重新构建选项

## 性能优化

### 构建速度优化
- 增量构建支持
- 缓存机制
- 并行处理
- 智能依赖分析

### 输出大小优化
- 排除不必要的模块
- 压缩选项配置
- UPX压缩集成
- 依赖树优化

## 扩展性考虑

### 多平台支持
- 平台特定配置
- 跨平台构建脚本
- CI/CD集成准备

### 未来扩展
- 插件系统支持
- 自定义构建配置
- 自动发布集成
- 构建历史管理