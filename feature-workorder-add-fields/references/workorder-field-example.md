# 工单新增字段动态样例

该参考文件提炼自 `工单新增字段改动点.md`，并结合当前 workspace 的真实文件分布整理。这里的 3 个字段只是样例，用来说明“新增字段通常会落到哪些层”，执行时必须替换为用户当前需求里的动态字段列表。

## 1. 如何使用本样例

- 把 `buzCustomerCode`、`buzCustomerName`、`buzProjectName` 当作占位模板，不要当作固定目标。
- 先用用户这次的字段列表做精确搜索和实现。
- 只有在需要判断改动面、SQL 写法、回刷方式时，才拿本样例做对照。

## 2. 样例字段

| 字段中文名 | Java 字段 | DB 字段 | 类型 | 来源 |
| --- | --- | --- | --- | --- |
| 客户编码 | `buzCustomerCode` | `buz_customer_code` | `varchar(20)` | 运单基础查询接口 |
| 客户名称 | `buzCustomerName` | `buz_customer_name` | `varchar(60)` | 运单基础查询接口 |
| 项目名称 | `buzProjectName` | `buz_project_name` | `varchar(30)` | 客户资料查询接口 |

赋值节点：工单创建时。

## 3. 当前 workspace 内的关键落点

### 3.1 `yl-jms-css-workorder-api`

- `src/main/java/com/yl/css/workorder/api/entity/WorkOrder.java`
- `src/main/java/com/yl/css/workorder/api/vo/WorkOrderPageVO.java`
- `src/main/java/com/yl/css/workorder/api/vo/WorkOrderExcelVO.java`
- `src/main/java/com/yl/css/workorder/api/dto/WorkOrderPageDTO.java`
- `src/main/java/com/yl/css/workorder/api/dto/WorkOrderSendOutPageDTO.java`
- `src/main/java/com/yl/css/workorder/api/service/impl/WorkOrderServiceImpl.java`
- `src/main/resources/mapper/WorkOrderMapper.xml`
- `src/main/java/com/yl/css/workorder/api/task/WorkOrderRefreshBuzCustomerFieldTask.java`

说明：
- `WorkOrderMapper.xml` 的 `Base_Column_List` 和 `Export_Column_List` 已包含上述字段，适合作为新增字段时补列的对照样例。
- `WorkOrderServiceImpl.java` 已存在按 `buz_customer_code` 过滤 ES 查询的逻辑，适合作为列表筛选样例。
- `WorkOrderRefreshBuzCustomerFieldTask.java` 体现了回刷任务的推荐结构：时间窗口、scroll 查询、批量更新、失败兜底、日志统计。

### 3.2 `yl-web-sqs-workorder`

- `src/main/java/com/yl/jms/sqsworkorder/model/vo/WorkOrderPageVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/vo/WorkOrderExcelVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderPageDTO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderSendOutPageDTO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebAddColumnVO.java`

### 3.3 `yl-jms-wd-sqs-workorder-web`

- `src/main/java/com/yl/jms/sqsworkorder/model/vo/WorkOrderPageVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/vo/WorkOrderExcelVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderPageDTO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderSendOutPageDTO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebAddColumnVO.java`

### 3.4 报表模块

参考 md 中提到 `yl-jms-css-report`、`yl-jms-wd-sqs-report-api` 也要补导出 VO 和异步导出查询条件。

当前 workspace 未包含这两个模块。使用该 skill 时，如需求涉及报表改造，必须明确说明“文档提到但当前 workspace 缺失”，不要直接编造文件路径。

## 4. ES 与 DDL 样例

### 4.1 ES mapping

```json
PUT /pro_css_work_order/_mapping/_doc
{
  "properties": {
    "buz_customer_code": {
      "type": "keyword"
    },
    "buz_customer_name": {
      "type": "keyword"
    },
    "buz_project_name": {
      "type": "keyword"
    }
  }
}
```

### 4.2 主表 DDL 样例

```sql
alter table yl_css_workorder_workorder
    add column buz_customer_code varchar(20)  null comment '客户编码',
    add column buz_customer_name varchar(60) null comment '客户名称',
    add column buz_project_name  varchar(30) null comment '项目名称';
```

### 4.3 需要联动核对的数据链路

- ADB：`pro_adb_css.yl_database`
- BI 同步表：`pro-doris.fine_bi.work_order`
- 备用链路：`jms-css-datacenter.yl_standby.sqs_standby_work_order`
- MySQL 主库分表：`pro-sqs-workorderhub-mysql.yl_sqs_workorder.work_order_0` 到 `work_order_31`

使用该 skill 时，不要机械复制以上实例名。应先确认目标环境，再输出实际需要执行的 DDL 清单。

## 5. 回刷任务样例

`WorkOrderRefreshBuzCustomerFieldTask.java` 的关键模式：

- 默认回刷最近 `lookbackDays` 天。
- 支持 `fillFlag`，仅回刷字段为空的记录。
- 先通过 ES scroll 拉取工单，再组装轻量更新对象批量回写。
- 批量失败时降级为逐条更新，避免整批丢失。
- 记录 `total/success/fail/skip/noChange` 指标，便于上线后追踪。

适用场景：
- 字段在创建逻辑增加后，历史工单存在空值。
- 字段来源依赖外部接口，可容忍按时间窗口渐进补齐。

## 6. 必报外部依赖

- 运单基础查询接口：提供客户编码、客户名称。
- 客户资料查询接口：通过客户编码补项目名称。
- BI 模型同步：`work_order` 表新增字段后需同步。
- ES 模板或索引：新增 mapping 后需验证查询与导出链路。

## 7. 推荐搜索语句

```powershell
rg -n --glob '!**/target/**' "<Java字段名1>|<Java字段名2>|<Java字段名3>" .
rg -n --glob '!**/target/**' "<DB字段名1>|<DB字段名2>|<DB字段名3>" .
rg -n --glob '!**/target/**' "WorkOrderRefreshBuzCustomerFieldTask|fillBuzCustomerMsg" .
rg -n --glob '!**/target/**' "WorkOrderPageVO|WorkOrderExcelVO|WorkOrderExcelWebVO|WorkOrderPageDTO|WorkOrderSendOutPageDTO" .
```
