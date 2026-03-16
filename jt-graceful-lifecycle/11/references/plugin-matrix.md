# Plugin Matrix

## Detection Rules

| Plugin | Common signals | First-pass recommendation |
| --- | --- | --- |
| `dataSource` | `mysql-connector-java`, Druid, MyBatis, ShardingSphere, datasource config | Enable |
| `eureka` | `spring-cloud-starter-netflix-eureka-client`, `@EnableDiscoveryClient` | Enable |
| `redis` | Redisson, Redis starter, `RedisTemplate`, custom Redis utils | Enable |
| `hystrix` | `spring-cloud-starter-netflix-hystrix`, `@EnableHystrix` | Enable |
| `stream-consumer` | `@StreamListener`, `@EnableBinding` input interface, consumer package | Enable |
| `stream-producer` | output bindings, `MessageChannel`, `MessageBuilder`, producer classes | Enable |
| `rocket-producer` | `RocketMQTemplate`, `RocketMQDynamicPublisher`, `syncSend` or `asyncSend` | Enable |
| `rocket-consumer` | `@RocketMQMessageListener`, `DefaultMQPushConsumer` | Enable |
| `rocket-consumer` with custom wrapper | `@RocketMQDynamicListener` or another custom listener abstraction | Keep disabled for phase 1, then validate compatibility |
| `web-server` | `spring-boot-starter-web` | Enable |
| `xxl-job` | `xxl-job-core`, `@XxlJob`, `XxlJobSpringExecutor` | Enable |
| `feign` | `spring-cloud-starter-openfeign`, `@EnableFeignClients` | Enable when detected |
| `feign.pre-request` | `RequestInterceptor`, `RequestTemplate`, existing Feign request hook code | Enable when detected |
| `kafka-consumer` | `spring-kafka`, `@KafkaListener`, listener container factory | Enable when detected |
| `kafka-producer` | `spring-kafka`, `KafkaTemplate`, `KafkaProducer`, producer factory | Enable when detected |

## Apollo Checklist

If the startup class uses `@EnableApolloConfig(value = {...})`, verify `graceful.properties` is present in that list. Adding the namespace only in Apollo is not enough when the application hardcodes namespaces.

## Thread-Pool Checklist

- Detect every `ForkJoinPool`, `ThreadPoolExecutor`, and `ThreadPoolTaskExecutor` bean.
- For `ThreadPoolTaskExecutor`, set:
  - `waitForTasksToCompleteOnShutdown=true`
  - `awaitTerminationSeconds=<bounded timeout>`
- For raw executors, add an explicit shutdown hook and log unfinished queue items on timeout.
- Call out the business policy for queued tasks if the code does not already define one.

## Recommended Apollo Template

```properties
graceful.enabled=true
graceful.plugin.dataSource.enabled=true
graceful.plugin.eureka.enabled=true
graceful.plugin.redis.enabled=true
graceful.plugin.hystrix.enabled=true
graceful.plugin.stream-consumer.enabled=true
graceful.plugin.stream-producer.enabled=true
graceful.plugin.rocket-producer.enabled=true
graceful.plugin.web-server.enabled=true
graceful.plugin.xxl-job.enabled=true

graceful.plugin.kafka-consumer.enabled=<detected>
graceful.plugin.kafka-producer.enabled=<detected>
graceful.plugin.feign.enabled=<detected>
graceful.plugin.feign.pre-request.enabled=<detected>
graceful.plugin.rocket-consumer.enabled=false

graceful.plugin.web-server.shutdownWaitTimeSeconds=30
graceful.plugin.rocket-consumer.shutdownWaitTimeSeconds=30
graceful.plugin.kafka-consumer.shutdownWaitTimeSeconds=30
graceful.executor.awaitTerminationSeconds=30
```

Keep `rocket-consumer.enabled=false` only when the repo uses a custom RocketMQ wrapper and starter compatibility is still unverified.
For `kafka` and `feign` related plugins, use detected project signals as the default and only override manually when rollout strategy requires it.
