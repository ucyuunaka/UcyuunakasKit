# 移除冗余状态更新调用

## ADDED Requirements

### Requirement 1: 识别所有冗余的update_stats()调用

#### Scenario: 搜索代码库中的所有update_stats调用
- **Given**: 完整的pyw2md代码库
- **When**: 执行全局搜索`update_stats()`
- **Then**: 应该找到以下调用位置：
  - `ui/app.py` 第464行（在`_on_drop_complete`方法中）
  - `ui/app.py` 第757行（在`_on_files_refreshed`方法中）

### Requirement 2: 安全移除app.py中的冗余调用

#### Scenario: 移除第464行的冗余调用
- **Given**: `app.py`文件中的`_on_drop_complete`方法
- **When**: 移除`self.control_panel.update_stats()`调用
- **Then**:
  - 文件添加功能仍然正常工作
  - 状态栏统计信息正确更新
  - 无控制台错误

#### Scenario: 移除第757行的冗余调用
- **Given**: `app.py`文件中的`_on_files_refreshed`方法
- **When**: 移除`self.control_panel.update_stats()`调用
- **Then**:
  - 文件刷新功能仍然正常工作
  - 状态栏统计信息正确更新
  - 无控制台错误

## MODIFIED Requirements

### Requirement 3: 更新调用后的状态更新逻辑

#### Scenario: 确保状态栏统计正确更新
- **Given**: 移除了冗余调用后的代码
- **When**: 执行文件添加或刷新操作
- **Then**:
  - 应该调用`self._update_status_bar_stats()`来更新统计
  - 状态栏应该显示正确的文件数量和总大小
  - 更新应该在UI线程中执行

### Requirement 4: 保持消息通知功能

#### Scenario: 验证操作反馈消息
- **Given**: 移除了control_panel更新调用的代码
- **When**: 执行文件操作
- **Then**:
  - 应该仍然显示相应的toast消息
  - 消息内容应该准确反映操作结果
  - 消息类型（成功/错误）应该正确

## REMOVED Requirements

### Requirement 5: 废弃的update_stats方法调用

#### Scenario: 确认没有遗漏的调用
- **Given**: 清理后的代码库
- **When**: 再次搜索`update_stats()`
- **Then**: 应该只找到方法定义，没有调用处

## 测试要求

### Requirement 6: 功能回归测试

#### Scenario: 文件拖放操作测试
- **Given**: 清理后的应用程序
- **When**: 拖放多个文件到应用窗口
- **Then**:
  - 文件列表正确显示新文件
  - 状态栏统计正确更新
  - 显示成功添加的toast消息

#### Scenario: 文件刷新操作测试
- **Given**: 清理后的应用程序
- **When**: 点击刷新按钮
- **Then**:
  - 文件列表正确刷新
  - 不存在的文件被移除
  - 状态栏统计正确更新

### Requirement 7: 性能验证

#### Scenario: 大量文件操作性能测试
- **Given**: 包含1000+文件的项目
- **When**: 执行批量文件添加
- **Then**:
  - 响应时间应该比之前更快（减少了冗余调用）
  - 内存使用没有异常增长
  - UI保持响应