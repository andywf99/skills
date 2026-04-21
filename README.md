# Skills 仓库

本仓库是 AI 辅助开发 Skill 集合，面向 Java/Spring Boot 工程化场景，覆盖消息中间件迁移、工单字段改造、单测生成、代码审查、文档生成等常见开发任务。每个 Skill 以独立目录组织，核心定义为 `SKILL.md` 文件。

## 命名规范

Skill 目录统一采用 `<类别>-<简述>` 格式，全小写、连字符分隔。

| 类别前缀 | 含义 | 说明 |
|----------|------|------|
| `java-` | Java 代码 | Java 代码编写、注释、测试等 |
| `mq-` | 消息队列 | RabbitMQ / RocketMQ 迁移、接入、引用分析 |
| `feature-` | 业务功能 | 特定业务功能的全链路开发（工单等） |
| `doc-` | 文档生成 | 各类文档、流程图、技术方案的生成 |
| `infra-` | 基础设施 | 框架接入、中间件配置、工程初始化 |
| `release-` | 发布/灰度 | 灰度开关、批量变更、多仓库发布 |
| `analysis-` | 分析工具 | 指标分析、Prompt 分析等 |
| `sqs-` | 服务质量 | 服务质量专项（SQL/ES 等） |
| （无前缀） | 通用工具 | 跨领域通用能力 |

## 仓库结构

```
skills/
├── <skill-name>/SKILL.md    # Skill 的完整定义（触发条件、工具权限、执行指令）
├── README.md                # 本文件，Skill 索引与说明
```

## Skill 索引

### java — Java 代码

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `java-unittest` | 为 Java/Spring Boot 项目生成或审查单元测试，关注 Git diff 范围、Mockito、JaCoCo | 新增单测、补覆盖率、review 测试代码 |
| `java-comments` | 为 Java 代码补类注释、JavaDoc、字段说明和关键业务注释 | 补注释、写 JavaDoc、提升可读性 |
| `java-code-review` | 按团队工程规则审查新增代码，重点看正确性、性能、事务、锁、ES/SQL/Redis 风险 | 新代码 review、生成代码 review、重点审查数据/性能/事务隐患 |

### mq — 消息队列

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `mq-rabbit-to-rocket` | 将 Spring Cloud Stream RabbitMQ 迁移为 RocketMQ，支持灰度切换 | RabbitMQ 切 RocketMQ、消息中间件迁移 |
| `mq-rabbit-clean` | 迁移完成后清理 RabbitMQ Input/Output 与灰度切换残留代码 | RocketMQ 已稳定，收尾清理旧 RabbitMQ 代码 |

### feature — 业务功能

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `feature-workorder-add-fields` | 普通工单/工单中心新增字段的全链路改造，覆盖实体、DTO/VO、Mapper/XML、DDL、ES、回刷、依赖报告 | 工单新增字段、列表/BI 同步加字段、按已有字段样例扩展 |
| `feature-workorder-export` | 工单导出链路开发与排查，覆盖导出 VO、Web VO、导出 SQL、异步导出 | 新增导出字段、列表字段同步导出、导出 Excel 加字段 |

### doc — 文档生成

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `doc-prd-to-trd` | 将 PRD 转成 TRD/概要设计文档，按既定设计文档流程输出 | 生成技术方案、PRD 转 TRD |
| `doc-preview-to-trd` | 将已预审的需求文档转换为 TRD 文档 | 预审通过后生成 TRD |
| `doc-prd-batch` | 批量处理 Word 文件，转换为 Markdown 预览，生成需求评审报告和汇总报告 | 批量预览 PRD、批量预审需求文档 |
| `doc-flowchart` | 将需求内容转换为 Mermaid Flowchart 流程图 | 生成流程图、需求转流程图、业务流程可视化 |
| `doc-whitepaper-tech` | 扫描 Java 项目结构并生成技术白皮书文档 | 生成项目结构文档、梳理 Controller/Service/Mapper/Feign 清单 |
| `doc-whitepaper-product` | 根据项目代码结构自动生成完整的产品白皮书文档 | 生成产品白皮书、输出产品功能文档 |
| `doc-sqs-sql` | 生成和审查服务质量生产数存发版 SQL / ES mapping 文档 | 补发版信息、编写生产 SQL、校验 ES mapping 与数存变更 |

### infra — 基础设施

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `infra-java-jacoco` | 为 Java Maven 项目添加 JaCoCo 单元测试覆盖率配置 | 项目需要接入 JaCoCo 覆盖率、补单测基础配置 |
| `infra-graceful` | 为 Spring Boot/Spring Cloud 应用接入优雅生命周期能力，生成扫描/配置文档 | 单仓扫描中间件、接入 graceful 配置 |
| `infra-graceful-batch` | 批量接入 yl-sqs-platform-graceful-starter，改造线程池优雅关停，支持批量提交/MR | 多仓库优雅启停接入、批量改造线程池、批量发版 |
| `infra-swagger` | 按 jt-swagger 规范集成新版 Swagger 文档，actuator 暴露端点 | 集成 Swagger 文档、API 管理页面接入 |
| `infra-speckit` | 初始化 Speckit 环境，配置项目技术栈和开发规范 | 项目要接入 Speckit 规范时 |
| `infra-openspec` | 检查 Node.js 版本并安装 OpenSpec CLI | 安装 OpenSpec CLI |
| `infra-rocketmq` | 在项目里接入 RocketMQ 依赖、配置和标准发送/消费用法 | 首次引入 RocketMQ、补依赖、补 Apollo 配置 |

### release — 发布/灰度

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `release-gray-switch` | 给生产行为变更加 gray switch，保证可纯配置回滚 | 改业务逻辑、改接口语义、加新流程、做安全/性能/兼容性改造 |
| `release-batch-update` | 在多个仓库执行同类代码/配置变更，支持抽样、批量修改、验证、提交流程 | 多仓库批量改依赖、配置、开关、接口替换、脚本迁移 |

### analysis — 分析工具

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `analysis-metrics-mcp` | 在 Git 工程改文件前后做快照与 Diff 指标上报 | Git 管理项目中修改文件时，走变更审计闭环 |
| `analysis-rabbit-refs` | 分析 RabbitMQ input/output 与 destination 引用关系，输出 CSV 报告 | 梳理 RabbitMQ 使用面、追踪 destination 被哪些项目引用 |

### 通用工具（一般是其他工具生成的，不要改名称）

| Skill | 功能用途 | 使用场景 |
|-------|---------|---------|
| `ask` | 向 AI 提问代码库中的实现细节和设计决策 | 探索代码库、理解某段代码的设计意图和实现原理 |
| `git-ai-search` | 从 git 历史中搜索和恢复 AI 对话上下文 | 找回之前的 AI 交互记录、恢复历史任务上下文 |
| `memory-mcp-workflow` | 通过 Memory MCP 在任务前搜索历史经验、任务后沉淀复用记忆 | 延续历史任务、复用之前的决策/修复经验 |
| `prompt-analysis` | 分析 AI 提示词模式和接受率 | 分析 Prompt 使用情况、优化提示词策略 |