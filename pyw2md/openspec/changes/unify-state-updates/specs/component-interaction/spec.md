## MODIFIED Requirements

### Requirement: 组件通信机制

系统SHALL提供标准化的组件间通信机制，状态更新应通过主应用统一协调，避免组件间的直接依赖。

#### Scenario: 组件状态同步
- **WHEN** 一个组件的状态发生变化
- **THEN** 相关组件应通过事件机制获得通知
- **AND** 状态更新应通过主应用的统一协调器进行
- **AND** 不应存在组件间的直接方法调用

#### Scenario: 统一协调器验证
- **WHEN** 检查app.py中的状态更新逻辑
- **THEN** 应存在_sync_ui_state()或类似的方法
- **AND** 所有状态更新应通过该方法协调

### Requirement: 批量操作支持

组件SHALL支持批量操作模式，通过StatusBar的批量更新接口优化性能。

#### Scenario: 批量文件操作
- **WHEN** 用户执行批量文件添加/删除
- **THEN** 组件应进入批量更新模式
- **AND** 所有更新应在批量结束后统一应用
- **AND** StatusBar应提供begin_batch_update()和end_batch_update()接口

#### Scenario: 批量更新性能验证
- **WHEN** 执行100个文件的批量添加
- **THEN** UI更新次数应显著减少（理想情况下为1次）
- **AND** 内存使用应保持稳定

### Requirement: 状态栏角色

状态栏SHALL作为统计信息的唯一展示中心，其他组件不应直接更新或显示统计信息。

#### Scenario: 统计信息更新
- **WHEN** 文件状态发生变化
- **THEN** 状态栏应通过统一接口更新显示
- **AND** 其他组件不应直接更新统计信息
- **AND** ControlPanel不应包含任何统计更新方法

#### Scenario: 状态栏接口验证
- **WHEN** 检查StatusBar类的方法
- **THEN** 应存在update_file_stats()等统一更新接口
- **AND** 不应存在其他组件直接修改统计标签的方法

## ADDED Requirements

### Requirement: 组件解耦设计

系统SHALL实现组件间的松耦合设计，避免直接的方法调用，使用事件或回调机制进行通信。

#### Scenario: 组件依赖检查
- **WHEN** 分析FileListPanel、ControlPanel和StatusBar的依赖关系
- **THEN** 不应存在组件间的直接import或方法调用
- **AND** 所有交互应通过主应用协调

### Requirement: 状态更新事务性

系统SHALL支持事务性的状态更新，确保在错误情况下可以回滚到一致状态。

#### Scenario: 更新失败回滚
- **WHEN** 状态更新过程中发生错误
- **THEN** 系统应捕获错误并记录日志
- **AND** 应尝试恢复到上一个已知的一致状态
- **AND** 用户应收到友好的错误提示

### Requirement: 性能监控接口

系统SHALL提供性能监控接口，用于跟踪状态更新的性能指标。

#### Scenario: 性能数据收集
- **WHEN** 执行状态更新操作
- **THEN** 系统应记录更新耗时
- **AND** 应统计批量操作的优化效果
- **AND** 在调试模式下应显示性能日志