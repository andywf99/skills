---
name: 生成项目信息
description: 扫描 Java 项目结构，根据模板生成项目框架文档（project-info.md）。自动识别项目架构模式，提取 Controller/Service/Mapper/Feign 等各层信息，生成标准化的项目信息文档。
---

# 生成项目信息

当用户要求生成项目信息、扫描项目结构、创建项目文档、输出 project-info.md 时，使用本技能。

## 适用范围

- Java/Spring Boot/Spring Cloud 项目
- 分层架构（Controller/Service/Mapper）
- DDD 架构（Interfaces/Application/Domain/Infrastructure）
- 微服务架构
- 需要 Feign 接口清单提取的项目

## 输入约定

- **模板文件**: `project-info-template.md`（当前项目根目录或 skill 目录）
- **参考示例**: `project-info.md`（当前项目根目录，如已存在）

## 执行步骤

### 步骤 1：识别项目架构模式

扫描项目根目录和 `src/main/java` 下的包结构，识别架构模式：

| 特征包名 | 架构模式 | 说明 |
|----------|----------|------|
| `controller/service/dao` 或 `mapper` | 分层架构 | Spring MVC 标准分层 |
| `interfaces/application/domain/infrastructure` | DDD 架构 | 领域驱动设计 |
| `api/rpc/job/mq` | 微服务架构 | 按调用方式划分 |
| `web/biz/dal` | 阿里巴巴架构 | 阿里内部规范 |

**扫描命令**：

```
Glob pattern: src/main/java/**/*
```

### 步骤 2：扫描各层组件

#### 2.1 扫描 Controller 层

```
Glob pattern: **/controller/**/*.java
Glob pattern: **/api/**/*.java
Glob pattern: **/interfaces/**/*.java
```

提取信息：
- 类名
- 路径
- `@RequestMapping` 等注解中的路径前缀
- 主要方法（通过 `@GetMapping`/`@PostMapping` 等识别）

#### 2.2 扫描 Service 层

```
Glob pattern: **/service/**/*.java
Glob pattern: **/application/**/*.java
```

提取信息：
- 接口名
- 实现类名（以 `Impl` 结尾）
- 主要方法名
- 子模块划分（如 `knowledge/`、`process/` 等）

#### 2.3 扫描 Mapper 层

```
Glob pattern: **/mapper/**/*.java
Glob pattern: **/dao/**/*.java
Glob pattern: **/repository/**/*.java
```

提取信息：
- Mapper 接口名
- 关联实体（通过泛型或命名推断）
- 主要 SQL 操作类型

#### 2.4 扫描 Feign 客户端

```
Glob pattern: **/feign/**/*.java
Glob pattern: **/client/**/*.java
```

**关键提取**：
1. 读取 `@FeignClient` 注解获取：
   - `name` / `value`: 目标服务名
   - `path`: 路径前缀
2. 读取接口方法上的 `@GetMapping`/`@PostMapping` 等获取：
   - 接口路径
   - HTTP 方法
   - 入参类型
   - 返回类型

**示例代码解析**：

```java
@FeignClient(name = "ylwaybillouterapi", path = "/waybillouterapi")
public interface WaybillFeignClient {
    @GetMapping({"/waybillDetailByNo"})
    Result<OmsWaybillDetailVO> getDetailByNo(@RequestParam("waybillNo") String waybillNo);
}
```

提取结果：
- 服务名: `ylwaybillouterapi`
- 接口路径: `/waybillouterapi/waybillDetailByNo`
- HTTP 方法: `GET`
- 入参: `waybillNo`
- 返回: `Result<OmsWaybillDetailVO>`

### 步骤 3：扫描其他组件

#### 3.1 缓存层

```
Glob pattern: **/cache/**/*.java
```

提取 Redis Key 前缀和过期策略。

#### 3.2 定时任务

```
Glob pattern: **/task/**/*.java
Glob pattern: **/job/**/*.java
```

提取 `@XxlJob` 注解中的任务名称。

#### 3.3 消息监听

```
Glob pattern: **/listener/**/*.java
Glob pattern: **/stream/**/*.java
```

### 步骤 4：读取配置文件

```
Read: pom.xml         -> 提取依赖和版本
Read: application.yml -> 提取配置信息
```

### 步骤 5：填充模板

1. 读取 `project-info-template.md`
2. 替换所有 `{{变量}}` 为实际值
3. 删除不需要的章节（如项目无 WebSocket）
4. 调整章节编号
5. 写入 `project-info.md`

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

### Feign 接口变量

| 变量 | 提取方式 |
|------|----------|
| `{{服务N名称}}` | `@FeignClient.name` |
| `{{/api/pathN}}` | 方法注解路径拼接 |
| `{{DTO}}` | `@RequestBody` 类型 |
| `{{VO}}` | 返回类型泛型参数 |

## 输出格式

### Feign 接口表格格式

```markdown
#### 3.4.N {{服务名称}} (`{{FeignClient}}`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `{{完整路径}}` | POST/GET | {{说明}} | 入参: `{{DTO}}`, 返回: `{{VO}}` |
```

### 调用链路格式

根据识别的架构模式选择对应的调用链路：

**Spring MVC 分层架构**：
```
HTTP Request -> Controller -> Service -> Mapper -> MySQL
                     ↓
                Redis Cache
                     ↓
               Feign Client -> 外部微服务
```

**DDD 架构**：
```
HTTP Request -> Controller -> Application Service -> Domain Service -> Repository -> PostgreSQL
                                           ↓
                                      Domain Model
                                           ↓
                                      Event Publisher -> Message Queue
```

## 参考文件

- **模板文件**: [project-info-template.md](project-info-template.md)
- **参考示例**: [project-info-example.md](references/project-info-example.md)

## 执行示例

### 示例 1：基础项目

**用户输入**：
```
/generate-project-info
```

**执行过程**：
1. 扫描项目结构
2. 识别为 Spring MVC 分层架构
3. 提取 8 个 Controller、25 个 Service、15 个 Mapper
4. 提取 10 个 Feign 客户端共 30 个接口
5. 生成 project-info.md

### 示例 2：指定模板

**用户输入**：
```
/generate-project-info --template custom-template.md
```

使用自定义模板生成。

## 注意事项

1. **Feign 接口提取**：必须读取接口文件内容，不能仅通过文件名推断
2. **路径拼接**：Feign 接口完整路径 = `@FeignClient.path` + `@XxxMapping.value`
3. **泛型解析**：返回类型需要解析泛型参数，如 `Result<OmsWaybillDetailVO>` 中的 `OmsWaybillDetailVO`
4. **章节删除**：如果项目没有某个模块（如 WebSocket），需要删除对应章节并调整编号
5. **时间戳**：文档更新时间使用当前时间，格式为 `YYYY-MM-DD HH:mm:ss`

## 常见问题

### Q1: 项目没有 feign 包怎么办？

扫描 `client/`、`remote/`、`rpc/` 等包，或跳过 Feign 章节。

### Q2: 如何识别 DDD 架构？

检查是否存在 `interfaces/`、`application/`、`domain/`、`infrastructure/` 包。

### Q3: 多模块项目怎么处理？

识别子模块，在模块架构图中展示多模块结构。

### Q4: Feign 接口方法过多怎么办？

按服务分组，每个服务一个子章节，接口过多时可以只列出主要接口并标注"等N个接口"。
