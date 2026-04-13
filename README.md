# Skills 仓库

本仓库是 AI 辅助开发 Skill 集合，面向 Java/Spring Boot 工程化场景，覆盖消息中间件迁移、工单字段改造、单测生成、代码审查、文档生成等常见开发任务。每个 Skill 以独立目录组织，核心定义为 `SKILL.md` 文件。

## 仓库结构

```
skills/
├── <skill-name>/SKILL.md    # Skill 的完整定义（触发条件、工具权限、执行指令）
├── README.md                # 本文件，Skill 索引与说明
```

## Skill 索引

| Skill                       | 功能用途                                                     | 使用场景                                                     |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| add-jacoco                  | 为 Java Maven 项目添加 JaCoCo 单元测试覆盖率配置，自动补 surefire/jacoco 插件和基础测试文件 | 项目需要接入 JaCoCo 覆盖率、补单测基础配置                   |
| add-workorder-fields        | 普通工单/工单中心新增字段的全链路改造，覆盖实体、DTO/VO、Mapper/XML、DDL、ES、回刷、依赖报告 | 工单新增字段、列表/BI同步加字段、按已有字段样例扩展          |
| implement-workorder-export  | 工单导出链路开发与排查，覆盖导出 VO、Web VO、导出 SQL、异步导出 | 新增导出字段、列表字段同步导出、导出 Excel 加字段、异步导出补齐 |
| ask                         | 向 AI 提问代码库中的实现细节和设计决策，像问原作者一样理解代码 | 探索代码库、理解某段代码的设计意图和实现原理                 |
| analyze-rabbitmq-references | 分析 RabbitMQ input/output 与 destination 引用关系，并输出 CSV 报告 | 需要梳理 RabbitMQ 使用面、追踪 destination 被哪些项目引用    |
| batch-prd-preview           | 批量处理 Word 文件，转换为 Markdown 预览，生成需求评审报告和汇总报告 | 批量预览 PRD、批量预审需求文档、生成评审报告                 |
| rabbit-to-rocketmq          | 将 Spring Cloud Stream RabbitMQ 迁移为 RocketMQ，并支持灰度切换 | RabbitMQ 切 RocketMQ、消息中间件迁移                         |
| clean-rabbitmq              | 在完成迁移后，清理 RabbitMQ Input/Output 与灰度切换残留代码  | RocketMQ 已稳定，需要收尾清理旧 RabbitMQ 代码                |
| use-rocketmq                | 在项目里接入 RocketMQ 依赖、配置和标准发送/消费用法          | 首次引入 RocketMQ、补依赖、补 Apollo 配置                    |
| enforce-gray-switch         | 给生产行为变更加 gray switch，保证可纯配置回滚               | 改业务逻辑、改接口语义、加新流程、做安全/性能/兼容性改造     |
| review-new-code-rules       | 按团队工程规则审查新增代码，重点看正确性、性能、事务、锁、ES/SQL/Redis 风险 | 新代码 review、生成代码 review、重点审查数据/性能/事务隐患   |
| java-comment-doc            | 为 Java 代码补类注释、JavaDoc、字段说明和关键业务注释        | 用户要求补注释、写 JavaDoc、提升可读性                       |
| java-unit-test              | 为 Java/Spring Boot 项目生成或审查单元测试，关注 Git diff 范围、Mockito、JaCoCo | 新增单测、补覆盖率、review 测试代码                          |
| generate-project-info       | 扫描 Java 项目结构并生成 project-info.md                     | 生成项目结构文档、梳理 Controller/Service/Mapper/Feign 清单  |
| git-ai-search               | 从 git 历史中搜索和恢复 AI 对话上下文                        | 找回之前的 AI 交互记录、恢复历史任务上下文                   |
| prd2trd                     | 将 PRD 转成 TRD/概要设计文档，按既定设计文档流程输出         | 生成技术方案、PRD 转 TRD、输出概要设计                       |
| preview2trd                 | 将已预审的需求文档转换为 TRD 文档，适用于已通过需求评审的场景 | 预审通过后生成 TRD、预审转技术方案                           |
| product-whitepaper-generator | 根据项目代码结构自动生成完整的产品白皮书文档，覆盖产品概述、功能架构、业务规则、状态流转、技术架构、ER 模型等 | 生成产品白皮书、输出产品功能文档                             |
| prompt-analysis             | 分析 AI 提示词模式和接受率                                   | 分析 Prompt 使用情况、优化提示词策略                         |
| init-spec-kit               | 初始化 Speckit 环境，补 .gitignore、初始化命令和 CLAUDE.md   | 项目要接入 Speckit 规范时                                    |
| coding_metrics_mcp          | 在 Git 工程改文件前后做快照与 Diff 指标上报                  | 在 Git 管理项目中修改文件时，需要走变更审计闭环              |
| memory-mcp-workflow         | 通过 Memory MCP 在任务前搜索历史经验、任务后沉淀复用记忆     | 延续历史任务、复用之前的决策/修复经验                        |
| batch-update                | 在多个仓库执行同类代码/配置变更，支持抽样、批量修改、验证、提交流程 | 多仓库批量改依赖、配置、开关、接口替换、脚本迁移             |
| graceful-starter            | 批量接入 yl-sqs-platform-graceful-starter，改造线程池优雅关停，支持批量提交/MR | 多仓库优雅启停接入、批量改造线程池、批量发版                 |
| graceful-publish            | 为 Spring Boot/Spring Cloud 应用接入优雅生命周期能力，并生成扫描/配置文档 | 单仓扫描中间件、接入 graceful 配置、生成 graceful.properties 建议 |

