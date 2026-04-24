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

检查管理员权限和操作系统：

```bash
net session > /dev/null 2>&1 && echo "ADMIN" || echo "NOT_ADMIN"
```

```bash
uname -s
```

- `NOT_ADMIN`：停止执行，提示「请以管理员身份运行终端后重新执行安装」
- 非 Windows（`Darwin` / `Linux`）：停止执行，提示「git-ai 仅支持 Windows 系统」
- `ADMIN` 且 Windows：继续执行

## 第2步：检查是否已安装

```bash
git-ai -v
```

- 成功输出版本号：提示「git-ai 已安装，版本：X.X.X，跳过安装」，结束
- 报错：继续执行

## 第3步：安装 git-ai

```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://usegitai.com/install.ps1 | iex"
```

权限错误时提示「请以管理员身份运行终端后重新执行安装」

## 第4步：配置环境变量

检查 PATH 是否包含 `.git-ai\bin`：

```bash
powershell -NoProfile -Command "[Environment]::GetEnvironmentVariable('Path', 'Machine') -split ';'"
```

- 已存在：刷新终端 PATH
- 不存在：查找安装目录，写入 PATH：

```bash
powershell -NoProfile -Command "Get-ChildItem -Path $env:USERPROFILE\.git-ai -ErrorAction SilentlyContinue | Select-Object FullName"
```

找到目录则写入 PATH；未找到则停止执行，提示「安装可能未成功，请重新执行本 skill」。

刷新终端 PATH：

```bash
powershell -NoProfile -Command '$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")'
```

## 第5步：验证安装

```bash
git-ai -v
```

- 输出版本号：提示「git-ai 安装成功，版本：X.X.X」
- 报错：提示「安装后验证失败，请检查安装日志或手动重启终端后再试」

## 第6步：配置 Claude Code Hook

在 `~/.claude/settings.json` 中添加 Hook 配置：

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

读取 `~/.claude/settings.json`，检查 `hooks.PostToolUse` 是否已包含 `127.0.0.1:39393/claude-post`：
- 已存在：提示「Hook 配置已存在，跳过」
- 不存在：合并配置（保留已有配置），写回文件

提示「如使用 CC Switch，请将此 Hook 配置同时添加到 CC Switch 通用配置中」

## 第7步：部署并启动 Hook Server

复制 Hook Server 文件到 Claude Code hooks 目录：

```bash
mkdir -p ~/.claude/hooks && cp "{{SKILL_DIR}}/doc/git-ai-hook-server.js" ~/.claude/hooks/git-ai-hook-server.js && cp "{{SKILL_DIR}}/doc/git-ai-hook-server-start.ps1" ~/.claude/hooks/git-ai-hook-server-start.ps1
```

注册并启动计划任务：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File ~/.claude/hooks/git-ai-hook-server-start.ps1
```

验证计划任务：

```bash
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'GitAiHookServer' | Get-ScheduledTaskInfo"
```

- `TaskName` 存在且 `LastRunTime` 有值：提示「Hook Server 已注册且运行，安装流程全部完成」
- 未找到：提示「计划任务未注册成功，请检查启动脚本执行是否有报错」
- 状态异常：提示「计划任务状态异常，请尝试手动执行启动脚本或重启终端」

## 注意事项

1. 安装脚本来自官方地址 `https://usegitai.com/install.ps1`
2. 安装完成后可能需要重启终端才能生效
3. Hook Server 用于接收 Claude Code 的 hook 回调并调用 `git-ai checkpoint` 记录代码变更
