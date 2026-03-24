---
name: add-workorder-fields
description: 用于普通工单或工单中心新增业务字段时，联动梳理并修改 Java 实体、DTO/VO、Mapper/XML、工单创建赋值逻辑、ES 映射、DDL、导出、回刷与外部依赖报告。适用于用户提到“工单新增字段”“普通工单加字段”“列表/导出/BI 同步新增字段”“按改动点生成实现清单/SQL/skill”或要求参照既有字段样例扩展同类改造的场景。
---

# 工单新增字段联动改造

按以下流程执行，不要跳步。

## 0. 先把字段当成动态输入

- 把用户本次提供的字段清单视为唯一目标，不要默认只处理某 3 个固定字段。
- 把仓库里已有字段样例当作模板，不要把样例字段名、库表名、实例名原样复制到新需求。
- 如果用户只给了中文名，先补齐 Java 字段名、DB 字段名、类型、来源接口、赋值节点，再开始实现。
- 需要对照已有写法时，再读取 `references/workorder-field-example.md`；其中的 `buzCustomerCode`、`buzCustomerName`、`buzProjectName` 只是样例，不是默认必改字段。

## 1. 先建立字段矩阵

- 先从用户提供的需求文档、DDL、接口定义或字段清单中整理字段矩阵：中文名、Java 字段、DB 字段、类型、来源接口、赋值节点、是否需要筛选、是否需要导出、是否需要回刷。
- 如果用户没有给完整清单，先在仓库内搜索同类字段样例，再补齐触点，不要直接猜。
- 如果字段是普通工单新增字段，默认先检查 `yl-jms-css-workorder-api`、`yl-web-sqs-workorder`、`yl-jms-wd-sqs-workorder-web` 三个模块。
- 如果需求提到报表、异步导出、BI 或备用链路，再继续检查报表模块、同步链路和备用库；如果当前 workspace 不包含对应模块，要明确报告缺失，不要虚构改动点。

## 2. 先搜索既有样例再落点

- 优先搜索已有字段或相似字段，确认真实落点后再改。
- 先用本次字段名做精确搜索，再用通用工单类名做结构搜索。
- 优先使用以下搜索模式：

```powershell
rg -n --glob '!**/target/**' "<Java字段名>|<DB字段名>|<中文名片段>" .
rg -n --glob '!**/target/**' "class WorkOrderPageVO|class WorkOrderExcelVO|class WorkOrderExcelWebVO|class WorkOrderPageDTO" .
rg -n --glob '!**/target/**' "WorkOrderMapper.xml|WorkOrderServiceImpl|fill.*WorkOrder|@XxlJob" .
```

- 如果仓库里已经存在一组同类型字段，优先复用这组字段的实体、DTO/VO、SQL、ES、回刷任务写法。
- 需要具体样例时，再读取 `references/workorder-field-example.md`。

## 3. 按改动链路逐层核对并实现

### 3.1 后端主模块

- 以 `yl-jms-css-workorder-api` 为主入口，至少核对以下触点：
- `entity/WorkOrder.java` 或等价实体：补字段、注释、序列化约束。
- `vo/WorkOrderPageVO.java`、`vo/WorkOrderExcelVO.java`：补列表和导出字段。
- `dto/WorkOrderPageDTO.java`、`dto/WorkOrderSendOutPageDTO.java`：仅在页面或导出确实支持筛选时补查询字段。
- 工单创建或填充逻辑：补赋值逻辑，优先复用已有 `fill...`、`build...`、`convert...` 方法，不要把外部接口调用散落到控制层。
- `mapper/WorkOrderMapper.xml` 与相关 Mapper：补 `Base_Column_List`、导出列、`resultMap`、分页 SQL、导出 SQL、筛选条件。
- `service/impl/WorkOrderServiceImpl.java`：补 ES 或 DB 查询过滤条件、列表转换、导出链路。

### 3.2 Web 与兔 win 模块

- 在 `yl-web-sqs-workorder` 和 `yl-jms-wd-sqs-workorder-web` 中补齐对外 DTO/VO：
- `model/vo/WorkOrderPageVO.java`
- `model/vo/WorkOrderExcelVO.java`
- `vo/WorkOrderExcelWebVO.java`
- `model/dto/WorkOrderPageDTO.java`
- 如果存在附加导出模型，例如 `WorkOrderExcelWebAddColumnVO.java`，一并核对。

### 3.3 ES、DDL 与同步链路

- 字段落 ES 时，补模板或 mapping，并确认查询字段名使用下划线风格的 ES 字段。
- 字段落 DB 时，至少覆盖主表；如果系统存在主库分表、ADB、备用库、BI 同步表或其他同步链路，逐一列出 DDL。
- 不要只写“数据库新增字段”，必须指出具体库表或明确说明当前仓库无法确认。

### 3.4 回刷与补数

- 如果字段在创建前的历史数据为空，需要评估是否补回刷任务、定时任务或一次性脚本。
- 优先复用已有回刷任务模式：限定时间窗口、分页或 scroll、单批失败不阻塞整体、记录失败明细、支持补刷。
- 如果仓库已有相近回刷任务，沿用其参数设计、日志格式和兜底更新策略。

## 4. 强制检查外部依赖与风险

- 必须报告字段依赖的外部接口、字典、缓存、BI 模型、ES 模板、同步任务、灰度开关或配置中心项。
- 如果字段值来自运单、客户、项目、组织等外部服务，明确“来源接口 + 调用节点 + 失败兜底”。
- 如果展示或导出上线会影响线上行为，评估是否需要接入灰度开关；需要时继续使用 `enforce-gray-switch`。
- 明确说明历史数据为空、外部接口失败、ES mapping 未更新、BI 未同步等风险。

## 5. 验证时覆盖端到端链路

- 至少核对以下内容：
- 创建接口是否正确赋值。
- DB、ES、列表、导出字段是否一致。
- 查询筛选是否按需求生效。
- 回刷任务是否只处理目标范围、是否记录失败明细。
- BI 或同步链路是否已同步字段。
- 如果只完成部分链路，要明确列出未验证项。

## 6. 输出时提供结构化交付

- 输出改动结果时，按以下结构汇报：
- 字段矩阵：字段名、来源、赋值节点、展示/导出/筛选范围。
- 代码改动：按模块列出实体、DTO/VO、Mapper/XML、Service、任务。
- 数据链路：ES、主库、分表、ADB、备用库、BI。
- 回刷方案：范围、分页策略、失败补刷、校验方式。
- 风险与回滚：缺失模块、未验证项、外部依赖、灰度方案。

## 7. 缺信息时按这个顺序补上下文

- 先读用户给的 md、SQL、接口说明。
- 再搜当前仓库的真实文件和字段样例。
- 再读取 `references/workorder-field-example.md` 对照已有实现。
- 仍然缺失时，再向用户指出缺的模块、库表或外部接口信息。

## 参考资料

- 动态字段样例与 DDL、ES、回刷参考：`references/workorder-field-example.md`