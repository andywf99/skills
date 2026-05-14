---
name: __MODULE_NAME__-operator
description: 按照 __MODULE_NAME__ 模块的 Harness 结构推进任务执行和产物落位。
---

## 职责

- 从 `AGENTS.md` 判断当前任务应加载的详细规则文档
- 按 `.harness/runtime-lifecycle.md` 中定义的生命周期推进任务
- 把长期文档写入 `.harness/`、`rules/` 或 `docs/`，把临时产物写入 `codes/`

## 守卫条件

- 严格工作在模块边界内
- 不假设模块外存在可直接使用的运行能力依赖
