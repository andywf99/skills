---
name: install-claude-notify-hooks
description: 安装 Claude Code 飞书通知 Hook，在 Claude 执行完毕或需要确认时自动推送飞书交互式卡片消息，包含项目、会话ID、权限模式等信息。适用于需要飞书通知的场景。
triggers:
  - 安装飞书通知
  - 配置飞书通知
  - Claude通知飞书
  - 安装notify hooks
  - 配置Claude通知
---

# 安装 Claude Code 飞书通知 Hook

## 适用场景

- 需要 Claude Code 执行完毕后推送飞书通知
- 需要 Claude Code 等待确认时推送飞书通知
- 新机器初始化开发环境时配置飞书通知

## 第1步：检测系统环境

检测当前操作系统：

```bash
uname -s
```

根据输出确定系统类型，保存为变量 `OS_TYPE`：

- `MINGW*` 或 `MSYS*` 或 `CYGWIN*`：`OS_TYPE=windows`
- `Darwin`：`OS_TYPE=macos`
- `Linux`：`OS_TYPE=linux`

提示用户当前检测到的系统环境，后续步骤将根据 `OS_TYPE` 执行不同操作。

## 第2步：获取飞书 Webhook URL

使用 AskUserQuestion 向用户询问飞书自定义机器人的 Webhook URL：

- 问题：「请输入飞书自定义机器人的 Webhook URL」
- 提示用户在飞书群中添加「自定义机器人」获取，格式为 `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx`

将用户输入的 URL 保存为变量 `FEISHU_WEBHOOK_URL`。

如果用户未提供有效 URL（不以 `https://open.feishu.cn` 开头），停止执行，提示「Webhook URL 格式不正确，请确认后重新执行」。

## 第3步：检查是否已配置

读取 `~/.claude/settings.json`，检查 `hooks.Stop` 和 `hooks.Notification` 中是否已包含 `feishu-notify`：

- 两个 hook 都已存在：提示「飞书通知 Hook 已配置，如需更新请先手动删除旧配置后重新执行」，停止执行
- 部分存在：提示「检测到部分 Hook 已配置，将补全缺失的 Hook」，继续执行
- 都不存在：继续执行

## 第4步：创建通知脚本

创建脚本目录（如不存在）：

```bash
mkdir -p ~/.claude/scripts
```

将 `{{SKILL_DIR}}/scripts/feishu-notify.sh` 复制到 `~/.claude/scripts/feishu-notify.sh`，并替换其中的 `__FEISHU_WEBHOOK_URL__` 为用户提供的 Webhook URL：

```bash
cp "{{SKILL_DIR}}/scripts/feishu-notify.sh" ~/.claude/scripts/feishu-notify.sh && sed -i "s|__FEISHU_WEBHOOK_URL__|${FEISHU_WEBHOOK_URL}|g" ~/.claude/scripts/feishu-notify.sh
```

### Linux / macOS 环境（OS_TYPE=linux 或 OS_TYPE=macos）

额外赋予执行权限：

```bash
chmod +x ~/.claude/scripts/feishu-notify.sh
```

### 验证脚本内容

```bash
cat ~/.claude/scripts/feishu-notify.sh
```

- 包含正确的 Webhook URL：继续执行
- 不包含：停止执行，提示「脚本创建失败，请手动创建」

## 第5步：配置 Hooks

读取 `~/.claude/settings.json`，在 `hooks` 中添加 `Stop` 和 `Notification` 配置。

所有系统统一使用 Bash 脚本，Claude Code 会通过 stdin 传递会话 JSON 数据给 hook 脚本。

需要添加的配置：

```json
{
  "hooks": {
    "Stop": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/scripts/feishu-notify.sh Stop"
          }
        ]
      }
    ],
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "bash ~/.claude/scripts/feishu-notify.sh Notification"
          }
        ]
      }
    ]
  }
}
```

**合并规则：**
- 保留 settings.json 中已有的所有配置
- 如果 `hooks` 键不存在，创建并添加
- 如果 `hooks.Stop` 已存在但不含 `feishu-notify`，追加到数组末尾
- 如果 `hooks.Notification` 已存在但不含 `feishu-notify`，追加到数组末尾
- 如果 `hooks.Stop` 或 `hooks.Notification` 已包含 `feishu-notify`，跳过该项（第3步已处理）

写回 `~/.claude/settings.json`。

提示用户：「如使用 CC Switch，请将此 Hook 配置同时添加到 CC Switch 通用配置中」

## 第6步：验证

```bash
echo '{"session_id":"test1234","cwd":"/home/user/my-project","permission_mode":"plan","hook_event_name":"Stop","reason":"completed"}' | bash ~/.claude/scripts/feishu-notify.sh Stop
```

- 命令执行成功（退出码 0）：提示「飞书通知配置完成！请检查飞书群是否收到测试卡片消息」
- 命令执行失败：提示「测试通知发送失败，请检查 Webhook URL 是否正确，或网络是否可达」

## 注意事项

1. 飞书 Webhook URL 需要在飞书群中添加「自定义机器人」获取
2. 如需飞书签名验证，需手动编辑通知脚本添加签名逻辑
3. 所有系统统一使用 Bash 脚本（.sh），Windows 通过 Git Bash 执行
4. 脚本内部通过 Python（`py -3`）构建 JSON 和发送 HTTP 请求，确保 UTF-8 编码正确，无需 jq 依赖
5. Hook 脚本通过 stdin 接收 Claude Code 传递的会话 JSON，包含 `session_id`、`cwd`、`permission_mode`、`hook_event_name`、`reason` 等字段
6. 卡片消息包含项目名称、会话ID、权限模式、事件类型、工作目录等信息
7. 卡片消息默认 @所有人（使用 `<at id=all></at>`），避免漏消息
8. Stop 事件卡片主题为蓝色，Notification 事件卡片主题为橙色
9. 如需卸载，手动删除 `~/.claude/scripts/feishu-notify.sh` 并从 `~/.claude/settings.json` 中移除对应 hook 配置