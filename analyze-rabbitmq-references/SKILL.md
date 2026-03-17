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

**⚠️ 重要警告：禁止并行读取多个 YAML 文件**

并行调用 Read 工具读取多个文件会导致**文件路径与内容不匹配**的问题（即读取文件A却返回文件B的内容）。

**正确的做法：**
1. **方案一（推荐）：使用 Bash 命令批量提取**
   ```bash
   # 进入 streams 目录，逐个文件提取 binding 和 destination
   for f in *.yml; do
     echo "=== $f ==="
     awk '/^        [a-zA-Z0-9_-]+-(input|output):/{binding=$1} /destination:/{if(binding) print binding, $0}' "$f"
   done
   ```
   这样可以确保文件名（即项目名）与提取的内容正确对应。

2. **方案二：逐个读取文件**
   如果必须使用 Read 工具，请**逐个**读取每个 yml 文件，不要并行读取多个。

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
参数:
  - project: {项目名称}           # 必填，当前所属项目名称
  - exchanges: {destination-name} # 必填，交换机名称，多个用英文逗号分隔
```

**调用示例：**
```
mcp__sqs-mcp-server-api__ArcherySQL-QueryRabbitExchangeReference(
  project: "yl-jms-css-api",
  exchanges: "limit-employee-log"
)
```

**返回结果格式：**
```json
[
  {
    "project": "yl-jms-css-api",
    "exchange": "limit-employee-log",
    "referenceProjects": [
      "yl-web-servicequality",
      "yl-jms-ops-write-api",
      "yl-jms-sts-api",
      "yl-web-sqs-workorder",
      "yl-jms-wd-sqs-workorder-web",
      "yl-jms-wd-sqs-servicequality-web",
      "yl-jms-sqs-leave-message-api",
      "yl-jms-sqs-cswot-manage-web"
    ]
  }
]
```

**返回字段说明：**
| 字段 | 说明 |
|------|------|
| project | 查询的项目名称 |
| exchange | 交换机名称（destination） |
| referenceProjects | 引用该交换机的项目列表（数组） |

从返回结果中提取 `referenceProjects` 数组，用逗号拼接后填入 CSV 的 `reference project` 列。

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
limit-employee-log-output,生产者,limit-employee-log,yl-jms-css-api,"yl-web-servicequality,yl-jms-ops-write-api,yl-jms-sts-api,yl-web-sqs-workorder,yl-jms-wd-sqs-workorder-web,yl-jms-wd-sqs-servicequality-web,yl-jms-sqs-leave-message-api,yl-jms-sqs-cswot-manage-web"
approval-handle-result-output,生产者,approval-handle-result,yl-jms-css-approval-api,"project_1,project_2"
```

---

## 注意事项

1. **⚠️ 关键警告 - 文件读取问题：**
   - **禁止并行读取多个 YAML 文件**：并行调用 Read 工具会导致文件路径与内容不匹配
   - **推荐方案**：使用 Bash 命令批量提取，确保文件名与内容正确对应
   - **示例命令**：
     ```bash
     for f in *.yml; do
       echo "=== $f ==="
       awk '/^        [a-zA-Z0-9_-]+-(input|output):/{binding=$1} /destination:/{if(binding) print binding, $0}' "$f"
     done
     ```
   - 输出格式为 `=== 项目名.yml ===` 后跟 binding 和 destination，便于建立项目-destination 映射

2. **YAML 解析注意事项：**
   - 注意处理注释行（以 `#` 开头）
   - 注意处理多层级嵌套
   - 有些 binding 可能没有显式指定 `binder`，需要检查 `default-binder` 配置

3. **MCP 调用注意事项：**
   - 必须传入 `project` 参数（当前所属项目名称，即 yml 文件名去掉 .yml 后缀）
   - `exchanges` 参数可以传入多个 destination（用英文逗号分隔）
   - 返回结果为数组格式，需要遍历获取每个 exchange 的引用信息
   - 从返回结果的 `referenceProjects` 字段提取引用项目列表
   - 如果 `referenceProjects` 为空数组，reference project 列填写 "无"
   - **MCP 调用可以并行执行**，提高查询效率

4. **输出格式注意事项：**
   - CSV 文件使用 UTF-8 编码
   - 如果 reference project 有多个，用逗号分隔并用双引号包裹
   - 项目名称从 yml 文件名提取（去掉 .yml 后缀）

---

## 执行示例

用户执行 `/analyze-rabbitmq-references` 后，AI 应：

1. 读取 `projects.txt` 获取项目列表
2. **使用 Bash 命令批量提取所有 yml 文件的 binding 和 destination**（避免并行读取导致的内容混乱）
3. 建立项目名 → destination 的正确映射关系
4. 调用 MCP 工具查询每个 destination 的引用项目（可并行调用 MCP）
5. 生成 `rabbitmq-reference-report.csv` 文件
6. 输出分析摘要，包括：
   - 分析的项目数量
   - 发现的 input/output 数量
   - 生产者数量
   - 消费者数量

## 完整执行流程示例

```bash
# 1. 读取项目列表
cat ../projects.txt

# 2. 批量提取所有 yml 文件的 binding 信息（推荐方式）
for f in *.yml; do
  echo "=== $f ==="
  awk '/^        [a-zA-Z0-9_-]+-(input|output):/{binding=$1} /destination:/{if(binding) print binding, $0}' "$f"
done
```

根据输出建立映射：
- `yl-jms-css-approval-api.yml` → `approval-handle-result-output` → destination: `approval-handle-result`
- `yl-jms-sqs-security-api.yml` → `jpush-app-alias-output` → destination: `jpush-app-alias`

然后调用 MCP 查询引用项目，生成 CSV 报告。