# 针对你的环境（Windows + Claude Code + PowerShell 7）的使用指南

## 📋 第一步：安装前提条件

确保你已安装以下工具：

```powershell
# 检查 Python 版本（需要 3.11+）
python --version

# 检查 Git
git --version

# 安装 uv（如果还没安装）
# 在 PowerShell 中运行：
irm https://astral.sh/uv/install.ps1 | iex
```

## 🚀 第二步：安装 Specify CLI

**推荐方式**（持久安装）：

```powershell
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
```

安装后可直接使用 `specify` 命令。

**升级命令**：
```powershell
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
```

```powershell
uptools
```

## 🎯 第三步：初始化项目

在 PowerShell 7 中运行：

```powershell
# 创建新项目（推荐为你的环境指定 PowerShell 脚本）
specify init my-project --ai claude --script ps

# 或者在当前目录初始化
specify init . --ai claude --script ps

# 或者使用 --here 标志
specify init --here --ai claude --script ps
```

**参数说明**：
- `--ai claude`：指定使用 Claude Code
- `--script ps`：使用 PowerShell 脚本（适合 Windows）

## 💻 第四步：在 Claude Code 中使用

1. **进入项目目录**：
```powershell
cd my-project
```

2. **启动 Claude Code**：
```powershell
claude
```

3. **验证命令可用**：
启动后应该能看到这些斜杠命令：
- `/speckit.constitution`
- `/speckit.specify`
- `/speckit.plan`
- `/speckit.tasks`
- `/speckit.implement`

## 📝 第五步：完整开发流程

### 1️⃣ 建立项目原则
```
/speckit.constitution 创建专注于代码质量、测试标准、用户体验一致性和性能要求的原则
```

### 2️⃣ 创建功能规格说明
```
/speckit.specify 构建一个照片管理应用，可以将照片组织到不同的相册中。相册按日期分组，可以在主页面通过拖放重新组织。相册之间不会嵌套。每个相册内，照片以瓷砖式界面预览。
```

### 3️⃣ 澄清需求（推荐，在 plan 之前）
```
/speckit.clarify
```

### 4️⃣ 创建技术实施计划
```
/speckit.plan 应用使用 Vite，尽量减少库的使用。尽可能使用原生 HTML、CSS 和 JavaScript。图片不会上传到任何地方，元数据存储在本地 SQLite 数据库中。
```

### 5️⃣ 生成任务分解
```
/speckit.tasks
```

### 6️⃣ 执行实施
```
/speckit.implement
```

## 🔧 常用检查命令

```powershell
# 检查系统是否安装了所需工具
specify check
```

## ⚠️ Windows 特别提示

1. **PowerShell 执行策略**：如果遇到脚本执行问题，可能需要调整执行策略：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. **路径问题**：Windows 使用反斜杠 `\`，但在命令中通常可以使用正斜杠 `/`

3. **Git 配置**：确保 Git 已正确配置用户信息：
```powershell
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## 📚 项目结构

初始化后你的项目会是这样的：

```
my-project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md
│   ├── scripts/          # PowerShell 脚本（因为用了 --script ps）
│   ├── specs/           # 功能规格说明
│   └── templates/       # 模板文件
└── CLAUDE.md           # Claude Code 的配置文件
```




看起来安装成功了！但还有**一个重要步骤**需要完成，另外我来回答你的更新问题。

## ⚠️ 首先：添加到 PATH（必须做）

你需要让系统能找到 `specify` 命令。有两种方法：

### 方法一：自动配置（推荐）✅

```powershell
uv tool update-shell
```

然后**重启 PowerShell**，这样就永久生效了。

### 方法二：手动永久添加

如果方法一不行，在 PowerShell 中运行：

```powershell
# 永久添加到用户环境变量
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$userPath;C:\Users\ucy\.local\bin", "User")
```

然后**重启 PowerShell**。

### 验证是否成功

重启 PowerShell 后运行：

```powershell
specify check
```

如果看到输出，说明配置成功了！

## 🔄 关于自动更新

好消息！**有更简单的更新命令**，不用记那么长的命令：

### 更新 specify-cli

```powershell
# 只更新 specify-cli
uv tool upgrade specify-cli

# 或者更新所有通过 uv 安装的工具
uv tool upgrade --all
```

### 查看已安装的工具

```powershell
# 查看所有已安装的 uv 工具
uv tool list
```

### 完全自动更新？

目前 `uv` **没有完全自动更新**的功能（类似浏览器那种），但你可以：

**选项 1：创建一个更新脚本**

创建文件 `update-tools.ps1`：

```powershell
# update-tools.ps1
Write-Host "更新 UV 工具..." -ForegroundColor Cyan
uv tool upgrade --all
Write-Host "✓ 更新完成！" -ForegroundColor Green
```

然后每隔一段时间运行：
```powershell
.\update-tools.ps1
```

**选项 2：创建 PowerShell 别名**（最方便）

在你的 PowerShell 配置文件中添加：

```powershell
# 编辑配置文件
notepad $PROFILE

# 在打开的文件中添加这一行：
function Update-DevTools { uv tool upgrade --all }
Set-Alias uptools Update-DevTools
```

保存后，以后只需要运行：
```powershell
uptools
```

就能更新所有工具了！

## 📝 总结

你现在需要做的：

1. ✅ **立即执行**：
   ```powershell
   uv tool update-shell
   ```
   
2. ✅ **重启 PowerShell**

3. ✅ **验证**：
   ```powershell
   specify check
   ```

4. ✅ **以后更新只需要**：
   ```powershell
   uv tool upgrade specify-cli
   ```

这样就完全配置好了！需要我继续讲解如何初始化第一个项目吗？