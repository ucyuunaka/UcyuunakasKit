# 统一多组件状态更新机制

## Why

pyw2md项目中多组件状态更新机制存在不协调问题，导致性能浪费、代码维护困难和用户体验不一致。具体表现为控制面板的废弃方法仍在调用、各组件防抖时间不统一、统计逻辑分散，需要通过重构建立统一的状态管理架构。

## What Changes

- 移除所有冗余的`control_panel.update_stats()`调用
- 统一所有UI组件的防抖时间为300ms
- 强化StatusBar作为统计信息中心的角色
- 实现批量更新优化和缓存机制
- 建立统一的状态更新接口和规范

## Impact

- Affected specs: `ui-state-management`, `component-interaction`
- Affected code:
  - `ui/app.py` - 主应用，移除冗余调用
  - `ui/components/control_panel.py` - 清理废弃方法
  - `ui/components/file_list_panel.py` - 统一防抖时间
  - `ui/components/status_bar.py` - 强化统计中心角色

## 实施策略

采用渐进式重构：
1. 第一阶段：移除冗余调用，立即解决性能浪费问题
2. 第二阶段：统一防抖机制，提升用户体验一致性
3. 第三阶段：优化统计逻辑，增强可维护性

## 验收标准

- 所有`control_panel.update_stats()`调用被移除
- 所有组件使用统一的300ms防抖时间
- 统计信息只通过StatusBar更新
- 功能测试通过，无回归问题
- 性能提升30%以上（批量操作场景）