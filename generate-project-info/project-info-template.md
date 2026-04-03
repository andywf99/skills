# {{项目名称}} 项目框架文档

## 项目简介

这是一个**{{项目类型}}**，提供{{核心功能描述}}。

### 核心能力

| 能力 | 描述 |
|------|------|
| {{能力1名称}} | {{能力1描述}} |
| {{能力2名称}} | {{能力2描述}} |
| {{能力3名称}} | {{能力3描述}} |
| {{能力4名称}} | {{能力4描述}} |
| {{能力5名称}} | {{能力5描述}} |

### 技术栈

| 类型 | 技术 |
|------|------|
| 基础框架 | {{框架名称及版本}} |
| ORM | {{ORM框架及版本}} |
| 数据库 | {{数据库类型及版本}} |
| 缓存 | {{缓存技术}} |
| 消息队列 | {{消息队列技术}} |
| 配置中心 | {{配置中心技术}} |
| 服务治理 | {{服务治理技术}} |
| 定时任务 | {{定时任务框架}} |
| 监控 | {{监控技术}} |
| 其他 | {{其他技术}} |

---

## 项目模块

### 模块架构图

```
{{项目名称}}
├── {{web/api/controller层包名}}/    # {{Web层说明，如：控制器层 - 接收 HTTP 请求}}
├── {{service层包名}}/                # {{Service层说明，如：服务层 - 业务逻辑处理}}
│   ├── {{业务子模块1}}/              # {{子模块1描述}}
│   ├── {{业务子模块2}}/              # {{子模块2描述}}
│   └── {{业务子模块3}}/              # {{子模块3描述}}
├── {{dao/mapper/repository层包名}}/  # {{数据访问层说明}}
│   ├── {{业务子模块1}}/
│   ├── {{业务子模块2}}/
│   └── {{业务子模块3}}/
├── {{model/entity/dto/vo包名}}/      # {{数据模型层说明}}
│   ├── {{entity/pojo包名}}/          # {{实体类说明}}
│   ├── {{dto/param包名}}/            # {{入参对象说明}}
│   ├── {{vo/result包名}}/            # {{出参对象说明}}
│   └── {{enums/constant包名}}/       # {{枚举/常量说明}}
├── {{feign/client包名}}/             # {{远程服务调用说明}}
├── {{cache/redis包名}}/              # {{缓存管理层说明}}
├── {{task/job/schedule包名}}/        # {{定时任务层说明}}
├── {{listener/consumer包名}}/        # {{消息监听层说明}}
├── {{stream/mq包名}}/                # {{消息流层说明}}
├── {{websocket包名}}/                # {{WebSocket通信说明}}
├── {{aop/aspect包名}}/               # {{AOP切面说明}}
├── {{config包名}}/                   # {{配置类说明}}
├── {{common/base包名}}/              # {{基础组件说明}}
└── {{util/helper包名}}/              # {{工具类说明}}

说明：
- 包名根据实际项目结构调整，如 Spring MVC 项目可能是 controller/service/dao
- DDD 项目可能是 interfaces/application/domain/infrastructure
- 请根据实际项目包结构进行填充
```

---

## 各模块详细说明

### Controller 层

| 类名 | 路径 | 功能 | 主要接口方法 |
|------|------|------|-------------|
| `{{Controller1}}` | `controller/{{Controller1}}.java` | {{功能描述}} | {{主要方法}} |
| `{{Controller2}}` | `controller/{{Controller2}}.java` | {{功能描述}} | {{主要方法}} |
| `{{Controller3}}` | `controller/{{Controller3}}.java` | {{功能描述}} | {{主要方法}} |

#### 调用链路示例

```
{{请求入口}} -> {{控制层}} -> {{服务层}} -> {{数据访问层}} -> {{数据存储}}
                     ↓
               {{缓存层}}
                     ↓
               {{远程调用层}} -> {{外部服务}}
```

**常见架构模式说明：**

| 架构模式 | 请求入口 | 控制层 | 服务层 | 数据访问层 | 数据存储 |
|----------|----------|--------|--------|------------|----------|
| Spring MVC | HTTP Request | Controller | Service | Mapper/DAO | Database |
| Spring Boot | HTTP Request | Controller | Service | Repository | Database |
| DDD | HTTP Request | Facade/Controller | Application Service | Repository | Database |
| 微服务 | HTTP/gRPC | Api/Controller | Service | Mapper | Database |
| Hexagonal | HTTP Request | Adapter | Port/Service | Repository | Database |

**示例（根据实际项目选择）：**

```
# Spring MVC 标准模式
HTTP Request -> Controller -> Service -> Mapper -> MySQL
                     ↓
                Redis Cache
                     ↓
               Feign Client -> 外部微服务

# DDD 领域驱动设计模式
HTTP Request -> Controller -> Application Service -> Domain Service -> Repository -> PostgreSQL
                                           ↓
                                      Domain Model
                                           ↓
                                      Event Publisher -> Message Queue
```

---

### Service 层

#### 核心业务 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `{{Service1}}` | `{{Service1}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |
| `{{Service2}}` | `{{Service2}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |
| `{{Service3}}` | `{{Service3}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |

#### {{子模块1}} 子模块

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `{{Service1}}` | `{{Service1}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |
| `{{Service2}}` | `{{Service2}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |

#### {{子模块2}} 子模块

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `{{Service1}}` | `{{Service1}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |
| `{{Service2}}` | `{{Service2}}Impl` | {{功能描述}} | `{{method1}}`, `{{method2}}` |

#### 其他重要 Service

| 接口名 | 实现类 | 功能 |
|--------|--------|------|
| `{{Service1}}` | `{{Service1}}Impl` | {{功能描述}} |
| `{{Service2}}` | `{{Service2}}Impl` | {{功能描述}} |
| `{{Service3}}` | `{{Service3}}Impl` | {{功能描述}} |

---

### Mapper 层

#### 核心 Mapper

| Mapper 接口 | XML 映射文件 | 关联实体 | 主要 SQL 操作 |
|-------------|--------------|----------|---------------|
| `{{Mapper1}}` | `{{Mapper1}}.xml` | `{{Entity1}}` | {{SQL操作描述}} |
| `{{Mapper2}}` | `{{Mapper2}}.xml` | `{{Entity2}}` | {{SQL操作描述}} |
| `{{Mapper3}}` | `{{Mapper3}}.xml` | `{{Entity3}}` | {{SQL操作描述}} |

#### {{子模块1}} 子模块 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `{{Mapper1}}` | `{{Entity1}}` | {{功能描述}} |
| `{{Mapper2}}` | `{{Entity2}}` | {{功能描述}} |

---

### Entity 实体类

#### 基础实体类

{{扫描项目中的基础实体类（通常以 Base、Abstract、Generic 开头或位于 common/base 包下），列出继承关系和公共字段}}

| 实体类 | 表名 | 说明 | 继承关系 |
|--------|------|------|----------|
| `{{BaseEntity1}}` | - | {{基础实体说明}} | `{{父类}}` |
| `{{BaseEntity2}}` | - | {{基础实体说明}} | `{{父类}}` |

**{{BaseEntity1}} 字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| {{字段名}} | {{类型}} | {{说明}} |

> 💡 **说明**：不同项目的基础实体类可能不同，常见模式包括：
> - MyBatis-Plus: `BaseEntity` 继承 `Model<T>`
> - JPA: `BaseEntity` 使用 `@MappedSuperclass`
> - 自定义: `BaseId` → `BaseEntity` → `Base` 三层继承
> - 无基础类: 所有实体独立定义字段

---

#### 业务实体类

{{按业务模块分类列出实体类，每个实体包含字段名、类型、说明}}

##### EntityName (表名: {{table_name}})

{{实体说明/功能描述}}

| 字段名 | 类型 | 说明 |
|--------|------|------|
| {{字段名}} | {{类型}} | {{说明}} |

---

### Feign 客户端 (远程服务调用)

#### {{服务1名称}} (`{{FeignClient1}}`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `{{/api/path1}}` | POST | {{接口说明}} | 入参: `{{DTO}}`, 返回: `{{VO}}` |
| `{{/api/path2}}` | GET | {{接口说明}} | 入参: `{{param}}`, 返回: `{{VO}}` |

#### {{服务2名称}} (`{{FeignClient2}}`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `{{/api/path1}}` | POST | {{接口说明}} | 入参: `{{DTO}}`, 返回: `{{VO}}` |
| `{{/api/path2}}` | GET | {{接口说明}} | 入参: `{{param}}`, 返回: `{{VO}}` |

#### {{服务3名称}} (`{{FeignClient3}}`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `{{/api/path1}}` | POST | {{接口说明}} | 入参: `{{DTO}}`, 返回: `{{VO}}` |
| `{{/api/path2}}` | GET | {{接口说明}} | 入参: `{{param}}`, 返回: `{{VO}}` |

---

### Cache 缓存层

| 缓存类 | Redis Key 前缀 | 功能 | 过期策略 |
|--------|----------------|------|----------|
| `{{Cache1}}` | `{{prefix1}}:` | {{功能描述}} | {{过期策略}} |
| `{{Cache2}}` | `{{prefix2}}:` | {{功能描述}} | {{过期策略}} |
| `{{Cache3}}` | `{{prefix3}}:` | {{功能描述}} | {{过期策略}} |

---

### Task 定时任务

| 任务类 | Cron 表达式 | 功能 |
|--------|-------------|------|
| `{{Task1}}` | {{cron表达式}} | {{功能描述}} |
| `{{Task2}}` | {{cron表达式}} | {{功能描述}} |
| `{{Task3}}` | {{cron表达式}} | {{功能描述}} |

---

### AOP 切面

| 切面类 | 注解 | 功能 | 应用场景 |
|--------|------|------|----------|
| `{{Aspect1}}` | `@{{Annotation1}}` | {{功能描述}} | {{应用场景}} |
| `{{Aspect2}}` | `@{{Annotation2}}` | {{功能描述}} | {{应用场景}} |
| `{{Aspect3}}` | `@{{Annotation3}}` | {{功能描述}} | {{应用场景}} |

---

### 消息中间件

> **说明**：项目中可能同时存在 Spring Cloud Stream 和 RocketMQ 两种消息中间件，根据实际扫描结果生成对应章节。

#### Spring Cloud Stream（如存在）

**概述**：项目使用 **Spring Cloud Stream** 实现消息驱动，具体 Topic 配置通过 **Apollo 配置中心** 管理。

| 配置项 | 说明 |
|--------|------|
| 框架 | Spring Cloud Stream |
| 消息队列 | {{RabbitMQ/RocketMQ}} |
| 配置管理 | Apollo |
| 生产者接口 | `OutputInterface.java` |
| 消费者接口 | `InputInterface.java` |

**Output（消息生产）配置**：

| Channel 名称 | Destination | 方法 | 消息类型 | 说明 |
|--------------|-------------|------|----------|------|
| {{channel-name-output}} | {{destination-name}} | `methodName()` | `MessageDTO` | {{消息说明}} |

**Input（消息消费）配置**：

| Channel 名称 | Destination | Group | 方法 | 消息类型 | 处理逻辑 | 说明 |
|--------------|-------------|-------|------|----------|----------|------|
| {{channel-name-input}} | {{destination-name}} | {{group-name}} | `methodName()` | `MessageDTO` | `service.method()` | {{消息说明}} |

#### RocketMQ（如存在）

**概述**：项目使用 **RocketMQ** 实现消息收发，可能使用 `spring-boot-starter-rocketmq` 或 `yl-sqs-platform-rocketmq`。

| 配置项 | 说明 |
|--------|------|
| 框架 | RocketMQ |
| Starter | {{spring-boot-starter-rocketmq / yl-sqs-platform-rocketmq}} |
| Name Server | 从配置文件获取 |

**Topic 生产者（标准模式）**：

| Topic 名称 | Tag | 生产者类 | 消息类型 | 说明 |
|------------|-----|----------|----------|------|
| {{topic-name-1}} | {{tag-name}} | `{{ProducerClass}}` | `{{MessageDTO}}` | {{发送场景说明}} |
| {{topic-name-2}} | {{tag-name}} | `{{ProducerClass}}` | `{{MessageDTO}}` | {{发送场景说明}} |

**Topic 动态发布器（如存在）**：

| Topic 名称 | Tag | 发布器类 | 调用位置 | 消息类型 | 说明 |
|------------|-----|----------|----------|----------|------|
| {{topic-name-1}} | {{tag-name}} | `RocketMQDynamicPublisher` | `{{ServiceClass.methodName()}}` | `{{MessageDTO}}` | {{发送场景说明}} |
| {{topic-name-2}} | {{tag-name}} | `RocketMQDynamicPublisher` | `{{ServiceClass.methodName()}}` | `{{MessageDTO}}` | {{发送场景说明}} |

**Topic 消费者（标准模式）**：

| Topic 名称 | 消费者类 | 消息类型 | 消费模式 | 说明 |
|------------|----------|----------|----------|------|
| {{topic-name-1}} | `{{ConsumerClass}}` | `{{MessageDTO}}` | 集群/广播 | {{消费场景说明}} |
| {{topic-name-2}} | `{{ConsumerClass}}` | `{{MessageDTO}}` | 集群/广播 | {{消费场景说明}} |

**Topic 动态监听器（如存在）**：

| Topic 名称 | 消费者类 | 注解 | 消息类型 | 消费模式 | 说明 |
|------------|----------|------|----------|----------|------|
| {{topic-name-1}} | `{{ConsumerClass}}` | `@RocketMQDynamicListener` | `{{MessageDTO}}` | 集群/广播 | {{消费场景说明}} |
| {{topic-name-2}} | `{{ConsumerClass}}` | `@RocketMQDynamicListener` | `{{MessageDTO}}` | 集群/广播 | {{消费场景说明}} |

---

### Config 配置类

| 配置类 | 功能 | 主要配置项 |
|--------|------|------------|
| `{{Config1}}` | {{功能描述}} | {{主要配置项}} |
| `{{Config2}}` | {{功能描述}} | {{主要配置项}} |
| `{{Config3}}` | {{功能描述}} | {{主要配置项}} |

---

## 配置文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| `pom.xml` | 根目录 | Maven 依赖配置 |
| `application.yaml` | `src/main/resources/` | Spring Boot 主配置 |
| `bootstrap.yml` | `src/main/resources/` | Spring Cloud 启动配置 |
| `logback-spring.xml` | `src/main/resources/` | Logback 日志配置 |
| `app.properties` | `src/main/resources/META-INF/` | 应用属性 |
| `mapper/*.xml` | `src/main/resources/mapper/` | MyBatis XML 映射 |

---

## 外部依赖服务

### AI 服务（如有）

| 服务名 | 客户端类 | 用途 | 主要接口 |
|--------|----------|------|----------|
| {{AI服务1}} | `{{ClientClass}}` | {{用途}} | `{{method}}` - {{说明}} |
| {{AI服务2}} | `{{ClientClass}}` | {{用途}} | `{{method}}` - {{说明}} |

### Feign 远程服务调用清单

| 序号 | 服务名 | 客户端类 | 接口数量 |
|------|--------|----------|----------|
| 1 | {{服务1}} | `{{FeignClient1}}` | {{数量}} |
| 2 | {{服务2}} | `{{FeignClient2}}` | {{数量}} |
| 3 | {{服务3}} | `{{FeignClient3}}` | {{数量}} |

> 详细接口地址和说明请参见 **Feign 客户端 (远程服务调用)** 章节

---

*文档更新时间: {{YYYY-MM-DD HH:mm:ss}}*
