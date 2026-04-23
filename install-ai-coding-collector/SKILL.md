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

## 第1步：检查管理员权限

执行以下命令检查当前终端是否具有管理员权限：

```bash
net session > /dev/null 2>&1 && echo "ADMIN" || echo "NOT_ADMIN"
```

**判断逻辑：**
- 输出 `ADMIN`：继续执行第2步
- 输出 `NOT_ADMIN`：**停止执行**，提示用户「当前终端没有管理员权限，请以管理员身份运行终端后重新执行安装。右键点击终端 → 选择"以管理员身份运行"」

## 第2步：检查操作系统

执行以下命令检查当前系统平台：

```bash
uname -s
```

**判断逻辑：**
- 输出以 `MINGW` 或 `Windows` 开头（Windows 上的 Git Bash）：继续执行第3步
- 输出为 `Darwin`（macOS）：**停止执行**，提示用户「git-ai 代码采集工具仅支持 Windows 系统，当前为 macOS，无法安装」
- 其他 Linux 输出：**停止执行**，提示用户「git-ai 代码采集工具仅支持 Windows 系统，当前为 Linux，无法安装」

## 第3步：检查是否已安装 git-ai

执行以下命令：

```bash
git-ai -v
```

**判断逻辑：**
- 命令成功输出版本号：提示用户「git-ai 已安装，版本：X.X.X，跳过安装步骤」，**结束**
- 命令报错（未找到命令等）：继续执行第4步

## 第4步：安装 git-ai

使用 PowerShell 管理员终端执行远程安装脚本：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://usegitai.com/install.ps1 | iex"
```

**注意：**
- 此命令需要通过 Bash 工具执行，Claude Code 的 Bash 环境支持直接调用 `powershell`
- 如果安装过程中出现权限相关错误，提示用户「请以管理员身份运行终端后重新执行安装」

## 第5步：刷新环境变量

安装完成后，需要刷新当前终端的 PATH 环境变量，否则 `git-ai` 命令可能无法识别：

```bash
powershell -NoProfile -Command '$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")'
```

## 第6步：验证安装

刷新环境变量后，执行：

```bash
git-ai -v
```

- 输出版本号：提示用户「git-ai 代码采集工具安装成功，版本：X.X.X」
- 仍然报错：提示用户「安装后验证失败，请检查安装日志或手动重启终端后再试」

## 第7步：配置 Claude Code Hook

在 Claude Code 的 `settings.json` 中添加 Hook 配置，使文件编辑操作自动触发 git-ai checkpoint。

配置文件路径：`~/.claude/settings.json`

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
1. 读取 `~/.claude/settings.json` 文件（不存在则视为空对象 `{}`）
2. 检查 `hooks.PostToolUse` 中是否已存在 `url` 包含 `127.0.0.1:39393/claude-post` 的条目
   - 已存在：提示用户「Hook 配置已存在，跳过该步骤」，直接进入第8步
   - 不存在：将上述 hook 配置合并到现有 `settings.json` 中（保留已有配置，仅追加新条目），然后写回文件

## 第8步：部署 Hook Server

将本 skill 目录下的两个文件复制到 Claude Code 的 hooks 目录中：

| 源文件（skill doc/ 目录下） | 目标路径 |
|---|---|
| `doc/git-ai-hook-server.js` | `~/.claude/hooks/git-ai-hook-server.js` |
| `doc/git-ai-hook-server-start.ps1` | `~/.claude/hooks/git-ai-hook-server-start.ps1` |

执行：

```bash
mkdir -p ~/.claude/hooks && cp "{{SKILL_DIR}}/doc/git-ai-hook-server.js" ~/.claude/hooks/git-ai-hook-server.js && cp "{{SKILL_DIR}}/doc/git-ai-hook-server-start.ps1" ~/.claude/hooks/git-ai-hook-server-start.ps1
```

其中 `{{SKILL_DIR}}` 为本 skill 所在目录（即 `install-ai-coding-collector` 文件夹的绝对路径）。

**注意：** 如果目标文件已存在，直接覆盖替换。

## 第9步：启动 Hook Server

使用 PowerShell 执行启动脚本，注册 Windows 计划任务并启动 Hook Server：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File ~/.claude/hooks/git-ai-hook-server-start.ps1
```

该脚本会：
- 生成隐藏启动的 VBS 脚本
- 注册 Windows 计划任务（开机/登录时自动启动）
- 立即启动 Hook Server

## 第10步：检查 Hook Server 启动情况

执行以下命令检查计划任务是否注册成功并正在运行：

```bash
powershell -NoProfile -Command "Get-ScheduledTask -TaskName 'GitAiHookServer' | Get-ScheduledTaskInfo"
```

**判断逻辑：**
- 输出中 `TaskName` 存在且 `LastRunTime` 有值：提示用户「Hook Server 计划任务已注册且已运行，安装流程完成」
- 命令报错（未找到计划任务）：提示用户「Hook Server 计划任务未注册成功，请检查第9步的启动脚本执行是否有报错」
- 计划任务存在但状态异常：提示用户「Hook Server 计划任务状态异常，请尝试手动执行启动脚本或重启终端」

## 第11步：配置 CC Switch 通用 Hook

提示用户将以下 Hook 配置添加到 **CC Switch 通用配置**中，避免切换模型后代码采集失效：

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

**说明：**
- 第7步已将此配置写入 `~/.claude/settings.json`，但如果使用 CC Switch 切换模型，模型特定的 settings 会覆盖通用配置
- 将此 Hook 配置放入 CC Switch 的**通用配置**中，可确保无论切换到哪个模型，代码采集都能正常工作
- 提示用户：「请将上述 Hook 配置添加到 CC Switch 通用配置中，避免切换模型后代码采集失效」

## 注意事项

1. 仅支持 Windows 系统，macOS 和 Linux 不支持
2. 必须以管理员权限运行终端，否则安装将无法执行
3. 安装脚本来自官方地址 `https://usegitai.com/install.ps1`
4. 安装完成后可能需要重启终端才能生效
5. Hook Server 用于接收 Claude Code 的 hook 回调并调用 `git-ai checkpoint` 记录代码变更
