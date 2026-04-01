---
name: 生成项目信息
description: 扫描 Java 项目结构，根据模板生成项目框架文档（project-info.md）。自动识别项目架构模式，提取 Controller/Service/Mapper/Feign 等各层信息，生成标准化的项目信息文档。
---

# 生成项目信息

当用户要求生成项目信息、扫描项目结构、创建项目文档、更新 project-info.md 时，使用本技能。

## 适用范围

- Java/Spring Boot/Spring Cloud 项目
- 分层架构（Controller/Service/Mapper）
- DDD 架构（Interfaces/Application/Domain/Infrastructure）
- 微服务架构
- 需要 Feign 接口清单提取的项目

## 执行流程

### 步骤 1：检查现有文档，确定执行模式并生成/更新文档

**首先检查项目根目录是否存在 `project-info.md` 文件：**

```
Glob pattern: project-info.md
```

| 模式 | 条件 | 执行策略 |
|------|------|----------|
| **增量更新** | 文件存在 | 读取现有文档，仅扫描变更模块，局部更新 |
| **完整生成** | 文件不存在 | 完整扫描所有模块，生成全新文档 |

#### 完整生成模式

1. 读取 `project-info-template.md`
2. 替换所有 `{{变量}}` 为实际值
3. 删除不需要的章节（如项目无 WebSocket）
4. 调整章节编号
5. 更新文档时间戳为当前系统时间
6. 写入 `project-info.md`

#### 增量更新模式

1. **读取现有文档**：解析当前 `project-info.md` 内容
2. **识别变更范围**：根据 Git 变更文件路径确定影响的章节
3. **局部更新**：仅重新扫描变更涉及的模块，保留未变更章节
4. **更新时间戳**：更新为当前系统时间
5. **写入更新**：覆盖原文件

**增量扫描命令**：

```bash
# 获取当前分支与 master 分支的差异 commits
git log master..HEAD --oneline

# 获取当前分支与 master 分支的变更文件列表
git diff master...HEAD --name-only

# 获取变更文件及状态（新增/修改/删除）
git diff master...HEAD --name-status
```

**章节与扫描路径对应关系**：

| 模板章节 | 章节名称 | 扫描路径 |
|----------|----------|----------|
| 3.1 | Controller 层 | `**/controller/**/*.java` |
| 3.2 | Service 层 | `**/service/**/*.java` |
| 3.3 | Mapper 层 | `**/mapper/**/*.java` |
| 3.4 | Entity 实体类 | `**/entity/**/*.java` |
| 3.5 | Feign 客户端 | `**/feign/**/*.java` |
| 3.6 | Cache 缓存层 | `**/cache/**/*.java` |
| 3.7 | Task 定时任务 | `**/task/**/*.java` |
| 3.8 | AOP 切面 | `**/aop/**/*.java` |
| 3.9 | 消息中间件 | `**/stream/**/*.java`, `**/consumer/**/*.java`, `**/producer/**/*.java` |
| 3.10 | Config 配置类 | `**/config/**/*.java` |

---

### 步骤 2：识别项目架构模式

扫描 `src/main/java` 下的包结构：

```
Glob pattern: src/main/java/**/*
```

| 特征包名 | 架构模式 | 说明 |
|----------|----------|------|
| `controller/service/dao` 或 `mapper` | 分层架构 | Spring MVC 标准分层 |
| `interfaces/application/domain/infrastructure` | DDD 架构 | 领域驱动设计 |
| `api/rpc/job/mq` | 微服务架构 | 按调用方式划分 |
| `web/biz/dal` | 阿里巴巴架构 | 阿里内部规范 |

---

### 步骤 3：生成模块架构图

**模块架构图必须根据实际扫描结果动态生成，不使用固定模板。**

#### 生成步骤

1. **扫描实际包结构**：
   ```
   Glob pattern: src/main/java/com/jt/**/*.java
   ```

2. **识别核心目录**：提取 `src/main/java/<base-package>/` 下的直接子目录

3. **根据实际存在生成树形图**：只展示项目中实际存在的包

#### 不同架构模式的示例

**Spring MVC 分层架构**：
```
src/main/java/com/jt/project/
├── controller/        # 控制器层
├── service/           # 服务层
│   └── impl/          # 服务实现
├── mapper/            # 数据访问层
├── model/
│   ├── entity/        # 实体类
│   ├── dto/           # 数据传输对象
│   ├── vo/            # 视图对象
│   └── enums/         # 枚举类
├── feign/             # Feign 客户端
├── config/            # 配置类
└── util/              # 工具类
```

#### 生成规则

- **只展示实际存在的包**：扫描后确认包下有 `.java` 文件才列出
- **最多展示两层**：核心包 + 一级子包（如 model/entity）
- **不展示实现细节**：`impl/`、`handler/`、`helper/` 等子包不单独列出
- **业务子模块可列出**：如 `service/order/`、`service/user/` 等明确业务划分
- **标注可选组件**：如 WebSocket、AOP 等非必需组件仅在存在时列出

---

### 步骤 4：扫描核心分层组件

#### 4.1 Controller 层（对应模板 3.1）

```
Glob pattern: **/controller/**/*.java
Glob pattern: **/api/**/*.java
Glob pattern: **/interfaces/**/*.java
```

**提取信息**：
- 类名、路径
- `@RequestMapping` 路径前缀
- 主要方法（`@GetMapping`/`@PostMapping` 等）

#### 4.2 Service 层（对应模板 3.2）

```
Glob pattern: **/service/**/*.java
Glob pattern: **/application/**/*.java
```

**提取信息**：
- 接口名、实现类名（以 `Impl` 结尾）
- 主要方法名
- 子模块划分（如 `knowledge/`、`process/` 等）

#### 4.3 Mapper 层（对应模板 3.3）

```
Glob pattern: **/mapper/**/*.java
Glob pattern: **/dao/**/*.java
Glob pattern: **/repository/**/*.java
```

**提取信息**：
- Mapper 接口名
- 关联实体（通过泛型或命名推断）
- 主要 SQL 操作类型

---

### 步骤 5：扫描数据模型

#### 5.1 Entity 实体类（对应模板 3.4）

```
Glob pattern: **/model/entity/**/*.java
Glob pattern: **/entity/**/*.java
Glob pattern: **/domain/**/*.java
Glob pattern: **/pojo/**/*.java
```

**关键提取**：

1. **识别基础实体类**：
   - 扫描以 `Base`、`Abstract`、`Generic` 开头的类
   - 扫描 `common/`、`base/`、`core/` 包下的实体类
   - 识别继承关系（`extends Model<T>`、`@MappedSuperclass`）
   - 常见模式：
     - MyBatis-Plus: 继承 `Model<T>` 的 `BaseEntity`
     - JPA: 使用 `@MappedSuperclass` 的抽象类
     - 自定义: `BaseId` → `BaseEntity` → `Base` 多层继承
     - 无基础类: 所有实体独立定义字段

2. **提取字段信息（必须完整列出所有字段）**：
   - 字段名、字段类型、字段说明（JavaDoc）
   - 表名（`@TableName` 注解）
   - **重要**：每个实体类必须列出所有字段的完整信息，包括继承的字段
   - 字段格式：`| 字段名 | 类型 | 说明 |`

3. **按业务模块分类**：
   - 根据包结构或命名前缀识别业务模块

4. **实体类文档格式**：

```markdown
##### EntityName (表名: {{table_name}})

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `field1` | `String` | 字段1说明 |
| `field2` | `Integer` | 字段2说明 |
```

#### 5.2 DTO/VO 类

```
Glob pattern: **/dto/**/*.java
Glob pattern: **/vo/**/*.java
Glob pattern: **/param/**/*.java
Glob pattern: **/request/**/*.java
Glob pattern: **/response/**/*.java
```

**提取信息**：
- 按用途分类：入参（DTO/Param/Request）、出参（VO/Result/Response）
- 主要字段和用途说明

---

### 步骤 6：扫描外部依赖

#### 6.1 Feign 客户端（对应模板 3.5）

```
Glob pattern: **/feign/**/*.java
Glob pattern: **/client/**/*.java
```

**关键提取**：

1. 读取 `@FeignClient` 注解：
   - `name` / `value`: 目标服务名
   - `path`: 路径前缀

2. **读取接口方法（必须完整列出所有接口）**：
   - 接口路径（`@GetMapping`/`@PostMapping` 等）
   - HTTP 方法、入参类型、返回类型
   - **重要**：每个 Feign 客户端必须列出所有接口的完整信息

3. **Feign 接口文档格式**：

```markdown
#### 服务名称 (`FeignClientName`)

| 属性 | 值 |
|------|-----|
| 服务名 | `service-name` |
| 路径前缀 | `/api-prefix` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/api/path1` | GET | 接口1说明 | `param1: Type` | `Result<VO>` |
| `/api/path2` | POST | 接口2说明 | `DTO` | `Result<VO>` |
```

**示例解析**：

```java
@FeignClient(name = "ylwaybillouterapi", path = "/waybillouterapi")
public interface WaybillFeignClient {
    @GetMapping({"/waybillDetailByNo"})
    Result<OmsWaybillDetailVO> getDetailByNo(@RequestParam("waybillNo") String waybillNo);
    
    @PostMapping(value = "/common/get")
    Result<OmsWaybillDetailVO> commonWaybillGet(@RequestBody WaybillDetailSearchDTO dto);
}
```

提取结果表格：
| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/waybillDetailByNo` | GET | 根据运单号获取运单详情 | `waybillNo: String` | `Result<OmsWaybillDetailVO>` |
| `/common/get` | POST | 通用运单查询 | `WaybillDetailSearchDTO` | `Result<OmsWaybillDetailVO>` |

---

### 步骤 7：扫描基础设施组件

#### 7.1 Cache 缓存层（对应模板 3.6）

```
Glob pattern: **/cache/**/*.java
Glob pattern: **/redis/**/*.java
```

**提取信息**：Redis Key 前缀、过期策略

#### 7.2 Task 定时任务（对应模板 3.7）

```
Glob pattern: **/task/**/*.java
Glob pattern: **/job/**/*.java
Glob pattern: **/schedule/**/*.java
```

**提取信息**：`@XxlJob` 或 `@Scheduled` 注解中的任务名称和 Cron 表达式

#### 7.3 AOP 切面（对应模板 3.8）

```
Glob pattern: **/aop/**/*.java
Glob pattern: **/aspect/**/*.java
```

**提取信息**：切面类、注解、功能、应用场景

#### 7.4 消息中间件（对应模板 3.9）

项目中可能同时存在 **Spring Cloud Stream** 和 **RocketMQ** 两种消息中间件用法，需要分别扫描。

##### 7.4.1 检测消息中间件类型

```
# 检测 Spring Cloud Stream
Glob pattern: **/stream/**/*.java
Grep pattern: @Input|@Output|InputInterface|OutputInterface|MessageProducer|MessageReceiver

# 检测 RocketMQ（标准模式）
Grep pattern: @RocketMQMessageListener|RocketMQTemplate|DefaultMQProducer|DefaultMQPushConsumer
Grep pattern: yl-sqs-platform-rocketmq|RocketMQProducer|RocketMQConsumer

# 检测 RocketMQ（动态模式）
Grep pattern: @RocketMQDynamicListener|RocketMQDynamicPublisher
```

##### 7.4.2 Spring Cloud Stream 扫描

```
Glob pattern: **/stream/**/*.java
```

**关键提取**：
1. 识别 `InputInterface` 和 `OutputInterface` 接口
2. 提取 `@Input` 和 `@Output` 注解的 channel 名称
3. 识别 `MessageProducer` 和 `MessageReceiver` 类
4. 提取消息类型和处理逻辑

**Output（消息生产）表格格式**：

| Channel 名称 | 方法 | 消息类型 | 说明 |
|--------------|------|----------|------|
| `channel-name-output` | `methodName()` | `MessageDTO` | 消息说明 |

**Input（消息消费）表格格式**：

| Channel 名称 | 方法 | 消息类型 | 处理逻辑 | 说明 |
|--------------|------|----------|----------|------|
| `channel-name-input` | `methodName()` | `MessageDTO` | `service.method()` | 消息说明 |

##### 7.4.3 RocketMQ 扫描

```
# 扫描生产者（标准模式）
Grep pattern: RocketMQTemplate|DefaultMQProducer|RocketMQProducer
Glob pattern: **/producer/**/*.java
Glob pattern: **/mq/**/*.java

# 扫描消费者（标准模式）
Grep pattern: @RocketMQMessageListener
Glob pattern: **/consumer/**/*.java
Glob pattern: **/listener/**/*.java

# 扫描生产者（动态模式）
Grep pattern: RocketMQDynamicPublisher
Grep pattern: -A 5 -B 5 RocketMQDynamicPublisher  # 查找调用位置上下文

# 扫描消费者（动态模式）
Grep pattern: @RocketMQDynamicListener
```

**关键提取**：
1. **Topic 信息**：从 `@RocketMQMessageListener` 或 `@RocketMQDynamicListener` 注解提取 topic
2. **生产者信息**：识别 `RocketMQTemplate`、`DefaultMQProducer` 或 `RocketMQDynamicPublisher` 的使用位置
3. **消息类型**：提取发送/消费的消息 DTO 类型
4. **消费模式**：识别集群消费还是广播消费
5. **动态发布器调用位置**：通过 `RocketMQDynamicPublisher` 的 grep 结果定位具体调用点，提取调用方法名、所在类名

**RocketMQ 生产者表格格式**：

| Topic 名称 | Tag | 生产者类 | 消息类型 | 说明 |
|------------|-----|----------|----------|------|
| `topic-name` | `tag-name` | `ProducerClass` | `MessageDTO` | 发送场景说明 |

**RocketMQ 动态发布器表格格式**：

| Topic 名称 | Tag | 发布器类 | 调用位置 | 消息类型 | 说明 |
|------------|-----|----------|----------|----------|------|
| `topic-name` | `tag-name` | `RocketMQDynamicPublisher` | `ServiceClass.methodName()` | `MessageDTO` | 发送场景说明 |

**RocketMQ 消费者表格格式**：

| Topic 名称 | 消费者类 | 消息类型 | 消费模式 | 说明 |
|------------|----------|----------|----------|------|
| `topic-name` | `ConsumerClass` | `MessageDTO` | 集群/广播 | 消费场景说明 |

**RocketMQ 动态监听器表格格式**：

| Topic 名称 | 消费者类 | 注解 | 消息类型 | 消费模式 | 说明 |
|------------|----------|------|----------|----------|------|
| `topic-name` | `ConsumerClass` | `@RocketMQDynamicListener` | `MessageDTO` | 集群/广播 | 消费场景说明 |

#### 7.5 Config 配置类（对应模板 3.10）

```
Glob pattern: **/config/**/*.java
Glob pattern: **/configuration/**/*.java
```

**提取信息**：配置类名、功能说明

---

### 步骤 8：读取配置文件

```
Read: pom.xml         -> 提取依赖和版本
Read: application.yml -> 提取配置信息
Read: bootstrap.yml   -> 提取 Spring Cloud 配置
```

---

## 模板变量映射

### 基础信息

| 变量 | 来源 | 提取方式 |
|------|------|----------|
| `{{项目名称}}` | 根目录名 | 从路径提取最后一个目录名 |
| `{{项目类型}}` | 人工确认或推断 | 根据 pom.xml 依赖推断 |
| `{{核心功能描述}}` | README 或人工 | 读取 README.md |
| `{{框架名称及版本}}` | pom.xml | `<parent>` 或 `<spring-boot.version>` |
| `{{ORM框架及版本}}` | pom.xml | `mybatis-plus-boot-starter` 版本 |
| `{{数据库类型及版本}}` | pom.xml | `mysql-connector` 版本 |
| `{{缓存技术}}` | pom.xml | `redis`/`redisson` 依赖 |
| `{{消息队列技术}}` | pom.xml | `rabbitmq`/`rocketmq` 依赖 |

### 包结构变量

| 变量 | 提取方式 |
|------|----------|
| `{{web/api/controller层包名}}` | 扫描存在的包名 |
| `{{service层包名}}` | 扫描存在的包名 |
| `{{dao/mapper/repository层包名}}` | 扫描存在的包名 |
| `{{model/entity/dto/vo包名}}` | 扫描存在的包名 |

### 类名变量

| 变量 | 提取方式 |
|------|----------|
| `{{ControllerN}}` | 从 Controller 类提取 |
| `{{ServiceN}}` | 从 Service 接口提取 |
| `{{MapperN}}` | 从 Mapper 接口提取 |
| `{{FeignClientN}}` | 从 Feign 接口提取 |

---

## 参考文件

- **模板文件**: [project-info-template.md](project-info-template.md)
- **参考示例**: [project-info-example.md](references/project-info-example.md)

---

## 注意事项

1. **Feign 接口提取**：必须读取接口文件内容，不能仅通过文件名推断
2. **路径拼接**：Feign 接口完整路径 = `@FeignClient.path` + `@XxxMapping.value`
3. **泛型解析**：返回类型需要解析泛型参数，如 `Result<OmsWaybillDetailVO>` 中的 `OmsWaybillDetailVO`
4. **章节删除**：如果项目没有某个模块，需要删除对应章节并调整编号
5. **时间戳**：文档更新时间使用当前系统时间，格式为 `YYYY-MM-DD HH:mm:ss`

---
