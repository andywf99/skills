---
name: jt-graceful-lifecycle
description: 为 Spring Boot / Spring Cloud 应用接入 jt-platform-graceful-starter，并在分析优雅启停、优雅关停、优雅上下线、Apollo graceful namespace / graceful.properties 内容、Eureka、Feign、Hystrix、Redis、Spring Cloud Stream、RocketMQ、XXL-Job、自定义线程池改造时使用。适用于需要扫描当前代码、识别项目实际使用的中间件、根据扫描结果输出配置文档、补充 starter 依赖和 Apollo namespace、生成接入计划、输出验收清单或补充线程池关停策略的场景。
---

# JT Graceful Lifecycle

## Self-Contained Rule

- This skill must work with `SKILL.md` alone.
- Do not rely on bundled scripts, references, or helper files to complete the task.
- If helper files exist, treat them as optional accelerators; the same result must still be achievable by following this markdown only.

## Workflow

1. Read the current code before proposing any configuration:
   - `pom.xml`
   - the startup class containing `@SpringBootApplication`
   - `bootstrap.yml`, `application.yml`, `application.properties`, and Apollo-related config
   - message listener and producer classes
   - XXL-Job config and `@XxlJob` handlers
   - custom thread-pool config
2. Build a middleware inventory from actual code and dependency signals, not from assumptions.
3. Check whether Apollo explicitly loads namespaces through `@EnableApolloConfig(...)`.
4. Generate two outputs from the scan result:
   - a markdown scan/configuration document
   - a `graceful.properties` content recommendation for Apollo
5. If the user wants code changes, prefer the smallest safe change set:
   - add `com.yl:jt-platform-graceful-starter`
   - ensure Apollo loads the `graceful` namespace
   - add a checked-in template such as `docs/graceful.properties.template` when runtime config lives outside the repo
   - make custom executors wait for in-flight work before shutdown
6. Keep rollout conservative only for middleware with unclear lifecycle compatibility. If a custom RocketMQ listener wrapper such as `@RocketMQDynamicListener` is already confirmed compatible in the target project, allow `rocket-consumer` to be enabled and record that conclusion in the output.
7. Document what was detected, what is recommended to enable, what stays disabled, and what still needs environment validation.

## Output

- Always produce a scan-based markdown document that explains which middleware was found in the current code and why each graceful plugin is enabled or disabled.
- Always produce or update a configuration document for the target project:
  - `graceful.properties` content for Apollo
  - or a checked-in template such as `docs/graceful.properties.template`
- Keep the configuration document aligned with the scan result. Do not enable middleware plugins that are not supported by the detected code.
- For `kafka` and `feign` related plugins, prefer scan-based defaults over hardcoded `false`.

## Detection Rules

Use the following signals when scanning the repo:

| Plugin / Area | Typical dependency or code signals | Default recommendation |
| --- | --- | --- |
| `dataSource` | `mysql-connector-java`, Druid, MyBatis, ShardingSphere, datasource config | Enable when detected |
| `eureka` | `spring-cloud-starter-netflix-eureka-client`, `@EnableDiscoveryClient`, `@EnableEurekaClient` | Enable when detected |
| `feign` | `spring-cloud-starter-openfeign`, `@EnableFeignClients`, Feign client interfaces | Enable when detected |
| `feign.pre-request` | `RequestInterceptor`, `RequestTemplate`, existing Feign request hook code | Enable when detected |
| `hystrix` | `spring-cloud-starter-netflix-hystrix`, `@EnableHystrix` | Enable when detected |
| `kafka-consumer` | `spring-kafka`, `kafka-clients`, `spring-cloud-stream-binder-kafka`, `@KafkaListener`, listener container factory, `ConsumerFactory` | Enable when detected |
| `kafka-producer` | `spring-kafka`, `kafka-clients`, `spring-cloud-stream-binder-kafka`, `KafkaTemplate`, `KafkaProducer`, `ProducerFactory` | Enable when detected |
| `redis` | Redisson, Redis starter, `RedisTemplate`, `RedissonClient`, custom Redis utils | Enable when detected |
| `stream-consumer` | `@StreamListener`, `@EnableBinding` input interface, consumer package | Enable when detected |
| `stream-producer` | output bindings, `MessageChannel`, `MessageBuilder`, producer classes | Enable when detected |
| `rocket-producer` | `RocketMQTemplate`, `RocketMQDynamicPublisher`, `syncSend`, `asyncSend` | Enable when detected |
| `rocket-consumer` standard | `@RocketMQMessageListener`, `DefaultMQPushConsumer`, `RocketMQListener` | Enable when detected |
| `rocket-consumer` custom wrapper | `@RocketMQDynamicListener` or another custom wrapper | Enable after project-level compatibility is validated; otherwise keep disabled |
| `web-server` | `spring-boot-starter-web` | Enable when detected |
| `xxl-job` | `xxl-job-core`, `@XxlJob`, `XxlJobSpringExecutor` | Enable when detected |
| custom thread pools | `ForkJoinPool`, `ThreadPoolExecutor`, `ThreadPoolTaskExecutor`, custom executor beans | Always assess shutdown behavior |

## Decision Rules

- Set plugin switches from detected project usage, not from fixed defaults.
- If `feign.pre-request` is detected, also treat `feign` as detected.
- For Kafka, require both:
  - Kafka-related dependency signals
  - corresponding consumer or producer code signals
- For RocketMQ consumer:
  - enable when standard listener signals are detected
  - if the repo uses custom wrappers such as `@RocketMQDynamicListener`, enable only when compatibility is confirmed for that project; otherwise keep disabled and explicitly write the reason into the output document
- If the startup class hardcodes Apollo namespaces with `@EnableApolloConfig`, add the `graceful` namespace there or the new config will not load. Do not append `.properties` in the annotation namespace list.
- If a rollout intentionally overrides a detected plugin to `false`, explain the override in the generated markdown document.

## Manual Scan Procedure

When no helper script is available, scan manually in this order:

1. `pom.xml`
   - collect dependencies related to Eureka, Feign, Hystrix, Kafka, Redis, Stream, RocketMQ, XXL-Job, datasource, and web.
2. Startup class
   - check `@EnableDiscoveryClient`, `@EnableFeignClients`, `@EnableHystrix`, `@EnableApolloConfig`.
3. Messaging code
   - check Stream consumers and producers
   - check Kafka listeners and producers
   - check RocketMQ listeners and producers
4. Scheduler code
   - count `@XxlJob` handlers
   - locate `XxlJobSpringExecutor`
5. Thread-pool code
   - identify every custom executor bean
   - check whether shutdown waiting is already implemented
6. Apollo config
   - verify whether the `graceful` namespace must be added to an explicit namespace list

## graceful.properties Construction

Generate `graceful.properties` in this order:

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
graceful.executor.awaitTerminationSeconds=30
```

Apply these construction rules:

- `dataSource`, `eureka`, `redis`, `hystrix`, `stream-consumer`, `stream-producer`, `rocket-producer`, `web-server`, `xxl-job`
  - set to `true` when detected, else `false`
- `kafka-consumer`, `kafka-producer`, `feign`, `feign.pre-request`
  - set from scan results, not from a hardcoded conservative default
- `rocket-consumer`
  - set to `true` when RocketMQ consumer signals are detected and no unresolved compatibility risk blocks it
  - if custom wrappers such as `@RocketMQDynamicListener` are present, use the project-specific compatibility conclusion instead of a hardcoded `false`

## Markdown Output Template

Write the scan/configuration document with this structure:

1. Project summary
   - project name
   - whether starter dependency is present
   - whether Apollo already loads the `graceful` namespace
   - count of XXL-Job handlers
   - count of custom executor beans
2. Key dependencies
   - list only the dependencies relevant to graceful lifecycle
3. Middleware signals
   - use a table with: `Area | Detected | Evidence | Recommended`
4. Apollo check
   - startup class
   - detected namespace list
   - whether the `graceful` namespace is missing
5. Recommended `graceful.properties`
   - include a complete properties block
6. Next actions
   - list remaining code changes or validation work
7. Special notes
   - especially for custom RocketMQ listener wrappers, including whether compatibility has been confirmed in the target project, or risky rollout overrides

## Code Change Checklist

- Add `com.yl:jt-platform-graceful-starter:1.0.0-RELEASE` when it is missing.
- If `@EnableApolloConfig(...)` exists and hardcodes namespaces, add the `graceful` namespace rather than `graceful.properties`.
- For `ThreadPoolTaskExecutor`, set:
  - `waitForTasksToCompleteOnShutdown=true`
  - `awaitTerminationSeconds`, sourced from configuration when the project already externalizes graceful timeout values
- For raw `ExecutorService`, `ThreadPoolExecutor`, or `ForkJoinPool`:
  - call `shutdown()`
  - wait with bounded timeout
  - log queued tasks if forced to `shutdownNow()`
- Record the business policy for queued tasks: finish, drop with alert, or persist for replay.

## Thread Pools

- Treat app-defined executors as first-class shutdown resources; the starter cannot infer business semantics for queued work.
- For `ThreadPoolTaskExecutor`, set `waitForTasksToCompleteOnShutdown=true` and `awaitTerminationSeconds`. If graceful timeout properties already exist or are being introduced, wire the code to those properties instead of hardcoding time values.
- For raw `ExecutorService`, `ThreadPoolExecutor`, or `ForkJoinPool`, add an explicit shutdown hook that:
  - calls `shutdown()`
  - waits for a bounded timeout
  - logs and escalates queued work if it must call `shutdownNow()`
- Record the business policy for queued tasks: finish, drop with alert, or persist for replay.

## Validation

- Validate at least these scenarios after the code change:
  - startup order and successful registration
  - instance drain / deregistration
  - in-flight HTTP requests during shutdown
  - XXL-Job execution while shutting down
  - Stream consumer stop and producer flush
  - Kafka consumer stop and producer flush when Kafka is detected
  - RocketMQ producer flush, and consumer stop only if the listener type is confirmed compatible
  - Feign request interceptor ordering and client timeout behavior when Feign is detected
  - custom thread-pool queue behavior
- If runtime validation cannot be executed locally, leave a concrete test checklist in the repo.
- When the user explicitly confirms that a custom RocketMQ wrapper is compatible in the current project, treat that as validated project context and reflect it in both the generated markdown document and `graceful.properties`.
