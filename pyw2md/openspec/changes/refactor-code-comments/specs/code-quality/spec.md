## ADDED Requirements
### Requirement: 注释规范标准
项目SHALL遵循基于Linus实用主义原则的注释规范。

#### Scenario: 删除冗余注释
- **WHEN** 函数名已经明确说明功能时
- **THEN** 不添加docstring或行内注释

#### Scenario: 保留有价值的注释
- **WHEN** 代码包含复杂的业务逻辑决策或第三方库限制的workaround时
- **THEN** 保留简洁的中文注释说明原因

#### Scenario: 统一注释语言
- **WHEN** 需要添加注释时
- **THEN** 使用简体中文保持一致性

### Requirement: 代码自解释优先
代码结构MUST优先考虑自解释能力，减少对注释的依赖。

#### Scenario: 优化函数命名
- **WHEN** 函数功能需要注释才能理解时
- **THEN** 重构函数名使其更清晰地表达意图

#### Scenario: 简化复杂逻辑
- **WHEN** 代码逻辑复杂需要大量注释说明时
- **THEN** 拆分为更小的、自解释的函数

### Requirement: 注释质量保证
所有保留的注释SHALL提供有价值的信息，解释"为什么"而不是"是什么"。

#### Scenario: 什么需要注释
- **WHEN** 代码处理特殊边界情况或采用非常规实现时
- **THEN** 添加注释解释决策原因和考虑因素

#### Scenario: 什么不需要注释
- **WHEN** 代码逻辑直观、变量和函数名清晰时
- **THEN** 不添加任何注释