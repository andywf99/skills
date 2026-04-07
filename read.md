| Skill                       | 功能用途                                                     | 使用场景                                                     |
| --------------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| add-workorder-fields        | 普通工单/工单中心新增字段的全链路改造，覆盖实体、DTO/VO、Mapper/XML、DDL、ES、回刷、依赖报告 | 工单新增字段、列表/BI同步加字段、按已有字段样例扩展          |
| implement-workorder-export  | 工单导出链路开发与排查，覆盖导出 VO、Web VO、导出 SQL、异步导出 | 新增导出字段、列表字段同步导出、导出 Excel 加字段、异步导出补齐 |
| analyze-rabbitmq-references | 分析 RabbitMQ input/output 与 destination 引用关系，并输出 CSV 报告 | 需要梳理 RabbitMQ 使用面、追踪 destination 被哪些项目引用    |
| rabbit-to-rocketmq          | 将 Spring Cloud Stream RabbitMQ 迁移为 RocketMQ，并支持灰度切换 | RabbitMQ 切 RocketMQ、消息中间件迁移                         |
| clean-rabbitmq              | 在完成迁移后，清理 RabbitMQ Input/Output 与灰度切换残留代码  | RocketMQ 已稳定，需要收尾清理旧 RabbitMQ 代码                |
| use-rocketmq                | 在项目里接入 RocketMQ 依赖、配置和标准发送/消费用法          | 首次引入 RocketMQ、补依赖、补 Apollo 配置                    |
| enforce-gray-switch         | 给生产行为变更加 gray switch，保证可纯配置回滚               | 改业务逻辑、改接口语义、加新流程、做安全/性能/兼容性改造     |
| review-new-code-rules       | 按团队工程规则审查新增代码，重点看正确性、性能、事务、锁、ES/SQL/Redis 风险 | 新代码 review、生成代码 review、重点审查数据/性能/事务隐患   |
| java-comment-doc            | 为 Java 代码补类注释、JavaDoc、字段说明和关键业务注释        | 用户要求补注释、写 JavaDoc、提升可读性                       |
| java-unit-test              | 为 Java/Spring Boot 项目生成或审查单元测试，关注 Git diff 范围、Mockito、JaCoCo | 新增单测、补覆盖率、review 测试代码                          |
| junit-test                  | 面向 JDK8 + Spring Boot 2.0.x 老项目的单测模板与验证方案     | 老项目写单测、处理静态依赖、修 Surefire/JaCoCo               |
| generate-project-info       | 扫描 Java 项目结构并生成 project-info.md                     | 生成项目结构文档、梳理 Controller/Service/Mapper/Feign 清单  |
| prd2trd                     | 将 PRD 转成 TRD/概要设计文档，按既定设计文档流程输出         | 生成技术方案、PRD 转 TRD、输出概要设计                       |
| init-spec-kit               | 初始化 Speckit 环境，补 .gitignore、初始化命令和 CLAUDE.md   | 项目要接入 Speckit 规范时                                    |
| coding_metrics_mcp          | 在 Git 工程改文件前后做快照与 Diff 指标上报                  | 在 Git 管理项目中修改文件时，需要走变更审计闭环              |
| memory-mcp-workflow         | 通过 Memory MCP 在任务前搜索历史经验、任务后沉淀复用记忆     | 延续历史任务、复用之前的决策/修复经验                        |
| batch-update                | 在多个仓库执行同类代码/配置变更，支持抽样、批量修改、验证、提交流程 | 多仓库批量改依赖、配置、开关、接口替换、脚本迁移             |
| graceful-starter            | 批量接入 yl-sqs-platform-graceful-starter，改造线程池优雅关停，支持批量提交/MR | 多仓库优雅启停接入、批量改造线程池、批量发版                 |
| graceful-publish            | 为 Spring Boot/Spring Cloud 应用接入优雅生命周期能力，并生成扫描/配置文档 | 单仓扫描中间件、接入 graceful 配置、生成 graceful.properties 建议 |

