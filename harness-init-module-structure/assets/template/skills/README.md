# 模块技能说明

这个目录用于存放 `__MODULE_NAME__` 模块私有的 Skills。

- `__MODULE_NAME__-analyst`：负责读取请求、抽取目标、补齐约束并沉淀到 `docs/memory/demand/<demand-name>/`
- `__MODULE_NAME__-operator`：负责按照模块生命周期推进任务，从输入走到产出
- `__MODULE_NAME__-reviewer`：负责检查结构、质量和模块边界是否被遵守
- `harness-init-module-structure`：负责基于当前仓库模板一键初始化 Harness 模块目录骨架和模板文件

这些 Skill 只服务于 `__MODULE_NAME__` 模块。
