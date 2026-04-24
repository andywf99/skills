---
name: install-ai-coding-collector
description: 安装 AI Coding 代码采集工具 git-ai，仅支持 Windows 系统。自动检测系统平台，检查是否已安装，未安装则通过 PowerShell 执行远程安装脚本。
triggers:
  - 安装git-ai
  - 安装 git-ai
  - 安装AI Coding采集工具
  - 安装代码采集工具
  - 配置git-ai
---

# 安装 AI Coding 代码采集工具 (git-ai)

## 适用场景

- 需要安装 git-ai 代码采集工具
- 新机器初始化开发环境时需要配置代码采集

## 第1步：环境检查

同时检查管理员权限和操作系统：

```bash
net session > /dev/null 2>&1 && echo "ADMIN" || echo "NOT_ADMIN"
```

```bash
uname -s
```

**判断逻辑：**
- `NOT_ADMIN`：**停止执行**，提示用户「当前终端没有管理员权限，请以管理员身份运行终端后重新执行安装。右键点击终端 → 选择"以管理员身份运行"」
- 非 Windows（`Darwin` / `Linux`）：**停止执行**，提示用户「git-ai 代码采集工具仅支持 Windows 系统，当前为 {系统}，无法安装」
- `ADMIN` 且 Windows（`MINGW` / `Windows` 开头）：继续执行第2步

## 第2步：检查是否已安装 git-ai

```bash
git-ai -v
```

- 成功输出版本号：提示用户「git-ai 已安装，版本：X.X.X，跳过安装步骤」，**结束**
- 报错（未找到命令等）：继续执行第3步

## 第3步：安装 git-ai

```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://usegitai.com/install.ps1 | iex"
```

**注意：**
- 此命令需要通过 Bash 工具执行，Claude Code 的 Bash 环境支持直接调用 `powershell`
- 如果安装过程中出现权限相关错误，提示用户「请以管理员身份运行终端后重新执行安装」

## 第4步：配置环境变量

检查系统 PATH 中是否已包含 git-ai 路径：

```bash
powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path', 'Machine') -split ';'"
```

- 输出中包含 `C:\Users\{用户名}\.git-ai\bin`：环境变量已存在，跳过写入，直接刷新
- 输出中不包含 `.git-ai\bin`：查找安装目录：

```bash
powershell -NoProfile -Command "Get-ChildItem -Path $env:USERPROFILE\.git-ai -ErrorAction SilentlyContinue | Select-Object FullName"
```

  - 找到 `$env:USERPROFILE\.git-ai\bin` 目录：写入系统 PATH：

```bash
powershell -NoProfile -Command "[Environment]::SetEnvironmentVariable('Path', [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetFolderPath('UserProfile') + '\.git-ai\bin', 'Machine')"
```

  - 未找到 `.git-ai` 目录：**停止执行**，提示用户「未找到 git-ai 安装目录，安装可能未成功，请重新执行本 skill」

刷新当前终端的 PATH（安装或写入环境变量后必须执行）：

```bash
powershell -NoProfile -Command '$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")'
```

## 第5步：验证安装

```bash
git-ai -v
```

- 输出版本号：提示用户「git-ai 代码采集工具安装成功，版本：X.X.X」
- 仍然报错：提示用户「安装后验证失败，请检查安装日志或手动重启终端后再试」

## 第6步：配置 Claude Code Hook

在 `~/.claude/settings.json` 中添加 Hook 配置，使文件编辑操作自动触发 git-ai checkpoint。

需要添加的配置：

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "http",
            "url": "http://127.0.0.1:39393/claude-post"
          }
        ],
        "matcher": "Write|Edit|MultiEdit"
      }
    ]
  }
}
```

**操作逻辑：**
1. 读取 `~/.claude/settings.json`（不存在则视为空对象 `{}`）
2. 检查 `hooks.PostToolUse` 中是否已存在 `url` 包含 `127.0.0.1:39393/claude-post` 的条目
   - 已存在：提示用户「Hook 配置已存在，跳过该步骤」
   - 不存在：将上述 hook 配置合并到现有 `settings.json` 中（保留已有配置，仅追加新条目），然后写回文件

**CC Switch 提示：** 配置完成后，提示用户「如果使用 CC Switch 切换模型，请将上述 Hook 配置同时添加到 CC Switch 通用配置中，避免切换模型后代码采集失效」

## 第7步：部署并启动 Hook Server

将本 skill 目录下的两个文件复制到 Claude Code 的 hooks 目录中：

```bash
mkdir -p ~/.claude/hooks && cp "{{SKILL_DIR}}/doc/git-ai-hook-server.js" ~/.claude/hooks/git-ai-hook-server.js && cp "{{SKILL_DIR}}/doc/git-ai-hook-server-start.ps1" ~/.claude/hooks/git-ai-hook-server-start.ps1
```

其中 `{{SKILL_DIR}}` 为本 skill 所在目录（即 `install-ai-coding-collector` 文件夹的绝对路径）。目标文件已存在则直接覆盖替换。

启动 Hook Server（注册 Windows 计划任务并立即启动）：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File ~/.claude/hooks/git-ai-hook-server-start.ps1
```

验证计划任务是否注册成功：

```bash
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'GitAiHookServer' | Get-ScheduledTaskInfo"
```

- `TaskName` 存在且 `LastRunTime` 有值：提示用户「Hook Server 计划任务已注册且已运行，安装流程全部完成」
- 未找到计划任务：提示用户「Hook Server 计划任务未注册成功，请检查启动脚本执行是否有报错」
- 计划任务存在但状态异常：提示用户「Hook Server 计划任务状态异常，请尝试手动执行启动脚本或重启终端」

## 注意事项

1. 安装脚本来自官方地址 `https://usegitai.com/install.ps1`
2. 安装完成后可能需要重启终端才能生效
3. Hook Server 用于接收 Claude Code 的 hook 回调并调用 `git-ai checkpoint` 记录代码变更
