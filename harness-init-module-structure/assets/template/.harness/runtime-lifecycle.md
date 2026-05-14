# 运行生命周期

## 任务流转

1. 从 `docs/memory/demand/<demand-name>/` 读取当前需求的背景、目标和约束。
2. 从 `AGENTS.md` 判断当前任务该加载哪些详细文档。
3. 从 `skills/` 选择匹配当前任务的角色技能。
4. 在 `docs/memory/` 下读取或沉淀当前工作所需的需求、摘要和记忆材料。
5. 把本次需求相关的背景、设计文档、实施记录和 superpowers 产物直接落到 `docs/memory/demand/<demand-name>/`，把代码相关产物落到 `codes/`。
6. 如果本次需求改动影响了系统接口，还要按规则更新 `docs/memory/memory.md`。
7. 需求上线后，将对应 `docs/memory/demand/<demand-name>/` 的关键信息归档到 `docs/memory/summary/`。

## 质量关卡

- 校验规则必须显式存在，不能靠隐含约定。
- 大体积的临时产物应留在 `codes/`，需要时再总结到其他位置。
- 一条规则只要会跨任务复用，就应该沉淀到 `.harness/` 或 `rules/` 中对应文档，由 `AGENTS.md` 提供入口。
- 需求变更对系统的影响必须落在 `docs/memory/memory.md`，具体记录约束以 `rules/agent-rules.md` 为准。
- 需求上线后的归档应优先沉淀到 `docs/memory/summary/`，不要让历史需求长期散落在活动目录里。


