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

## 第1步：检查操作系统

执行以下命令检查当前系统平台：

```bash
uname -s
```

**判断逻辑：**
- 输出以 `MINGW` 或 `Windows` 开头（Windows 上的 Git Bash）：继续执行第2步
- 输出为 `Darwin`（macOS）：**停止执行**，提示用户「git-ai 代码采集工具仅支持 Windows 系统，当前为 macOS，无法安装」
- 其他 Linux 输出：**停止执行**，提示用户「git-ai 代码采集工具仅支持 Windows 系统，当前为 Linux，无法安装」

## 第2步：检查是否已安装 git-ai

执行以下命令：

```bash
git-ai -v
```

**判断逻辑：**
- 命令成功输出版本号：提示用户「git-ai 已安装，版本：X.X.X，跳过安装步骤」，**结束**
- 命令报错（未找到命令等）：继续执行第3步

## 第3步：安装 git-ai

使用 PowerShell 管理员终端执行远程安装脚本：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://usegitai.com/install.ps1 | iex"
```

**注意：**
- 此命令需要通过 Bash 工具执行，Claude Code 的 Bash 环境支持直接调用 `powershell`
- 如果安装过程中出现权限相关错误，提示用户「请以管理员身份运行终端后重新执行安装」

## 第4步：验证安装

安装完成后，再次执行：

```bash
git-ai -v
```

- 输出版本号：提示用户「git-ai 代码采集工具安装成功，版本：X.X.X」
- 仍然报错：提示用户「安装后验证失败，请检查安装日志或手动重启终端后再试」

## 第5步：配置 Claude Code Hook

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
   - 已存在：提示用户「Hook 配置已存在，跳过该步骤」，直接进入第6步
   - 不存在：将上述 hook 配置合并到现有 `settings.json` 中（保留已有配置，仅追加新条目），然后写回文件

## 第6步：部署 Hook Server

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

## 第7步：启动 Hook Server

使用 PowerShell 执行启动脚本，注册 Windows 计划任务并启动 Hook Server：

```bash
powershell -NoProfile -ExecutionPolicy Bypass -File ~/.claude/hooks/git-ai-hook-server-start.ps1
```

该脚本会：
- 生成隐藏启动的 VBS 脚本
- 注册 Windows 计划任务（开机/登录时自动启动）
- 立即启动 Hook Server

## 注意事项

1. 仅支持 Windows 系统，macOS 和 Linux 不支持
2. 安装脚本来自官方地址 `https://usegitai.com/install.ps1`
3. 安装完成后可能需要重启终端才能生效
4. Hook Server 用于接收 Claude Code 的 hook 回调并调用 `git-ai checkpoint` 记录代码变更
