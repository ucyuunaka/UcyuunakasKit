# 集中管理统计信息逻辑

## ADDED Requirements

### Requirement 1: 强化StatusBar的统计中心接口

#### Scenario: 创建统一的统计更新接口
- **Given**: `ui/components/status_bar.py`中的StatusBar类
- **When**: 添加以下公共方法：
  ```python
  def update_file_stats(self, file_count: int, total_size: int, selected_count: int = 0)
  def update_conversion_stats(self, converted_count: int, failed_count: int)
  def update_filter_stats(self, total_files: int, filtered_files: int)
  ```
- **Then**:
  - 所有统计信息都通过这些接口更新
  - 接口支持批量更新优化
  - 提供实时更新和延迟更新选项

### Requirement 2: 实现统计信息缓存机制

#### Scenario: 添加统计缓存避免重复计算
- **Given**: StatusBar需要频繁更新统计信息
- **When**: 实现内部缓存机制：
  ```python
  class StatusBar:
      def __init__(self):
          self._stats_cache = {
              'file_count': 0,
              'total_size': 0,
              'selected_count': 0,
              'converted_count': 0,
              'failed_count': 0
          }
  ```
- **Then**:
  - 相同数值不重复更新UI
  - 提供缓存验证机制
  - 支持强制刷新缓存

### Requirement 3: 创建批量更新优化

#### Scenario: 支持批量操作后的统一更新
- **Given**: 批量添加或删除多个文件
- **When**: 使用批量更新接口：
  ```python
  def begin_batch_update(self)
  def end_batch_update(self)
  ```
- **Then**:
  - 批量操作期间暂停实时更新
  - 批量结束后统一更新UI
  - 减少UI刷新次数提高性能

## MODIFIED Requirements

### Requirement 4: 重构主应用的状态更新调用

#### Scenario: 统一使用StatusBar更新统计
- **Given**: `ui/app.py`中的状态更新逻辑
- **When**: 修改所有统计更新为调用StatusBar接口：
  ```python
  # 原代码
   self._update_status_bar_stats()

  # 新代码
   self.status_bar.update_file_stats(
       file_count=len(self.file_handler.get_files()),
       total_size=self.file_handler.get_total_size(),
       selected_count=len(self.file_handler.get_selected_files())
   )
  ```
- **Then**:
  - 统计信息准确显示
  - 代码意图更清晰
  - 便于维护和调试

#### Scenario: 优化文件变化后的状态更新
- **Given**: 文件被添加、删除或修改
- **When**: 统一状态更新流程：
  ```python
  def _on_file_update(self):
      """文件更新后的统一处理"""
      # 获取最新统计信息
      stats = self.file_handler.get_statistics()

      # 批量更新StatusBar
      self.status_bar.begin_batch_update()
      self.status_bar.update_file_stats(**stats['file'])
      self.status_bar.update_filter_stats(**stats['filter'])
      self.status_bar.end_batch_update()
  ```
- **Then**:
  - 所有相关统计同时更新
  - 避免UI闪烁
  - 提高更新性能

### Requirement 5: 优化统计信息计算逻辑

#### Scenario: 在FileHandler中集中统计计算
- **Given**: `core/file_handler.py`中的文件管理逻辑
- **When**: 添加统计信息计算方法：
  ```python
  def get_statistics(self):
      """获取完整的统计信息"""
      files = self.get_files()
      selected = self.get_selected_files()

      return {
          'file': {
              'file_count': len(files),
              'total_size': sum(f.size for f in files),
              'selected_count': len(selected)
          },
          'filter': {
              'total_files': len(self.all_files),
              'filtered_files': len(files)
          }
      }
  ```
- **Then**:
  - 统计计算逻辑集中管理
  - 避免重复遍历文件列表
  - 提供完整的统计视图

### Requirement 6: 实现智能更新策略

#### Scenario: 根据操作类型选择更新策略
- **Given**: 不同类型的用户操作
- **When**: 实现智能更新：
  - 单个文件操作：实时更新
  - 批量文件操作：批量更新
  - 过滤操作：只更新过滤相关统计
- **Then**:
  - 最小化UI更新开销
  - 保持界面响应性
  - 提供最佳用户体验

## 性能要求

### Requirement 7: 更新性能基准

#### Scenario: 大量文件统计更新性能
- **Given**: 包含10000个文件的项目
- **When**: 执行批量更新操作
- **Then**:
  - 统计更新时间 < 50ms
  - UI无卡顿感
  - 内存使用无异常增长

### Requirement 8: 缓存有效性验证

#### Scenario: 验证缓存机制的有效性
- **Given**: 启用缓存机制的StatusBar
- **When**: 重复更新相同的统计值
- **Then**:
  - UI更新调用次数减少90%+
  - 统计信息保持准确
  - 无缓存不一致问题

## 测试要求

### Requirement 9: 统计准确性测试

#### Scenario: 验证各类统计信息的准确性
- **Given**: 已知数量和大小的文件集合
- **When**: 执行各种文件操作
- **Then**:
  - 文件计数始终准确
  - 总大小计算正确
  - 选中文件数正确

#### Scenario: 边界条件测试
- **Given**: 极端情况（空列表、单文件、最大文件数）
- **When**: 更新统计信息
- **Then**:
  - 空列表显示为"0文件"
  - 单文件信息显示正确
  - 大文件数使用合适单位（KB/MB/GB）

### Requirement 10: 并发更新测试

#### Scenario: 快速连续操作测试
- **Given**: 启用批量更新的StatusBar
- **When**: 快速连续添加/删除文件
- **Then**:
  - 批量更新正确工作
  - 最终统计信息准确
  - 无竞态条件

## 可维护性要求

### Requirement 11: 代码清晰度

#### Scenario: 统计更新代码的可读性
- **Given**: 重构后的统计更新代码
- **When**: 新开发者阅读代码
- **Then**:
  - 更新意图清晰明确
  - 方法命名合理
  - 有充分的注释说明

### Requirement 12: 扩展性支持

#### Scenario: 添加新的统计类型
- **Given**: 需要添加新的统计信息
- **When**: 扩展StatusBar接口
- **Then**:
  - 可以方便地添加新方法
  - 不影响现有功能
  - 遵循相同的模式