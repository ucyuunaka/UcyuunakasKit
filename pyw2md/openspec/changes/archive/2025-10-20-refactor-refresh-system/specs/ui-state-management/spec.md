## MODIFIED Requirements

### Requirement 1: UI状态更新机制

系统应提供统一的UI状态更新机制，确保各组件状态同步。

#### Scenario: 状态更新触发
- **WHEN** 文件列表发生变化
- **THEN** 所有相关UI组件应在300ms内完成状态更新
- **AND** 状态更新应通过统一的防抖机制执行

#### Scenario: 文件变化状态管理
- **WHEN** 文件被修改或删除
- **THEN** 文件变化状态应通过 `FileStateManager` 统一管理
- **AND** 状态变化应包含文件路径和变化类型

### Requirement 2: 防抖机制

所有UI更新操作应使用统一的防抖机制，避免频繁更新。

#### Scenario: 快速连续操作
- **WHEN** 用户在300ms内连续执行多次操作
- **THEN** 只执行最后一次操作对应的状态更新
- **AND** 防抖时间应统一为300ms

#### Scenario: 文件监控防抖
- **WHEN** 文件系统检测到文件变化事件
- **THEN** 应使用300ms防抖延迟处理变化事件
- **AND** 防抖机制应支持批量处理多个文件变化

### Requirement 3: 统计信息更新

统计信息应通过统一接口更新，避免冗余调用。

#### Scenario: 文件添加后的统计更新
- **WHEN** 新文件被添加到列表
- **THEN** 状态栏应显示最新的文件数量和总大小
- **AND** 不应触发冗余的统计更新调用

#### Scenario: 文件变化后的统计更新
- **WHEN** 文件被检测到修改或删除
- **THEN** 统计信息应通过统一的状态管理器更新
- **AND** 更新应使用防抖机制避免频繁刷新

## ADDED Requirements

### Requirement 4: 文件状态管理器

系统应提供统一的文件状态管理器，集中管理所有文件变化状态。

#### Scenario: 状态变化记录
- **WHEN** 文件系统检测到文件变化
- **THEN** `FileStateManager` 应记录变化类型、文件路径和时间戳
- **AND** 状态记录应支持线程安全访问

#### Scenario: 批量状态处理
- **WHEN** 应用需要处理文件变化
- **THEN** `FileStateManager` 应提供批量获取和清除状态的方法
- **AND** 处理完成后状态应被自动清除

### Requirement 5: 简化的通知系统

系统应使用简化的通知机制显示文件变化，避免复杂的UI组件。

#### Scenario: 文件变化通知
- **WHEN** 检测到文件变化
- **THEN** 系统应通过状态栏显示简洁的变化消息
- **AND** 消息应包含变化文件的数量和类型

#### Scenario: 通知消息管理
- **WHEN** 多个文件变化事件同时发生
- **THEN** 通知消息应合并显示，避免消息堆积
- **AND** 消息显示应使用统一的防抖时间

## REMOVED Requirements

### Requirement: 复杂通知栏组件

**Reason**: 复杂的通知栏UI组件与简单的信息显示需求不匹配，增加了不必要的交互复杂度。

**Migration**: 
- 移除 `notification_bar` 和相关的UI组件
- 使用状态栏的 `show_message()` 方法替代
- 保持消息内容的一致性，确保用户理解