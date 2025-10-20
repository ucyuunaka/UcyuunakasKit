## MODIFIED Requirements

### Requirement: UI状态更新机制

系统SHALL提供统一的UI状态更新机制，确保各组件状态同步，移除所有冗余的状态更新调用。

#### Scenario: 状态更新触发
- **WHEN** 文件列表发生变化
- **THEN** 所有相关UI组件应在300ms内完成状态更新
- **AND** 不应触发冗余的control_panel.update_stats()调用

#### Scenario: 冗余调用移除验证
- **WHEN** 执行文件添加、删除或转换操作
- **THEN** 系统中不应存在任何control_panel.update_stats()调用
- **AND** 状态栏应通过统一接口更新统计信息

### Requirement: 防抖机制

所有UI更新操作SHALL实现统一的防抖机制，防抖时间统一为300ms，避免频繁更新。

#### Scenario: 快速连续操作
- **WHEN** 用户在300ms内连续执行多次操作
- **THEN** 只执行最后一次操作对应的状态更新
- **AND** 所有组件使用相同的300ms防抖时间

#### Scenario: 防抖时间一致性验证
- **WHEN** 检查file_list_panel、主应用和其他组件的防抖设置
- **THEN** 所有组件应使用统一的UI_UPDATE_DEBOUNCE = 300常量

### Requirement: 统计信息更新

统计信息SHALL通过统一接口更新，由StatusBar作为唯一的信息展示中心，避免冗余调用。

#### Scenario: 文件添加后的统计更新
- **WHEN** 新文件被添加到列表
- **THEN** 状态栏应显示最新的文件数量和总大小
- **AND** 统计更新应直接通过StatusBar的更新接口
- **AND** 不应触发任何中间组件的冗余统计更新

#### Scenario: 批量操作后的统计更新
- **WHEN** 执行批量文件操作
- **THEN** StatusBar应支持批量更新模式
- **AND** 所有统计信息应在批量操作完成后统一更新

## ADDED Requirements

### Requirement: 批量更新优化

系统SHALL支持批量更新模式，优化大量文件操作时的性能。

#### Scenario: 批量更新模式
- **WHEN** 开始批量文件操作
- **THEN** StatusBar应进入批量更新模式
- **AND** 所有统计更新应被缓存
- **AND** 在批量操作结束后统一刷新UI

### Requirement: 状态更新缓存机制

系统SHALL实现状态更新缓存机制，避免重复计算相同的统计信息。

#### Scenario: 缓存命中
- **WHEN** 连续两次请求相同的统计信息
- **THEN** 第二次应从缓存获取
- **AND** 不应重新计算统计信息

### Requirement: 状态一致性检查

系统SHALL定期检查UI状态的一致性，确保各组件显示的信息同步。

#### Scenario: 状态不一致检测
- **WHEN** FileListPanel和StatusBar显示的文件数量不一致
- **THEN** 系统应自动触发状态同步
- **AND** 以FileHandler的实际数据为准更新所有组件