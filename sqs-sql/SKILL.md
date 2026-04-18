---
name: sqs-sql skill
description: 生成和审查服务质量生产数存发版 SQL / ES mapping 文档。适用于新建表和表结构变更，包括 CREATE TABLE、ALTER TABLE、MySQL 分表 DDL、ADB/SR 字段同步、ES mapping 更新、执行顺序、字段长度和格式校验。
---

# 服务质量发版 SQL

## 适用范围

用于生成或审查服务质量相关的发版 SQL / ES mapping，目标通常是需求文档中的 `发版信息` 小节。

先读取：

- `references/sql_template.md`
- `references/服务质量数存.xlsx`

生成前必须先用 Excel 确认生产环境中实际有效的 MySQL / ADB / SR / ES 目标。只处理发版 SQL / ES mapping；除非用户明确要求，不修改业务代码。

## 输出要求

发版信息至少包含：

- `背景说明`
- `解决问题`
- `数据库: MySQL`
- `是否需要备份`
- `是否同步ES`
- `是否同步ADB`
- `是否影响下游`
- `是否有默认值`
- `是否有索引`
- `回刷数据`
- `涉及数据量`
- `执行顺序`
- `期望执行时间`

补充规则：

- 用户没提供完整背景时，可基于表名、字段名、变更类型补出简短且自洽的说明。
- `是否有默认值` 只写 `是/否`，不要把默认值细节写在同一行。
- `涉及数据量` 能从 Excel 取到时，统一写成 `W` 口径。
- 默认执行顺序：已有表变更写成 `ES -> ADB -> SR -> MYSQL`；新建表只写 `ES -> MYSQL`。
- 默认执行时间：`晚上21点之后执行`。

## 目标判定

- MySQL：如果存在连续分表 `xxx_0 ~ xxx_{N-1}`，则忽略同名原始表 `xxx`，只处理分表。
- MySQL：如果不存在分表，才处理原始表。
- ES：只使用状态为 `使用中` 的索引或模板；忽略 `已迁移`、`已停用`、`已废弃` 等目标。
- ADB / SR：只处理实际存在的有效主表。
- 表名、索引名、分表数量、数据量都以 Excel 为准，不要凭记忆猜测。

## ES 规则

- 优先参考 `references/sql_template.md` 中已有的 ES 示例、字段类型、模板命名和索引命名。
- 已有表结构变更使用请求式 mapping，不要只给裸 `properties`。
- 时间字段统一使用 `yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis`。
- 新增字符串字段默认优先 `keyword`；若模板或现有 mapping 已有明确约定，则以现有约定为准。
- 数值字段按现有 mapping 选择 `integer`、`long` 等类型。

已有表变更示例：

```json
PUT /目标索引或模板/_mapping/_doc
{
    "properties": {
        "fieldName": {
            "type": "keyword"
        }
    }
}
```

新建规则：

- 新建单表：输出完整索引创建内容，不要只给 `_mapping`。
- 新建分表：输出完整模板内容，不要只给 `_mapping`。

## DDL 规则

- 新建表使用 `CREATE TABLE`，字段类型、长度、默认值、注释风格优先参考 `references/sql_template.md`。
- 新建前先确认 Excel 中不存在同名有效表或索引，避免重复创建。
- 新建表只输出 `ES` 和 `MYSQL`，不生成 ADB / SR。
- 同一张表的所有变更合并到一条 `ALTER TABLE` 中，不要拆多条。
- 常见操作：`ADD COLUMN`、`MODIFY COLUMN`、`DROP COLUMN`。
- 删除字段、修改字段、非 nullable 变更或明显有数据风险时，优先标记需要备份。
- MySQL 如果存在唯一约束，则唯一约束名称必须以 `uniq_` 开头，例如：`UNIQUE KEY uniq_waybill_no (waybill_no)`。

示例：

```SQL
ALTER TABLE example_table
ADD COLUMN `field_a` VARCHAR(24) DEFAULT NULL COMMENT '说明',
MODIFY COLUMN `field_b` INT(10) DEFAULT NULL COMMENT '说明',
DROP COLUMN `field_c`;
```


## 字段长度

- 先对照生产表同类字段，不要随意放大长度。
- `references/sql_template.md` 中若存在多个相近样例，优先取更稳妥的长度；同类字段长度不一致时，默认取较大值。
- MySQL / ADB 常用基准：
  - 枚举或状态字段：`TINYINT(4)`
  - 组织类 id：`INT(10)`
  - 用户 id / 主键类 id：按现有表选择 `BIGINT(20)` 或 `INT(10)`
  - 编码类字段：`VARCHAR(24)`
  - 名称类字段：`VARCHAR(30)`
  - 时间字段：统一 `DATETIME`，不要新增 `TIMESTAMP`
- 发版 SQL 中不要显式写 `CHARACTER SET` 或 `COLLATE`。
- SR 的字符串字段长度按 MySQL / ADB 长度乘 4；数值和时间字段不乘 4。

## 分表规则

- 已有分表时，每张分表各生成一条 `ALTER TABLE`，每条语句内部合并全部字段变更。
- 生成最终 SQL 时不要使用 `{n}` 占位符，必须显式展开所有有效分表。
- 新建分表时，分表数量来自需求或既有设计，不能默认写死。
- 新建分表时，每张分表都要给完整 `CREATE TABLE`，不要用 `LIKE`、循环伪代码或“其余同上”。

## Markdown 格式

- SQL 使用 ```SQL
- JSON 使用 ```json
- Properties 使用 ```properties
- 必须使用完整三反引号代码块，不要出现单反引号或双反引号围栏。

## 最终校验

- 已确认有效的 MySQL / ADB / SR / ES 目标。
- 新建表时，已确认不存在同名有效表或索引。
- 区块顺序正确：已有表为 `ES -> ADB -> SR -> MYSQL`，新建表为 `ES -> MYSQL`。
- ES 类型、目标索引、模板命名已参考 `references/sql_template.md`。
- ES 时间字段格式正确，字符串字段未随意偏离现有 mapping。
- MySQL 若已有分表，没有再给原始表生成 DDL。
- 同一张表只有一条 `ALTER TABLE`。
- 新建表使用 `CREATE TABLE`，新建分表已完整展开。
- 字段长度与生产表和模板一致，SR 字符串长度已乘 4。
- 未引入 `TIMESTAMP`、`CHARACTER SET`、`COLLATE`。
- `背景说明`、`解决问题`、备份/同步/影响等元信息已补齐。
- Markdown 代码块、SQL 引号、分号格式正确。

## 使用提醒

- 生成结果只作为参考，不应直接无审核执行。
- 开发人员需要重点复核：
- SQL 字段长度、默认值、注释是否合理。
- ES 字段类型是否与现有索引 / 模板保持一致。
- ES 的分片数、副本数、生命周期配置是否满足当前场景。
- 分表数量、目标表名、索引名、模板名是否与生产实际一致。


