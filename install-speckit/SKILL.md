---
name: install-speckit
description: 快速初始化 Speckit 环境，配置项目技术栈和开发规范。
---

# 使用说明

当用户说 **[初始化 speckit]** 时，按以下任务顺序执行：

---

## 任务 1：更新 .gitignore 文件

**目标**：确保项目忽略 Speckit 相关文件和 IDE 配置。

**操作步骤**：
1. 检索当前项目中所有 `.gitignore` 文件
2. 在每个 `.gitignore` 文件末尾追加以下内容（如已存在则跳过）：

```gitignore
# Speckit
.specify/
.claude/
specs/

# IDE
.idea/
CLAUDE.md
```

**验证**：确认所有 `.gitignore` 文件都包含上述内容。

---

## 任务 2：执行 Speckit 初始化命令

**目标**：初始化 Speckit 环境。

**操作步骤**：在项目根目录执行以下命令：

```bash
specify init --here --force --ai claude --script ps
```

**错误处理**：
- 如果命令执行失败，最多重试 3 次
- 每次重试前等待 2 秒
- 3 次重试后仍失败，向用户报告错误信息

**验证**：确认命令执行成功，无错误输出。

---

## 任务 3：创建技术栈配置文件

**目标**：在项目根目录创建 `CLAUDE.md` 文件，定义项目技术栈和开发规范。

**操作步骤**：创建 `CLAUDE.md` 文件，内容如下：

```markdown
# 项目技术栈

## 核心框架

| 框架 | 用途 |
|------|------|
| Spring Boot | 基础框架 |
| Mybatis-Plus | ORM 框架 |
| Spring Cloud | 微服务框架 |
| Spring Cloud Alibaba | 阿里巴巴微服务组件 |
| Spring Cloud Stream | 消息驱动 |
| Spring Cloud OpenFeign | 服务调用 |
| Redisson | 分布式锁/Redis 客户端 |
| Sharding-JDBC Spring Boot Starter | 分库分表 |

## 项目结构

### 分层架构

```
Controller (请求处理) -> Service (业务逻辑) -> Mapper (数据访问) -> Database (数据存储)
```

| 层级 | 职责 |
|------|------|
| Controller | 接收请求、参数校验、调用 Service |
| Service | 业务逻辑处理、事务管理 |
| Mapper | 数据库操作、SQL 映射 |
| Database | 数据持久化存储 |

## 开发规范

### 接口设计

| 规范项 | 要求 |
|--------|------|
| HTTP 方法 | 仅允许 GET 和 POST |
| OSS 操作 | 使用 `YlFileUtil` |
| 分布式锁 | 使用 `Redisson` 或 `IDlock` |
| ES 查询 | 使用 `ESSearchHelper` |

### 命名规范

| 类型 | 命名规则 | 示例 |
|------|----------|------|
| 入参对象（分页） | `XxxPageDTO` | `UserQueryPageDTO` |
| 入参对象（普通） | `XxxDTO` | `UserCreateDTO` |
| 出参对象 | `XxxVO` | `UserDetailVO` |
| Service 接口 | `IXxxService` | `IUserService` |
| Service 实现 | `XxxServiceImpl` | `UserServiceImpl` |

### 基础类

| 用途 | 类路径 |
|------|--------|
| 操作人信息 | `com.yl.common.base.model.dto.BaseOperatorDTO` |
| 操作人 + 分页 | `com.yl.common.base.model.dto.BaseOperatorPageDTO` |
| 分页查询 | `com.yl.common.base.model.dto.BasePageDTO` |
| 分页 + 时间范围 | `com.yl.common.base.model.dto.BaseTimePageDTO` |

### 统一返回实体

```java
com.yl.common.base.model.vo.Result<T>
```

### 实体映射工具

| 工具 | 优先级 |
|------|--------|
| Mapstruct | 优先使用（如项目已有） |
| OrikaBeanMapper | 备选方案 |

### ID 生成策略

```java
IdGenerator<Long>
```
```

**验证**：确认 `CLAUDE.md` 文件已创建且内容正确。

---

## 执行总结

所有任务完成后，向用户报告：
1. 已更新的 `.gitignore` 文件数量
2. Speckit 初始化是否成功
3. `CLAUDE.md` 文件创建状态