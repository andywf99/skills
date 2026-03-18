---
name: code-collection-mcp-service
description: 为任何创建或修改 git管理的文件任务强制执行 SQS spec MCP 编辑记录。用于 Codex\Claude 即将生成代码、修改配置、重构文件、应用补丁或以其他方式变更仓库内容时，确保每一次文件变更都会记录 `specBeforeEditFile`、`specAfterEditFile`，并优先使用 `specEditFile` 或 `specWriteFile`。
---

# Code Collection MCP Service

在修改任何git管理文件之前先遵循这套流程。不要先编辑，再补记录。

使用 MCP server `yl-jis-sqs-mcp-server-api` 调用 `specBeforeEditFile`、`specAfterEditFile`、`specEditFile` 和 `specWriteFile`。

## 必填默认值

- 整个用户任务中只保留一个稳定的 `sessionId`。
- 先读取 `$TERM_SESSION_ID`。
- 如果为空或不存在，只生成一次 `codex-<YYYYMMDD>-<task-slug>`，并在整个任务中复用。
- 保持 `sessionId` 可读、稳定，且长度不超过 `128`。
- 在目标仓库中执行 `git rev-parse --abbrev-ref HEAD`，把实时结果作为 `gitBranch` 传入。
- 如果命令失败，先定位正确仓库再编辑。不要伪造分支名。
- 执行 `git config user.name`，把结果作为 `userId` 传入。
- 除非用户明确指定了其他账号标识，否则绝不传 `unknown`、`codex` 或其他占位值作为 `userId`。
- 除非用户明确要求其他团队标识，否则 `teamId` 固定传 `sqs`。
- 绝不把 `unknown` 或其他占位值传给 `teamId`。
- 传入真实的绝对文件路径。
- `appName` 优先使用仓库名或系统名。

## 强制单文件闭环

每个文件变更都按一个闭环执行：

1. 解析 `sessionId`、`gitBranch`、`userId`、`teamId` 和 `appName`。
2. 只针对当前这一个文件调用 `specBeforeEditFile`。新文件的当前内容传 `""`。
3. 修改该文件并保存。
4. 保存后立刻为同一个文件调用 `specAfterEditFile`，并传入保存后的完整内容。
5. 完成后才能处理下一个文件。

## 不可违反的规则

- 绝不先批量调用多个 `specBeforeEditFile`，再集中编辑。
- 绝不在 MCP 记录流程里同时打开两个文件。
- 保存后绝不跳过 `specAfterEditFile`。
- 在记录 `specBeforeEditFile` 快照之前绝不编辑文件。
- 使用 `apply_patch` 时，也要把多文件变更拆成一次只处理一个文件的闭环。

## 优先使用的 Diff 调用

当变更形态明确时，在强制闭环之外优先使用更适合的 diff 类 MCP 工具：

- 已知 `oldString` 和 `newString` 的局部替换，优先使用 `specEditFile`。
- 整文件重写或新生成文件，优先使用 `specWriteFile`。
- 这些工具可以提升 diff 结算质量，但不能替代必须执行的 `specBeforeEditFile -> save -> specAfterEditFile` 顺序。

## 参数解析模板

在任务开始时使用这套模式，并在用户没有明确要求变更的情况下保持这些值稳定：

```powershell
$sessionId = if ($env:TERM_SESSION_ID) {
  $env:TERM_SESSION_ID
} else {
  "codex-$(Get-Date -Format yyyyMMdd)-task-slug"
}

$gitBranch = git rev-parse --abbrev-ref HEAD
$userId = git config user.name
$teamId = "sqs"
```

把 `task-slug` 规范成简短的小写连字符单词，例如 `workflow-node-log`。每个任务只选一次，并在整个任务中复用。

## 最小执行清单

- 第一次编辑前先确定稳定的 `sessionId`。
- 每次编辑文件前都实时获取 `gitBranch`。
- 每次编辑文件前都确认 `userId` 仍然来自 `git config user.name`，除非用户明确覆盖。
- 每个文件都必须先完成 `before -> save -> after`，再处理下一个文件。
- 当变更形态清晰时，优先使用 `specEditFile` 或 `specWriteFile`。

## 停止条件

遇到以下任一情况时，先解决环境问题，不要继续编辑：

- 目标目录不在预期的 git 仓库内。
- `git rev-parse --abbrev-ref HEAD` 执行失败。
- `git config user.name` 为空，且用户没有提供允许使用的覆盖值。
- 所需的 MCP tools 不可用。
