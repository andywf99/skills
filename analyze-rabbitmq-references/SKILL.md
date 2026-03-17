---
name: analyze-rabbitmq-references
description: 分析项目中 RabbitMQ 的 input/output 配置，通过 MCP 查询 destination 被引用的项目列表，输出 CSV 报告。
---

# RabbitMQ 引用分析技能

该技能用于分析项目中 RabbitMQ 的 input/output 配置，查询 destination 被引用的项目列表，并输出 CSV 报告。

## 使用场景

当用户提到以下关键词时，**必须**加载并执行此技能：
- "分析 RabbitMQ 引用"
- "RabbitMQ input/output 分析"
- "RabbitMQ destination 引用"
- "导出 RabbitMQ 配置报告"

---

## 执行步骤

### 步骤一：读取项目列表

读取工作目录下的 `projects.txt` 文件，获取项目列表。

```
文件路径: {工作目录}/projects.txt
```

### 步骤二：读取 Stream 配置文件

对于每个项目，读取对应的 stream.yml 配置文件：

```
文件路径: {工作目录}/streams/{项目名}.yml
```

### 步骤三：解析 RabbitMQ 的 input/output 配置

从 YAML 文件中解析以下结构：

```yaml
spring:
  cloud:
    stream:
      bindings:
        {binding-name}-input:    # 以 -input 结尾的是消费者
          destination: {destination-name}
          binder: rabbit1        # binder 类型为 rabbit
        {binding-name}-output:   # 以 -output 结尾的是生产者
          destination: {destination-name}
          binder: rabbit1
      binders:
        rabbit1:
          type: rabbit           # 确认是 RabbitMQ
```

**提取规则：**
1. 只提取 `binder` 类型为 `rabbit` 的配置
2. `input` 结尾的 binding 为消费者
3. `output` 结尾的 binding 为生产者
4. 提取 `destination` 字段作为目标队列/交换机名称

### 步骤四：通过 MCP 查询引用项目

对于每个 destination，使用 MCP 工具查询被引用的项目列表：

```
工具名称: mcp__sqs-mcp-server-api__ArcherySQL-QueryRabbitExchangeReference
参数: exchanges = {destination-name}
```

### 步骤五：生成 CSV 报告

将所有信息整合后输出 CSV 文件，包含以下表头：

| 表头 | 说明 |
|------|------|
| input/output | stream 配置的 input 或 output 的 key |
| 类型 | 生产者或消费者（input 为消费者，output 为生产者） |
| destination | input 或 output 的目标 |
| project | 所属项目 |
| reference project | destination 被引用的项目 |

**输出文件路径：** `{工作目录}/rabbitmq-reference-report.csv`

**CSV 格式示例：**
```csv
input/output,类型,destination,project,reference project
session-create-close-evaluation-result-input,消费者,session-create-close-evaluation-result,yl-jms-css-approval-api,"project_1,project_2"
approval-handle-result-output,生产者,approval-handle-result,yl-jms-css-approval-api,"project_1"
```

---

## 注意事项

1. **YAML 解析注意事项：**
   - 注意处理注释行（以 `#` 开头）
   - 注意处理多层级嵌套
   - 有些 binding 可能没有显式指定 `binder`，需要检查 `default-binder` 配置

2. **MCP 调用注意事项：**
   - 可以批量查询多个 destination（用逗号分隔）
   - 如果查询结果为空，reference project 列填写 "无"

3. **输出格式注意事项：**
   - CSV 文件使用 UTF-8 编码
   - 如果 reference project 有多个，用逗号分隔并用双引号包裹

---

## 执行示例

用户执行 `/analyze-rabbitmq-references` 后，AI 应：

1. 读取 `projects.txt` 获取项目列表
2. 遍历每个项目的 `streams/{项目名}.yml` 文件
3. 解析 RabbitMQ 相关的 input/output 配置
4. 调用 MCP 工具查询每个 destination 的引用项目
5. 生成 `rabbitmq-reference-report.csv` 文件
6. 输出分析摘要，包括：
   - 分析的项目数量
   - 发现的 input/output 数量
   - 唯一的 destination 数量