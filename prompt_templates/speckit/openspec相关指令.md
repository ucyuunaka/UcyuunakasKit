
### 第三步：在项目中初始化

```powershell
cd your-project-path  # 进入你的项目目录
openspec init
```

**初始化时会询问你使用的 AI 工具**，选择 **Claude Code**（会自动配置斜杠命令）

完成后会创建以下结构：
```
your-project/
├── openspec/
│   ├── specs/          # 当前规范（真实来源）
│   ├── changes/        # 提案/进行中的变更
│   └── archive/        # 已完成的变更
├── AGENTS.md           # AI 助手使用说明
└── .claudecodeignore  # Claude Code 配置（自动生成）
```

---

## 核心工作流程（在 Claude Code 中使用）

### 1️⃣ 创建变更提案

**在 Claude Code 聊天框中输入：**

```
/openspec:proposal 添加用户登录功能
```

或者自然语言：
```
请创建一个 OpenSpec 变更提案，用于添加用户登录功能
```

Claude Code 会自动生成：
- `openspec/changes/add-user-login/proposal.md` （变更说明）
- `openspec/changes/add-user-login/tasks.md` （任务清单）
- `openspec/changes/add-user-login/specs/...` （规范增量）

---

### 2️⃣ 验证和审查

**在 PowerShell 中运行：**

```powershell
# 查看所有变更
openspec list

# 验证格式
openspec validate add-user-login

# 查看详细内容
openspec show add-user-login

# 或使用交互式仪表板
openspec view
```

如果需要修改规范，直接在 Claude Code 中说：
```
请在登录规范中添加"记住我"功能的验收标准
```

---

### 3️⃣ 实施变更

**确认规范无误后，在 Claude Code 中输入：**

```
/openspec:apply add-user-login
```

或：
```
规范看起来不错，请开始实施这个变更
```

Claude Code 会：
- 读取 `tasks.md` 中的任务列表
- 逐步实现代码
- 标记完成的任务（✓）

---

### 4️⃣ 归档变更

**所有任务完成后，在 Claude Code 中输入：**

```
/openspec:archive add-user-login
```

或在 PowerShell 中直接运行：
```powershell
openspec archive add-user-login --yes
```

这会：
- 将变更文件夹移到 `openspec/archive/`
- 将规范增量合并到 `openspec/specs/`
- 更新真实来源文档

---

## 常用命令速查

| 命令                           | 说明                |
| ---------------------------- | ----------------- |
| openspec list                | 列出所有活动变更          |
| openspec view                | 交互式仪表板            |
| openspec show <变更名>          | 显示变更详情            |
| openspec validate <变更名>      | 验证格式              |
| openspec archive <变更名> --yes | 归档变更（无交互）         |
| openspec update              | 更新 AI 指令（切换工具时使用） |

---

## Claude Code 专属快捷命令

| 快捷命令                    | 完整说明      |
| ----------------------- | --------- |
| /openspec:proposal <描述> | 创建新的变更提案  |
| /openspec:apply <变更名>   | 应用/实施指定变更 |
| /openspec:archive <变更名> | 归档已完成的变更  |

---

## 实际例子：添加深色模式

### 在 Claude Code 中操作：

```
你: /openspec:proposal 添加深色模式支持

Claude: 我已创建变更提案 add-dark-mode，包含：
        - 主题切换按钮
        - 颜色变量定义
        - 用户偏好存储
```

### 在 PowerShell 中验证：

```powershell
openspec validate add-dark-mode
openspec show add-dark-mode
```

### 继续在 Claude Code 中：

```
你: 请在设计文档中说明颜色对比度需符合 WCAG AA 标准

Claude: 已更新 design.md，添加无障碍要求

你: /openspec:apply add-dark-mode

Claude: 开始实施...
        ✓ 1.1 添加主题上下文
        ✓ 1.2 定义颜色变量
        ✓ 2.1 实现切换按钮
        ...

你: /openspec:archive add-dark-mode

Claude: 变更已归档，规范已更新 ✓
```

---

## 故障排除

### Claude Code 看不到斜杠命令？

1. **重启 Claude Code**（斜杠命令在启动时加载）
2. 确认项目根目录有 `.claudecodeignore` 或相关配置文件
3. 重新运行 `openspec init` 并选择 Claude Code

### 升级 OpenSpec

```powershell
# 更新全局包
npm install -g @fission-ai/openspec@latest

# 在项目目录中刷新配置
cd your-project
openspec update
```

---

## 高级技巧

### 跨多个规范的变更

```
/openspec:proposal 重构认证系统

# Claude Code 会自动识别需要更新：
# - openspec/changes/refactor-auth/specs/auth/spec.md
# - openspec/changes/refactor-auth/specs/session/spec.md
# - openspec/changes/refactor-auth/specs/api/spec.md
```

### 查看归档历史

```powershell
ls openspec/archive/  # 查看所有已完成的功能
```

---

更新
```powershell
uptools```
