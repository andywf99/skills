---
name: implement-workorder-export
description: 用于工单场景下新增、调整或排查导出字段与导出链路，联动梳理导出 VO、Web VO、Mapper/XML 导出列、导出 SQL、Service 转换、异步导出查询条件与外部依赖。只要需求中包含导出能力，就应使用此 skill；适用于用户提到“工单导出开发”“新增导出字段”“导出 Excel 加字段”“列表字段同步导出”“异步导出字段补齐”“导出链路排查”，以及在工单新增字段、列表改造、报表改造中同时要求支持导出的场景。
---

# 工单导出开发

按以下流程执行。只要当前需求包含导出能力，就联动使用本 skill；不要把 DDL、ES、回刷默认带入，只有需求明确涉及这些链路时再扩展。

## 0. 先把导出字段当成动态输入

- 把用户本次提供的字段清单视为唯一目标，不要默认只处理某几个固定字段。
- 把仓库里已有导出字段当作模板，不要把样例字段名、中文列头、别名原样复制到新需求。
- 如果用户只给了中文名，先补齐 Java 字段名、DB 字段名、导出列头、类型、来源接口、格式化规则，再开始实现。
- 需要对照当前 workspace 的导出样例时，再读取 `references/workorder-export-example.md`。

## 1. 先建立导出字段矩阵

- 先整理字段矩阵：字段中文名、Java 字段、DB 字段或 SQL 别名、导出列头、类型、来源接口、赋值节点、格式化方式、是否同步到异步导出或报表导出。
- 如果用户没有给完整清单，先在仓库内搜索同类导出字段样例，再补齐触点，不要直接猜。
- 如果需求只说“列表也要导出”，至少同时核对列表 VO、导出 VO、导出 SQL、导出转换逻辑。
- 如果需求提到异步导出、报表导出或备用导出链路，继续检查对应报表模块；当前 workspace 不包含目标模块时，必须明确报告缺失。

## 2. 先搜索既有导出样例再落点

- 优先搜索已有导出字段或相似字段，确认真实落点后再改。
- 先用本次字段名做精确搜索，再用导出模型和 SQL 标识做结构搜索。
- 优先使用以下搜索模式：

```powershell
rg -n --glob '!**/target/**' "<Java字段名>|<DB字段名>|<中文名片段>" .
rg -n --glob '!**/target/**' "class WorkOrderExcelVO|class WorkOrderExcelWebVO|class WorkOrderExcelWebAddColumnVO" .
rg -n --glob '!**/target/**' "Export_Column_List|select.*Export|export.*List|async.*export" .
rg -n --glob '!**/target/**' "WorkOrderMapper.xml|WorkOrderServiceImpl|PageDTO|SendOutPageDTO" .
```

- 如果仓库里已经存在一组同类型导出字段，优先复用这组字段的 VO、注解、SQL 别名、转换逻辑和格式化写法。
- 需要具体样例时，再读取 `references/workorder-export-example.md`。

## 3. 按导出链路逐层核对并实现

### 3.1 后端主模块

- 以 `yl-jms-css-workorder-api` 或等价模块为主入口，至少核对以下触点：
- `vo/WorkOrderExcelVO.java` 或等价导出 VO：补字段、导出注解、格式化约束。
- `dto/WorkOrderPageDTO.java`、`dto/WorkOrderSendOutPageDTO.java`：仅在导出链路确实支持筛选时补查询字段。
- `mapper/WorkOrderMapper.xml` 与相关 Mapper：补 `Export_Column_List`、导出 `resultMap`、导出 SQL、筛选条件、排序字段和 SQL 别名映射。
- `service/impl/WorkOrderServiceImpl.java`：补导出查询、对象转换、字典翻译、枚举文案、时间格式化和批量补充逻辑。
- 如果导出值来自创建时未落库的数据，先确认导出链路是实时补值还是读库字段，不要只在 VO 上补字段。

### 3.2 Web 与对外模型

- 在 `yl-web-sqs-workorder` 和 `yl-jms-wd-sqs-workorder-web` 中补齐对外导出模型：
- `model/vo/WorkOrderExcelVO.java`
- `vo/WorkOrderExcelWebVO.java`
- `vo/WorkOrderExcelWebAddColumnVO.java`
- `model/dto/WorkOrderPageDTO.java`
- `model/dto/WorkOrderSendOutPageDTO.java`
- 如果前端导出依赖单独的 web VO 或附加列模型，不要只改 api 模块。

### 3.3 异步导出与报表链路

- 如果需求提到报表、异步导出、批量导出任务，继续核对报表模块中的导出 VO、查询 DTO 和任务入参。
- 当前 workspace 的历史样例提到 `yl-jms-css-report`、`yl-jms-wd-sqs-report-api` 也可能需要联动；如果当前仓库缺失这些模块，要明确说明“文档提到但当前 workspace 不包含”，不要编造路径。
- 如果同步导出和异步导出共用 SQL，优先抽公共列清单和公共转换逻辑，避免两处字段不一致。

### 3.4 外部依赖与风险

- 必须报告导出字段依赖的外部接口、字典、缓存、翻译函数、报表任务参数和配置中心项。
- 如果字段值来自客户、项目、组织、运单等外部服务，明确“来源接口 + 调用节点 + 导出兜底”。
- 如果导出列新增会影响前端模板、下载模板、列宽顺序、国际化文案或下游 BI 文件，必须一并提示。
- 不要只写“补导出字段”，必须指出改动发生在哪个导出模型、哪段 SQL、哪段转换逻辑。

## 4. 验证时覆盖导出端到端链路

- 至少核对以下内容：
- 导出列头、列顺序、字段值是否与需求一致。
- 列表筛选条件是否正确传入导出链路。
- SQL 查询字段、VO 字段、Excel 注解名称是否一致。
- 枚举翻译、字典转换、时间格式化、空值兜底是否符合既有规则。
- 同步导出、异步导出、报表导出是否存在字段不一致。
- 如果只完成部分链路，要明确列出未验证项。

## 5. 输出时提供结构化交付

- 输出改动结果时，按以下结构汇报：
- 字段矩阵：字段名、导出列头、来源、格式化规则、覆盖链路。
- 代码改动：按模块列出导出 VO、Web VO、DTO、Mapper/XML、Service、任务。
- 导出链路：同步导出、异步导出、报表导出是否覆盖。
- 依赖与风险：缺失模块、未验证项、外部接口、模板联动点。

## 6. 缺信息时按这个顺序补上下文

- 先读用户给的字段清单、接口说明、导出样例或 PRD。
- 再搜当前仓库的真实导出文件和字段样例。
- 再读取 `references/workorder-export-example.md` 对照导出链路。
- 仍然缺失时，再向用户指出缺的模块、导出入口或外部接口信息。

## 参考资料

- 导出模型、导出 SQL 与报表缺失模块样例：`references/workorder-export-example.md`
