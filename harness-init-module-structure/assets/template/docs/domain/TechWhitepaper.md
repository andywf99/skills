# __MODULE_NAME__ 代码总览

## 文档状态

当前文档是占位文件。

`harness-init-module-structure` 只负责初始化模块骨架，不负责预填业务代码分析结果。因此在模块刚创建、业务代码尚未拉取时，这份文档默认保持为空白总览状态。

## 初始化时机

当 `codes/` 下已经拉取到当前模块绑定的业务代码仓后，应初始化并更新本文件。

建议在以下场景触发：

- 首次拉取当前模块绑定的业务代码仓之后
- 新增、删除或替换绑定代码仓之后
- 需要让 Agent 快速理解多仓分工、技术栈和系统边界时

## 初始化后应包含的内容

- 当前模块绑定了哪些代码仓
- 各代码仓的系统定位和职责分工
- 主要技术栈、架构分层和关键中间件
- 代码阅读顺序和排查入口
- 与当前模块需求分析直接相关的技术边界说明

## 文档映射要求

`docs/domain/TechWhitepaper.md` 是总览入口，必须映射到 `codes/` 下每个已绑定代码仓的单仓技术文档。

约定如下：

- 每个业务代码仓根目录应补充一份 `project-info.md`
- 路径模式为：`codes/<repo-name>/project-info.md`
- 当前文档应列出“仓库名 -> project-info.md”的对应关系

推荐阅读顺序：

1. 先看 `docs/domain/TechWhitepaper.md`
2. 再进入目标仓的 `codes/<repo-name>/project-info.md`

## 关联入口

- 绑定仓信息：`AGENTS.md`
- 业务代码目录：`codes/`
- 单仓技术文档：在各代码仓根目录补充 `project-info.md`


