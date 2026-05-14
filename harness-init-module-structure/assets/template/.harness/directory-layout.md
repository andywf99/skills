# 目录布局

## 顶层规则

- `.harness/` 存放 Harness 结构、目录边界和任务流转说明。
- `rules/` 存放 Agent、工程交付和代码审查规则。
- `docs/` 存放领域白皮书、需求材料、摘要和系统影响记忆。
- `skills/` 存放模块私有的角色技能说明。
- `codes/` 存放本模块关联业务代码仓。

## 目录职责

- `.harness/` 存放 Harness 总览、目录布局和运行生命周期，不承载业务领域内容。
- `rules/` 存放跨任务复用的工作规则、工程规则和代码审查规则。
- `docs/domain/` 存放产品白皮书和技术白皮书等领域长期文档。
- `docs/memory/demand/` 按需求分目录存放问题定义、范围说明、设计文档、实施记录和 superpowers 产物。
- `docs/memory/summary/` 存放已归档需求摘要。
- `docs/memory/memory.md` 持续记录需求改动对系统接口造成的实际影响。
- `skills/` 存放角色化、阶段化的模块技能定义。
- `codes/` 存放实际业务代码和与实现直接相关的工作内容。

## 禁止混放

- 不要把临时任务产物直接丢进 `docs/`。
- 不要继续新增 `docs/prd/`、`docs/superpowers/` 或旧的 `docs/demand/`；需求过程材料统一归到 `docs/memory/demand/<demand-name>/`。
- 不要恢复旧的 `docs/architecture/`、`docs/rules/` 或 `docs/context/` 目录；Harness 说明、规则和记忆分别归到 `.harness/`、`rules/`、`docs/memory/`。
- 不要把详细规则继续堆进 `AGENTS.md`；详细说明应写进 `.harness/`、`rules/` 或其他合适的长期文档。
- 不要把模块外部目录当成 `__MODULE_NAME__` 模块的运行时依赖。



