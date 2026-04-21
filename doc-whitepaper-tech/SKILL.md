---
name: doc-whitepaper-tech
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

> **核心原则**：采用 **分阶段串行执行**，每扫描完一个模块立即填充文档对应章节，避免一次性加载所有信息导致上下文过长。

### 执行流程总览

```
阶段1: 项目结构扫描 → 生成文档骨架
         ↓
阶段2: 逐模块扫描 → 立即填充对应章节
         ├── Controller 层 → 填充 Controller 章节
         ├── Service 层 → 填充 Service 章节
         ├── Mapper 层 → 填充 Mapper 章节
         ├── Entity 实体类 → 填充 Entity 章节
         ├── Feign 客户端 → 填充 Feign 章节
         ├── Cache/Task/AOP → 填充对应章节
         ├── 消息中间件 → 填充消息章节
         └── Elasticsearch → 填充 ES 搜索引擎章节
         ↓
阶段3: 收尾 → 更新时间戳、验证完整性
```

---

### 步骤 1：检查现有文档，确定执行模式

**首先检查项目根目录是否存在 `project-info.md` 文件：**

```
Glob pattern: project-info.md
```

| 模式 | 条件 | 执行策略 |
|------|------|----------|
| **增量更新** | 文件存在 | 读取现有文档，仅扫描变更模块，局部更新 |
| **完整生成** | 文件不存在 | 完整扫描所有模块，生成全新文档 |

#### 完整生成模式

**阶段 1：生成文档骨架**

1. 读取 `project-info-template.md`
2. 扫描项目根目录名，替换 `{{项目名称}}`
3. 扫描 `pom.xml`，提取技术栈信息填充"技术栈"章节
4. 扫描 `src/main/java` 包结构，生成"模块架构图"
5. 生成只包含骨架的 `project-info.md`（章节标题已确定，内容待填充）

**阶段 2：逐模块扫描填充（核心执行流程）**

> ⚠️ **强制要求**：必须严格按照以下流程执行，禁止跳过或合并步骤！

**执行伪代码**：

```
FOR EACH 模块 IN [Controller, Service, Mapper, Entity, Feign, Cache, Task, AOP, MQ, Config]:
    # 步骤A: 仅扫描当前模块
    Glob/Grep 扫描该模块的文件列表

    # 步骤B: 读取必要的文件内容
    Read 需要详细分析的文件

    # 步骤C: 立即填充文档（关键！）
    Edit project-info.md 填充该模块对应章节

    # 步骤D: 清空上下文，继续下一个模块
    （进入下一轮循环，之前的扫描结果不再保留）
```

**扫描顺序与命令**：

| 序号 | 模块 | 扫描命令 | 填充章节 |
|------|------|----------|----------|
| 1 | Controller | `Glob **/controller/**/*.java` | Controller 层 |
| 2 | Service | `Glob **/service/**/*.java` | Service 层 |
| 3 | Mapper | `Glob **/mapper/**/*.java` | Mapper 层 |
| 4 | Entity | `Glob **/entity/**/*.java` | Entity 实体类 |
| 5 | Feign | `Glob **/feign/**/*.java` | Feign 客户端 |
| 6 | Cache | `Glob **/cache/**/*.java` | Cache 缓存层 |
| 7 | Task | `Glob **/task/**/*.java` | Task 定时任务 |
| 8 | AOP | `Glob **/aop/**/*.java` | AOP 切面 |
| 9 | MQ | `Grep RocketMQ\|Stream` | 消息中间件 |
| 10 | Elasticsearch | `Grep RestHighLevelClient\|ElasticsearchTemplate` | Elasticsearch 搜索引擎 |
| 11 | Config | `Glob **/config/**/*.java` | Config 配置类 |

**❌ 禁止的做法**：
- ❌ 一次性 Glob 所有模块，再统一处理
- ❌ 把所有扫描结果存在变量里，最后一次性 Write
- ❌ 跳过某个模块，留到最后补填

**✅ 正确的做法**：
- ✅ 每扫描完一个模块，**立即**调用 Edit 更新文档
- ✅ Edit 完成后，再开始下一个模块的扫描
- ✅ 如果模块不存在（Glob 结果为空），直接跳过或删除该章节

**阶段 3：收尾**

1. 删除不需要的章节（如项目无 WebSocket）
2. **更新文档时间戳**：**必须**通过 Bash 执行 `date '+%Y-%m-%d %H:%M:%S'` 获取当前系统时间，严禁自行编造时间
3. 验证文档完整性

#### 增量更新模式

**阶段 1：识别变更范围**

1. **读取现有文档**：解析当前 `project-info.md` 内容
2. **识别变更模块**：根据 Git 变更文件路径确定影响的章节

**阶段 2：按需扫描更新**

仅重新扫描变更涉及的模块，**每扫描完一个模块立即 Edit 更新对应章节**：

```bash
# 获取当前分支与 master 分支的变更文件列表
git diff master...HEAD --name-only
```

**变更文件路径与章节对应**：

| 变更路径 | 需更新的章节 |
|----------|--------------|
| `**/controller/**/*.java` | Controller 层 |
| `**/service/**/*.java` | Service 层 |
| `**/mapper/**/*.java` | Mapper 层 |
| `**/entity/**/*.java` | Entity 实体类 |
| `**/feign/**/*.java` | Feign 客户端 |
| `**/cache/**/*.java` | Cache 缓存层 |
| `**/task/**/*.java` | Task 定时任务 |
| `**/aop/**/*.java` | AOP 切面 |
| `**/consumer/**/*.java` | 消息中间件 |
| `**/constants/**/*Index*.java` | Elasticsearch 搜索引擎 |
| `**/config/**/*.java` | Config 配置类 |

**阶段 3：收尾**

1. **更新时间戳**：**必须**通过 Bash 执行 `date '+%Y-%m-%d %H:%M:%S'` 获取当前系统时间，严禁自行编造时间

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

> **说明**：模板中不使用固定序号，章节编号在生成文档时根据实际存在的模块动态编排。下表仅表示章节名称与扫描路径的对应关系。

| 章节名称 | 扫描路径 |
|----------|----------|
| Controller 层 | `**/controller/**/*.java` |
| Service 层 | `**/service/**/*.java` |
| Mapper 层 | `**/mapper/**/*.java` |
| Entity 实体类 | `**/entity/**/*.java` |
| Feign 客户端 | `**/feign/**/*.java` |
| Cache 缓存层 | `**/cache/**/*.java` |
| Task 定时任务 | `**/task/**/*.java` |
| AOP 切面 | `**/aop/**/*.java` |
| 消息中间件 | `**/stream/**/*.java`, `**/consumer/**/*.java`, `**/producer/**/*.java` |
| Elasticsearch 搜索引擎 | `**/constants/**/*Index*.java`, `**/utils/**/ES*.java` |
| Config 配置类 | `**/config/**/*.java` |

---

## 模块扫描方法参考

> ⚠️ **重要**：以下章节仅作为各模块的扫描方法参考，**不是独立执行步骤**！
>
> 实际执行时，应严格按照"步骤1"中"阶段2"的流程：**扫描一个模块 → 立即 Edit 填充 → 再扫描下一个模块**

---

### 2.1 项目架构识别

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

### 2.2 模块架构图生成

> ⚠️ **注意**：本节仅为架构图生成方法参考，实际执行时按"步骤1-阶段2"的流程进行。

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

### 2.3 核心分层组件扫描

> ⚠️ **注意**：本节仅为各层扫描方法参考，实际执行时按"步骤1-阶段2"的流程进行。

#### Controller 层

```
Glob pattern: **/controller/**/*.java
Glob pattern: **/api/**/*.java
Glob pattern: **/interfaces/**/*.java
```

**提取信息**：
- 类名、路径
- `@RequestMapping` 路径前缀
- 主要方法（`@GetMapping`/`@PostMapping` 等）

#### Service 层

```
Glob pattern: **/service/**/*.java
Glob pattern: **/application/**/*.java
```

**提取信息**：
- 接口名、实现类名（以 `Impl` 结尾）
- 主要方法名
- 子模块划分（如 `knowledge/`、`process/` 等）

#### Mapper 层

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

### 2.4 数据模型扫描

> ⚠️ **注意**：本节仅为数据模型扫描方法参考，实际执行时按"步骤1-阶段2"的流程进行。

#### Entity 实体类

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

#### DTO/VO 类

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

### 2.5 外部依赖扫描

> ⚠️ **注意**：本节仅为外部依赖扫描方法参考，实际执行时按"步骤1-阶段2"的流程进行。

#### Feign 客户端

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

#### 7.1 Cache 缓存层

```
Glob pattern: **/cache/**/*.java
Glob pattern: **/redis/**/*.java
```

**提取信息**：Redis Key 前缀、过期策略

#### 7.2 Task 定时任务

```
Glob pattern: **/task/**/*.java
Glob pattern: **/job/**/*.java
Glob pattern: **/schedule/**/*.java
```

**提取信息**：`@XxlJob` 或 `@Scheduled` 注解中的任务名称和 Cron 表达式

#### 7.3 AOP 切面

```
Glob pattern: **/aop/**/*.java
Glob pattern: **/aspect/**/*.java
```

**提取信息**：切面类、注解、功能、应用场景

#### 7.4 消息中间件

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

#### 7.4.4 Elasticsearch 扫描

```
# 检测 Elasticsearch 使用
Grep pattern: RestHighLevelClient|ElasticsearchTemplate|@Document|@Index|elasticsearch
Glob pattern: **/constants/**/*Index*.java
Glob pattern: **/utils/**/ES*.java
```

**关键提取**：

1. **识别索引常量类**：
   - 扫描 `constants/` 包下的索引定义类（如 `ESIndex.java`）
   - 提取索引名称常量（`String INDEX_NAME = "index_name"`）
   - 识别索引用途（通过常量命名和注释推断）

2. **识别 ES 工具类**：
   - 扫描 `utils/` 包下的 ES 相关工具类
   - 提取文档操作类（`ESDocHolder`、`ESDocumentHelper` 等）
   - 提取搜索查询类（`ESSearchHolder`、`ESSearchHelper` 等）

3. **提取索引信息**：
   - 索引名称、常量定义、用途说明
   - 索引模式（单索引/按时间分索引）
   - 数据来源（通过查找 `index()`、`update()` 等方法的调用位置）

4. **Elasticsearch 文档格式**：

```markdown
### Elasticsearch 搜索引擎

**概述**：项目使用 **Elasticsearch** 实现数据搜索和分析，主要用于{{主要用途}}。

| 配置项 | 说明 |
|--------|------|
| 框架 | Elasticsearch {{版本号}} |
| 客户端类 | `RestHighLevelClient` |
| 工具类 | `{{ESDocHolder}}` (文档操作), `{{ESSearchHolder}}` (搜索查询) |

#### 索引信息

| 索引名称 | 常量定义 | 用途 | 索引模式 |
|----------|----------|------|----------|
| {{index-name-1}} | `{{INDEX_CONSTANT_1}}` | {{索引用途}} | 单索引/按月分索引 |
| {{index-name-2}} | `{{INDEX_CONSTANT_2}}` | {{索引用途}} | 单索引/按月分索引 |
```

#### 7.5 Config 配置类

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

1. **分阶段串行执行（重要）**：
   - ✅ **扫描一个，填充一个**：每完成一个模块扫描，立即 Edit 文档填充对应章节
   - ❌ **禁止批量扫描后统一写入**：这会导致上下文过长，信息遗漏或错误
   - 使用 `Edit` 工具增量更新文档，而非 `Write` 全量覆盖

2. **Feign 接口提取**：必须读取接口文件内容，不能仅通过文件名推断

3. **路径拼接**：Feign 接口完整路径 = `@FeignClient.path` + `@XxxMapping.value`

4. **泛型解析**：返回类型需要解析泛型参数，如 `Result<OmsWaybillDetailVO>` 中的 `OmsWaybillDetailVO`

5. **章节删除**：如果项目没有某个模块，需要删除对应章节

6. **时间戳**：**必须**通过 Bash 执行 `date '+%Y-%m-%d %H:%M:%S'` 获取当前系统时间，格式为 `YYYY-MM-DD HH:mm:ss`，严禁自行编造时间

---
