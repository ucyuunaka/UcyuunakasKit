## Why
当前刷新操作会动态创建和销毁通知栏，导致UI布局重排和视觉闪烁，影响用户体验。

## What Changes
- 将通知栏改为常驻组件，初始状态显示默认提示信息
- 刷新操作时更新通知栏内容而非创建/销毁组件
- 添加平滑过渡动画减少视觉突兀感
- 优化通知栏布局避免影响主要内容区域

## Impact
- Affected specs: ui
- Affected code: ui/app.py, ui/components/file_list_panel.py