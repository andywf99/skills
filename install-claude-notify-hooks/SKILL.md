---
name: install-claude-notify-hooks
description: 安装 Claude Code Lark 通知 Hook，在 Claude 执行完毕、需要确认或运行异常时自动推送 Lark 交互式卡片消息，包含项目、会话ID、权限模式、消息内容等信息。适用于需要 Lark 通知的场景。
triggers:
  - 安装 Lark 通知
  - 配置 Lark 通知
  - Claude通知Lark
  - 安装notify hooks
  - 配置Claude通知
---

# 安装 Claude Code Lark 通知 Hook

## 适用场景

- 需要 Claude Code 执行完毕后推送 Lark 通知
- 需要 Claude Code 等待确认时推送 Lark 通知
- 需要 Claude Code 运行异常（API 错误）时推送 Lark 通知
- 新机器初始化开发环境时配置 Lark 通知

## 支持的通知场景

| 事件 | 主题色 | 说明 |
| :--- | :--- | :--- |
| `Stop` | 蓝色 | Claude 执行完毕，展示执行结果摘要 |
| `SubagentStop` | 蓝色 | 子任务执行完毕 |
| `StopFailure` | 红色 | API 调用失败（限流、认证、计费等），展示错误详情 |
| `Notification` → `permission_prompt` | 橙色 | 需要授权批准，展示权限消息 |
| `Notification` → `idle_prompt` | 橙色 | Claude 空闲等待响应，展示等待消息 |
| `Notification` → `elicitation_dialog` | 橙色 | 需要用户输入，展示问题内容 |
| `Notification` → `elicitation_complete` | 绿色 | 交互完成，展示交互消息 |
| `Notification` → `elicitation_response` | 青色 | 收到用户交互响应，展示响应内容 |
| `Notification` → `auth_success` | 绿色 | 认证成功 |

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

## 第2步：获取 Lark Webhook URL

使用 AskUserQuestion 向用户询问 Lark 自定义机器人的 Webhook URL：

- 问题：「请输入 Lark 自定义机器人的 Webhook URL」
- 提示用户在 Lark 群中添加「自定义机器人」获取，格式为 `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx`

将用户输入的 URL 保存为变量 `LARK_WEBHOOK_URL`。

如果用户未提供有效 URL（不以 `https://open.feishu.cn` 开头），停止执行，提示「Webhook URL 格式不正确，请确认后重新执行」。

## 第3步：检查是否已配置

读取 `~/.claude/settings.json`，检查 `hooks.Stop`、`hooks.StopFailure` 和 `hooks.Notification` 中是否已包含 `lark-notify`：

- 三个 hook 都已存在：提示「Lark 通知 Hook 已配置，如需更新请先手动删除旧配置后重新执行」，停止执行
- 部分存在：提示「检测到部分 Hook 已配置，将补全缺失的 Hook」，继续执行
- 都不存在：继续执行

## 第4步：创建通知脚本

创建脚本目录（如不存在）：

```bash
mkdir -p ~/.claude/scripts
```

将 `{{SKILL_DIR}}/scripts/lark-notify.py` 复制到 `~/.claude/scripts/lark-notify.py`，并替换其中的 `__LARK_WEBHOOK_URL__` 为用户提供的 Webhook URL：

```bash
cp "{{SKILL_DIR}}/scripts/lark-notify.py" ~/.claude/scripts/lark-notify.py && sed -i "s|__LARK_WEBHOOK_URL__|${LARK_WEBHOOK_URL}|g" ~/.claude/scripts/lark-notify.py
```

### 验证脚本内容

```bash
cat ~/.claude/scripts/lark-notify.py
```

- 包含正确的 Webhook URL：继续执行
- 不包含：停止执行，提示「脚本创建失败，请手动创建」

## 第5步：配置 Hooks

读取 `~/.claude/settings.json`，在 `hooks` 中添加 `Stop`、`StopFailure` 和 `Notification` 配置。

Hook 命令通过 `py -3` 直接调用 Python 脚本，Claude Code 会通过 stdin 传递会话 JSON 数据。

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
            "command": "py -3 ~/.claude/scripts/lark-notify.py Stop"
          }
        ]
      }
    ],
    "StopFailure": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "py -3 ~/.claude/scripts/lark-notify.py StopFailure"
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
            "command": "py -3 ~/.claude/scripts/lark-notify.py Notification"
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
- 如果 `hooks.Stop` 已存在但不含 `lark-notify`，追加到数组末尾
- 如果 `hooks.StopFailure` 已存在但不含 `lark-notify`，追加到数组末尾
- 如果 `hooks.Notification` 已存在但不含 `lark-notify`，追加到数组末尾
- 如果 `hooks.Stop`、`hooks.StopFailure` 或 `hooks.Notification` 已包含 `lark-notify`，跳过该项（第3步已处理）

写回 `~/.claude/settings.json`。

提示用户：「如使用 CC Switch，请将此 Hook 配置同时添加到 CC Switch 通用配置中」

## 第6步：验证

```bash
echo '{"session_id":"test1234","cwd":"/home/user/my-project","permission_mode":"plan","hook_event_name":"Stop","last_assistant_message":"测试消息：执行完毕"}' | py -3 ~/.claude/scripts/lark-notify.py Stop
```

- 命令执行成功（退出码 0）：提示「Lark 通知配置完成！请检查 Lark 群是否收到测试卡片消息」
- 命令执行失败：提示「测试通知发送失败，请检查 Webhook URL 是否正确，或网络是否可达」

## 注意事项

1. Lark Webhook URL 需要在 Lark 群中添加「自定义机器人」获取
2. 如需 Lark 签名验证，需手动编辑通知脚本添加签名逻辑
3. 所有系统统一使用 Python 脚本（.py），通过 `py -3` 调用，无 Bash 依赖
4. 脚本通过 stdin 接收 Claude Code 传递的会话 JSON，通过 `sys.argv[1]` 接收事件类型
5. 会话 JSON 包含 `session_id`、`cwd`、`permission_mode`、`hook_event_name`、`message`、`last_assistant_message`、`error` 等字段
6. Stop 事件会展示 `last_assistant_message`（Claude 最终回复摘要）；StopFailure 事件会展示 `error` 和 `error_details`
7. Notification 事件会根据 `notification_type` 展示对应的 `message` 内容
8. 消息内容超过 500 字符会自动截断，避免卡片过长
9. 卡片消息默认 @所有人（使用 `<at id=all></at>`），避免漏消息
10. Stop 事件卡片主题为蓝色，StopFailure 事件为红色，Notification 事件根据类型为橙色/绿色/青色
11. 如需卸载，手动删除 `~/.claude/scripts/lark-notify.py`，并从 `~/.claude/settings.json` 中移除对应 hook 配置
