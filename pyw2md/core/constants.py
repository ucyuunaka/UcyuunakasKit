"""
pyw2md 核心常量定义
Central constants for pyw2md core functionality
"""

# 文件变化类型
FILE_CHANGE_MODIFIED = 'modified'
FILE_CHANGE_DELETED = 'deleted'
FILE_CHANGE_CREATED = 'created'

# 防抖时间配置 (毫秒)
DEFAULT_DEBOUNCE_MS = 300
UI_UPDATE_DEBOUNCE_MS = 300
MESSAGE_DISPLAY_MS = 3000

# 文件监控配置
MAX_WATCH_ERRORS = 10
RESTART_COOLDOWN_MS = 1000

# UI 消息模板
MSG_FILE_MODIFIED = "文件已修改: {filename}"
MSG_FILE_DELETED = "文件已删除: {filename}"
MSG_REFRESH_COMPLETE = "已刷新: {modified} 个修改, {deleted} 个删除"
MSG_NO_CHANGES = "没有需要刷新的文件变化"
MSG_REFRESH_FAILED = "刷新失败: {error}"
MSG_WATCH_FAILED = "文件监控启动失败: {error}"
MSG_WATCH_RESTARTED = "文件监控已重新启动"

# 状态栏消息类型
MSG_TYPE_INFO = "info"
MSG_TYPE_SUCCESS = "success"
MSG_TYPE_WARNING = "warning"
MSG_TYPE_ERROR = "error"