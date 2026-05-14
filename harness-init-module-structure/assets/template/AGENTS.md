# __MODULE_NAME__ Agent 地图

## 模块目标

`__MODULE_NAME__/` 是一个自包含 Harness 模块。这个文件只负责给 Agent 指路，不承载详细规则正文。

## 文档索引

- Harness 架构：`.harness/harness-overview.md`
- 目录边界：`.harness/directory-layout.md`
- 任务流转：`.harness/runtime-lifecycle.md`
- 代码总览：`docs/domain/TechWhitepaper.md`
- 需求目录：`docs/memory/demand/`
- 需求摘要：`docs/memory/summary/`
- 系统影响记忆：`docs/memory/memory.md`
- Agent 详细规则：`rules/agent-rules.md`
- 工程交付规则：`rules/engineering-rules.md`

- 模块技能：`skills/README.md`

## 绑定项目代码

- 在这里登记 `__MODULE_NAME__` 模块绑定的业务代码仓名称与 Git 地址。
- 如果暂无绑定代码仓，可先保留本段作为占位。

## 按任务加载

- 需要查看、整理或更新某次需求材料：读 `docs/memory/demand/`；每次需求应单独落到 `docs/memory/demand/<demand-name>/`
- 需要 Agent 详细工作规则：读 `rules/agent-rules.md`
- 需要工程交付规则：读 `rules/engineering-rules.md`
- 需要记录需求改动对系统的影响：先读 `rules/agent-rules.md` 中的系统影响记忆规则，再更新 `docs/memory/memory.md`,本动作需要主动触发
- 需要定位 `__MODULE_NAME__` 模块绑定的业务代码仓：先查看 `codes/` 下是否已有本地代码；如果本地不存在，再看本文件“绑定项目代码”章节获取仓库信息
- 调整目录、边界或放置规则：读 `.harness/directory-layout.md`
- 需要了解当前绑定代码仓的整体技术结构和分工：读 `docs/domain/TechWhitepaper.md`；如果业务代码刚拉取完成，应先初始化这份文档
- 调整任务链路、上下文流转或 Hook：读 `.harness/runtime-lifecycle.md`

- 需要理解角色分工：读 `skills/README.md`

## 硬边界

- 只处理 `__MODULE_NAME__/` 模块内部内容。
- 详细规则写进 `.harness/`、`rules/` 或 `docs/` 对应文档，不要继续把 `AGENTS.md` 扩成手册。
- 如果运行时能力尚未实现，不要把设计稿描述成已可执行能力。
- `__MODULE_NAME__` 模块绑定的项目代码如果本地不存在，应从对应 Git 地址拉取，并放在 `codes/` 目录下。
- 涉及需求变更对系统的影响时，必须按 `rules/agent-rules.md` 的约束更新 `docs/memory/memory.md`。
