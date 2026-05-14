---
name: git-ai-manual
description: 为 git-ai 手工补写或覆盖 AI authorship notes。用于 git-ai status 显示 untracked 100%、AI 写的文件被记录成 Human、git-ai checkpoint 无法重新归因、需要提交后修复 refs/notes/ai 归因的场景。
---

# Git AI Manual Attribution

## 目标

把“AI 实际写了代码/文档，但 git-ai 没有捕获到 AI checkpoint”的补救流程标准化。只处理已提交数据：先根据目标 commit 的 diff 生成 AI note 内容，展示给用户确认，再写入或覆盖 `refs/notes/ai`。

## 判断

先在业务 worktree 根目录执行，不要在 `.git/modules/...` 内操作：

```powershell
git-ai status
git status --short
git notes --ref=ai show HEAD
```

如果 `git-ai status` 显示 `untracked 100%`，并且 `.git/modules/<repo>/ai/working_logs/<base>/checkpoints.jsonl` 里对应文件是：

```json
"kind": "Human",
"agent_id": null,
"transcript": null
```

说明 git-ai 没拿到 AI 工具的 agent/session/prompt，不会自动猜测这些内容是 AI 写的。

## 工作流

1. 回到 worktree：

```powershell
cd C:\Users\pan.pan2\IdeaProjects\sqs-harness\modules\exception-event
```

2. 确认要补归因的改动已经提交。手工补 notes 是提交级操作，不处理未提交工作区 diff：

```powershell
git status --short
git commit -m "your message"
```

3. 用本 skill 的包装脚本检查目标 commit 是否已有 AI note。没有 note 时先询问是否修复；选择修复后生成 note 预览，并再次确认写入。已有 note 时生成预览，并询问是否覆盖：

```powershell
python .\skills\git-ai-manual\scripts\write_git_ai_note.py --commit HEAD --tool codex --model gpt-5
```

4. 验证：

```powershell
git notes --ref=ai show HEAD
git-ai stats HEAD
git-ai show HEAD
```

## 脚本

使用 `scripts/write_git_ai_note.py`。它直接读取目标 commit 的 diff，生成 AI authorship note 预览，确认后写入 `refs/notes/ai`。

常用参数：

- `--repo` / `-R`：业务仓 worktree 或真实 git-dir，默认当前目录。
- `--commit` / `-C`：要补 notes 的提交，默认 `HEAD`。
- `--tool` / `-T`：归因工具名，默认 `codex`。
- `--model` / `-M`：模型名，默认 `manual`。
- `--agent-id` / `-A`：agent id，默认 `manual-<commit>`。
- `--human-author` / `-H`：人类发起者，默认由提交作者推导。
- `--dry-run`：只打印将写入的 note，不询问、不落盘。

## 注意

- 不要使用 `git-ai manual checkpoint`，当前 CLI 没有这个命令。
- `git-ai checkpoint codex ...` 只适合实时捕获；如果文件已经被 checkpoint 成 Human，通常会提示 `already checkpointed`，不能自动改成 AI。
- 如果目标 commit 已经有 note，脚本会在预览后询问是否覆盖；未确认前不会写入。
- `--repo` 可以指向 worktree，也可以指向真实 git-dir，例如 `C:\Users\pan.pan2\IdeaProjects\sqs-harness\.git\modules\exception-event`。
- 如果远端需要 notes，同步时需要推送 `refs/notes/ai`，按团队规则执行。
