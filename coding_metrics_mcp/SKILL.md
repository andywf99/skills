---
name: Coding Metrics MCP
description: 通过本地 Python MCP 服务拦截文件变更并上传结算指标，避免让模型发送全量文本给 Java 服务端。
---

# Coding Metrics MCP (File Edit Constraints)

这个技能配套了一个底层的 Python MCP 服务（`spec_metrics_mcp.py`），用于本地高速计算大模型修改文件前后的 Diff 数据，并将新增、删除、修改行数的指标轻量上报给远端 Java 数据库引擎。

## 文件修改记录核心约束

当您需要修改和保存任何源码文件时，**绝对禁止**直接执行静默写文件动作！请时刻谨记以下铁律：

- 修改任意文件前，必须先调用 `specBeforeEditFile` 进行内存拍照（防篡改与初始值锚定）。
- 修改完成并保存后，必须立即调用 `specAfterEditFile` 指示监控服务对快照作差异比对，将指标送至库中结算。
- 必须遵循“单文件单修改闭环”的原子性执行模式，禁止先批量 before 多文件，再集中修，又集中 after！
- `sessionId` 必须在同一用户任务内保持稳定一致：优先尝试读取终端环境变量 `$env:TERM_SESSION_ID`；实在没有则遵循规范按 `codex-<YYYYMMDD>-<task-slug>` 结构自造一个稳定字符，并死锁在全工作流中。
- `gitBranch` 由节点实时自取，或您代借 `git rev-parse --abbrev-ref HEAD` 命令进行动态填充。
- `userId` 默认由 `git config user.name` 获取或让使用者补全。
- `teamId` 默认恒定填充字串 `sqs`。
- 如果大模型未走这套快照验证流程强改文件，等同违抗最高级别的安全开发准则。
- 安装命令pip install mcp httpx
