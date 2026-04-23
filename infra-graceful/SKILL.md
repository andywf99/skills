---
name: infra-graceful
description: 为 Spring Boot / Spring Cloud 应用接入 jt-platform-graceful-starter，并在分析优雅启停、优雅关停、优雅上下线、Apollo graceful namespace / graceful.properties 内容、Eureka、Feign、Hystrix、Redis、Spring Cloud Stream、RocketMQ、XXL-Job 时使用。适用于需要扫描当前代码、识别项目实际使用的中间件、根据扫描结果输出配置文档、补充 starter 依赖和 Apollo namespace、生成接入计划或输出验收清单的场景。
---

# JT 优雅生命周期

## 自包含规则

- 这个 skill 必须仅凭 `SKILL.md` 就能工作。
- 不要依赖打包的脚本、参考资料或辅助文件才能完成任务。
- 如果存在辅助文件，只把它们当作可选加速器；即使不使用它们，也必须能够仅按照本文档完成同样的结果。

## 工作流程

1. 在提出任何配置建议之前，先阅读当前代码：
   - `pom.xml`
   - 包含 `@SpringBootApplication` 的启动类
   - `bootstrap.yml`、`application.yml`、`application.properties` 以及 Apollo 相关配置
   - 消息监听与消息生产相关类
   - XXL-Job 配置和 `@XxlJob` 处理器
2. 基于真实代码和依赖信号梳理中间件清单，不要靠猜测。
3. 检查 Apollo 是否通过 `@EnableApolloConfig(...)` 显式加载了 namespace。
4. 根据扫描结果产出两类内容：
   - 一份 markdown 扫描/配置文档
   - 一份给 Apollo 使用的 `graceful.properties` 内容建议
5. 如果用户需要代码改动，优先选择最小且安全的改动集：
   - 添加 `com.yl:jt-platform-graceful-starter`
   - 确保 Apollo 加载 `graceful` namespace
   - 当运行时配置不在仓库中时，补一个仓库内模板，如 `docs/graceful.properties.template`
6. 只有在中间件生命周期兼容性不明确时，才保守发布。如果项目里自定义 RocketMQ 监听包装器（如 `@RocketMQDynamicListener`）已经确认兼容，则允许启用 `rocket-consumer`，并在输出中记录这一结论。
7. 清楚记录：检测到了什么、建议启用什么、哪些保持关闭、哪些仍需要环境验证。

## 输出要求

- 始终生成一份基于扫描结果的 markdown 文档，说明当前代码里发现了哪些中间件，以及每个 graceful plugin 为什么启用或禁用。
- 始终为目标项目生成或更新一份配置文档：
  - Apollo 使用的 `graceful.properties` 内容
  - 或者仓库内模板，例如 `docs/graceful.properties.template`
- 配置文档必须和扫描结果保持一致。不要启用代码中未检测到或不受支持的中间件插件。
- 对于 `kafka` 和 `feign` 相关插件，优先采用基于扫描结果的默认值，而不是硬编码成 `false`。

## 检测规则

扫描仓库时使用以下信号：

| 插件 / 领域 | 常见依赖或代码信号 | 默认建议 |
| --- | --- | --- |
| `dataSource` | `mysql-connector-java`、Druid、MyBatis、ShardingSphere、数据源配置 | 检测到则启用 |
| `eureka` | `spring-cloud-starter-netflix-eureka-client`、`@EnableDiscoveryClient`、`@EnableEurekaClient` | 检测到则启用 |
| `feign` | `spring-cloud-starter-openfeign`、`@EnableFeignClients`、Feign client 接口 | 检测到则启用 |
| `feign.pre-request` | `RequestInterceptor`、`RequestTemplate`、现有 Feign 请求钩子代码 | 检测到则启用 |
| `hystrix` | `spring-cloud-starter-netflix-hystrix`、`@EnableHystrix` | 检测到则启用 |
| `kafka-consumer` | `spring-kafka`、`kafka-clients`、`spring-cloud-stream-binder-kafka`、`@KafkaListener`、listener container factory、`ConsumerFactory` | 检测到则启用 |
| `kafka-producer` | `spring-kafka`、`kafka-clients`、`spring-cloud-stream-binder-kafka`、`KafkaTemplate`、`KafkaProducer`、`ProducerFactory` | 检测到则启用 |
| `redis` | Redisson、Redis starter、`RedisTemplate`、`RedissonClient`、自定义 Redis 工具类 | 检测到则启用 |
| `stream-consumer` | `@StreamListener`、`@EnableBinding` 输入接口、consumer 包 | 检测到则启用 |
| `stream-producer` | output bindings、`MessageChannel`、`MessageBuilder`、producer 类 | 检测到则启用 |
| `rocket-producer` | `RocketMQTemplate`、`RocketMQDynamicPublisher`、`syncSend`、`asyncSend` | 检测到则启用 |
| `rocket-consumer` 标准监听 | `@RocketMQMessageListener`、`DefaultMQPushConsumer`、`RocketMQListener` | 检测到则启用 |
| `rocket-consumer` 自定义包装 | `@RocketMQDynamicListener` 或其他自定义包装器 | 项目级兼容性验证通过后再启用，否则保持关闭 |
| `web-server` | `spring-boot-starter-web` | 检测到则启用 |
| `xxl-job` | `xxl-job-core`、`@XxlJob`、`XxlJobSpringExecutor` | 检测到则启用 |

## 决策规则

- 插件开关要根据项目真实检测结果设置，不要使用固定默认值。
- 如果检测到 `feign.pre-request`，也要视为检测到了 `feign`。
- 对 Kafka 必须同时满足：
  - Kafka 相关依赖信号
  - 对应的 consumer 或 producer 代码信号
- 对 RocketMQ consumer：
  - 检测到标准监听信号时启用
  - 如果仓库使用了 `@RocketMQDynamicListener` 这类自定义包装器，则只有在该项目确认兼容后才启用；否则保持关闭，并在输出文档中明确写出原因
- 如果启动类通过 `@EnableApolloConfig` 硬编码了 namespace 列表，必须把 `graceful` 加进去，否则新配置不会生效。不要在注解的 namespace 列表里写成 `.properties` 后缀。
- 如果发布策略有意把某个已检测到的插件强制设为 `false`，必须在生成的 markdown 文档中解释原因。

## 手工扫描步骤

当没有可用辅助脚本时，按以下顺序手工扫描：

1. `pom.xml`
   - 收集和 Eureka、Feign、Hystrix、Kafka、Redis、Stream、RocketMQ、XXL-Job、数据源、Web 相关的依赖。
2. 启动类
   - 检查 `@EnableDiscoveryClient`、`@EnableFeignClients`、`@EnableHystrix`、`@EnableApolloConfig`。
3. 消息代码
   - 检查 Stream consumer 和 producer
   - 检查 Kafka listener 和 producer
   - 检查 RocketMQ listener 和 producer
4. 调度代码
   - 统计 `@XxlJob` 处理器数量
   - 定位 `XxlJobSpringExecutor`
5. Apollo 配置
   - 确认显式 namespace 列表中是否需要新增 `graceful`

## graceful.properties 生成规则

按以下顺序生成 `graceful.properties`：

```properties
graceful.enabled=true
graceful.plugin.dataSource.enabled=<true|false>
graceful.plugin.eureka.enabled=<true|false>
graceful.plugin.redis.enabled=<true|false>
graceful.plugin.hystrix.enabled=<true|false>
graceful.plugin.stream-consumer.enabled=<true|false>
graceful.plugin.stream-producer.enabled=<true|false>
graceful.plugin.rocket-producer.enabled=<true|false>
graceful.plugin.web-server.enabled=<true|false>
graceful.plugin.xxl-job.enabled=<true|false>

graceful.plugin.kafka-consumer.enabled=<true|false>
graceful.plugin.kafka-producer.enabled=<true|false>
graceful.plugin.feign.enabled=<true|false>
graceful.plugin.feign.pre-request.enabled=<true|false>
graceful.plugin.rocket-consumer.enabled=<true|false>

graceful.plugin.web-server.shutdownWaitTimeSeconds=30
graceful.plugin.rocket-consumer.shutdownWaitTimeSeconds=30
graceful.plugin.kafka-consumer.shutdownWaitTimeSeconds=30
```

应用以下生成规则：

- `dataSource`、`eureka`、`redis`、`hystrix`、`stream-consumer`、`stream-producer`、`rocket-producer`、`web-server`、`xxl-job`
  - 检测到则设为 `true`，否则设为 `false`
- `kafka-consumer`、`kafka-producer`、`feign`、`feign.pre-request`
  - 根据扫描结果设置，不要使用硬编码的保守默认值
- `rocket-consumer`
  - 检测到 RocketMQ consumer 信号且不存在未解决的兼容性风险时，设为 `true`
  - 如果存在 `@RocketMQDynamicListener` 这类自定义包装器，应使用该项目确认过的兼容性结论，而不是硬编码 `false`

## Markdown 输出模板

扫描/配置文档应包含以下结构：

1. 项目摘要
   - 项目名称
   - 是否已存在 starter 依赖
   - Apollo 是否已经加载 `graceful` namespace
   - XXL-Job 处理器数量
2. 关键依赖
   - 只列出与 graceful lifecycle 相关的依赖
3. 中间件信号
   - 使用表格：`Area | Detected | Evidence | Recommended`
4. Apollo 检查
   - 启动类
   - 检测到的 namespace 列表
   - 是否缺少 `graceful` namespace
5. 推荐的 `graceful.properties`
   - 给出完整的 properties 配置块
6. 后续动作
   - 列出剩余代码改动或验证工作
7. 特殊说明
   - 尤其说明自定义 RocketMQ listener 包装器是否已在目标项目确认兼容，以及是否存在带风险的发布覆盖策略

## 代码改动清单

- 缺失时，补充 `com.yl:jt-platform-graceful-starter:1.0.0-RELEASE`。
- 如果存在 `@EnableApolloConfig(...)` 且硬编码了 namespace，新增的是 `graceful`，不是 `graceful.properties`。

## 验证要求

- 代码改动后，至少验证以下场景：
  - 启动顺序与注册成功
  - 实例摘流量 / 下线
  - 关闭过程中的 HTTP 在途请求
  - 关闭过程中的 XXL-Job 执行
  - Stream consumer 停止与 producer flush
  - 检测到 Kafka 时，Kafka consumer 停止与 producer flush
  - RocketMQ producer flush，以及仅在 listener 类型确认兼容时验证 consumer 停止
  - 检测到 Feign 时，Feign 请求拦截器顺序与客户端超时行为
- 如果本地无法执行运行时验证，就在仓库中留下具体的测试清单。
- 当用户明确确认当前项目里的自定义 RocketMQ 包装器兼容时，应把它视为已验证的项目上下文，并同步反映到生成的 markdown 文档和 `graceful.properties` 中。
