# 工单导出开发样例

该参考文件从 `add-workorder-fields` skill 中抽出导出相关触点，专门用于说明“新增或调整导出字段通常会落到哪些层”。这里的字段和模块都只是样例，执行时必须替换为用户当前需求里的真实字段与仓库结构。

## 1. 如何使用本样例

- 把已有字段当作导出链路模板，不要当作固定目标。
- 先用用户本次字段名精确搜索，只有在需要判断落点或 SQL 写法时，才拿本样例对照。
- 如果需求涉及 DDL、ES、回刷，这份参考只负责提醒你继续扩展，不替代那些专项改造。

## 2. 当前 workspace 的关键导出落点

### 2.1 `yl-jms-css-workorder-api`

- `src/main/java/com/yl/css/workorder/api/vo/WorkOrderExcelVO.java`
- `src/main/resources/mapper/WorkOrderMapper.xml`
- `src/main/java/com/yl/css/workorder/api/service/impl/WorkOrderServiceImpl.java`
- `src/main/java/com/yl/css/workorder/api/dto/WorkOrderPageDTO.java`
- `src/main/java/com/yl/css/workorder/api/dto/WorkOrderSendOutPageDTO.java`

说明：

- `WorkOrderExcelVO.java` 适合作为导出字段、导出注解、格式化方式的对照样例。
- `WorkOrderMapper.xml` 适合作为 `Export_Column_List`、导出 SQL、筛选条件和字段别名映射的对照样例。
- `WorkOrderServiceImpl.java` 适合作为导出查询、对象转换、字典翻译、枚举文案和时间格式化的对照样例。

### 2.2 `yl-web-sqs-workorder`

- `src/main/java/com/yl/jms/sqsworkorder/model/vo/WorkOrderExcelVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebAddColumnVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderPageDTO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderSendOutPageDTO.java`

### 2.3 `yl-jms-wd-sqs-workorder-web`

- `src/main/java/com/yl/jms/sqsworkorder/model/vo/WorkOrderExcelVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/vo/WorkOrderExcelWebAddColumnVO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderPageDTO.java`
- `src/main/java/com/yl/jms/sqsworkorder/model/dto/WorkOrderSendOutPageDTO.java`

## 3. 报表与异步导出提醒

- 历史样例提到 `yl-jms-css-report`、`yl-jms-wd-sqs-report-api` 也可能需要补导出 VO 和异步导出查询条件。
- 当前 workspace 未包含这两个模块。使用该 skill 时，如需求涉及报表或异步导出改造，必须明确报告缺失，不要直接编造文件路径。

## 4. 推荐搜索语句

```powershell
rg -n --glob '!**/target/**' "<Java字段名1>|<Java字段名2>|<中文名片段>" .
rg -n --glob '!**/target/**' "WorkOrderExcelVO|WorkOrderExcelWebVO|WorkOrderExcelWebAddColumnVO" .
rg -n --glob '!**/target/**' "Export_Column_List|select.*Export|export.*List|async.*export" .
rg -n --glob '!**/target/**' "WorkOrderMapper.xml|WorkOrderServiceImpl|WorkOrderPageDTO|WorkOrderSendOutPageDTO" .
```

## 5. 交付时至少说明这些问题

- 导出列头、字段值、格式化规则是否与需求一致。
- 列表筛选是否同步到了导出链路。
- 是否同时覆盖同步导出、异步导出、报表导出。
- 是否依赖外部接口、字典或模板联动。
