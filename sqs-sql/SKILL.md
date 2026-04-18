---
name: sqs-sql skill
description: 生成和审查服务质量生产数存发版 SQL / ES mapping 文档。适用于新建表和任意表结构变更，包括新增字段、修改字段、删除字段、CREATE TABLE、MySQL 分表 DDL、ADB/SR 字段同步、ES mapping 更新、执行顺序、Markdown 代码块围栏、字段长度和 SQL 校验。
---

# 服务质量发版 SQL

## 适用范围

用于生成或审查服务质量相关生产数存的发版信息，适用于新建业务表和任意业务表的表结构变更，包括新增字段、修改字段、删除字段、同步 ADB/SR、更新 ES mapping 等场景。

常见目标文档是需求目录下的 `概要设计.md` 的 `发版信息` 小节。技能目录内已内置参考文件，优先读取：

- `references/sql_template.md`：发版 SQL 模板。
- `references/服务质量数存.xlsx`：生产 MySQL/ADB/SR/ES 表、索引、模板清单。

生成 SQL 前需要先读取生产数存 Excel，确认 MySQL/ADB/SR/ES 中实际存在且有效的目标表或索引。

只处理发版 SQL / ES mapping 相关内容。除非用户明确要求，不要修改 XML、导出、Controller、Service、单元测试等代码。

## 发版元信息

发版信息中需要按实际变更保留并明确写出这些内容：

- 先写 `背景说明` 和 `解决问题`。如果用户没有提供完整背景，可以基于表名、字段名和变更类型补出一版合理、简短且自洽的说明，至少各 1 条。
- `数据库: MySQL`
- `是否需要备份: 是/否`，删除字段、修改字段、非 nullable 变更或有数据风险时优先标记需要备份。
- `是否同步ES: 是/否`
- `是否同步ADB: 是/否`
- `是否影响下游: 是/否`，涉及 ES、ADB、SR
- `是否有默认值: 是/否`。这里只写 `是` 或 `否`，不要把默认值说明拼在这一行里；如果确实需要说明默认值或存量数据处理方式，单独在正文补充。
- `是否有索引: 是/否`
- `回刷数据: 有/无`
- `涉及数据量: 有/无`。能从生产数存 Excel 取到行数时，要写成以 `W` 为最小单位的值，例如 `10W`、`1948W`、`1000W`，不要直接写原始行数。
- `执行顺序: 先执行 ES mapping / ADB / SR 字段，再执行 MySQL 分表 DDL`
- `期望执行时间: 晚上21点之后执行`

## 区块顺序

已有表结构变更按以下顺序生成：

1. `ES`
2. `ADB`
3. `SR`
4. `MYSQL`

这个顺序是通用约束：先准备 ES mapping / ADB / SR 字段，再执行 MySQL DDL。顺序到 `MYSQL` 结束，不要把 Apollo、XXL-JOB 等非 SQL 区块纳入本技能的固定顺序。

新建表只需要 `ES -> MYSQL`，不生成 ADB/SR 区块。

## 生产数存清单判定

读取生产数存 Excel 时按以下规则判断有效目标：

- MySQL：如果存在连续分表，例如 `xxx_0 ~ xxx_{N-1}`，则认为同名原始表 `xxx` 已废弃，表结构变更只处理分表。N 以生产数存实际表清单为准，常见可能是 12、16、32、128 等。
- MySQL：如果不存在分表，才对实际存在的原始表生成 DDL。
- ES：如果某个集群中索引或模板状态是 `已迁移`、`已停用`、`已废弃` 等非使用中状态，直接忽略。
- ES：优先选择状态为 `使用中` 的模板/索引作为发版目标。
- ADB/SR：按实际存在的有效主表生成 DDL。
- 表名、索引名和数据量以生产数存 Excel 为准，不要凭记忆猜测。

## ES Mapping 格式

优先参考 `references/sqlcreate.md` 中维护的 ES 信息，包括 mapping 示例、字段命名、字段类型和目标索引格式。生产数存 Excel 用于判断哪个 ES 集群、模板或索引是有效的 `使用中` 目标。

已有表结构变更时，ES mapping 使用请求式格式，不要只给裸 `properties` 对象：

```json
PUT /目标索引或模板/_mapping/_doc
{
    "properties": {
        "fieldName": {
            "type": "keyword"
        },
        "timeField": {
            "type": "date",
            "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis"
        }
    }
}
```

所有 ES 时间字段统一使用：

```json
"format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis"
```

ES 字段类型按业务和现有 mapping 对齐。常见映射：

- 新增字符串字段默认优先给 `keyword`，包括编码类字段和名称类字段；除非 `references/sqlcreate.md` 或现有 mapping 明确要求使用 `text` 或 `text + keyword` 多字段。
- 数值字段用 `integer`、`long` 或对应数值类型。
- 金额字段按现有索引习惯选择。

如果 `references/sqlcreate.md` 中已经给出同类字段的 ES 类型，以模板中的类型为优先参考；如果和推断类型冲突，先按模板和现有 mapping 判断，不要直接凭字段名猜类型。

### 新建单表的 ES

如果是新建单表，优先输出完整索引创建内容，而不是只给 `_mapping`。格式参考：

```json
PUT /目标索引
{
    "settings": {
        "index": {
            "search": {
                "slowlog": {
                    "level": "info",
                    "threshold": {
                        "fetch": {
                            "warn": "1s",
                            "trace": "200ms",
                            "debug": "500ms",
                            "info": "800ms"
                        },
                        "query": {
                            "warn": "10s",
                            "trace": "500ms",
                            "debug": "2s",
                            "info": "5s"
                        }
                    }
                }
            },
            "refresh_interval": "1s",
            "number_of_shards": "1",
            "number_of_replicas": "1"
        }
    },
    "mappings": {
        "_doc": {
            "properties": {
                "fieldName": {
                    "type": "keyword"
                }
            }
        }
    }
}
```

如果 `references/sqlcreate.md` 中存在更贴近目标场景的单表 ES 索引示例，优先与示例保持一致。

### 新建分表的 ES

如果是新建分表，优先输出完整模板内容，而不是只给 `_mapping`。格式参考：

```json
PUT /_template/目标模板名
{
    "order": 0,
    "index_patterns": [
        "目标索引前缀-*"
    ],
    "settings": {
        "index": {
            "lifecycle": {
                "name": "390_days_policy"
            },
            "search": {
                "slowlog": {
                    "level": "info",
                    "threshold": {
                        "fetch": {
                            "warn": "1s",
                            "trace": "200ms",
                            "debug": "500ms",
                            "info": "800ms"
                        },
                        "query": {
                            "warn": "10s",
                            "trace": "500ms",
                            "debug": "2s",
                            "info": "5s"
                        }
                    }
                }
            },
            "refresh_interval": "1s",
            "number_of_shards": "5",
            "number_of_replicas": "1"
        }
    },
    "mappings": {
        "目标mapping名": {
            "properties": {
                "fieldName": {
                    "type": "keyword"
                }
            }
        }
    }
}
```

模板名、`index_patterns`、`mappings` 下的类型名要优先参考 `references/sqlcreate.md` 里的同类模板命名方式，不要随意自造风格不一致的名字。

## DDL 生成规则

如果是新建表，使用 `CREATE TABLE`，并优先参考 `references/sqlcreate.md` 中的已有表结构样例确定字段类型、长度、默认值、注释风格和基础字段。新建表前必须结合生产数存 Excel 判断同名表是否已存在，避免重复建表。

新建表只输出 ES 和 MySQL。MySQL 如果需要分表，按 `references/sqlcreate.md` 中的分表模板和需求指定的分表数量生成；MySQL 如果不分表，参考 `references/sqlcreate.md` 中的非分表表结构样例。ES 参考 `references/sqlcreate.md` 中的非模板/实际 mapping 示例生成。

每个目标表只生成一条 `ALTER TABLE`。同一张表上的多个变更合并到同一条语句中：

- 新增字段使用 `ADD COLUMN`。
- 修改字段使用 `MODIFY COLUMN` 或项目约定的变更语法。
- 删除字段使用 `DROP COLUMN`，并在元信息中明确备份和影响范围。
- 同一张表同时新增、修改、删除字段时，也合并到同一条 `ALTER TABLE`，按风险从低到高或用户指定顺序排列。

示例：

```SQL
ALTER TABLE example_table
ADD COLUMN `field_a` VARCHAR(24) DEFAULT NULL COMMENT '说明',
MODIFY COLUMN `field_b` INT(10) DEFAULT NULL COMMENT '说明',
DROP COLUMN `field_c`;
```

不要把同一张表拆成多条 `ALTER TABLE`，除非数据库限制或用户明确要求。

如果是已有分表的混合变更，同一张分表上的 `ADD COLUMN`、`MODIFY COLUMN`、`DROP COLUMN` 也必须合并到同一条 `ALTER TABLE` 中，不能拆开。

## 字段长度规则

生成字段时，先对照生产表里已有同类字段，不要随意放大长度。

优先参考 `references/sqlcreate.md` 中维护的表结构样例。该文件中如果存在多个可参考表结构，需要一起对照；如果同一个字段或同类字段在不同表中的长度不一致，推荐使用其中长度最大的定义，避免新字段长度不足。

MySQL 和 ADB 使用以下通用基准：

- 轮次/状态/小范围枚举字段：优先使用 `TINYINT(4)`。
- 网点/代理区/组织 id 字段：通常使用 `INT(10)`。
- 用户 id 或业务主键 id：按现有同类字段选择 `BIGINT(20)` 或 `INT(10)`。
- 网点/代理区/组织编码字段：通常使用 `VARCHAR(24)`。
- 网点/代理区/组织名称字段：通常使用 `VARCHAR(30)`。
- 较长业务名称、客户名称、品牌名称等：必须对照生产表同类字段，不要默认放大。
- 时间字段：统一使用 `DATETIME`。不要再使用 `TIMESTAMP`，即使旧表结构中仍存在 `TIMESTAMP` 字段。
- 发版 SQL 中不要显式设置 `CHARACTER SET utf8mb4` 或 `COLLATE utf8mb4_general_ci`，使用表默认字符集和排序规则。

SR 只对 String/VARCHAR 字段做字节长度转换：

- MySQL/ADB `VARCHAR(24)` -> SR `VARCHAR(96)`。
- MySQL/ADB `VARCHAR(30)` -> SR `VARCHAR(120)`。
- 其他 String/VARCHAR 长度同理乘以 4。
- 数值和时间字段不乘 4，除非 SR 有额外明确类型要求。

## MySQL 分表 DDL

如果生产数存表清单中存在连续分表，例如：

```text
example_table_0 ~ example_table_{N-1}
```

则每张分表生成一条 `ALTER TABLE`，每条语句内部合并所有字段变更。分表数量不固定，可能是 12、16、32、128 或其他数量，必须以生产数存 Excel 中实际连续存在的分表为准。

示例：

```SQL
-- example_table_0
ALTER TABLE example_table_0
ADD COLUMN `field_a` VARCHAR(24) DEFAULT NULL COMMENT '说明',
MODIFY COLUMN `field_b` INT(10) DEFAULT NULL COMMENT '说明';

-- example_table_1
ALTER TABLE example_table_1
ADD COLUMN `field_a` VARCHAR(24) DEFAULT NULL COMMENT '说明',
MODIFY COLUMN `field_b` INT(10) DEFAULT NULL COMMENT '说明';
```

如果用户要求生成最终 SQL，不要使用 `{n}` 占位符，必须显式展开所有有效分表。

如果生产数存表清单中同时存在 `example_table` 和连续分表 `example_table_0 ~ example_table_{N-1}`，说明同名原始表已废弃。之后修改表结构时直接省略原始表，只生成实际存在的分表 DDL。

新建分表时，分表数量必须来自需求或既有同类表设计；不能默认使用 32 张。生成最终 SQL 时显式展开所有分表的 `CREATE TABLE`。

新建分表时，最终输出必须为每张分表各自完整的 `CREATE TABLE` 语句，不要使用 `CREATE TABLE xxx LIKE yyy`、占位符、循环伪代码或“其余分表同上”这类缩写。

## Markdown 代码块

使用完整的三反引号代码块：

- SQL 块：```` ```SQL ````
- JSON 块：```` ```json ````
- Properties 块：```` ```properties ````

不要留下单反引号或双反引号围栏，例如 `` `SQL ``、`` `json ``、`` ``SQL ``。

## 校验清单

编辑完成后校验发版信息：

- 生产数存 Excel 中的有效 MySQL/ADB/SR/ES 目标已确认。
- 新建表时，已确认生产数存 Excel 中不存在同名有效表或索引。
- 新建表时，只输出 `ES -> MYSQL`，没有输出 ADB/SR。
- 新建单表的 ES 使用完整索引创建内容，包含 `settings` 和 `mappings._doc.properties`。
- 新建分表的 ES 使用完整模板内容，包含 `order`、`index_patterns`、`settings`、`mappings`。
- 新建 MySQL 分表时，已参考 `references/sqlcreate.md` 的分表模板和需求指定的分表数量。
- 新建 MySQL 非分表时，已参考 `references/sqlcreate.md` 的非分表表结构样例。
- 新建表的 ES 已参考 `references/sqlcreate.md` 中的非模板/实际 mapping 示例。
- MySQL 如果已有分表，则没有为同名原始表生成 DDL。
- ES 忽略 `已迁移`、`已停用`、`已废弃` 等非使用中模板/索引，只使用 `使用中` 目标。
- ES mapping 使用 `PUT /目标索引或模板/_mapping/_doc`。
- ES 字段包在 `"properties"` 下。
- ES 字段命名、字段类型和目标索引已参考 `references/sqlcreate.md` 中的 ES 信息。
- 新增字符串字段默认优先使用 `keyword`，除非模板或现有 mapping 明确要求其他类型。
- ES 时间字段使用 `yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis`。
- 区块顺序是 `ES -> ADB -> SR -> MYSQL`，到 `MYSQL` 结束。
- `背景说明` 和 `解决问题` 已填写。
- `是否有默认值` 仅填写 `是/否`。
- `涉及数据量` 如可从 Excel 获取，已转成 `W` 口径。
- MySQL 和 ADB 字段长度对齐生产表同类字段。
- 如果参考表中同一字段或同类字段长度不一致，已选择最大长度。
- 时间字段使用 `DATETIME`，没有使用 `TIMESTAMP`。
- SR 的 String/VARCHAR 字段长度是 MySQL 长度乘以 4。
- SR 标题或说明文字保持实际使用口径，例如 `中国区离线-pro-doris.fine_bi`。
- 发版 SQL 中没有 `CHARACTER SET` / `COLLATE`。
- 每张表只有一条 `ALTER TABLE`，同表所有 `ADD COLUMN` / `MODIFY COLUMN` / `DROP COLUMN` 合并在同一条语句中。
- 新建表使用 `CREATE TABLE`，字段类型、长度、默认值和注释风格已参考 `references/sqlcreate.md`。
- 新建分表已显式展开所有分表的完整 `CREATE TABLE`，没有使用 `LIKE`、占位或“同上”省略。
- Markdown 代码块都是三反引号。
- SQL 单引号成对，语句以分号结束。
