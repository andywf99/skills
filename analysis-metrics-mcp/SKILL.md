---
name: analysis-metrics-mcp
description: 通过本地 Python MCP 服务拦截文件变更并上传结算指标，避免让模型发送全量文本给 Java 服务端。
---

# Coding Metrics MCP (File Edit Constraints)

这个技能配套了一个底层的 Python MCP 服务（`spec_metrics_mcp.py`），用于本地高速计算大模型修改文件前后的 Diff 数据，并将新增、删除、修改行数的指标轻量上报给远端 Java 数据库引擎。

## 何时必须调用本技能

- 只要当前任务是在**已经被 Git 管理的工程项目中**执行文件改动，就**必须调用**本技能。
- “已经被 Git 管理”指目标工程目录存在有效 Git 仓库，且改动文件位于该仓库管理范围内。
- 对这类工程项目中的文件修改，不允许绕过本技能直接写文件。
- 非 Git 管理目录、纯临时目录，或明确不在工程仓库管理范围内的文件，不属于本技能的强制调用范围。

## 文件修改记录核心约束

当您需要在已被 Git 管理的工程项目中修改和保存文件时，**绝对禁止**直接执行静默写文件动作！请时刻谨记以下铁律：

- 修改任意文件前，必须先调用 `specBeforeEditFile` 进行内存拍照（防篡改与初始值锚定）。
- 修改完成并保存后，必须立即调用 `specAfterEditFile` 指示监控服务对快照作差异比对，将指标送至库中结算。
- 必须遵循“单文件单修改闭环”的原子性执行模式，禁止先批量 before 多文件，再集中修，又集中 after！
- `teamId` 默认恒定填充字串 `sqs`。
- 如果大模型未走这套快照验证流程强改文件，等同违抗最高级别的安全开发准则。
- 安装命令pip install mcp httpx

## 强制字段规则

- `sessionId` 是整次用户任务的唯一稳定标识，**必须保持前后一致，禁止同一任务内漂移或重算**：优先尝试读取终端环境变量 `$env:TERM_SESSION_ID`；实在没有则遵循规范按 `codex-<YYYYMMDD>-<task-slug>` 结构自造一个稳定字符，并在全工作流中固定使用。
- `gitBranch` **必须按当前节点实时取值**，不得手填历史值或猜测填充；优先由节点自动获取，或显式执行 `git rev-parse --abbrev-ref HEAD` 动态填充。
- `userId` **必须有可靠来源**：默认通过 `git config user.name` 获取；若仓库未配置或获取失败，必须让使用者补全后再继续。
- `appName` **必须优先通过 Git 命令从当前改动代码的仓库实时推导**：在 PowerShell 中默认执行 `(git rev-parse --show-toplevel | Split-Path -Leaf)`，直接获取仓库根目录名作为 `appName`，例如输出 `yl-jms-css-api`；若当前目录不在 Git 仓库内、命令执行失败，或目录名与真实应用名明显不一致，必须停止猜测并让使用者明确指定后再继续。
