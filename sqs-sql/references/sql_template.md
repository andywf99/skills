## #1228507 【业务需求】【项目-智能仲裁】【仲裁】平台考核：桃花岛春节大促申诉数据 - pro-msdmcss-mysql.yl_css - 孟冬川

- 背景说明:
1. 桃花岛春节大促申诉数据
- 解决问题:
1. 桃花岛春节大促申诉数据回推PDD

数据库: MySQL

是否需要备份: 否

是否同步ES: 是

是否同步ADB: 是

是否影响下游: 否

是否有默认值: 否

是否有索引: 否

回刷数据: 无

涉及数据量: 无

执行顺序: 先执行 ES mapping / ADB / SR 字段 ，再执行 MySQL 分表 DDL

期望执行时间:晚上21点之后执行

1. ### ADB：pro_adb_css.yl_database

```SQL
ALTER TABLE yl_jms_css_arbitration
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
```

2. ### SR：中国区离线-pro-doris.fine_bi

```SQL
ALTER TABLE arbitration
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
```

3. ### MYSQL： pro-msdmcss-mysql.yl_css

```sql
-- mysql
ALTER TABLE arbitration_0
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_1
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_2
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_3
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_4
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_5
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_6
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_7
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_8
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_9
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_10
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_11
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_12
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_13
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_14
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_15
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_16
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_17
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_18
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_19
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_20
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_21
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_22
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_23
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_24
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_25
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_26
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_27
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_28
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_29
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_30
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
ALTER TABLE arbitration_31
ADD COLUMN `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
ADD COLUMN `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
ADD COLUMN `push_pdd_fail_msg` varchar(50) DEFAULT NULL COMMENT '推送PDD失败原因';
```

4. ### es

```sql
PUT /pro_sqs_arbitration/_mapping/_doc
{
    "properties": {
        "ticket_id": {
            "type": "long"
        },
        "push_pdd_status": {
            "type": "integer"
        },
        "push_pdd_fail_msg": {
            "type": "keyword"
        }
    }
}
```

## 常见生产表结构-mysql

```sql
CREATE TABLE `arbitration_0` (
  `id` bigint(20) NOT NULL COMMENT 'ID',
  `code` varchar(24)  NOT NULL COMMENT '申报单编号',
  `waybill_no` varchar(30)  NOT NULL COMMENT '运单号',
  `goods_type_id` bigint(20) DEFAULT NULL COMMENT '物品类型id',
  `goods_type_code` varchar(24)  DEFAULT NULL COMMENT '物品类型编号(冗余)',
  `goods_type_name` varchar(30)  DEFAULT NULL COMMENT '物品类型名称(冗余)',
  `goods_name` varchar(60)  NOT NULL COMMENT '物品名称',
  `goods_value` decimal(12, 2) NOT NULL COMMENT '物品价值',
  `first_type_id` bigint(20) NOT NULL COMMENT '一级异常类型id',
  `first_type_code` varchar(20)  NOT NULL DEFAULT '' COMMENT '一级异常类型code',
  `first_type` varchar(30)  NOT NULL COMMENT '一级异常类型名称(冗余)',
  `second_type_id` bigint(20) NOT NULL COMMENT '二级异常类型id',
  `second_type_code` varchar(20)  NOT NULL DEFAULT '' COMMENT '二级异常类型code',
  `second_type` varchar(30)  NOT NULL COMMENT '二级异常类型名称(冗余)',
  `exception_desc` varchar(500)  NOT NULL COMMENT '异常说明',
  `status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '仲裁状态: 1、责任方处理中 2、已撤销 3、待仲裁分配 4、仲裁受理中 5、仲裁核实中 6、仲裁退回 7、仲裁裁定完成 8、申诉受理中 9、申诉核实中 10、已结案 11、申诉待分配',
  `responsibility_reply_status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '责任方回复状态：1、未回复 2、已回复',
  `responsibility_confirm_status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '责任方认责状态：1、未认责 2、已认责',
  `arbitration_reply_status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '仲裁核实回复状态：1、未回复 2、已回复',
  `appeal_reply_status` tinyint(4) NOT NULL DEFAULT '1' COMMENT '申诉核实回复状态：1、未回复 2、已回复',
  `responsibility_reply_opinion` varchar(500)  DEFAULT '' COMMENT '责任方回复处理意见（冗余）',
  `process_type` tinyint(4) DEFAULT NULL COMMENT '仲裁单处理类型：1、分配 2、申领',
  `process_user_id` bigint(20) DEFAULT NULL COMMENT '仲裁单处理人id',
  `process_user_code` varchar(24)  DEFAULT NULL COMMENT '仲裁单处理人编号',
  `process_user_name` varchar(30)  DEFAULT NULL COMMENT '仲裁单处理人名称',
  `process_network_id` int(10) DEFAULT NULL COMMENT '仲裁单处理网点id',
  `process_network_code` varchar(24)  DEFAULT NULL COMMENT '仲裁单处理网点编号',
  `process_network_name` varchar(30)  DEFAULT NULL COMMENT '仲裁单处理网点名称',
  `arbitration_auto_receive_time` timestamp NULL DEFAULT NULL COMMENT '仲裁自动接收时间(定时任务执行时间)',
  `arbitration_receive_time` timestamp NULL DEFAULT NULL COMMENT '仲裁接收时间',
  `assign_time` timestamp NULL DEFAULT NULL COMMENT '仲裁分配时间',
  `arbitration_award_network_id` int(10) DEFAULT NULL COMMENT '仲裁裁定网点id',
  `arbitration_award_network_code` varchar(24)  DEFAULT NULL COMMENT '仲裁裁定网点编号',
  `arbitration_award_network_name` varchar(30)  DEFAULT NULL COMMENT '仲裁裁定网点名称',
  `arbitrator_id` bigint(20) DEFAULT NULL COMMENT '仲裁裁定人id',
  `arbitrator_code` varchar(24)  DEFAULT NULL COMMENT '仲裁裁定人编号',
  `arbitrator_name` varchar(30)  DEFAULT NULL COMMENT '仲裁裁定人名称',
  `arbitration_award_time` timestamp NULL DEFAULT NULL COMMENT '仲裁裁定时间',
  `edit_count` smallint(6) DEFAULT '0' COMMENT '编辑次数',
  `edit_time` timestamp NULL DEFAULT NULL COMMENT '仲裁编辑时间',
  `return_user_id` int(10) DEFAULT '0' COMMENT '仲裁退回处理人id（冗余）',
  `return_user_code` varchar(24)  DEFAULT '' COMMENT '仲裁退回处理人code',
  `return_user_name` varchar(30)  DEFAULT '' COMMENT '仲裁退回处理人name',
  `return_opinion` varchar(500)  DEFAULT '' COMMENT '仲裁退回处理意见',
  `return_time` timestamp NULL DEFAULT NULL COMMENT '仲裁退回时间',
  `appeal_decision_network_id` int(10) DEFAULT NULL COMMENT '申诉裁定网点id',
  `appeal_decision_network_code` varchar(24)  DEFAULT NULL COMMENT '申诉裁定网点编号',
  `appeal_decision_network_name` varchar(30)  DEFAULT NULL COMMENT '申诉裁定网点名称',
  `appeal_adjudicator_id` bigint(20) DEFAULT NULL COMMENT '申诉裁定人id',
  `appeal_adjudicator_code` varchar(24)  DEFAULT NULL COMMENT '申诉裁定人编号',
  `appeal_adjudicator_name` varchar(30)  DEFAULT NULL COMMENT '申诉裁定人名称',
  `is_appeal_fee` tinyint(4) NOT NULL DEFAULT '0' COMMENT '是否有申诉费用（1是，2否）',
  `appeal_time` timestamp NULL DEFAULT NULL COMMENT '申诉时间',
  `appeal_assign_time` timestamp NULL DEFAULT NULL COMMENT '申诉分配时间',
  `appeal_decision_time` timestamp NULL DEFAULT NULL COMMENT '申诉裁定时间',
  `arbitration_auto_close_time` timestamp NULL DEFAULT NULL COMMENT '自动结案时间(定时任务执行时间)',
  `closing_time` timestamp NULL DEFAULT NULL COMMENT '结案时间',
  `payable_amount_total` decimal(12, 2) DEFAULT NULL COMMENT '合计应付金额',
  `handling_fee_total` decimal(12, 2) DEFAULT NULL COMMENT '合计手续费',
  `award_amount_total` decimal(12, 2) DEFAULT NULL COMMENT '合计裁定金额',
  `create_by` bigint(20) NOT NULL COMMENT '申报人id',
  `create_by_code` varchar(24)  NOT NULL DEFAULT '' COMMENT '申报人code',
  `create_by_name` varchar(30)  NOT NULL COMMENT '申报人名称(冗余)',
  `create_network_id` int(10) NOT NULL COMMENT '申报网点id',
  `create_network_code` varchar(24)  NOT NULL COMMENT '申报网点编号(冗余)',
  `create_network_name` varchar(30)  NOT NULL COMMENT '申报网点名称(冗余)',
  `create_parent_id` int(10) DEFAULT NULL COMMENT '申报网点父级网点id',
  `create_parent_code` varchar(24)  DEFAULT NULL COMMENT '申报网点父级(冗余)',
  `create_parent_name` varchar(30)  DEFAULT NULL COMMENT '申报网点父级(冗余)',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '申报时间',
  `delay_day` smallint(6) NOT NULL DEFAULT '0' COMMENT '延误天数(当延误时,即一级异常类型code为01时有效)',
  `restart_count` smallint(6) NOT NULL DEFAULT '0' COMMENT '重启次数',
  `finance_status` tinyint(4) NOT NULL DEFAULT '2' COMMENT '财务流水单生成状态: 1已生成 2未生成',
  `end_status` tinyint(4) NOT NULL DEFAULT '2' COMMENT '完结件推送状态: 1已推送 2未推送',
  `delay_adju_status` tinyint(4) NOT NULL DEFAULT '2' COMMENT '延误裁定状态: 1已裁定 2未裁定 3无需裁定',
  `arbitration_remark` varchar(50)  NOT NULL DEFAULT '' COMMENT '仲裁备注(冗余)',
  `update_by` bigint(20) DEFAULT NULL COMMENT '修改人id',
  `update_by_code` varchar(24)  DEFAULT NULL COMMENT '更新人code',
  `update_by_name` varchar(30)  DEFAULT NULL COMMENT '修改人姓名',
  `update_time` timestamp NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间',
  `collect_time` timestamp NULL DEFAULT NULL COMMENT '订单揽收时间',
  `verify_time` timestamp NULL DEFAULT NULL COMMENT '核实时间',
  `shipment_no` varchar(20)  NOT NULL DEFAULT '' COMMENT '任务编号',
  `adjudications` json DEFAULT NULL COMMENT '裁定集合(冗余)',
  `networks` json DEFAULT NULL COMMENT '网点集合(冗余)',
  `process_records` json DEFAULT NULL COMMENT '处理记录集合(冗余)',
  `is_appeal` tinyint(4) NOT NULL DEFAULT '2' COMMENT '责任方是否需要标记申诉: 1.是 2否',
  `is_closed_last` tinyint(1) DEFAULT NULL COMMENT '是否完结（用于仲裁遗失统计）(1.是，2.否)',
  `third_remark` varchar(10)  DEFAULT NULL COMMENT '三级备注',
  `order_source_code` varchar(20)  NOT NULL DEFAULT '' COMMENT '工单来源编码',
  `order_source_name` varchar(60)  NOT NULL DEFAULT '' COMMENT '工单来源名称',
  `channel` tinyint(1) DEFAULT NULL COMMENT '(运单渠道 1.极兔 2.百世)',
  `is_vip` tinyint(1) DEFAULT NULL COMMENT '(是否vip 1.是 2.否)',
  `is_renew_pod_track` tinyint(1) DEFAULT NULL COMMENT '(是否更新物流轨迹 1.是 2.否)',
  `arrival_time` timestamp NULL DEFAULT NULL COMMENT '责任网点到件时间',
  `redundancy` json DEFAULT NULL COMMENT '冗余属性',
  `audit_status` tinyint(1) DEFAULT NULL COMMENT '审核状态\r\n1待总部审核、2总部审核通过、3总部审核不通过、4待网点审核、5网点审核通过、6网点审核不通过',
  `first_comp_network_id` int(10) DEFAULT NULL COMMENT '投诉网点1id',
  `first_comp_network_code` varchar(24)  DEFAULT NULL COMMENT '投诉网点1编码',
  `first_comp_network_name` varchar(30)  DEFAULT NULL COMMENT '投诉网点1名称',
  `first_comp_parent_id` int(10) DEFAULT NULL COMMENT '投诉代理区1id',
  `first_comp_parent_code` varchar(24)  DEFAULT NULL COMMENT '投诉代理区1编码',
  `first_comp_parent_name` varchar(30)  DEFAULT NULL COMMENT '投诉代理区1名称',
  `second_comp_network_id` int(10) DEFAULT NULL COMMENT '投诉网点2id',
  `second_comp_network_code` varchar(24)  DEFAULT NULL COMMENT '投诉网点2编码',
  `second_comp_network_name` varchar(30)  DEFAULT NULL COMMENT '投诉网点2名称',
  `second_comp_parent_id` int(10) DEFAULT NULL COMMENT '投诉代理区2id',
  `second_comp_parent_code` varchar(24)  DEFAULT NULL COMMENT '投诉代理区2编码',
  `second_comp_parent_name` varchar(30)  DEFAULT NULL COMMENT '投诉代理区2名称',
  `first_resp_network_id` int(10) DEFAULT NULL COMMENT '责任网点1id',
  `first_resp_network_code` varchar(24)  DEFAULT NULL COMMENT '责任网点1编码',
  `first_resp_network_name` varchar(30)  DEFAULT NULL COMMENT '责任网点1名称',
  `first_resp_parent_id` int(10) DEFAULT NULL COMMENT '责任代理区1id',
  `first_resp_parent_code` varchar(24)  DEFAULT NULL COMMENT '责任代理区1编码',
  `first_resp_parent_name` varchar(30)  DEFAULT NULL COMMENT '责任代理区1名称',
  `first_confirm_status` tinyint(4) DEFAULT NULL COMMENT '责任网点1认责状态：1、未认责 2、已认责',
  `second_resp_network_id` int(10) DEFAULT NULL COMMENT '责任网点2id',
  `second_resp_network_code` varchar(24)  DEFAULT NULL COMMENT '责任网点2编码',
  `second_resp_network_name` varchar(30)  DEFAULT NULL COMMENT '责任网点2名称',
  `second_resp_parent_id` int(10) DEFAULT NULL COMMENT '责任代理区2id',
  `second_resp_parent_code` varchar(24)  DEFAULT NULL COMMENT '责任代理区2编码',
  `second_resp_parent_name` varchar(30)  DEFAULT NULL COMMENT '责任代理区2名称',
  `second_confirm_status` tinyint(4) DEFAULT NULL COMMENT '责任网点2认责状态：1、未认责 2、已认责',
  `third_resp_network_id` int(10) DEFAULT NULL COMMENT '责任网点3id',
  `third_resp_network_code` varchar(24)  DEFAULT NULL COMMENT '责任网点3编码',
  `third_resp_network_name` varchar(30)  DEFAULT NULL COMMENT '责任网点3名称',
  `third_resp_parent_id` int(10) DEFAULT NULL COMMENT '责任代理区3id',
  `third_resp_parent_code` varchar(24)  DEFAULT NULL COMMENT '责任代理区3编码',
  `third_resp_parent_name` varchar(30)  DEFAULT NULL COMMENT '责任代理区3名称',
  `third_confirm_status` tinyint(4) DEFAULT NULL COMMENT '责任网点3认责状态：1、未认责 2、已认责',
  `four_resp_network_id` int(10) DEFAULT NULL COMMENT '责任网点4id',
  `four_resp_network_code` varchar(24)  DEFAULT NULL COMMENT '责任网点4编码',
  `four_resp_network_name` varchar(30)  DEFAULT NULL COMMENT '责任网点4名称',
  `four_resp_parent_id` int(10) DEFAULT NULL COMMENT '责任代理区4id',
  `four_resp_parent_code` varchar(24)  DEFAULT NULL COMMENT '责任代理区4编码',
  `four_resp_parent_name` varchar(30)  DEFAULT NULL COMMENT '责任代理区4名称',
  `four_confirm_status` tinyint(4) DEFAULT NULL COMMENT '责任网点4认责状态：1、未认责 2、已认责',
  `five_resp_network_id` int(10) DEFAULT NULL COMMENT '责任网点5id',
  `five_resp_network_code` varchar(24)  DEFAULT NULL COMMENT '责任网点5编码',
  `five_resp_network_name` varchar(30)  DEFAULT NULL COMMENT '责任网点5名称',
  `five_resp_parent_id` int(10) DEFAULT NULL COMMENT '责任代理区5id',
  `five_resp_parent_code` varchar(24)  DEFAULT NULL COMMENT '责任代理区5编码',
  `five_resp_parent_name` varchar(30)  DEFAULT NULL COMMENT '责任代理区5名称',
  `five_confirm_status` tinyint(4) DEFAULT NULL COMMENT '责任网点5认责状态：1、未认责 2、已认责',
  `station_name` varchar(100)  DEFAULT NULL COMMENT '门店名称',
  `business_name` varchar(100)  DEFAULT NULL COMMENT '品牌名称',
  `is_value_prove` tinyint(4) DEFAULT NULL COMMENT '是否有价值证明 0、无   1、有',
  `is_public_distribution_network` tinyint(4) DEFAULT NULL COMMENT '是否公配网点(用于仲裁明细统计): 1.是 2.否',
  `arb_source` int(10) DEFAULT NULL COMMENT '仲裁单来源',
  `express_type_id` int(11) DEFAULT NULL COMMENT '产品类型id',
  `express_type_code` varchar(30)  DEFAULT NULL COMMENT '产品类型code',
  `express_type_name` varchar(60)  DEFAULT NULL COMMENT '产品类型名称',
  `arb_behavior` tinyint(4) DEFAULT NULL COMMENT '仲裁行为 (0、默认 1、人工 2、自动)',
  `customer_code` varchar(20)  DEFAULT '' COMMENT '客户编码',
  `customer_name` varchar(100)  DEFAULT '' COMMENT '客户名称',
  `is_first_error` tinyint(1) DEFAULT NULL COMMENT '是否首次错误 1是，2否',
  `first_error_desc` varchar(100)  DEFAULT NULL COMMENT '错误描述',
  `is_package_inner_lost` tinyint(1) DEFAULT NULL COMMENT '是否包内件遗失 1：是, 2：否',
  `first_resp_network_type_id` int(11) DEFAULT '0' COMMENT '第一个责任网点类型id',
  `second_resp_network_type_id` int(11) DEFAULT '0' COMMENT '第二个责任网点类型id',
  `third_resp_network_type_id` int(11) DEFAULT '0' COMMENT '第三个责任网点类型id',
  `four_resp_network_type_id` int(11) DEFAULT '0' COMMENT '第四个责任网点类型id',
  `five_resp_network_type_id` int(11) DEFAULT '0' COMMENT '第五个责任网点类型id',
  `zy_dynamic_scan_time` timestamp NULL DEFAULT NULL COMMENT '异常时间(自有平台实际扫描时间)',
  `resp_network_num` tinyint(4) DEFAULT NULL COMMENT '责任网点个数',
  `trans_res_count` tinyint(4) DEFAULT '0' COMMENT '转责次数',
  `create_process_time` datetime DEFAULT NULL COMMENT '申报方处理时间',
  `revoke_time` datetime DEFAULT NULL COMMENT '撤销时间',
  `is_network_abnormal` tinyint(1) DEFAULT '2' COMMENT '是否网点异常 1：是, 2：否',
  `system_usage_fee_second` tinyint(4) DEFAULT NULL COMMENT '二次系统使用费 1是 2否',
  `first_auto_crawl_real_resp_network_id` int(10) DEFAULT NULL COMMENT '自动抓取实际责任网点1id',
  `first_auto_crawl_real_resp_network_code` varchar(30)  DEFAULT NULL COMMENT '自动抓取实际责任网点1编码',
  `first_auto_crawl_real_resp_network_name` varchar(60)  DEFAULT NULL COMMENT '自动抓取实际责任网点1名称',
  `first_auto_crawl_real_resp_network_type_id` int(10) DEFAULT NULL COMMENT '自动抓取实际责任网点1类型',
  `second_auto_crawl_real_resp_network_id` int(10) DEFAULT NULL COMMENT '自动抓取实际责任网点2id',
  `second_auto_crawl_real_resp_network_code` varchar(30)  DEFAULT NULL COMMENT '自动抓取实际责任网点2编码',
  `second_auto_crawl_real_resp_network_name` varchar(60)  DEFAULT NULL COMMENT '自动抓取实际责任网点2名称',
  `second_auto_crawl_real_resp_network_type_id` int(10) DEFAULT NULL COMMENT '自动抓取实际责任网点2类型',
  `just_allow_resp` int(11) NOT NULL DEFAULT '2' COMMENT '只允许认责[提交仲裁之后只允许认责，不允许回复] (1.是 2.否)',
  `arb_labels` varchar(1000)  DEFAULT NULL COMMENT '仲裁单标签（标签id,拼接）',
  `is_packaging_standard` tinyint(1) DEFAULT NULL COMMENT '是否包装规范: 1.是 2.否',
  `system_create_time` datetime DEFAULT NULL COMMENT '系统创建时间-不变',
  `transfer_award_amount` decimal(20, 2) DEFAULT NULL COMMENT '转责裁定金额',
  `transfer_payable_amount` decimal(20, 2) DEFAULT NULL COMMENT '转责应付金额',
  `transfer_system_usage_fee` decimal(20, 2) DEFAULT NULL COMMENT '转责系统使用费',
  `first_auto_crawl_real_resp_proxy_id` int(11) DEFAULT NULL COMMENT '自动抓取实际责任代理区1id',
  `first_auto_crawl_real_resp_proxy_code` varchar(30)  DEFAULT NULL COMMENT '自动抓取实际责任代理区1编码',
  `first_auto_crawl_real_resp_proxy_name` varchar(60)  DEFAULT NULL COMMENT '自动抓取实际责任代理区1名称',
  `second_auto_crawl_real_resp_proxy_id` int(11) DEFAULT NULL COMMENT '自动抓取实际责任代理区2id',
  `second_auto_crawl_real_resp_proxy_code` varchar(30)  DEFAULT NULL COMMENT '自动抓取实际责任代理区2编码',
  `second_auto_crawl_real_resp_proxy_name` varchar(60)  DEFAULT NULL COMMENT '自动抓取实际责任代理区2名称',
  `settlement_status` tinyint(1) DEFAULT '0' COMMENT '结算状态: 1已结算 2未结算',
  `push_time` datetime DEFAULT NULL COMMENT '推送时间',
  `suspected_resp` tinyint(4) DEFAULT NULL COMMENT '疑似遗失认责（1.是 2.否）',
  `is_package_inner_damage` tinyint(4) DEFAULT NULL COMMENT '是否包内件破损 1：是, 2：否',
  `is_resp_not_verified` tinyint(4) DEFAULT '2' COMMENT '是否收取未核实清楚费用(责任方) 1.是 2.否',
  `original_first_type_code` varchar(20)  DEFAULT NULL COMMENT '原一级异常类型code',
  `original_first_type` varchar(30)  DEFAULT NULL COMMENT '原一级异常类型名称',
  `original_second_type_code` varchar(20)  DEFAULT NULL COMMENT '原二级异常类型code',
  `original_second_type` varchar(30)  DEFAULT NULL COMMENT '原二级异常类型名称',
  `out_packing_case` varchar(100)  DEFAULT NULL COMMENT '外包装问题 支持多选,分割',
  `internal_case` varchar(100)  DEFAULT NULL COMMENT '内件问题 支持多选,分割',
  `is_network_change` tinyint(4) DEFAULT '2' COMMENT '提交仲裁时，是否变更网点 (1.是 2.否)',
  `earliest_complaint_networks` json DEFAULT NULL COMMENT '首次投诉网点集合',
  `create_network_area` json DEFAULT NULL COMMENT '申报网点网管片区',
  `resp_network_areas` json DEFAULT NULL COMMENT '责任网点网管片区集合',
  `project_assessment_value` decimal(12, 2) DEFAULT NULL COMMENT '项目考核金额',
  `subscribe_source_code` varchar(20)  DEFAULT NULL COMMENT '订阅来源编码',
  `subscribe_source_name` varchar(60)  DEFAULT NULL COMMENT '订阅来源名称',
  `port_type` tinyint(1) DEFAULT NULL COMMENT '进出港类型:1进港,0出港',
  `process_deadline_time` datetime DEFAULT NULL COMMENT '剩余处理时间（截止时间）',
  `ticket_id` bigint(20) DEFAULT NULL COMMENT '平台申诉单ID',
  `push_pdd_status` int(10) DEFAULT NULL COMMENT '推送PDD状态（0.未推送 1.推送成功 2.推送失败）',
  `push_pdd_fail_msg` varchar(50)  DEFAULT NULL COMMENT '推送PDD失败原因',
  `transfer_resp_type` tinyint(4) DEFAULT NULL COMMENT '转运责任标识(1始发中心,2中转中心,3目的中心)')










CREATE TABLE `work_order_0` (
  `id` bigint(20) NOT NULL COMMENT 'id',
  `work_order_no` varchar(20)  DEFAULT NULL COMMENT '工单编号',
  `customer_name` varchar(50)  DEFAULT NULL COMMENT '客户名称',
  `customer_sex` tinyint(2) DEFAULT NULL COMMENT '客户性别 1:男 2:女',
  `customer_phone` varchar(20)  DEFAULT NULL COMMENT '客户电话',
  `customer_type` tinyint(2) DEFAULT NULL COMMENT '客户类型 1:寄件人 2:收件人 3:其他',
  `receiver_province_name` varchar(60)  DEFAULT NULL COMMENT '收件省份名称',
  `receiver_province_id` int(11) DEFAULT NULL COMMENT '收件省份id',
  `receiver_city_name` varchar(60)  DEFAULT NULL COMMENT '收件城市名称',
  `receiver_city_id` int(11) DEFAULT NULL COMMENT '收件城市id',
  `receiver_area_name` varchar(60)  DEFAULT NULL COMMENT '收件区域名称',
  `receiver_area_id` int(11) DEFAULT NULL COMMENT '收件区域id',
  `receiver_detailed_address` varchar(300)  DEFAULT NULL COMMENT '收件详细地址',
  `waybill_no` varchar(30)  DEFAULT NULL COMMENT '运单号',
  `first_type_id` bigint(20) DEFAULT NULL COMMENT '一级类型id',
  `first_type_code` varchar(20)  DEFAULT NULL COMMENT '一级类型编码',
  `first_type_name` varchar(40)  DEFAULT NULL COMMENT '一级类型名称',
  `second_type_id` bigint(20) DEFAULT NULL COMMENT '二级类型id',
  `second_type_code` varchar(20)  DEFAULT NULL COMMENT '二级类型编码',
  `second_type_name` varchar(40)  DEFAULT NULL COMMENT '二级类型名称',
  `second_type_reminder_count` int(5) DEFAULT NULL COMMENT '二级类型中配置的催单次数',
  `second_type_treatment_limitation` float(5, 1) DEFAULT NULL COMMENT '二级类型中配置的处理时效(h)',
  `problem_description` varchar(500)  DEFAULT NULL COMMENT '问题描述',
  `emergency_level` tinyint(2) DEFAULT NULL COMMENT '紧急程度 1:紧急 2:一般',
  `accept_network_id` int(11) DEFAULT NULL COMMENT '受理网点id',
  `accept_network_code` varchar(30)  DEFAULT NULL COMMENT '受理网点编码',
  `accept_network_name` varchar(60)  DEFAULT NULL COMMENT '受理网点名称',
  `accept_network_type_id` int(11) DEFAULT NULL COMMENT '受理网点类型ID',
  `call_back_name` varchar(30)  DEFAULT NULL COMMENT '回电对象',
  `call_back_phone` varchar(30)  DEFAULT NULL COMMENT '回电号码',
  `reminder_count` int(11) DEFAULT NULL COMMENT '实际催单次数',
  `upgrade_status` tinyint(2) DEFAULT NULL COMMENT '升级状态 1:是 2:否',
  `upgrade_count` int(11) DEFAULT NULL COMMENT '升级次数',
  `upgrade_path` varchar(500)  DEFAULT NULL COMMENT '升级路径',
  `status` tinyint(2) DEFAULT NULL COMMENT '普通工单状态 1:待分配 2:处理中 3:已关闭',
  `source_code` tinyint(2) DEFAULT NULL COMMENT '工单来源编码 1:网点组 2:代理组 3:总部组 4:电话组别 5:总部工单组',
  `registration_network_id` int(11) DEFAULT NULL COMMENT '登记网点id',
  `registration_network_code` varchar(30)  DEFAULT NULL COMMENT '登记网点编码',
  `registration_network_name` varchar(60)  DEFAULT NULL COMMENT '登记网点名称',
  `registration_network_type_id` int(11) DEFAULT NULL COMMENT '登记网点类型ID',
  `accept_by` int(11) DEFAULT NULL COMMENT '受理人ID',
  `accept_by_code` varchar(30)  DEFAULT NULL COMMENT '受理人编码',
  `accept_by_name` varchar(60)  DEFAULT NULL COMMENT '受理人名称',
  `is_enable` tinyint(2) DEFAULT NULL COMMENT '是否启用:1启用,2不启用',
  `is_delete` tinyint(2) DEFAULT NULL COMMENT '是否删除:1未删除,2已删除',
  `create_by` int(11) DEFAULT NULL COMMENT '创建人ID(登记人ID)',
  `update_by` int(11) DEFAULT NULL COMMENT '最后更新人ID',
  `create_by_code` varchar(30)  DEFAULT NULL COMMENT '创建人编码(登记人编码)',
  `update_by_code` varchar(30)  DEFAULT NULL COMMENT '最后修改人编码',
  `create_by_name` varchar(60)  DEFAULT NULL COMMENT '创建人名称(登记人名称)',
  `update_by_name` varchar(60)  DEFAULT NULL COMMENT '最后修改人名称',
  `create_time` timestamp NULL DEFAULT NULL COMMENT '创建时间(登记时间)',
  `update_time` timestamp NULL DEFAULT NULL COMMENT '更新时间',
  `phone_count` int(11) DEFAULT NULL COMMENT '来电次数',
  `accept_time` timestamp NULL DEFAULT NULL COMMENT '受理时间',
  `response_time` timestamp NULL DEFAULT NULL COMMENT '响应时间',
  `upgrade_time` timestamp NULL DEFAULT NULL COMMENT '升级时间',
  `sound_record_id` varchar(60)  DEFAULT NULL COMMENT '录音id',
  `total_duration` bigint(20) DEFAULT NULL COMMENT '工单总时长(分钟)',
  `duty_network_id` int(11) DEFAULT NULL COMMENT '责任网点id',
  `duty_network_code` varchar(30)  DEFAULT NULL COMMENT '责任网点编码',
  `duty_network_name` varchar(60)  DEFAULT NULL COMMENT '责任网点名称',
  `duty_network_type_id` int(11) DEFAULT NULL COMMENT '责任网点类型ID',
  `record_group` tinyint(2) NOT NULL DEFAULT '1' COMMENT '录单组别 1:电话组 2:在线组',
  `process_status` tinyint(2) NOT NULL DEFAULT '1' COMMENT '处理状态 1:未处理 2:已处理',
  `service_code` varchar(10)  DEFAULT NULL COMMENT '服务商编码',
  `service_name` varchar(30)  DEFAULT NULL COMMENT '服务商名称',
  `old_accept_network_id` int(11) DEFAULT NULL COMMENT '原受理网点id',
  `old_accept_network_code` varchar(30)  DEFAULT NULL COMMENT '原受理网点编码',
  `old_accept_network_name` varchar(60)  DEFAULT NULL COMMENT '原受理网点名称',
  `old_accept_network_type_id` int(11) DEFAULT NULL COMMENT '原受理网点类型id',
  `accept_belong_network_id` int(11) DEFAULT NULL COMMENT '归属网点id',
  `accept_belong_network_code` varchar(30)  DEFAULT NULL COMMENT '归属网点编码',
  `accept_belong_network_name` varchar(60)  DEFAULT NULL COMMENT '归属网点名称',
  `accept_belong_network_type_id` int(11) DEFAULT NULL COMMENT '归属网点类型id',
  `response_state` tinyint(2) DEFAULT NULL COMMENT '响应状态 1:及时响应 2:超时响应 3:尚未响应',
  `transfer_network_id` int(11) DEFAULT NULL COMMENT '转单责任网点id',
  `transfer_network_code` varchar(30)  DEFAULT NULL COMMENT '转单责任网点编码',
  `transfer_network_name` varchar(60)  DEFAULT NULL COMMENT '转单责任网点名称',
  `transfer_network_type_id` int(11) DEFAULT NULL COMMENT '转单责任网点类型id',
  `service_registrant_code` varchar(30)  DEFAULT NULL COMMENT '服务商登记人编码',
  `service_registrant_name` varchar(30)  DEFAULT NULL COMMENT '服务商登记人名称',
  `monitoring_time` bigint(20) NOT NULL DEFAULT '0' COMMENT '监控报表时间',
  `is_repeat` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否重复:1不重复,2重复,判断规则：一级问题类型、二级问题类型、运单号一致',
  `accept_network_logo` tinyint(1) NOT NULL DEFAULT '0' COMMENT '受理网点标识,1网点,2转运中心,3集散点',
  `accept_league_network_id` bigint(11) NOT NULL DEFAULT '0' COMMENT '受理网点加盟商id',
  `reg_league_network_id` bigint(11) NOT NULL DEFAULT '0' COMMENT '登记网点加盟商id',
  `reg_network_logo` tinyint(1) NOT NULL DEFAULT '0' COMMENT '登记网点标识,1网点,2转运中心,3集散点',
  `reg_belong_network_id` int(11) NOT NULL DEFAULT '0' COMMENT '登记归属网点id',
  `accept_franchisee_network_id` int(11) DEFAULT NULL COMMENT '受理网点加盟商id',
  `accept_franchisee_network_code` varchar(30)  DEFAULT NULL COMMENT '受理网点加盟商编码',
  `accept_franchisee_network_name` varchar(60)  DEFAULT NULL COMMENT '受理网点加盟商名称',
  `response_network_id` int(11) DEFAULT NULL COMMENT '响应网点id',
  `response_network_code` varchar(30)  DEFAULT NULL COMMENT '响应网点编码',
  `response_network_name` varchar(60)  DEFAULT NULL COMMENT '响应网点名称',
  `transfer_network_type` int(11) DEFAULT NULL COMMENT '转单责任网点类型',
  `user_code` varchar(30)  DEFAULT NULL COMMENT '运单基础信息客户编码',
  `user_name` varchar(60)  DEFAULT NULL COMMENT '运单基础信息客户名称',
  `accept_belong_mr_code` varchar(10)  DEFAULT NULL COMMENT '归属网点管理大区编号',
  `accept_belong_mr_name` varchar(10)  DEFAULT NULL COMMENT '归属网点管理大区名称',
  `order_source_name` varchar(60)  NOT NULL DEFAULT '' COMMENT '工单来源名称',
  `order_source_code` varchar(20)  NOT NULL DEFAULT '' COMMENT '工单来源编码',
  `is_call` tinyint(1) NOT NULL DEFAULT '2' COMMENT '是否存在外呼 1：存在 2:不存在',
  `call_num` smallint(6) NOT NULL DEFAULT '0' COMMENT '外呼次数',
  `member_type` tinyint(1) DEFAULT NULL COMMENT '是否会员：1 是,2 否',
  `order_id` bigint(20) DEFAULT NULL COMMENT '订单号',
  `provider_id` int(11) DEFAULT NULL COMMENT '受理网点省份id',
  `provider_desc` varchar(60)  DEFAULT NULL COMMENT '受理网点省份名称',
  `city_id` int(11) DEFAULT NULL COMMENT '受理网点城市id',
  `city_desc` varchar(60)  DEFAULT NULL COMMENT '受理网点城市名称',
  `reopen` tinyint(4) DEFAULT NULL COMMENT '是否重启',
  `delivery_code` varchar(30)  DEFAULT NULL COMMENT '派件员编码',
  `delivery_name` varchar(60)  DEFAULT NULL COMMENT '派件员名称',
  `pick_network_code` varchar(30)  DEFAULT NULL COMMENT '寄件网点编码',
  `pick_network_name` varchar(60)  DEFAULT NULL COMMENT '寄件网点名称',
  `incoming_time` datetime DEFAULT NULL COMMENT '入库时间(物流轨迹,最新一条入库扫描时间)',
  `send_type` varchar(30)  DEFAULT NULL COMMENT '投递类型(物流轨迹,最新一条入库扫描中的remark1)',
  `send_type_address` varchar(200)  DEFAULT NULL COMMENT '投递类型地址(物流轨迹,最新一条入库扫描中的remark2)',
  `is_dispatcher` tinyint(1) DEFAULT '1' COMMENT '是否下发派件员 1未下发2已下发',
  `transfer_agent_network_code` varchar(30)  DEFAULT NULL COMMENT '转单责任网点所属代理区编码',
  `transfer_agent_network_name` varchar(60)  DEFAULT NULL COMMENT '转单责任网点所属代理区名称',
  `terminal_dispatch_code` varchar(128)  DEFAULT NULL COMMENT '三段码',
  `is_vip` tinyint(1) DEFAULT '2' COMMENT '是否为VIP工单:1是,2否(判断规则：转单组别选择总部vip组录入的普通工单)',
  `wx_user_id` varchar(32)  DEFAULT NULL COMMENT '微信用户id',
  `evaluate` tinyint(2) DEFAULT NULL COMMENT '客户评价 1:非常满意 2:满意 3:一般 4:不满意',
  `wx_file_flag` tinyint(2) DEFAULT '0' COMMENT '微信小程序上传附件标识 1是 0否',
  `collect_time` timestamp NULL DEFAULT NULL COMMENT '快件揽收时间',
  `close_time` timestamp NULL DEFAULT NULL COMMENT '关闭时间',
  `receiver_name` varchar(50)  DEFAULT NULL COMMENT '收件人姓名',
  `accept_virtual_proxy_code` varchar(30)  DEFAULT NULL COMMENT '受理网点所属虚拟代理区编码',
  `accept_virtual_proxy_name` varchar(60)  DEFAULT NULL COMMENT '受理网点所属虚拟代理区名称',
  `transfer_district_id` int(11) DEFAULT NULL COMMENT '转单责任网点片区id',
  `transfer_district_code` varchar(30)  DEFAULT NULL COMMENT '转单责任网点片区code',
  `transfer_district_name` varchar(60)  DEFAULT NULL COMMENT '转单责任网点片区name',
  `transfer_city_id` int(11) DEFAULT NULL COMMENT '转单责任网点城市id',
  `transfer_city_desc` varchar(60)  DEFAULT NULL COMMENT '转单责任网点城市name',
  `station_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '驿站工单状态 1:未下发 2:已回复 3:已评价 默认1',
  `claim_id` bigint(20) DEFAULT NULL COMMENT '理赔id',
  `claim_status` tinyint(2) DEFAULT NULL COMMENT '理赔状态 1:待审核 2:待付款 3:付款中 4:付款成功 5:付款失败 6:已驳回',
  `product_type` varchar(20)  DEFAULT NULL COMMENT '产品类型',
  `is_send_message` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否发送短信(0否 1是)',
  `resp_customer_code` varchar(30)  DEFAULT NULL COMMENT '首响客服编码',
  `resp_customer_name` varchar(60)  DEFAULT NULL COMMENT '首响客服名称',
  `station_business_id` varchar(20)  DEFAULT NULL COMMENT '驿站品牌id',
  `effective_resp_state` tinyint(1) DEFAULT NULL COMMENT '有效响应状态 1:有效响应 2:无效响应 3:尚未响应',
  `order_mark_code` varchar(200)  DEFAULT NULL COMMENT '订单标签编码',
  `order_mark_name` varchar(200)  DEFAULT NULL COMMENT '订单标签名称',
  `is_except_track` tinyint(4) DEFAULT NULL COMMENT '是否异常轨迹',
  `upgrade_sta` tinyint(2) DEFAULT '1' COMMENT '升级状态',
  `customer_phone_enc` varchar(60)  DEFAULT NULL COMMENT '客户电话加密',
  `call_back_phone_enc` varchar(60)  DEFAULT NULL COMMENT '回电号码加密',
  `old_registrant_code` varchar(30)  DEFAULT NULL COMMENT '原工单登记人编码',
  `old_registrant_name` varchar(60)  DEFAULT NULL COMMENT '原工单登记人名称',
  `labels` varchar(500)  DEFAULT NULL COMMENT '标签',
  `vip_wo_type` tinyint(2) DEFAULT NULL COMMENT 'vip工单类型 1-普通工单，2-理赔工单',
  `vip_claim_type` tinyint(2) DEFAULT NULL COMMENT 'vip理赔类型，1-延误，2-遗失，3-破损',
  `task_code` varchar(60)  DEFAULT NULL COMMENT '任务编号',
  `product_amount` decimal(8, 2) DEFAULT NULL COMMENT '商品金额',
  `item_type` varchar(10)  DEFAULT NULL COMMENT '物品类型',
  `item_name` varchar(60)  DEFAULT NULL COMMENT '内件名称',
  `compensation_obj` varchar(20)  DEFAULT NULL COMMENT '赔付对象:寄件人、收件人、其他',
  `im_customer_name` varchar(20)  DEFAULT NULL COMMENT '客户姓名',
  `im_customer_phone` varchar(20)  DEFAULT NULL COMMENT '客户联系方式',
  `im_customer_phone_enc` varchar(60)  DEFAULT NULL COMMENT '客户联系方式密文',
  `account_name` varchar(20)  DEFAULT NULL COMMENT '账户类型:支付宝、微信、银行卡、现金',
  `value_atta` varchar(1000)  DEFAULT NULL COMMENT '价值证明截图附件',
  `compensation_atta` varchar(1000)  DEFAULT NULL COMMENT '赔付截图附件',
  `insured` tinyint(2) DEFAULT NULL COMMENT '是否保价 1是，0否',
  `payee_account` varchar(60)  DEFAULT NULL COMMENT '收款账户',
  `payment_type` tinyint(2) DEFAULT NULL COMMENT '支付类型 1:线上 2:线下',
  `early_warning_flag` tinyint(2) NOT NULL DEFAULT '2' COMMENT '是否预警 1-是 2-否 默认否',
  `claim_remark` tinyint(2) DEFAULT NULL COMMENT '理赔说明 1已理赔, lock = none;2【无需理赔】客户不追究我司赔偿责任;3【无需理赔】快件实际无损坏，客户无需理赔',
  `is_24h_finish` tinyint(4) DEFAULT NULL COMMENT '是否24小时完结 1是 0否',
  `online_channel_source_code` varchar(50)  DEFAULT NULL COMMENT '在线渠道来源编码(逍遥峰-KS、极地湾-JD、紫金山-逆向、桃花岛-逆向、CaiNiao群聊、微博、桃花岛-正向、官网、微信、VIP渠道、菜鸟-七星潭、抖音-紫金山、百度小程序、支付宝小程序；)',
  `mark_color` varchar(30)  DEFAULT NULL COMMENT '标记字体颜色',
  `mark` varchar(100)  DEFAULT NULL COMMENT '标记',
  `payee_name` varchar(30)  DEFAULT NULL COMMENT '收款人姓名',
  `sign_type` varchar(20)  DEFAULT NULL COMMENT '签收类型',
  `sign_time` varchar(30)  DEFAULT NULL COMMENT '运单签收时间',
  `sign_name` varchar(50)  DEFAULT NULL COMMENT '签收人',
  `internal_problem_type_code` varchar(10)  DEFAULT NULL COMMENT '内部问题分类编码',
  `internal_problem_type_name` varchar(30)  DEFAULT NULL COMMENT '内部问题分类名称',
  `paths` json DEFAULT NULL COMMENT '附件path',
  `transfer_post_flag` tinyint(4) DEFAULT NULL COMMENT '是否转邮件 1：是 0：否',
  `town_send_flag` tinyint(4) DEFAULT NULL COMMENT '是否乡镇加时件 1：是 0：否',
  `psr_network_id` int(11) DEFAULT NULL COMMENT '主动认责网点id',
  `psr_network_code` varchar(30)  DEFAULT NULL COMMENT '主动认责网点编码',
  `psr_network_name` varchar(60)  DEFAULT NULL COMMENT '主动认责网点名称',
  `response_deadline_time` datetime DEFAULT NULL COMMENT '响应截止时间',
  `process_deadline_time` datetime DEFAULT NULL COMMENT '处理截止时间',
  `option_one_name` varchar(10)  DEFAULT NULL COMMENT '客户一级选项name',
  `option_two_name` varchar(10)  DEFAULT NULL COMMENT '客户二级选项name',
  `option_three_name` varchar(10)  DEFAULT NULL COMMENT '客户三级选项name',
  `mark_time` datetime DEFAULT NULL COMMENT '标注时间',
  `visite_total` int(11) DEFAULT NULL COMMENT '来访次数',
  `responsible_network_id` int(11) DEFAULT NULL COMMENT '责任方网点id-二级问题类型选择服务态度时专用',
  `responsible_network_code` varchar(30)  DEFAULT NULL COMMENT '责任方网点编码-二级问题类型选择服务态度时专用',
  `responsible_network_name` varchar(60)  DEFAULT NULL COMMENT '责任方网点名称-二级问题类型选择服务态度时专用',
  `shop_name` varchar(100)  DEFAULT NULL COMMENT '店铺名称',
  `subbill_code` varchar(60)  DEFAULT '' COMMENT '门店编码',
  `close_network_id` int(11) DEFAULT NULL COMMENT '关单网点id',
  `close_network_code` varchar(30)  DEFAULT NULL COMMENT '关单网点编码',
  `close_network_name` varchar(60)  DEFAULT NULL COMMENT '关单网点名称',
  `close_network_type_id` int(11) DEFAULT NULL COMMENT '关单网点类型ID',
  `is_shared_process` tinyint(4) NOT NULL DEFAULT '2' COMMENT '是否共享客服 1是，2否',
  `claim_reason` varchar(30)  DEFAULT NULL COMMENT '理赔原因',
  `evaluate_level` tinyint(4) DEFAULT NULL COMMENT '评价等级 1-非常不满意、2-不满意、3-一般、4-满意、5-非常满意',
  `agreement_customer_flag` tinyint(1) DEFAULT NULL COMMENT '协议客户标识：0否 1是',
  `headquarters_guarantee` tinyint(4) DEFAULT NULL COMMENT '是否总部兜底 0-否 1-是',
  `responsibility_admit_time` datetime DEFAULT NULL COMMENT '主动认责时间',
  `is_intelligent_close` tinyint(4) DEFAULT NULL COMMENT '是否智能关单 1是，2否',
  `is_courier_liable` tinyint(4) DEFAULT NULL COMMENT '是否快递责任：1-是，2-否',
  `cust_proof_time` datetime DEFAULT NULL COMMENT '客户举证完成时间',
  `courier_liable_time` datetime DEFAULT NULL COMMENT '确认快递责任时间',
  `comp_mat_provided_time` datetime DEFAULT NULL COMMENT '赔付资料已提供时间',
  `update_by_customer_type` tinyint(4) DEFAULT NULL COMMENT '最后修改人客服类型',
  `buz_customer_type` tinyint(4) DEFAULT NULL COMMENT '客户类型: 1 散单&逆向、2 小B、3 KA、4 商家',
  `follow_order_remarks` json DEFAULT NULL COMMENT '跟单备注',
  `first_response_deadline_time` datetime DEFAULT NULL COMMENT '首响截止时间，固定登记时间加60分钟',
  `buz_customer_code` varchar(20)  DEFAULT NULL COMMENT '客户编码',
  `buz_customer_name` varchar(60)  DEFAULT NULL COMMENT '客户名称',
  `buz_project_name` varchar(30)  DEFAULT NULL COMMENT '项目名称',
  `audit_status` tinyint(4) DEFAULT NULL COMMENT '审核状态 1-待审核，2-审核驳回，3-审核通过',
  `audit_by` int(11) DEFAULT NULL COMMENT '审核人id',
  `audit_by_code` varchar(30)  DEFAULT NULL COMMENT '审核人编码',
  `audit_by_name` varchar(60)  DEFAULT NULL COMMENT '审核人名称',
  `audit_time` datetime DEFAULT NULL COMMENT '审核时间',
  `external_delivery_time` datetime DEFAULT NULL COMMENT '外投时间',
  `public_opinion_level` tinyint(4) DEFAULT NULL COMMENT '舆情等级',
  `submit_close_time` datetime DEFAULT NULL COMMENT '工单提交关闭时间',
  `session_id` bigint(20) DEFAULT NULL COMMENT '会话id')



CREATE TABLE `project_work_order` (
  `id` bigint(20) NOT NULL COMMENT '主键id',
  `work_order_no` varchar(64)  DEFAULT '' COMMENT '工单号',
  `waybill_no` varchar(64)  NOT NULL DEFAULT '' COMMENT '运单号',
  `order_no` varchar(24)  NOT NULL DEFAULT '' COMMENT '拼多多工单号',
  `work_order_channel` tinyint(4) NOT NULL DEFAULT '1' COMMENT '渠道来源(1.PDD，2.紫金山)',
  `work_order_status` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '工单状态 0 待分配 1待处理 2 处理中 3 已关闭',
  `finish_status` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '完结处理状态  0 待分配 1待处理 2 处理中 3 已关闭',
  `first_problem_type` int(11) DEFAULT NULL COMMENT '一级问题类型',
  `work_order_source_id` tinyint(3) unsigned NOT NULL COMMENT '工单创建来源 0：平台 1：消费者 2：商家',
  `send_back_code` tinyint(3) unsigned NOT NULL DEFAULT '2' COMMENT '退回标识 1 是 2 否',
  `send_back_count` tinyint(3) unsigned NOT NULL COMMENT '退回次数',
  `problem_desc` varchar(2048)  NOT NULL DEFAULT '' COMMENT '问题描述',
  `remarks` varchar(2048)  NOT NULL DEFAULT '' COMMENT '投诉内容',
  `file_json` varchar(4096)  DEFAULT '' COMMENT '附件链接',
  `initiator_name` varchar(64)  NOT NULL COMMENT '发起人姓名',
  `initiator_mobile` varchar(60)  NOT NULL COMMENT '发起人手机',
  `accept_network_id` mediumint(8) unsigned DEFAULT NULL COMMENT '受理网点id',
  `accept_network_name` varchar(200)  DEFAULT NULL COMMENT '受理网点名称',
  `accept_code` varchar(64)  DEFAULT NULL COMMENT '受理人code',
  `accept_name` varchar(20)  DEFAULT '' COMMENT '受理人姓名',
  `accept_agency_network_id` mediumint(9) DEFAULT NULL COMMENT '受理网点代理区id',
  `accept_agency_network_name` varchar(50)  DEFAULT NULL COMMENT '受理网点代理区名称',
  `emergency_level` tinyint(3) unsigned DEFAULT NULL COMMENT '紧急程度',
  `operator_id` bigint(10) DEFAULT NULL COMMENT '操作人id',
  `operator_name` varchar(20)  DEFAULT NULL COMMENT '操作人姓名',
  `responsibility_network_id` mediumint(8) unsigned DEFAULT NULL COMMENT '责任网点',
  `responsibility_network_name` varchar(200)  DEFAULT NULL COMMENT '责任网点名称',
  `sham_signed_flag` tinyint(3) unsigned DEFAULT NULL COMMENT '虚假判定 0 是 1 否',
  `pdd_created_at` datetime NOT NULL COMMENT '拼多多创建时间',
  `pdd_updated_at` datetime DEFAULT NULL COMMENT '拼多多更新时间',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `return_time` datetime DEFAULT NULL COMMENT '退回时间',
  `last_close_time` datetime DEFAULT NULL COMMENT '最后关闭时间',
  `last_reply` varchar(500)  DEFAULT '' COMMENT '最后回复意见',
  `last_duration_time` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '最后处理时长',
  `overtime_finish` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '超时完结 0 否 1 是',
  `auto_finish` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '自动完结 0 否 1 是',
  `receive_address` varchar(512)  DEFAULT '' COMMENT '收件人地址',
  `pay_amount` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '商品价值 单位分',
  `receiver_id` int(10) unsigned DEFAULT NULL COMMENT '受理人用户id',
  `sync` tinyint(3) unsigned DEFAULT '0' COMMENT '是否同步 0 否 1 是',
  `reject_count` tinyint(4) DEFAULT NULL COMMENT '拒绝次数',
  `last_reject_time` timestamp NULL DEFAULT NULL COMMENT '最后审核拒绝时间',
  `last_approval_time` timestamp NULL DEFAULT NULL COMMENT '最后审核通过时间',
  `last_approval_user_id` int(11) DEFAULT NULL COMMENT '审核人用户id',
  `last_approval_name` varchar(32)  DEFAULT NULL COMMENT '最后审核人名字',
  `approval_status` tinyint(4) DEFAULT '0' COMMENT '审核状态 1 审核中 2 审核通过 3 审核不通过',
  `approval_comment` varchar(500)  DEFAULT '' COMMENT '审核意见',
  `upgrade_status` tinyint(4) DEFAULT '0' COMMENT '升级状态: 0 否 1 是',
  `response_status` tinyint(3) DEFAULT '0' COMMENT '响应状态：1 尚未响应 2 及时响应 3 超时响应',
  `partner_name` varchar(64)  DEFAULT '' COMMENT '合作伙伴名称',
  `express_cabinet` varchar(200)  DEFAULT '' COMMENT '快递柜',
  `send_address` varchar(200)  DEFAULT NULL COMMENT '工单来源为商家时，传揽件地址，其他来源该字段为空',
  `first_level_code` varchar(5)  DEFAULT NULL COMMENT '一级类型编码',
  `first_level_name` varchar(15)  DEFAULT NULL COMMENT '一级类型名称',
  `second_level_code` varchar(5)  DEFAULT NULL COMMENT '二级类型编码',
  `second_level_name` varchar(15)  DEFAULT NULL COMMENT '二级类型名称',
  `res_franchisee_network_id` int(10) DEFAULT NULL COMMENT '责任网点加盟商id',
  `res_franchisee_network_name` varchar(60)  DEFAULT NULL COMMENT '责任网点加盟商名称',
  `res_agency_network_id` int(10) DEFAULT NULL COMMENT '责任网点代理区id',
  `res_agency_network_name` varchar(60)  DEFAULT NULL COMMENT '责任网点代理区名称',
  `close_network_id` varchar(128)  DEFAULT NULL COMMENT '关闭网点id(逗号分隔)',
  `close_network_name` varchar(200)  DEFAULT NULL COMMENT '关闭网点名称(逗号分隔)',
  `accept_network_type` tinyint(1) DEFAULT NULL COMMENT '网点标识,1网点,2转运中心,3集散点,4其它',
  `response_duration` bigint(20) DEFAULT NULL COMMENT '响应时长(第一次处理记录时间)',
  `monitoring_time` timestamp NULL DEFAULT NULL COMMENT '监控时间（定时任务刷新）',
  `process_duration` bigint(20) DEFAULT NULL COMMENT '处理时长(工单关闭时间-工单创建时间)',
  `is_monitor_history` tinyint(4) NOT NULL DEFAULT '1' COMMENT '是否监控工单历史数据1是2否',
  `service_id` varchar(20)  DEFAULT NULL COMMENT '紫金山业务线(crossborder.跨境进口 internal.国内)',
  `project_work_company` varchar(20)  DEFAULT NULL COMMENT '抖音物流商',
  `ticket_expire_time` timestamp NULL DEFAULT NULL COMMENT '抖音工单超时时间',
  `ticket_status` tinyint(4) DEFAULT NULL COMMENT '抖音工单状态(1.处理中)',
  `ticket_first_type` smallint(5) DEFAULT NULL COMMENT '工单一级类型id',
  `ticket_second_type` int(11) DEFAULT NULL COMMENT '二级问题类型',
  `second_complaint` tinyint(4) DEFAULT NULL COMMENT '二次投诉（0.不是 1.是）',
  `handle_times` smallint(2) DEFAULT NULL COMMENT '下发次数，工单第n次下发',
  `product_info` json DEFAULT NULL COMMENT '商品信息',
  `callback_contact` varchar(64)  DEFAULT NULL COMMENT '反馈电话',
  `creator_role` varchar(20)  DEFAULT NULL COMMENT '创建人角色(customer.消费者, platform.平台客服)',
  `receiver_name` varchar(128)  DEFAULT NULL COMMENT '收件人姓名',
  `receiver_contact` varchar(64)  DEFAULT NULL COMMENT '收件人电话',
  `incoming_time` datetime DEFAULT NULL COMMENT '入库时间',
  `accept_franchisee_id` int(11) DEFAULT NULL COMMENT '受理加盟商id',
  `accept_franchisee_name` varchar(255)  DEFAULT NULL COMMENT '受理加盟商名称',
  `sub_bill_code` varchar(60)  DEFAULT NULL COMMENT '快递柜code码',
  `staff_name` varchar(50)  DEFAULT NULL COMMENT '派件员',
  `accept_network_mr_code` varchar(10)  DEFAULT NULL COMMENT '受理网点管理大区编号',
  `accept_network_mr_name` varchar(10)  DEFAULT NULL COMMENT '受理网点管理大区名称',
  `resp_network_mr_code` varchar(10)  DEFAULT NULL COMMENT '责任网点管理大区编号',
  `resp_network_mr_name` varchar(10)  DEFAULT NULL COMMENT '责任网点管理大区名称',
  `reminders_status` tinyint(1) DEFAULT '2' COMMENT '是否催单 1 是 2 否 ',
  `reminders_num` tinyint(1) DEFAULT '0' COMMENT '催单次数',
  `order_source_name` varchar(60)  DEFAULT '' COMMENT '订单来源名称',
  `order_source_code` varchar(20)  DEFAULT '' COMMENT '订单来源编码',
  `is_call` tinyint(1) NOT NULL DEFAULT '2' COMMENT '是否存在外呼 1：存在 2:不存在',
  `call_num` smallint(6) NOT NULL DEFAULT '0' COMMENT '外呼次数',
  `task_id` varchar(64)  DEFAULT NULL COMMENT '菜鸟工单任务id',
  `task_name` varchar(128)  DEFAULT NULL COMMENT '菜鸟工单任务名称',
  `work_order_type` tinyint(1) DEFAULT NULL COMMENT '菜鸟工单类型,1-投诉单,2-咨询单',
  `cainiao_first_reply_sign` tinyint(1) DEFAULT '0' COMMENT '菜鸟工单首响回复类型,0、未回复  1、已回复',
  `responsibility_network_code` varchar(64)  DEFAULT NULL COMMENT '责任网点编码',
  `accept_network_code` varchar(64)  DEFAULT NULL COMMENT '受理网点编码',
  `provider_id` int(11) DEFAULT NULL COMMENT '受理网点省份id',
  `provider_desc` varchar(60)  DEFAULT NULL COMMENT '受理网点省份名称',
  `city_id` int(11) DEFAULT NULL COMMENT '受理网点城市id',
  `city_desc` varchar(60)  DEFAULT NULL COMMENT '受理网点城市名称',
  `staff_code` varchar(30)  DEFAULT NULL COMMENT '派件员编码',
  `is_dispatcher` tinyint(1) DEFAULT '1' COMMENT '是否下发派件员 1未下发2已下发',
  `customer_evaluation` tinyint(3) DEFAULT NULL COMMENT '客户评价状态  4-已解决',
  `response_network_code` varchar(30)  DEFAULT NULL COMMENT '响应网点编码',
  `response_network_name` varchar(60)  DEFAULT NULL COMMENT '响应网点名称',
  `response_time` datetime DEFAULT NULL COMMENT '响应时间',
  `receiver_province_name` varchar(60)  DEFAULT NULL COMMENT '收件省份名称',
  `receiver_province_id` int(11) DEFAULT NULL COMMENT '收件省份id',
  `receiver_city_name` varchar(60)  DEFAULT NULL COMMENT '收件城市名称',
  `receiver_city_id` int(11) DEFAULT NULL COMMENT '收件城市id',
  `receiver_area_name` varchar(60)  DEFAULT NULL COMMENT '收件区域名称',
  `receiver_area_id` int(11) DEFAULT NULL COMMENT '收件区域id',
  `accept_network_type_id` int(11) DEFAULT NULL COMMENT '受理网点类型ID',
  `accept_agency_network_code` varchar(30)  DEFAULT NULL COMMENT '受理网点代理区编码',
  `accept_virtual_proxy_code` varchar(30)  DEFAULT NULL COMMENT '受理网点所属虚拟代理区编码',
  `accept_virtual_proxy_name` varchar(60)  DEFAULT NULL COMMENT '受理网点所属虚拟代理区名称',
  `close_time` datetime DEFAULT NULL COMMENT '二次关闭时间',
  `last_overtime_finish` tinyint(1) unsigned NOT NULL DEFAULT '0' COMMENT '二次超时完结        \r\n 0 否 1 是',
  `first_return_time` datetime DEFAULT NULL COMMENT '首次退回时间',
  `station_status` tinyint(1) NOT NULL DEFAULT '1' COMMENT '驿站工单状态 1:未下发 2:已回复 3:已评价 默认1',
  `product_type` varchar(20)  DEFAULT NULL COMMENT '产品类型',
  `dl_customer_result` tinyint(1) DEFAULT NULL COMMENT '电联客户结果 1:客户电话已接通 2:客户电话未接通 3:未电联客户',
  `order_dl_result` tinyint(1) DEFAULT NULL COMMENT '工单电联结果 1:未接通-停机空号 2:未接通-无人接听 3:未接通-被叫拒绝 4:已接通',
  `dl_push_result` tinyint(1) DEFAULT NULL COMMENT '电联推送结果 1:是 2:否',
  `is_send_message` tinyint(1) NOT NULL DEFAULT '0' COMMENT '是否发送短信(0否 1是)',
  `resp_customer_code` varchar(30)  DEFAULT NULL COMMENT '首响客服编码',
  `resp_customer_name` varchar(60)  DEFAULT NULL COMMENT '首响客服名称',
  `station_business_id` varchar(20)  DEFAULT NULL COMMENT '驿站品牌id',
  `effective_resp_state` tinyint(1) DEFAULT NULL COMMENT '有效响应状态 1:有效响应 2:无效响应 3:尚未响应',
  `order_mark_code` varchar(200)  DEFAULT NULL COMMENT '订单标签编码',
  `order_mark_name` varchar(200)  DEFAULT NULL COMMENT '订单标签名称',
  `fast_claim_id` bigint(20) DEFAULT NULL COMMENT '极速理赔ID',
  `fast_claim_status` tinyint(2) DEFAULT NULL COMMENT '极速理赔状态 1:待审核 2:待付款 3:付款中 4:付款成功 5:付款失败 6:已驳回',
  `biz_line_id` bigint(20) DEFAULT NULL COMMENT '业务线id',
  `biz_line_name` varchar(64)  DEFAULT NULL COMMENT '业务线名称',
  `processing_timeliness` tinyint(2) DEFAULT '23' COMMENT '处理时效（H）',
  `exceed_process_time` datetime DEFAULT NULL COMMENT '超时效处理时间',
  `initiator_mobile_enc` varchar(200)  DEFAULT NULL COMMENT '发起人手机加密',
  `callback_contact_enc` varchar(200)  DEFAULT NULL COMMENT '反馈电话加密',
  `receiver_contact_enc` varchar(200)  DEFAULT NULL COMMENT '收件人电话加密',
  `is_first_duty` tinyint(2) DEFAULT NULL COMMENT '一次处理是否认责  1:是 2:否',
  `is_second_duty` tinyint(2) DEFAULT NULL COMMENT '二次处理是否申诉 1:是 2:否',
  `second_ruling` tinyint(2) DEFAULT NULL COMMENT '平台二次裁定结果 4 二次仲裁成立 5 二次仲裁不成立',
  `max_claim_amount` bigint(20) DEFAULT NULL COMMENT '最大理赔金额（单位分）',
  `warehouse_address` varchar(512)  DEFAULT NULL COMMENT '中转仓地址',
  `payment_type` tinyint(2) DEFAULT NULL COMMENT '支付类型 1:线上 2:线下',
  `early_warning_flag` tinyint(2) NOT NULL DEFAULT '2' COMMENT '是否预警 1-是 2-否 默认否',
  `first_close_customer_code` varchar(30)  DEFAULT NULL COMMENT '首次关闭客服编码',
  `first_close_customer_name` varchar(60)  DEFAULT NULL COMMENT '首次关闭客服名称',
  `sign_type` varchar(20)  DEFAULT NULL COMMENT '签收类型',
  `sign_time` varchar(30)  DEFAULT NULL COMMENT '运单签收时间',
  `sign_name` varchar(50)  DEFAULT NULL COMMENT '签收人',
  `platform_work_order_status` varchar(50)  DEFAULT NULL COMMENT '平台工单状态',
  `scan_time` datetime DEFAULT NULL COMMENT '最新扫描时间',
  `internal_problem_type_code` varchar(10)  DEFAULT NULL COMMENT '内部问题分类编码',
  `internal_problem_type_name` varchar(30)  DEFAULT NULL COMMENT '内部问题分类名称',
  `transfer_post_flag` tinyint(4) DEFAULT NULL COMMENT '是否转邮件 1：是 0：否',
  `town_send_flag` tinyint(4) DEFAULT NULL COMMENT '是否乡镇加时件 1：是 0：否',
  `exceed_response_time` datetime DEFAULT NULL COMMENT '超时响应时间',
  `is_send_sms_evaluation` tinyint(4) DEFAULT '2' COMMENT '是否满意度调研 1是2否',
  `sms_evaluation_result` varchar(10)  DEFAULT NULL COMMENT '满意度调研结果',
  `mark_time` datetime DEFAULT NULL COMMENT '标注时间',
  `visite_total` int(11) DEFAULT NULL COMMENT '来访次数',
  `first_close_customer_type` int(11) DEFAULT NULL COMMENT '首次关闭客服类型 1总部、2代理区、3网点客服、4共享客服',
  `first_close_network_code` varchar(30)  DEFAULT NULL COMMENT '首次关闭网点编码',
  `first_close_network_name` varchar(60)  DEFAULT NULL COMMENT '首次关闭网点名称',
  `agreement_customer_flag` tinyint(1) DEFAULT NULL COMMENT '协议客户标识：0否 1是',
  `headquarters_guarantee` tinyint(1) DEFAULT '0' COMMENT '是否总部兜底 0-否 1-是',
  `follow_order_remarks` json DEFAULT NULL COMMENT '跟单备注',
  `platform_assessment_amount` varchar(10)  DEFAULT NULL COMMENT '平台考核金额（单位元）',
  `is_auto_first_resp` tinyint(4) DEFAULT NULL COMMENT '是否自动首响（1是 2否）',
  `is_trigger_first_resp_backup` tinyint(4) DEFAULT NULL COMMENT '是否触发首响外呼兜底（1是 2否）',
  `is_first_resp_backup_connected` tinyint(4) DEFAULT NULL COMMENT '首响外呼兜底是否接通（1是 2否）')
```

## 常见生产ES结构-es

```sql
模板

pro_sqs_arbitration_template
{
    "order": 0,
    "index_patterns": [
        "pro_sqs_arbitration-*"
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
        "pro_sqs_arbitration": {
            "properties": {
                "third_confirm_status": {
                    "type": "integer"
                },
                "third_resp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "arbitration_auto_close_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "five_resp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_closed_last": {
                    "type": "integer"
                },
                "arbitrator_id": {
                    "type": "long"
                },
                "arbitration_receive_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "process_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "create_network_area": {
                    "type": "nested",
                    "properties": {
                        "code": {
                            "type": "keyword"
                        },
                        "networkCode": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "keyword"
                        },
                        "networkName": {
                            "type": "keyword"
                        },
                        "networkId": {
                            "type": "integer"
                        },
                        "id": {
                            "type": "integer"
                        }
                    }
                },
                "process_records": {
                    "type": "nested",
                    "properties": {
                        "createByName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "arbitrationId": {
                            "type": "long"
                        },
                        "verifyBeforeNetwork": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "processNetworkId": {
                            "type": "integer"
                        },
                        "verifyAfterNetwork": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "processOpinion": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "arbitrationCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "createBy": {
                            "type": "integer"
                        },
                        "createTime": {
                            "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                            "type": "date"
                        },
                        "paths": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "id": {
                            "type": "long"
                        },
                        "processType": {
                            "type": "integer"
                        },
                        "processNetworkCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "processNetworkName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                },
                "business_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_network_abnormal": {
                    "type": "integer"
                },
                "is_vip": {
                    "type": "integer"
                },
                "first_confirm_status": {
                    "type": "integer"
                },
                "first_comp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "four_resp_network_type_id": {
                    "type": "integer"
                },
                "first_type_id": {
                    "type": "long"
                },
                "return_user_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "subscribe_source_name": {
                    "type": "keyword"
                },
                "arbitration_award_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "collect_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_auto_crawl_real_resp_network_id": {
                    "type": "long"
                },
                "second_type_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "port_type": {
                    "type": "integer"
                },
                "second_type_id": {
                    "type": "long"
                },
                "third_resp_network_id": {
                    "type": "integer"
                },
                "process_user_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "networks": {
                    "type": "nested",
                    "properties": {
                        "arbitrationCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "parentName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "arbitrationId": {
                            "type": "long"
                        },
                        "parentCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "networkCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "networkName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "confirmStatus": {
                            "type": "integer"
                        },
                        "arbitrationParentCount": {
                            "type": "integer"
                        },
                        "networkId": {
                            "type": "integer"
                        },
                        "id": {
                            "type": "long"
                        },
                        "type": {
                            "type": "integer"
                        },
                        "parentId": {
                            "type": "integer"
                        }
                    }
                },
                "express_type_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "closing_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "second_auto_crawl_real_resp_network_id": {
                    "type": "long"
                },
                "four_resp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "update_by": {
                    "type": "long"
                },
                "second_resp_parent_id": {
                    "type": "integer"
                },
                "return_opinion": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "create_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_resp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_comp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_resp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_auto_crawl_real_resp_proxy_id": {
                    "type": "long"
                },
                "arb_labels": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "four_confirm_status": {
                    "type": "integer"
                },
                "payable_amount_total": {
                    "type": "double"
                },
                "trans_res_count": {
                    "type": "integer"
                },
                "four_resp_network_id": {
                    "type": "integer"
                },
                "customer_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_resp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "five_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "process_network_id": {
                    "type": "long"
                },
                "create_by_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_auto_crawl_real_resp_network_type_id": {
                    "type": "long"
                },
                "first_comp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "subscribe_source_code": {
                    "type": "keyword"
                },
                "second_auto_crawl_real_resp_network_code": {
                    "type": "keyword"
                },
                "second_resp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "goods_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "create_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "second_resp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_resp_network_type_id": {
                    "type": "integer"
                },
                "four_resp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_network_change": {
                    "type": "integer"
                },
                "five_resp_parent_id": {
                    "type": "integer"
                },
                "zy_dynamic_scan_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_auto_crawl_real_resp_proxy_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "five_confirm_status": {
                    "type": "integer"
                },
                "finance_status": {
                    "type": "integer"
                },
                "resp_network_areas": {
                    "type": "nested",
                    "properties": {
                        "code": {
                            "type": "keyword"
                        },
                        "networkCode": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "keyword"
                        },
                        "networkName": {
                            "type": "keyword"
                        },
                        "networkId": {
                            "type": "integer"
                        },
                        "id": {
                            "type": "integer"
                        }
                    }
                },
                "process_user_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "responsibility_reply_status": {
                    "type": "integer"
                },
                "first_error_desc": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "appeal_assign_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_comp_network_id": {
                    "type": "integer"
                },
                "project_assessment_value": {
                    "type": "double"
                },
                "delay_adju_status": {
                    "type": "integer"
                },
                "create_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "arbitrator_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "earliest_complaint_networks": {
                    "type": "nested",
                    "properties": {
                        "code": {
                            "type": "keyword"
                        },
                        "name": {
                            "type": "keyword"
                        },
                        "id": {
                            "type": "integer"
                        },
                        "type": {
                            "type": "integer"
                        }
                    }
                },
                "second_comp_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "process_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "arrival_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "settlement_status": {
                    "type": "integer"
                },
                "second_resp_network_id": {
                    "type": "integer"
                },
                "five_resp_network_id": {
                    "type": "integer"
                },
                "third_remark": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "appeal_adjudicator_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "ticket_id": {
                    "type": "long"
                },
                "delay_day": {
                    "type": "integer"
                },
                "is_package_inner_damage": {
                    "type": "integer"
                },
                "transfer_system_usage_fee": {
                    "type": "float"
                },
                "appeal_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "appeal_decision_network_id": {
                    "type": "long"
                },
                "first_auto_crawl_real_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "goods_value": {
                    "type": "double"
                },
                "push_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_comp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "third_resp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "appeal_reply_status": {
                    "type": "integer"
                },
                "first_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_resp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_resp_network_type_id": {
                    "type": "integer"
                },
                "arbitration_auto_receive_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "channel": {
                    "type": "integer"
                },
                "audit_status": {
                    "type": "integer"
                },
                "verify_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "arbitration_remark": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "return_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_comp_parent_id": {
                    "type": "integer"
                },
                "id": {
                    "type": "long"
                },
                "is_appeal_fee": {
                    "type": "integer"
                },
                "station_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_value_prove": {
                    "type": "integer"
                },
                "edit_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "is_packaging_standard": {
                    "type": "integer"
                },
                "order_source_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_auto_crawl_real_resp_proxy_code": {
                    "type": "keyword"
                },
                "create_by_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_renew_pod_track": {
                    "type": "integer"
                },
                "award_amount_total": {
                    "type": "double"
                },
                "appeal_adjudicator_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "five_resp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "push_pdd_status": {
                    "type": "integer"
                },
                "arb_behavior": {
                    "type": "integer"
                },
                "process_user_id": {
                    "type": "long"
                },
                "status": {
                    "type": "integer"
                },
                "second_comp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "end_status": {
                    "type": "integer"
                },
                "transfer_award_amount": {
                    "type": "float"
                },
                "arb_source": {
                    "type": "integer"
                },
                "shipment_no": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "just_allow_resp": {
                    "type": "long"
                },
                "arbitration_award_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "goods_type_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "update_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_type_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "suspected_resp": {
                    "type": "integer"
                },
                "arbitration_award_network_id": {
                    "type": "long"
                },
                "goods_type_id": {
                    "type": "long"
                },
                "redundancy": {
                    "type": "nested",
                    "properties": {
                        "arbSource": {
                            "type": "long"
                        },
                        "isPublicDistributionNetwork": {
                            "type": "long"
                        },
                        "expressTypeId": {
                            "type": "long"
                        },
                        "isValueProve": {
                            "type": "long"
                        },
                        "expressTypeName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "businessName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "expressTypeCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "arbSourceName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        },
                        "stationName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "valueProveName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "ignore_above": 256,
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                },
                "five_resp_network_type_id": {
                    "type": "integer"
                },
                "appeal_decision_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "return_user_id": {
                    "type": "long"
                },
                "restart_count": {
                    "type": "integer"
                },
                "update_by_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "transfer_resp_type": {
                    "type": "integer"
                },
                "appeal_decision_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "four_resp_parent_id": {
                    "type": "integer"
                },
                "second_auto_crawl_real_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "create_process_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "appeal_decision_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "appeal_adjudicator_id": {
                    "type": "long"
                },
                "first_auto_crawl_real_resp_network_code": {
                    "type": "keyword"
                },
                "third_resp_network_type_id": {
                    "type": "integer"
                },
                "assign_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_auto_crawl_real_resp_network_type_id": {
                    "type": "long"
                },
                "customer_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "third_resp_parent_id": {
                    "type": "integer"
                },
                "second_confirm_status": {
                    "type": "integer"
                },
                "five_resp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "responsibility_confirm_status": {
                    "type": "integer"
                },
                "adjudications": {
                    "type": "nested",
                    "properties": {
                        "createByName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "updateByName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "handlingFee": {
                            "type": "double"
                        },
                        "arbitrationId": {
                            "type": "long"
                        },
                        "updateTime": {
                            "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                            "type": "date"
                        },
                        "settlementNetworkId": {
                            "type": "integer"
                        },
                        "type": {
                            "type": "integer"
                        },
                        "payableAmount": {
                            "type": "double"
                        },
                        "responsibilityNetworkName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "settlementNetworkCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "arbitrationCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "createBy": {
                            "type": "integer"
                        },
                        "total": {
                            "type": "double"
                        },
                        "adjudicateNetworkId": {
                            "type": "integer"
                        },
                        "createTime": {
                            "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                            "type": "date"
                        },
                        "updateBy": {
                            "type": "integer"
                        },
                        "responsibilityNetworkCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "settlementNetworkName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "adjudicateNetworkCode": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "id": {
                            "type": "long"
                        },
                        "responsibilityNetworkId": {
                            "type": "integer"
                        },
                        "adjudicateOpinion": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        },
                        "adjudicateNetworkName": {
                            "type": "text",
                            "fields": {
                                "keyword": {
                                    "type": "keyword"
                                }
                            }
                        }
                    }
                },
                "is_public_distribution_network": {
                    "type": "integer"
                },
                "responsibility_reply_opinion": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "third_resp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "system_create_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_resp_parent_id": {
                    "type": "integer"
                },
                "order_source_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "goods_type_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "resp_network_num": {
                    "type": "integer"
                },
                "third_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "edit_count": {
                    "type": "integer"
                },
                "arbitrator_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "create_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_comp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_comp_network_id": {
                    "type": "integer"
                },
                "code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "process_deadline_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "update_by_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "create_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_appeal": {
                    "type": "integer"
                },
                "arbitration_award_network_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "exception_desc": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_comp_parent_id": {
                    "type": "integer"
                },
                "create_by": {
                    "type": "long"
                },
                "arbitration_reply_status": {
                    "type": "integer"
                },
                "express_type_id": {
                    "type": "integer"
                },
                "second_comp_parent_code": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "second_auto_crawl_real_resp_proxy_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "transfer_payable_amount": {
                    "type": "float"
                },
                "waybill_no": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "process_type": {
                    "type": "integer"
                },
                "first_auto_crawl_real_resp_proxy_code": {
                    "type": "keyword"
                },
                "handling_fee_total": {
                    "type": "double"
                },
                "revoke_time": {
                    "format": "yyyy-MM-dd HH:mm:ss||strict_date_optional_time||epoch_millis",
                    "type": "date"
                },
                "first_auto_crawl_real_resp_proxy_id": {
                    "type": "long"
                },
                "four_resp_network_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "system_usage_fee_second": {
                    "type": "integer"
                },
                "create_parent_id": {
                    "type": "long"
                },
                "four_resp_parent_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "first_resp_network_id": {
                    "type": "integer"
                },
                "return_user_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "express_type_name": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_first_error": {
                    "type": "integer"
                },
                "second_type": {
                    "type": "text",
                    "fields": {
                        "keyword": {
                            "type": "keyword"
                        }
                    }
                },
                "is_package_inner_lost": {
                    "type": "integer"
                },
                "push_pdd_fail_msg": {
                    "type": "keyword"
                },
                "create_network_id": {
                    "type": "long"
                }
            }
        }
    },
    "aliases": {
        "pro_sqs_arbitration": {}
    }
}









非模板es

PUT /pro_css_operation_guide_config
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
        "create_time": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "deleted": {
          "type": "integer"
        },
        "firstTypeCode": {
          "type": "keyword"
        },
        "firstTypeName": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "first_type_code": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "first_type_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "guideCode": {
          "type": "keyword"
        },
        "guideName": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "guide_code": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "guide_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "guide_status": {
          "type": "keyword"
        },
        "id": {
          "type": "long"
        },
        "secondTypeCode": {
          "type": "keyword"
        },
        "secondTypeName": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "second_type_code": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "second_type_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "updateByCode": {
          "type": "keyword"
        },
        "updateByCodeName": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "updateByName": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "updateTime": {
          "type": "date",
          "format": "strict_date_optional_time||yyyy-MM-dd HH:mm:ss||yyyy-MM-dd'T'HH:mm:ss||epoch_millis"
        },
        "updateTimestamp": {
          "type": "long"
        },
        "update_by_code": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "update_by_code_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "update_by_name": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "update_time": {
          "type": "text",
          "fields": {
            "keyword": {
              "type": "keyword",
              "ignore_above": 256
            }
          }
        },
        "workOrderType": {
          "type": "integer"
        },
        "work_order_type": {
          "type": "long"
        }
      }
    }
  }
}




```
