# yl-jms-sqs-online-api 项目框架文档

## 一、项目简介

这是一个**在线客服系统 (Online Customer Service System)**，提供客户与客服的实时聊天、机器人自动回复、会话管理、知识库、流程引擎等核心功能。

### 核心能力

| 能力 | 描述 |
|------|------|
| 实时聊天 | WebSocket 实现客户与客服的双向通信 |
| 机器人回复 | AI 机器人自动应答，支持 Coze/Dify 集成 |
| 会话管理 | 会话分配、排队、转接、结束全流程 |
| 知识库 | 知识分类、问答管理、智能匹配 |
| 流程引擎 | 可配置的业务流程节点编排 |
| 多渠道接入 | 支持淘天等第三方渠道 |

### 技术栈

| 类型 | 技术 |
|------|------|
| 基础框架 | Spring Boot 2.3.12 + Spring Cloud Hoxton.SR9 |
| ORM | MyBatis-Plus 3.5.3.1 |
| 数据库 | MySQL 8.0 + ShardingSphere 5.4.1 |
| 缓存 | Redis + Redisson |
| 消息队列 | RabbitMQ + RocketMQ |
| 配置中心 | Apollo 1.4.0 |
| 服务治理 | Eureka + OpenFeign + Hystrix |
| 定时任务 | XXL-Job 2.3.0 |
| 监控 | Prometheus + Sleuth |
| AI 集成 | Coze API + Dify Java Client |

---

## 二、项目模块

### 2.1 模块架构图

```
yl-jms-sqs-online-api
├── controller/          # 控制器层 - 接收 HTTP 请求
├── service/             # 服务层 - 业务逻辑处理
│   ├── assistant/       # AI 助手模块
│   ├── knowledge/       # 知识库模块
│   └── process/         # 流程处理模块
├── mapper/              # 数据访问层 - MyBatis Mapper
│   ├── assistant/
│   ├── knowledge/
│   └── process/
├── model/               # 数据模型
│   ├── entity/          # 实体类
│   ├── dto/             # 数据传输对象
│   ├── vo/              # 视图对象
│   └── enums/           # 枚举类
├── feign/               # 远程服务调用
├── cache/               # 缓存管理
├── task/                # 定时任务
├── listener/            # 消息监听器
├── stream/              # Spring Cloud Stream
├── websocket/           # WebSocket 通信
├── aop/                 # AOP 切面
├── config/              # 配置类
├── base/                # 基础组件
└── util/                # 工具类
```

---

## 三、各模块详细说明

### 3.1 Controller 层

| 类名 | 路径 | 功能 | 主要接口方法 |
|------|------|------|-------------|
| `AgentController` | `controller/AgentController.java` | 客服代理接口 | 会话管理、消息收发、状态变更 |
| `UserController` | `controller/UserController.java` | 用户接口 | 用户登录、认证、信息查询 |
| `RobotController` | `controller/RobotController.java` | 机器人接口 | 机器人对话、配置管理 |
| `GuideController` | `controller/GuideController.java` | 引导页接口 | 引导配置、欢迎语、公告 |
| `NotifyController` | `controller/NotifyController.java` | 通知接口 | 系统通知、消息推送 |
| `CustomerNotifyController` | `controller/CustomerNotifyController.java` | 客户通知接口 | 客户端消息通知 |
| `ThirdApiController` | `controller/ThirdApiController.java` | 第三方API接口 | 外部系统对接 |

#### 调用链路示例

```
HTTP Request -> Controller -> Service -> Mapper -> Database
                        ↓
                      Cache (Redis)
                        ↓
                      Feign Client -> External Service
```

---

### 3.2 Service 层

#### 4.2.1 核心业务 Service

| 接口名 | 实现类 | 功能 | 主要方法 | 调用链路 |
|--------|--------|------|----------|----------|
| `CustomerSessionService` | `CustomerSessionServiceImpl` | 客户会话管理 | `createSession`, `endSession`, `transferSession` | Controller → Service → CustomerSessionMapper → DB |
| `CustomerService` | `CustomerServiceImpl` | 客户信息管理 | `getCustomer`, `saveCustomer`, `updateCustomer` | Controller → Service → CustomerMapper → DB |
| `CustomerChatRecordService` | `CustomerChatRecordServiceImpl` | 聊天记录管理 | `saveRecord`, `queryRecords`, `syncRecords` | Controller → Service → CustomerChatRecordMapper → DB |
| `UserService` | `UserServiceImpl` | 客服用户管理 | `login`, `logout`, `getUserInfo` | Controller → Service → UserMapper → DB |
| `UserOnlineStateService` | `UserOnlineStateServiceImpl` | 在线状态管理 | `updateState`, `getOnlineAgents` | Controller → Service → UserOnlineStateMapper → DB |
| `AgentLoginService` | `AgentLoginServiceImpl` | 客服登录服务 | `login`, `heartbeat`, `reconnect` | AgentController → Service → UserMapper/Cache |
| `AgentConnectService` | `AgentConnectServiceImpl` | 客服连接服务 | `connect`, `disconnect`, `changeStatus` | WebSocket → Service → Cache |
| `RobotService` | `RobotServiceImpl` | 机器人服务 | `chat`, `matchKnowledge`, `autoReply` | RobotController → Service → CozeService/DifyService |
| `SessionProcessService` | `SessionProcessServiceImpl` | 会话流程服务 | `startProcess`, `nextNode`, `endProcess` | Controller → Service → ProcessService |
| `SessionAllocationService` | `SessionAllocationServiceImpl` | 会话分配服务 | `allocateSession`, `queueSession` | Service → Service → SkillGroupService |
| `SessionQueueService` | `SessionQueueServiceImpl` | 会话排队服务 | `enqueue`, `dequeue`, `getQueueInfo` | Service → Service → QueueSessionCache |
| `SessionEndService` | `SessionEndServiceImpl` | 会话结束服务 | `endSession`, `evaluate`, `statistics` | Service → Service → SessionStatisticsMapper |
| `MessageSendService` | `MessageSendServiceImpl` | 消息发送服务 | `sendMessage`, `sendToAgent`, `sendToCustomer` | Controller → Service → WebSocket/Cache |
| `TransferAgentService` | `TransferAgentServiceImpl` | 转接客服服务 | `transfer`, `getAvailableAgents` | Service → Service → SkillGroupService |
| `InboxService` | `InboxServiceImpl` | 收件箱服务 | `getMessages`, `markRead` | Controller → Service → InboxMapper |
| `ThirdApiService` | `ThirdApiServiceImpl` | 第三方API服务 | `handleCallback`, `pushMessage` | ThirdApiController → Service → FeignClient |

#### 4.2.2 Knowledge 子模块

| 接口名 | 实现类 | 功能 | 主要方法 | 调用链路 |
|--------|--------|------|----------|----------|
| `KnowledgeService` | `KnowledgeServiceImpl` | 知识综合服务 | `search`, `match`, `hit` | RobotService → KnowledgeService → Mapper |
| `KnowledgeBaseService` | `KnowledgeBaseServiceImpl` | 知识库管理 | `createBase`, `updateBase`, `deleteBase` | Controller → Service → KnowledgeBaseMapper |
| `KnowledgeClassifyService` | `KnowledgeClassifyServiceImpl` | 知识分类管理 | `addClassify`, `moveClassify` | Service → Service → KnowledgeClassifyMapper |
| `KnowledgeHitService` | `KnowledgeHitServiceImpl` | 知识命中统计 | `recordHit`, `getHitStats` | Service → Service → KnowledgeHitMapper |
| `KnowledgeRootService` | `KnowledgeRootServiceImpl` | 知识根管理 | `createRoot`, `updateRoot` | Service → Service → KnowledgeRootMapper |
| `KnowledgeAnswerService` | `KnowledgeAnswerServiceImpl` | 知识答案管理 | `addAnswer`, `updateAnswer` | Service → Service → KnowledgeAnswerMapper |

#### 4.2.3 Process 子模块

| 接口名 | 实现类 | 功能 | 主要方法 | 调用链路 |
|--------|--------|------|----------|----------|
| `ProcessService` | `ProcessServiceImpl` | 流程管理 | `createProcess`, `executeProcess` | Controller → Service → ProcessMapper |
| `ProcessNodeService` | `ProcessNodeServiceImpl` | 流程节点管理 | `addNode`, `executeNode`, `nextNode` | ProcessService → ProcessNodeService → Mapper |
| `RobotBlackListVerificationService` | `RobotBlackListVerificationServiceImpl` | 黑名单验证 | `verify`, `addToBlackList` | RobotService → Service → Cache |

#### 4.2.4 Assistant 子模块

| 接口名 | 实现类 | 功能 | 主要方法 | 调用链路 |
|--------|--------|------|----------|----------|
| `IAiPromptService` | `AiPromptServiceImpl` | AI提示词服务 | `getPrompt`, `buildPrompt` | RobotService → Service → Config |
| `IIntentionConfigurationService` | `IntentionConfigurationServiceImpl` | 意图配置服务 | `recognizeIntent`, `matchIntent` | RobotService → Service → Mapper |

#### 4.2.5 其他重要 Service

| 接口名 | 实现类 | 功能 |
|--------|--------|------|
| `CozeService` | `CozeServiceImpl` | Coze AI 服务对接 |
| `ChatBotKnowledgeService` | `ChatBotKnowledgeServiceImpl` | 聊天机器人知识服务 |
| `GuideTabService` | `GuideTabServiceImpl` | 引导标签页服务 |
| `GuideWelcomeService` | `GuideWelcomeServiceImpl` | 引导欢迎服务 |
| `GuideNoticeService` | `GuideNoticeServiceImpl` | 引导公告服务 |
| `GuideHintCardService` | `GuideHintCardServiceImpl` | 引导提示卡服务 |
| `GuideQuickChannelService` | `GuideQuickChannelServiceImpl` | 引导快捷通道服务 |
| `EvaluationTagService` | `EvaluationTagServiceImpl` | 评价标签服务 |
| `CustomerEvaluationService` | `CustomerEvaluationServiceImpl` | 客户评价服务 |
| `QuickReplyService` | `QuickReplyServiceImpl` | 快捷回复服务 |
| `SensitiveWordsService` | `SensitiveWordsServiceImpl` | 敏感词服务 |
| `SkillGroupService` | `SkillGroupServiceImpl` | 技能组服务 |
| `ServiceProviderService` | `ServiceProviderServiceImpl` | 服务商服务 |
| `ServiceConfigService` | `ServiceConfigServiceImpl` | 服务配置服务 |

---

### 3.3 Mapper 层

#### 4.3.1 核心 Mapper

| Mapper 接口 | XML 映射文件 | 关联实体 | 主要 SQL 操作 |
|-------------|--------------|----------|---------------|
| `CustomerSessionMapper` | `CustomerSessionMapper.xml` | `CustomerSession` | 会话 CRUD、状态更新、统计查询 |
| `CustomerChatRecordMapper` | `CustomerChatRecordMapper.xml` | `CustomerChatRecord` | 聊天记录保存、分页查询 |
| `CustomerMapper` | `CustomerMapper.xml` | `Customer` | 客户信息管理 |
| `CustomerEvaluationMapper` | `CustomerEvaluationMapper.xml` | `CustomerEvaluation` | 评价记录管理 |
| `UserMapper` | `UserMapper.xml` | `User` | 客服用户管理 |
| `UserOnlineStateMapper` | `UserOnlineStateMapper.xml` | `UserOnlineState` | 在线状态管理 |
| `UserSkillGroupMapper` | `UserSkillGroupMapper.xml` | `UserSkillGroup` | 用户技能组关联 |
| `SkillGroupMapper` | `SkillGroupMapper.xml` | `SkillGroup` | 技能组管理 |
| `SessionStatisticsMapper` | `SessionStatisticsMapper.xml` | `SessionStatistics` | 会话统计 |
| `InboxMapper` | `InboxMapper.xml` | `Inbox` | 收件箱管理 |
| `EvaluationTagMapper` | `EvaluationTagMapper.xml` | `EvaluationTag` | 评价标签 |
| `QuickReplyMapper` | `QuickReplyMapper.xml` | `QuickReply` | 快捷回复 |
| `SensitiveWordsMapper` | `SensitiveWordsMapper.xml` | `SensitiveWords` | 敏感词 |
| `RobotBaseConfigMapper` | `RobotBaseConfigMapper.xml` | `RobotBaseConfig` | 机器人基础配置 |
| `ServiceConfigMapper` | `ServiceConfigMapper.xml` | `ServiceConfig` | 服务配置 |

#### 4.3.2 Knowledge 子模块 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `KnowledgeMapper` | `Knowledge` | 知识综合查询 |
| `KnowledgeBaseMapper` | `KnowledgeBase` | 知识库管理 |
| `KnowledgeClassifyMapper` | `KnowledgeClassify` | 知识分类管理 |
| `KnowledgeRootMapper` | `KnowledgeRoot` | 知识根管理 |
| `KnowledgeAnswerMapper` | `KnowledgeAnswer` | 知识答案管理 |

#### 4.3.3 Process 子模块 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `ProcessMapper` | `Process` | 流程管理 |
| `ProcessNodeMapper` | `ProcessNode` | 流程节点管理 |
| `ProcessComplaintReasonMapper` | `ProcessComplaintReason` | 投诉原因管理 |

#### 4.3.4 Assistant 子模块 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `IntentionConfigurationMapper` | `IntentionConfiguration` | 意图配置管理 |

---

### 3.4 Feign 客户端 (远程服务调用)

#### 3.4.1 ChatBot 知识服务 (`ChatBotKnowledgeApiFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/sqsonlinechatbotapi/knowledge/im/match` | POST | 知识匹配 | 入参: `ChatBotKnowledgeMatchDTO`, 返回: `List<ChatBotKnowledgeMatchVO>` |
| `/sqsonlinechatbotapi/knowledge/im/add` | POST | 添加知识 | 入参: `ChatBotKnowledgeAddDTO`, 返回: `List<String>` |
| `/sqsonlinechatbotapi/knowledge/im/delete` | POST | 删除知识 | 入参: `List<String>`, 返回: `Boolean` |
| `/sqsonlinechatbotapi/knowledge/im/drop_index` | POST | 删除索引 | 入参: `db`, 返回: `Boolean` |

#### 3.4.2 CSS API 服务 (`CssApiFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/cssapi/phoneCall/callPhone` | POST | 企微报表异常告警-电话 | 入参: `PhoneCallDTO`, 返回: `Boolean` |
| `/cssapi/sysSensitiveWord/sensitiveVerification` | POST | 敏感词验证 | 入参: `Map<String, String>`, 返回: `Boolean` |
| `/cssapi/dispatcherWorkOrder/checkExist` | POST | 派送员工单校验存在 | 入参: `DispatcherWorkOrderCheckDTO`, 返回: `Boolean` |
| `/cssapi/networkAbnormalWaybill/checkIsTimeDelayByWaybill` | POST | 校验运单是否时效顺延 | 入参: `ExceptionDTO`, 返回: `Boolean` |
| `/cssapi/networkAbnormalWaybill/isExceptionWaybill` | GET | 是否异常运单 | 入参: `waybillNo`, 返回: `SecondaryAbnormalWaybillNoVO` |

#### 3.4.3 客户细分服务 (`SysCustomerNicheFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/customerapi/niche/addH5` | POST | H5添加商机客户 | 入参: `SysCustomerNicheAddDTO`, 返回: `SysCustomerNicheQueryVO` |
| `/customerapi/niche/selectNicheByMobile` | POST | 手机号查询商机信息 | 入参: `SysCustomerNichePageDTO`, 返回: `List<SysCustomerNicheQueryAllVO>` |

#### 3.4.4 MS 渠道服务 (`MSChannelFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/channelapi/api/wx/getMobileByOpenid` | GET | 根据OpenId获取手机号 | 入参: `openid`, 返回: `String` |

#### 3.4.5 网络服务 (`NetworkFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/networkapi/web/servicequality/network/getNetworkAndUpperById` | GET | 根据ID查询网点及上级 | 入参: `id`, 返回: `SqGetNetworkAndUpperVO` |
| `/networkapi/web/servicequality/network/getNetworkAndUpperByCode` | GET | 根据Code查询网点及上级 | 入参: `code`, 返回: `SqGetNetworkAndUpperVO` |
| `/networkapi/web/servicequality/network/getNetworkAgentByCodes` | POST | 查询虚拟代理区 | 入参: `List<String>`, 返回: `List<SqNetworkAgentVO>` |
| `/networkapi/web/servicequality/network/getNetworkByCode` | GET | 查询网点信息 | 入参: `code`, 返回: `SqNetworkVO` |
| `/networkapi/web/css/network/getDetailById` | GET | 根据ID获取网点详情 | 入参: `id`, 返回: `SqNetworkVO` |
| `/networkapi/web/servicequality/staff/getStaffPhoneByCodes` | POST | 收派员手机号查询 | 入参: `List<String>`, 返回: `List<SqStaffVO>` |

#### 3.4.6 运营服务 (`OpsFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/ops/pod/opsPodTracking/qos/keywordList` | POST | 批量查询物流轨迹-内部 | 入参: `PodTrackingInnerQueryDTO`, 返回: `List<PodTrackingListVO>` |
| `/ops/pod/opsPodTracking/outer/qos/keywordList` | POST | 批量查询物流轨迹-外部 | 入参: `List<String>`, 返回: `List<PodTrackingListVO>` |

#### 3.4.7 运营查询服务 (`OpsQueryFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/scanquery/external/search/fwzl/getZysmAndXzfjByWaybillNo` | POST | 批量查询物流轨迹(转运/下载) | 入参: `List<String>`, 返回: `List<ZysmAndXzfjByWaybillNoVO>` |

#### 3.4.8 订单查询服务 (`OrderQueryFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/order-query-api/waybill/queryOrderInfo` | POST | 根据运单号获取订单信息 | 入参: `QueryOrderInfoByWaybillDTO`, 返回: `List<OrderInfoQueryVO>` |
| `/order-query-api/sqs/orderQuery/queryOrderByWaybillIds` | POST | 根据运单ID批量查询订单 | 入参: `QueryOrderInfoByWaybillDTO`, 返回: `List<OrderInfoQueryVO>` |
| `/order-query-api/orderMarkExpand/queryOrderMark/{waybillNo}` | GET | 获取订单标记信息 | 入参: `waybillNo`, 返回: `List<OrderMarkVO>` |

#### 3.4.9 邮政组合信息服务 (`CombineInfoFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/csspostalapi/combineInfo/getHasPostalMap` | POST | 批量查询运单是否有工单 | 入参: `GetHasPostalMapDTO`, 返回: `Map<String, Boolean>` |

#### 3.4.10 QT 任务服务 (`TaskFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| 继承 `IEngineTaskFeignClient` | - | QT引擎任务服务 | 任务推送、查询 |

#### 3.4.11 短信服务 (`SmsSendFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/sms/v2/sendBatch` | POST | 发送短信 | 入参: `SmsSendDTO`, 返回: `SmsSendVO` |

#### 3.4.12 第三方服务回调 (`ThirdApiCallbackFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/sqsonlinethird/third/invoke/querySessionMessage` | POST | 查询访客与第三方机器人聊天记录 | 入参: `ThirdQuerySessionMsgDTO`, 返回: `List<ThirdCustomerChatRecordVO>` |
| `/sqsonlinethird/third/invoke/sendWorkOrderMessage` | POST | 发送工单消息 | 入参: `ThirdSendWorkOrderMessageDTO`, 返回: `Void` |
| `/sqsonlinethird/third/invoke/sendShopTaskMessage` | POST | 发送商家任务单消息 | 入参: `ThirdSendShopTaskMessageDTO`, 返回: `Void` |
| `/sqsonlinethird/third/invoke/sendTaoTianWorkOrder` | POST | 发送淘天工单 | 入参: `SqsTaoTianWorkOrderPushDTO`, 返回: `SqsTaoTianWorkOrderResultVO` |
| `/sqsonlinethird/third/invoke/sendTaoTianSessionDiagnosisResult` | POST | 发送淘天会话诊断结果 | 入参: `SqsTaoTianSessionDiagnosisResultPushDTO`, 返回: `SqsTaoTianWorkOrderResultVO` |

#### 3.4.13 运输服务 (`ShipmentFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/transportcooperate/shipmentstate/queryByShipmentNo` | GET | 根据运输单号查询状态 | 入参: `shipmentNo`, 返回: `ShipmentStateVO` |

#### 3.4.14 运单服务 (`WaybillFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/waybillouterapi/waybillDetailByNo` | GET | 根据运单号获取详情 | 入参: `waybillNo`, 返回: `OmsWaybillDetailVO` |
| `/waybillouterapi/common/get` | POST | 通用运单查询 | 入参: `WaybillDetailSearchDTO`, 返回: `OmsWaybillDetailVO` |
| `/waybillouterapi/css/getWaybillsByPhoneNum` | POST | 根据手机号查询运单列表 | 入参: `WaybillDetailByPhoneDTO`, 返回: `Page<WaybillDetailByPhoneVO>` |
| `/waybillouterapi/css/getWaybillsByPhoneNumNew` | POST | 根据手机号查询运单列表(新) | 入参: `WaybillDetailByPhoneDTO`, 返回: `Page<WaybillDetailByPhoneVO>` |

#### 3.4.15 工单服务 (`WorkOrderFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/cssworkorderapi/audioOrderInfo/queryByAudioIds` | GET | 根据录音ID查询工单 | 入参: `audioIds`, 返回: `List<AudioWorkOrderDTO>` |
| `/cssworkorderapi/audioOrderInfo/hasWorkOrder` | GET | 是否有工单操作 | 入参: `audioId`, 返回: `Boolean` |
| `/cssworkorderapi/workOrderInfo/information` | GET | 工单详情 | 入参: `workOrderNo`, 返回: `WorkOrderDetailDTO` |
| `/cssworkorderapi/workOrder/imSave` | POST | IM工单保存 | 入参: `IMWorkOrderAddDTO`, 返回: `Boolean` |
| `/cssworkorderapi/workOrder/save` | POST | 录单/问题记录保存 | 入参: `WorkOrderAddDTO`, 返回: `Boolean` |
| `/cssworkorderapi/workOrderType/page/workOrderSecondType` | POST | 分页查询工单二级类型 | 入参: `WorkOrderTypeSecondSearchDTO`, 返回: `Page<WorkOrderTypeSecondVO>` |
| `/cssworkorderapi/workOrder/queryTransportation` | GET | 查询运输状态 | 入参: `waybillNo, historyType`, 返回: `TransportationStatusVO` |
| `/cssworkorderapi/workOrder/getRegularWorkOrder` | GET | 获取普通工单 | 入参: `waybillNo`, 返回: `List<WorkOrderProblemRecordVO>` |

#### 3.4.16 普通工单服务 (`WorkOrderClientFeign`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/cssworkorderapi/workOrder/getRegularWorkOrder` | GET | 获取普通工单 | 入参: `waybillNo`, 返回: `List<WorkOrderProblemRecordVO>` |

#### 3.4.17 项目工单服务 (`ProjectWorkOrderFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/platformorderapi/projectWorkOrder/getPlatformWorkOrder` | GET | 获取平台工单 | 入参: `waybillNo`, 返回: `List<WorkOrderProblemRecordVO>` |

#### 3.4.18 来电记录服务 (`CallRecordsFeign`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/sqsproblemapi/callRecords/getCallRecord` | POST | 查询来电记录 | 入参: `CallRecordsAddDTO`, 返回: `List<CallRecordsVO>` |
| `/sqsproblemapi/problemPiece/queryProblemPieceByWaybillNo` | GET | 根据运单号获取问题件记录 | 入参: `wayBillNo`, 返回: `List<ProblemPieceInfoVO>` |

#### 3.4.19 订单敏感信息服务 (`CcmOrderSensitiveFeignClient`)

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/ccmordersensitiveapi/order/sensitive/query` | POST | 订单敏感信息反查 | 入参: `OrderSensitiveQueryDTO`, 返回: `List<OrderSensitiveQueryVO>` |

---

### 3.5 Cache 缓存层

| 缓存类 | Redis Key 前缀 | 功能 | 过期策略 |
|--------|----------------|------|----------|
| `AgentSkillGroupCache` | `agent:skillgroup:` | 客服技能组缓存 | 定时刷新 |
| `AgentTokenCache` | `agent:token:` | 客服 Token 缓存 | 会话级 |
| `GuideFaqCache` | `guide:faq:` | 引导 FAQ 缓存 | 配置变更刷新 |
| `GuideHintCardCache` | `guide:hintcard:` | 引导提示卡缓存 | 配置变更刷新 |
| `GuideNoticeCache` | `guide:notice:` | 引导公告缓存 | 配置变更刷新 |
| `GuideQuickChannelCache` | `guide:quickchannel:` | 引导快捷通道缓存 | 配置变更刷新 |
| `GuideTabCache` | `guide:tab:` | 引导标签页缓存 | 配置变更刷新 |
| `GuideWelcomeCache` | `guide:welcome:` | 引导欢迎缓存 | 配置变更刷新 |
| `InboxCache` | `inbox:` | 收件箱缓存 | 消息级 |
| `KnowledgeBaseCache` | `knowledge:base:` | 知识库缓存 | 定时刷新 |
| `KnowledgeTopCache` | `knowledge:top:` | 知识置顶缓存 | 定时刷新 |
| `QueueSessionCache` | `queue:session:` | 队列会话缓存 | 会话级 |
| `RobotBaseConfigCache` | `robot:config:` | 机器人配置缓存 | 配置变更刷新 |
| `RobotEvaluationConfigCache` | `robot:evaluation:` | 机器人评价配置缓存 | 配置变更刷新 |
| `ServiceConfigCache` | `service:config:` | 服务配置缓存 | 配置变更刷新 |
| `ServiceNetworkCache` | `service:network:` | 服务网络缓存 | 定时刷新 |
| `UserOnlineCountCache` | `user:online:count:` | 用户在线计数缓存 | 实时更新 |
| `UserTokenCache` | `user:token:` | 用户 Token 缓存 | 会话级 |
| `WebsocketSessionCache` | `ws:session:` | WebSocket 会话缓存 | 连接级 |
| `SessionProcessCache` | `session:process:` | 会话流程缓存 | 会话级 |
| `UserPhoneVerifyCache` | `user:phone:verify:` | 用户手机验证缓存 | 验证码过期 |
| `AiWorkOrderRecommendContextCache` | `ai:workorder:context:` | AI 工单推荐上下文缓存 | 会话级 |

---

### 3.6 Task 定时任务

| 任务类 | Cron 表达式 | 功能 | 调用链路 |
|--------|-------------|------|----------|
| `AgentReconnectOvertimeTask` | 定时执行 | 客服重连超时检测 | Task → AgentConnectService → Cache |
| `AgentReplyOvertimeTask` | 定时执行 | 客服回复超时检测 | Task → CustomerSessionService → DB |
| `AgentSendMessageTimeoutTask` | 定时执行 | 客服发送消息超时检测 | Task → MessageSendService → Cache |
| `ClearTimeoutCache` | 定时执行 | 清理超时缓存 | Task → 多个 Cache 类 |
| `CustomerReplyRobotTimeoutTask` | 定时执行 | 客户回复机器人超时 | Task → RobotService → DB |
| `CustomerReplyTimeoutTask` | 定时执行 | 客户回复超时检测 | Task → CustomerSessionService → DB |
| `KnowledgeTopRefreshTask` | 定时执行 | 知识置顶刷新 | Task → KnowledgeTopCache |
| `PushQTRecordTask` | 定时执行 | 推送 QT 记录 | Task → QTTaskFeignClient |
| `QueuingAlarmTask` | 定时执行 | 排队告警 | Task → SessionQueueService → Notify |
| `SensitiveWordsInitTask` | 启动时执行 | 敏感词初始化 | Task → SensitiveWordsService → Cache |
| `SessionBatchUpdateDayCountTask` | 每日执行 | 会话统计日更新 | Task → SessionStatisticsMapper → DB |
| `SessionOnlineCountTask` | 定时执行 | 会话在线计数 | Task → UserOnlineCountCache |
| `SessionQueueAllocationTask` | 定时执行 | 会话排队分配 | Task → SessionAllocationService |
| `SessionQueueIndexTask` | 定时执行 | 会话排队索引 | Task → SessionQueueService |
| `SyncSession2EvaluateEndTypeTask` | 定时执行 | 同步会话评价结束类型 | Task → CustomerEvaluationMapper |
| `UserReconnectOvertimeTask` | 定时执行 | 用户重连超时检测 | Task → UserOnlineStateService |

---

### 3.7 WebSocket 模块

| 类名 | 功能 | 消息类型 |
|------|------|----------|
| `WebSocketConfig` | WebSocket 配置 | - |
| `AgentWebSocketHandler` | 客服端 WebSocket 处理 | 聊天消息、状态变更、心跳 |
| `CustomerWebSocketHandler` | 客户端 WebSocket 处理 | 聊天消息、心跳 |

#### WebSocket 消息流转

```
Client ↔ WebSocket Handler ↔ Service ↔ Mapper/Cache
                              ↓
                          Feign Client (外部服务)
```

---

### 3.8 AOP 切面

| 切面类 | 注解 | 功能 | 应用场景 |
|--------|------|------|----------|
| `DistributedLockAspect` | `@DistributedLock` | 分布式锁 | 防止并发操作 |
| `OperationLogAspect` | `@OperationLog` | 操作日志记录 | 关键操作审计 |
| `LogProcessorAspect` | `@LogProcessor` | 日志处理 | 方法调用日志 |

---

### 3.9 Listener 消息监听器

| 监听器类 | 消息源 | 功能 |
|----------|--------|------|
| RabbitMQ Listener | RabbitMQ | 接收 MQ 消息，触发业务处理 |
| RocketMQ Listener | RocketMQ | 接收 MQ 消息，触发业务处理 |

---

### 3.10 Stream 消息流

| Stream 类 | Channel | 功能 |
|-----------|---------|------|
| Spring Cloud Stream | RabbitMQ/RocketMQ | 消息生产与消费 |

---

## 五、配置文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| `pom.xml` | 根目录 | Maven 依赖配置 |
| `application.yaml` | `src/main/resources/` | Spring Boot 主配置 |
| `bootstrap.yml` | `src/main/resources/` | Spring Cloud 启动配置 |
| `logback-spring.xml` | `src/main/resources/` | Logback 日志配置 |
| `app.properties` | `src/main/resources/META-INF/` | 应用属性 |
| `mapper/*.xml` | `src/main/resources/mapper/` | MyBatis XML 映射 |

---

## 六、外部依赖服务

### 6.1 AI 服务

| 服务名 | 客户端类 | 用途 | 主要接口 |
|--------|----------|------|----------|
| Coze AI | `CozeService` / `CozeServiceImpl` | AI 对话服务 | `chat` - AI 对话 |
| Dify | `DifyClient` | AI 对话服务 | `chat` - AI 对话 |

### 6.2 Feign 远程服务调用清单

| 序号 | 服务名 | 客户端类 | 接口数量 |
|------|--------|----------|----------|
| 1 | ChatBot 知识服务 | `ChatBotKnowledgeApiFeignClient` | 4 |
| 2 | CSS API 服务 | `CssApiFeignClient` | 5 |
| 3 | 客户细分服务 | `SysCustomerNicheFeignClient` | 2 |
| 4 | MS 渠道服务 | `MSChannelFeignClient` | 1 |
| 5 | 网络服务 | `NetworkFeignClient` | 6 |
| 6 | 运营服务 | `OpsFeignClient` | 2 |
| 7 | 运营查询服务 | `OpsQueryFeignClient` | 1 |
| 8 | 订单查询服务 | `OrderQueryFeignClient` | 3 |
| 9 | 邮政组合信息服务 | `CombineInfoFeignClient` | 1 |
| 10 | QT 任务服务 | `TaskFeignClient` | 继承自 `IEngineTaskFeignClient` |
| 11 | 短信服务 | `SmsSendFeignClient` | 1 |
| 12 | 第三方服务回调 | `ThirdApiCallbackFeignClient` | 5 |
| 13 | 运输服务 | `ShipmentFeignClient` | 1 |
| 14 | 运单服务 | `WaybillFeignClient` | 4 |
| 15 | 工单服务 | `WorkOrderFeignClient` | 8 |
| 16 | 普通工单服务 | `WorkOrderClientFeign` | 1 |
| 17 | 项目工单服务 | `ProjectWorkOrderFeignClient` | 1 |
| 18 | 来电记录服务 | `CallRecordsFeign` | 2 |
| 19 | 订单敏感信息服务 | `CcmOrderSensitiveFeignClient` | 1 |

> 详细接口地址和说明请参见 **3.4 Feign 客户端 (远程服务调用)** 章节

---

*文档更新时间: 2026-03-31 14:30:00*
