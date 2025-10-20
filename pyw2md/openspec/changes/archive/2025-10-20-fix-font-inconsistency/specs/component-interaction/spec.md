# 组件交互

## MODIFIED Requirements

### Requirement 1: 组件通信机制

系统 MUST 提供标准化的组件间通信机制，并使用统一的字体方法。

#### Scenario: 组件状态同步
- **WHEN** 一个组件的状态发生变化
- **THEN** 相关组件应通过事件机制获得通知
- **AND** 状态更新应通过统一的协调器进行
- **AND** 所有组件应使用动态字体方法而不是静态字体常量

#### Scenario: 统一字体方法
**Given** UI组件需要设置字体
**When** 组件初始化时
**Then** FileListPanel应调用 `MD.get_font_headline()` 而不是使用 `MD.FONT_HEADLINE`
**And** Btn控件应使用 `MD.get_font_ui()` 而不是 `MD.FONT_UI`
**And** StatusBar应使用 `MD.get_font_body()` 而不是 `MD.FONT_BODY`

#### Scenario: 无表情符号UI
**Given** UI组件需要显示图标或文本
**When** 渲染UI元素时
**Then** 应使用文本标签而不是表情符号图标
**And** 状态消息应使用文本描述而不是表情符号指示器
**And** 对话框标题不应包含表情符号字体或字符

#### Scenario: 文本标签替换
**Given** 系统使用表情符号作为图标
**When** 显示部分标题时
**Then** "📂" 图标应显示为 "文件管理" 文本标签
**And** "⚙️" 图标应显示为 "转换设置" 文本标签
**And** 操作反馈应使用清晰的文本描述而不是表情符号