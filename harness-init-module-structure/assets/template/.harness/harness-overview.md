# Harness 总览

## 模块定位

`__MODULE_NAME__/` 是一个自包含 Harness 模块。它自己管理记忆、规范、技能、上下文和运行骨架，不依赖模块外部的信息来完成内部说明。

## Harness 分层映射

- 导航入口层：`AGENTS.md`
- Harness 结构层：`.harness/`
- 规则层：`rules/`
- 领域文档层：`docs/domain/`
- 上下文与记忆层：`docs/memory/`
- 需求输入层：`docs/memory/demand/`
- 角色技能层：`skills/`
- 业务代码工作区：`codes/`

## 模块边界

所有属于 `__MODULE_NAME__` 模块的运行时结构、上下文规则和文档入口都应该落在 `__MODULE_NAME__/` 内部。

## 复用方式

这套结构可以作为一个独立模块的参考形状，在其他场景中按需复制和调整。

## AGENTS 定位

`AGENTS.md` 在本模块里是地图，不是手册。它只保留入口、索引和按任务加载路径，详细规则沉到 `rules/agent-rules.md` 等文档中按需读取。

## 系统影响记忆

`docs/memory/memory.md` 只用于持续记录每次需求改动对系统的实际影响；记录约束和格式说明放在 `rules/agent-rules.md`。



