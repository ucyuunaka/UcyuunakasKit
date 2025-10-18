# DPI Scaling Support Design

## Architecture Overview

### DPI Detection Module
Create a new module `utils/dpi_helper.py` to handle platform-specific DPI detection:

```python
class DPIHelper:
    """跨平台DPI检测和缩放辅助类"""

    @staticmethod
    def get_system_dpi() -> float:
        """获取系统DPI设置"""

    @staticmethod
    def get_scaling_factor() -> float:
        """计算缩放因子（相对于96 DPI）"""

    @staticmethod
    def set_dpi_awareness() -> None:
        """设置应用程序DPI感知（Windows）"""
```

### Integration Points

1. **Application Startup (main.py)**
   - 在创建任何UI之前调用DPI设置
   - 设置进程DPI感知级别

2. **Theme System (config/theme.py)**
   - 修改字体定义为可调用的函数
   - 根据缩放因子动态计算字体大小

3. **Configuration System (config/settings.py)**
   - 添加DPI相关配置项
   - 支持用户手动覆盖自动检测

4. **UI Components**
   - 在初始化时应用缩放后的尺寸
   - 保持布局比例一致性

## Platform-Specific Implementation

### Windows
- 使用 `ctypes` 调用 Windows API
- 支持 `SetProcessDpiAwareness` 和 `GetDpiForSystem`
- 处理每显示器DPI感知

### Linux
- 检测 `GDK_SCALE` 环境变量
- 使用 `tk scaling` 命令
- 支持主流桌面环境

### macOS
- 使用 `tk scaling` 自动检测
- 处理Retina显示器的缩放

## Scaling Strategy

1. **Automatic Detection**
   - 启动时自动检测系统DPI
   - 计算相对于96 DPI的缩放因子
   - 应用到所有UI元素

2. **Font Scaling**
   - 基础字体大小乘以缩放因子
   - 保持字体比例关系
   - 支持最小/最大字体大小限制

3. **Layout Scaling**
   - 间距和边距按比例调整
   - 控件尺寸保持相对比例
   - 避免硬编码像素值

## Configuration Options

```json
{
  "dpi_scaling": {
    "auto_detect": true,
    "scaling_factor": 1.0,
    "min_font_size": 8,
    "max_font_size": 24
  }
}
```

## Testing Strategy

1. **Virtual Machine Testing**
   - Windows: 125%, 150%, 200% 缩放
   - Linux: GNOME/KDE 不同缩放设置
   - macOS: Retina 和非Retina 显示器

2. **Automated Testing**
   - 模拟不同DPI环境
   - 验证字体大小计算
   - 检查UI元素比例

## Backward Compatibility

- 默认保持当前行为（无缩放）
- 通过配置启用DPI适配
- 提供禁用选项用于故障排除