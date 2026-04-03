# yl-jms-sqs-online 项目框架文档

## 项目简介

这是一个**在线客服系统**,提供客服会话管理、知识库管理、智能机器人、报表统计、工单管理等核心功能。

### 核心能力

| 能力 | 描述 |
|------|------|
| 会话管理 | 客服会话全生命周期管理,包括会话分配、转接、结束等 |
| 知识库管理 | 知识库分类、知识点管理,支持多级分类和全文检索 |
| 智能机器人 | 机器人配置、自动回复、智能推荐等功能 |
| 报表统计 | 多维度报表统计,包括会话报表、客服绩效报表、机器人报表等 |
| 工单管理 | 工单创建、流转、处理全流程管理 |

### 技术栈

| 类型 | 技术 |
|------|------|
| 基础框架 | Spring Boot 2.3.1.RELEASE |
| 微服务框架 | Spring Cloud Hoxton.SR9 |
| ORM | MyBatis-Plus 3.5.3.1 |
| 数据库 | MySQL 8.0.32 |
| 缓存 | Redis (yl-redis 2.0.1-RELEASE) |
| 消息队列 | RocketMQ (yl-sqs-platform-rocketmq 2.0.1.0-RELEASE) + Spring Cloud Stream RabbitMQ |
| 配置中心 | Apollo 1.4.0 |
| 服务治理 | Eureka + Feign + Ribbon + Hystrix |
| 定时任务 | XXL-Job 2.3.0 |
| 监控 | Prometheus + Micrometer |
| 搜索引擎 | Elasticsearch 7.16.2 |
| 分库分表 | ShardingSphere 5.4.1 |
| 其他 | EasyExcel、Orika、MapStruct、Hutool、Guava |

---

## 项目模块

### 模块架构图

```
yl-jms-sqs-online
├── controller/           # 控制器层 - 接收 HTTP 请求
│   ├── assistant/       # AI 助手相关接口
│   ├── knowledge/       # 知识库管理接口
│   ├── process/         # 流程配置接口
│   ├── quickphrases/    # 快捷短语接口
│   └── report/          # 报表统计接口
├── service/              # 服务层 - 业务逻辑处理
│   ├── impl/            # 服务实现
│   ├── assistant/       # AI 助手服务
│   ├── knowledge/       # 知识库服务
│   ├── process/         # 流程服务
│   ├── quickphrases/    # 快捷短语服务
│   ├── report/          # 报表服务
│   └── hotlinerobot/    # 热线机器人服务
├── mapper/               # 数据访问层 - 数据库操作
│   ├── assistant/       # AI 助手 Mapper
│   ├── knowledge/       # 知识库 Mapper
│   ├── process/         # 流程 Mapper
│   ├── quickphrases/    # 快捷短语 Mapper
│   ├── report/          # 报表 Mapper
│   └── robot/           # 机器人 Mapper
├── model/                # 数据模型层
│   ├── entity/          # 实体类
│   │   ├── assistant/   # AI 助手实体
│   │   ├── knowledge/   # 知识库实体
│   │   ├── process/     # 流程实体
│   │   ├── report/      # 报表实体
│   │   └── robot/       # 机器人实体
│   ├── dto/             # 数据传输对象(入参)
│   ├── vo/              # 视图对象(出参)
│   └── enums/           # 枚举类
├── feign/                # 远程服务调用 - Feign 客户端
│   ├── bpo/             # BPO 服务
│   ├── chatbot/         # 聊天机器人服务
│   ├── network/         # 网点服务
│   ├── ops/             # OPS 服务
│   └── order/           # 订单服务
├── task/                 # 定时任务层 - XXL-Job 任务
│   └── report/          # 报表相关定时任务
├── stream/               # 消息流层 - Spring Cloud Stream
│   ├── MessageProducer  # 消息生产者
│   └── MessageReceiver  # 消息消费者
├── aop/                  # AOP 切面
│   ├── annotation/      # 自定义注解
│   └── aspect/          # 切面实现
├── config/               # 配置类
├── base/                 # 基础组件
│   ├── config/          # 基础配置
│   ├── constant/        # 常量定义
│   ├── enums/           # 基础枚举
│   ├── filter/          # 过滤器
│   ├── model/           # 基础模型
│   └── util/            # 工具类
└── constants/            # 业务常量

说明:
- 项目采用标准 Spring MVC 分层架构
- 支持多业务模块: AI 助手、知识库、流程配置、报表统计等
- 使用 Feign 进行微服务间调用
- 使用 XXL-Job 进行定时任务调度
- 使用 RocketMQ 进行异步消息处理
```

---

## 各模块详细说明

### Controller 层

#### 认证授权模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `AuthController` | `/auth` | 用户认证授权 | `/login` - 登录, `/permissions` - 获取权限列表 |
| `UserAuthenticationController` | `/userAuthentication` | 用户会话认证 | `/existToken` - Token验证, `/getUserSessionByToken` - 获取用户会话 |

#### 用户管理模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `UserController` | `/user` | 用户管理 | `/list` - 用户列表, `/add` - 新增用户, `/update` - 更新用户, `/roles` - 用户角色 |
| `RoleController` | `/role` | 角色管理 | 角色增删改查, 角色权限配置 |
| `ResourceController` | `/resource` | 资源权限管理 | 资源增删改查, 权限配置 |

#### 会话管理模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `CustomerSessionController` | `/customerSession` | 客服会话管理 | `/detail` - 会话详情, `/page` - 会话分页查询, `/phone/decrypt` - 手机号解密 |
| `CustomerChatRecordController` | `/customerChatRecord` | 聊天记录管理 | 聊天记录查询, 建议回复 |
| `SessionStatisticsController` | `/sessionStatistics` | 会话统计 | 会话数据统计 |

#### AI 助手模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `AiAssistantController` | `/aiAssistant` | AI 助手服务 | `/polish` - 文本润色, `/getSessionWorkOrderSuggest` - 工单建议, `/getSessionAiSummary` - AI 会话总结 |
| `AiWorkOrderSummaryRecordController` | `/aiWorkOrderSummaryRecord` | AI 工单总结记录 | 工单总结记录管理 |
| `AiWorkOrderRecommendRecordController` | `/aiWorkOrderRecommendRecord` | AI 工单推荐记录 | 工单推荐记录管理 |
| `IntentionConfigurationController` | `/intentionConfiguration` | 意图配置 | 意图识别配置管理 |
| `AiWorkOrderTypeConfigController` | `/ai/WorkOrderTypeConfig` | AI 工单类型配置 | 工单类型配置管理 |

#### 知识库模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `KnowledgeRootController` | `/knowledgeRoot` | 知识库根节点管理 | 知识库根节点增删改查 |
| `KnowledgeBaseController` | `/knowledgeBase` | 知识库管理 | 知识库增删改查 |
| `KnowledgeClassifyController` | `/knowledgeClassify` | 知识分类管理 | 知识分类增删改查 |
| `KnowledgeController` | `/knowledge` | 知识点管理 | 知识点增删改查 |

#### 流程配置模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `ProcessController` | `/process` | 流程管理 | 流程增删改查 |
| `ProcessNodeController` | `/processNode` | 流程节点管理 | 节点增删改查 |
| `ProcessComplaintReasonController` | `/processComplaintReason` | 投诉原因配置 | 投诉原因管理 |
| `RobotBaseConfigController` | `/robotBaseConfig` | 机器人基础配置 | 机器人配置管理 |
| `RobotBlackListConfigController` | `/robotBlackListConfig` | 机器人黑名单配置 | 黑名单增删改查 |
| `RobotEvaluationConfigController` | `/robotEvaluationConfig` | 机器人评价配置 | 评价配置管理 |

#### 引导配置模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `GuideController` | `/guide` | 引导配置(Tab+FAQ) | `/tab/add` - 新增Tab, `/faq/add` - 新增FAQ, `/faq/page` - FAQ分页 |
| `GuideWelcomeController` | `/guide/guideWelcome` | 欢迎语配置 | 欢迎语管理 |
| `GuideNoticeController` | `/guide/guideNotice` | 公告配置 | 公告增删改查 |
| `GuideHintCardController` | `/guide/guideHintCard` | 提示卡片配置 | 提示卡片管理 |
| `GuideQuickChannelController` | `/guideQuickChannel` | 快捷渠道配置 | 快捷渠道管理 |
| `GuideManualKeywordController` | `/guideManualKeyword` | 手动关键词配置 | 关键词管理 |

#### 报表统计模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `OverallServiceReportController` | `/overallServiceReport` | 整体服务报表 | `/page` - 分页查询, `/sum` - 汇总统计 |
| `PersonalReportController` | `/report/personal` | 个人报表 | 个人绩效统计 |
| `SessionReportController` | `/report/session` | 会话报表 | 会话数据统计 |
| `RobotSessionReportController` | `/report/robotSession` | 机器人会话报表 | 机器人会话统计 |
| `RobotChannelReportController` | `/report/robotChannel` | 机器人渠道报表 | 渠道数据统计 |
| `RobotHotQuestionReportController` | `/report/robotHotQuestion` | 机器人热门问题报表 | 热门问题统计 |
| `NetworkServiceReportController` | `/report/network` | 网点服务报表 | 网点数据统计 |
| `GroupOverallServiceReportController` | `/groupOverallServiceReport` | 团队整体服务报表 | 团队服务统计 |
| `GroupMonitorDashboardController` | `/groupMonitorDashboard` | 团队监控大屏 | 实时监控数据 |
| `ReportDayWeekMonthController` | `/report/dayWeekMonth` | 日报周报月报 | 周期性报表 |
| `ReportIncomingHourController` | `/report/incomingHour` | 进线小时报表 | 进线量统计 |
| `ReportWaybillRepeatSessionController` | `/report/repeat` | 重复进线报表 | 重复进线统计 |

#### 其他功能模块

| 类名 | 路径 | 功能 | 主要接口 |
|------|------|------|---------|
| `QuickReplyController` | `/quickReply` | 快捷回复管理 | 快捷回复增删改查 |
| `QuickPhrasesController` | `/quickPhrases` | 快捷短语管理 | 快捷短语增删改查 |
| `SensitiveWordsController` | `/sensitiveWords` | 敏感词管理 | 敏感词增删改查 |
| `CustomerSensitiveWordsController` | `/customerSensitiveWords` | 客户敏感词管理 | 客户敏感词管理 |
| `EvaluationTagController` | `/evaluationTag` | 评价标签管理 | 评价标签增删改查 |
| `EvaluateController` | `/evaluate/` | 评价管理 | 评价相关操作 |
| `SkillGroupController` | `/skillGroup` | 技能组管理 | 技能组增删改查 |
| `ServiceProviderController` | `/serviceProvider` | 服务商管理 | 服务商增删改查 |
| `ServiceProviderDiversionController` | `/serviceProviderDiversion` | 服务商分流配置 | 分流规则管理 |
| `ServiceConfigMgtController` | `/sessionServiceConfig/` | 服务配置管理 | 服务配置 |
| `HelpCenterController` | `/helpCenter` | 帮助中心 | 帮助中心管理 |
| `CustomerStaffManagerController` | `/customerStaffManager` | 客服人员管理 | 客服人员管理 |

#### 调用链路示例

```
HTTP Request -> Controller -> Service -> Mapper -> MySQL
                     ↓
                Redis Cache
                     ↓
               Feign Client -> 外部微服务
```

---

### Service 层

#### 认证授权 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `UserService` | `UserServiceImpl` | 用户管理服务 | `userLogin` - 用户登录, `getUserListByAccount` - 根据账号获取用户列表 |
| `UserRoleService` | `UserRoleServiceImpl` | 用户角色服务 | `getUserRoles` - 获取用户角色, `assignRoles` - 分配角色 |
| `ResourceService` | `ResourceServiceImpl` | 资源权限服务 | `getUserResources` - 获取用户资源权限 |
| `RoleResourceService` | `RoleResourceServiceImpl` | 角色资源服务 | `getRoleResources` - 获取角色资源 |

#### 会话管理 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `CustomerSessionService` | `CustomerSessionServiceImpl` | 会话管理服务 | `page` - 分页查询, `detail` - 会话详情, `sessionPhoneDecrypt` - 手机号解密 |
| `CustomerChatRecordService` | `CustomerChatRecordServiceImpl` | 聊天记录服务 | `getChatRecords` - 获取聊天记录, `suggestReply` - 建议回复 |
| `CustomerEvaluationService` | `CustomerEvaluationServiceImpl` | 客户评价服务 | `getEvaluations` - 获取评价列表 |
| `AgentStateFlowService` | `AgentStateFlowServiceImpl` | 客服状态流转服务 | `changeState` - 状态变更 |

#### AI 助手 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `IAiAssistantService` | `AiAssistantServiceImpl` | AI 助手服务 | `polish` - 文本润色, `getSessionWorkOrderSuggestVO` - 工单建议, `getSessionAiSummaryVO` - AI 总结 |
| `ISessionAiSummarizeService` | `SessionAiSummarizeServiceImpl` | 会话 AI 总结服务 | `summarizeSession` - 会话总结 |
| `IAiPromptService` | `AiPromptServiceImpl` | AI 提示词服务 | `getPrompt` - 获取提示词 |
| `CozeService` | `CozeServiceImpl` | Coze AI 服务 | `chat` - AI 对话 |
| `IAiWorkOrderTypeConfigService` | `AiWorkOrderTypeConfigServiceImpl` | AI 工单类型配置服务 | 工单类型配置管理 |
| `IIntentionConfigurationService` | `IntentionConfigurationServiceImpl` | 意图配置服务 | 意图识别配置管理 |
| `AiWorkOrderSummaryRecordService` | `AiWorkOrderSummaryRecordServiceImpl` | AI 工单总结记录服务 | 工单总结记录管理 |
| `IAiWorkOrderRecommendRecordService` | `AiWorkOrderRecommendRecordServiceImpl` | AI 工单推荐记录服务 | 工单推荐记录管理 |

#### 知识库 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `KnowledgeRootService` | `KnowledgeRootServiceImpl` | 知识库根节点服务 | 知识库根节点增删改查 |
| `KnowledgeBaseService` | `KnowledgeBaseServiceImpl` | 知识库服务 | 知识库增删改查 |
| `KnowledgeClassifyService` | `KnowledgeClassifyServiceImpl` | 知识分类服务 | 知识分类增删改查 |
| `KnowledgeService` | `KnowledgeServiceImpl` | 知识点服务 | 知识点增删改查 |
| `KnowledgeAnswerService` | `KnowledgeAnswerServiceImpl` | 知识答案服务 | 知识答案管理 |

#### 流程配置 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `ProcessService` | `ProcessServiceImpl` | 流程管理服务 | 流程增删改查 |
| `ProcessNodeService` | `ProcessNodeServiceImpl` | 流程节点服务 | 节点增删改查 |
| `IProcessComplaintReasonService` | `ProcessComplaintReasonServiceImpl` | 投诉原因服务 | 投诉原因管理 |
| `RobotBaseConfigService` | `RobotBaseConfigServiceImpl` | 机器人基础配置服务 | 机器人配置管理 |
| `RobotBlackListConfigService` | `RobotBlackListConfigServiceImpl` | 机器人黑名单服务 | 黑名单管理 |
| `RobotEvaluationConfigService` | `RobotEvaluationConfigServiceImpl` | 机器人评价配置服务 | 评价配置管理 |

#### 引导配置 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `GuideTabService` | `GuideTabServiceImpl` | 引导 Tab 服务 | Tab 增删改查 |
| `GuideFaqService` | `GuideFaqServiceImpl` | 引导 FAQ 服务 | FAQ 增删改查 |
| `GuideWelcomeService` | `GuideWelcomeServiceImpl` | 欢迎语服务 | 欢迎语管理 |
| `GuideNoticeService` | `GuideNoticeServiceImpl` | 公告服务 | 公告增删改查 |
| `GuideHintCardService` | `GuideHintCardServiceImpl` | 提示卡片服务 | 提示卡片管理 |
| `GuideQuickChannelService` | `GuideQuickChannelServiceImpl` | 快捷渠道服务 | 快捷渠道管理 |
| `GuideManualKeywordService` | `GuideManualKeywordServiceImpl` | 手动关键词服务 | 关键词管理 |

#### 报表统计 Service

| 接口名 | 实现类 | 功能 | 主要方法 |
|--------|--------|------|----------|
| `IOverallServiceReportService` | `OverallServiceReportServiceImpl` | 整体服务报表服务 | `page` - 分页查询, `sum` - 汇总统计 |
| `IPersonalReportService` | `PersonalReportServiceImpl` | 个人报表服务 | 个人绩效统计 |
| `GroupReportService` | `GroupReportServiceImpl` | 团队报表服务 | 团队绩效统计 |
| `IGroupOverallServiceReportService` | `GroupOverallServiceReportServiceImpl` | 团队整体服务报表服务 | 团队服务统计 |
| `GroupMonitoringDashboardService` | `GroupMonitoringDashboardServiceImpl` | 团队监控大屏服务 | 实时监控数据 |
| `AgentStateChangeLogService` | `AgentStateChangeLogServiceImpl` | 客服状态变更日志服务 | 状态变更记录 |
| `AgentStateDurationReportService` | `AgentStateDurationReportServiceImpl` | 客服状态时长报表服务 | 状态时长统计 |
| `ICustomerSessionQueueOverflowService` | `CustomerSessionQueueOverflowServiceImpl` | 会话排队溢出服务 | 排队溢出统计 |
| `GroupOverallServiceReportStageService` | `GroupOverallServiceReportStageServiceImpl` | 团队整体服务报表阶段服务 | 阶段数据统计 |

#### 其他重要 Service

| 接口名 | 实现类 | 功能 |
|--------|--------|------|
| `QuickReplyService` | `QuickReplyServiceImpl` | 快捷回复服务 |
| `SkillGroupService` | `SkillGroupServiceImpl` | 技能组服务 |
| `ServiceProviderService` | `ServiceProviderServiceImpl` | 服务商服务 |
| `ServiceProviderDiversionService` | `ServiceProviderDiversionServiceImpl` | 服务商分流服务 |
| `SensitiveWordsService` | `SensitiveWordsServiceImpl` | 敏感词服务 |
| `EvaluationTagService` | `EvaluationTagServiceImpl` | 评价标签服务 |
| `CustomerStaffManagerService` | `CustomerStaffManagerServiceImpl` | 客服人员管理服务 |
| `HotLineRobotService` | `HotLineRobotServiceImpl` | 热线机器人服务 |
| `FileService` | `FileServiceImpl` | 文件服务 |
| `FileApiService` | `FileApiServiceImpl` | 文件 API 服务 |
| `NetworkQueryService` | `NetworkQueryServiceImpl` | 网点查询服务 |
| `MonitorDashboardService` | `MonitorDashboardServiceImpl` | 监控大屏服务 |

---

### Mapper 层

#### 核心 Mapper

| Mapper 接口 | 关联实体 | 功能 | 主要 SQL 操作 |
|-------------|----------|------|---------------|
| `UserMapper` | `User` | 用户数据访问 | 用户增删改查, 用户角色关联 |
| `RoleMapper` | `Role` | 角色数据访问 | 角色增删改查 |
| `ResourceMapper` | `Resource` | 资源权限数据访问 | 资源增删改查 |
| `RoleResourceMapper` | `RoleResource` | 角色资源关联数据访问 | 角色资源关联查询 |
| `CustomerMapper` | `Customer` | 客户数据访问 | 客户增删改查 |
| `CustomerSessionMapper` | `CustomerSession` | 会话数据访问 | 会话增删改查, 会话统计 |
| `CustomerChatRecordMapper` | `CustomerChatRecord` | 聊天记录数据访问 | 聊天记录查询, 建议回复 |

#### AI 助手 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `AiWorkOrderSummaryRecordMapper` | `AiWorkOrderSummaryRecord` | AI 工单总结记录数据访问 |
| `AiWorkOrderRecommendRecordMapper` | `AiWorkOrderRecommendRecord` | AI 工单推荐记录数据访问 |
| `AiWorkOrderTypeConfigMapper` | `AiWorkOrderTypeConfig` | AI 工单类型配置数据访问 |
| `IntentionConfigurationMapper` | `IntentionConfiguration` | 意图配置数据访问 |
| `SessionAiSummarizeMapper` | `SessionAiSummarize` | 会话 AI 总结数据访问 |

#### 知识库 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `KnowledgeRootMapper` | `KnowledgeRoot` | 知识库根节点数据访问 |
| `KnowledgeBaseMapper` | `KnowledgeBase` | 知识库数据访问 |
| `KnowledgeClassifyMapper` | `KnowledgeClassify` | 知识分类数据访问 |
| `KnowledgeMapper` | `Knowledge` | 知识点数据访问 |
| `KnowledgeAnswerMapper` | `KnowledgeAnswer` | 知识答案数据访问 |

#### 流程配置 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `ProcessMapper` | `Process` | 流程数据访问 |
| `ProcessNodeMapper` | `ProcessNode` | 流程节点数据访问 |
| `ProcessComplaintReasonMapper` | `ProcessComplaintReason` | 投诉原因数据访问 |
| `RobotBaseConfigMapper` | `RobotBaseConfig` | 机器人基础配置数据访问 |
| `RobotBlackListConfigMapper` | `RobotBlackListConfig` | 机器人黑名单数据访问 |
| `RobotEvaluationConfigMapper` | `RobotEvaluationConfig` | 机器人评价配置数据访问 |

#### 引导配置 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `GuideFaqMapper` | `GuideFaq` | 引导 FAQ 数据访问 |
| `GuideHintCardMapper` | `GuideHintCard` | 提示卡片数据访问 |
| `GuideManualKeywordMapper` | `GuideManualKeyword` | 手动关键词数据访问 |
| `GuideNoticeMapper` | `GuideNotice` | 公告数据访问 |
| `GuideQuickChannelMapper` | `GuideQuickChannel` | 快捷渠道数据访问 |
| `GuideTabMapper` | `GuideTab` | 引导 Tab 数据访问 |
| `GuideWelcomeMapper` | `GuideWelcome` | 欢迎语数据访问 |

#### 报表统计 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `OverallServiceReportMapper` | `OverallServiceReport` | 整体服务报表数据访问 |
| `GroupOverallServiceReportMapper` | `GroupOverallServiceReport` | 团队整体服务报表数据访问 |
| `ReportPersonalMapper` | `ReportPersonal` | 个人报表数据访问 |
| `AgentStateChangeLogMapper` | `AgentStateChangeLog` | 客服状态变更日志数据访问 |
| `AgentStateDurationReportMapper` | `AgentStateDurationReport` | 客服状态时长报表数据访问 |
| `CustomerSessionQueueOverflowMapper` | `CustomerSessionQueueOverflow` | 会话排队溢出数据访问 |
| `ReportDayWeekMonthMapper` | `ReportDayWeekMonth` | 日报周报月报数据访问 |
| `ReportIncomingHourMapper` | `ReportIncomingHour` | 进线小时报表数据访问 |

#### 机器人相关 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `CustomerEvaluationMsgMapper` | `CustomerEvaluationMsg` | 客户评价消息数据访问 |
| `CustomerEvaluationRobotMapper` | `CustomerEvaluationRobot` | 客户评价机器人数据访问 |
| `RobotChannelReportMapper` | `RobotChannelReport` | 机器人渠道报表数据访问 |
| `RobotHotQuestionReportMapper` | `RobotHotQuestionReport` | 机器人热门问题报表数据访问 |
| `RobotSessionHitKnowledgeMapper` | `RobotSessionHitKnowledge` | 机器人会话命中知识数据访问 |
| `RobotSessionIndexDetailMapper` | `RobotSessionIndexDetail` | 机器人会话指标详情数据访问 |
| `RobotSessionWorkOrderMapper` | `RobotSessionWorkOrder` | 机器人会话工单数据访问 |
| `HelpCenterGroupMapper` | `HelpCenterGroup` | 帮助中心分组数据访问 |
| `HelpCenterQaMapper` | `HelpCenterQa` | 帮助中心问答数据访问 |

#### 其他 Mapper

| Mapper 接口 | 关联实体 | 功能 |
|-------------|----------|------|
| `QuickReplyMapper` | `QuickReply` | 快捷回复数据访问 |
| `SensitiveWordsMapper` | `SensitiveWords` | 敏感词数据访问 |
| `CustomerSensitiveWordsMapper` | `CustomerSensitiveWords` | 客户敏感词数据访问 |
| `EvaluationTagMapper` | `EvaluationTag` | 评价标签数据访问 |
| `SkillGroupMapper` | `SkillGroup` | 技能组数据访问 |
| `UserSkillGroupMapper` | `UserSkillGroup` | 用户技能组数据访问 |
| `ServiceProviderMapper` | `ServiceProvider` | 服务商数据访问 |
| `ServiceProviderChannelDiversionMapper` | `ServiceProviderChannelDiversion` | 服务商渠道分流数据访问 |
| `QuickPhrasesMapper` | `QuickPhrases` | 快捷短语数据访问 |
| `ServiceConfigMapper` | `ServiceConfig` | 服务配置数据访问 |

---

### Entity 实体类

#### 基础实体类

项目存在多个基础实体类,用于不同场景:

| 实体类 | 表名 | 说明 | 继承关系 |
|--------|------|------|----------|
| `Base` | - | 通用基础实体(包含审计字段) | `Model<T>` |
| `BaseId` | - | 简化基础实体(仅ID和时间) | `Model<T>` |
| `BaseEntity` | - | 完整基础实体(包含所有审计字段) | 无 |

**Base 字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `isDelete` | `Integer` | 删除标记 1:删除 2:正常 |
| `isEnable` | `Integer` | 是否启用:1启用,2不启用 |
| `createBy` | `String` | 创建人 code |
| `createByName` | `String` | 创建人名称 |
| `createTime` | `LocalDateTime` | 创建时间 |
| `updateBy` | `String` | 修改人 code |
| `updateByName` | `String` | 修改人名称 |
| `updateTime` | `LocalDateTime` | 更新时间 |

**BaseId 字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `createTime` | `LocalDateTime` | 创建时间 |
| `updateTime` | `LocalDateTime` | 更新时间 |

**BaseEntity 字段说明**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `createBy` | `Integer` | 创建人ID |
| `createByCode` | `String` | 创建人CODE |
| `createByName` | `String` | 创建人名称 |
| `updateBy` | `Integer` | 最后更新人ID |
| `updateByCode` | `String` | 最后更新人CODE |
| `updateByName` | `String` | 最后修改人名称 |
| `createTime` | `LocalDateTime` | 创建时间 |
| `updateTime` | `LocalDateTime` | 更新时间 |
| `isEnable` | `Integer` | 是否启用 1启用 2不启用 |
| `isDelete` | `Integer` | 是否删除 1未删除 2已删除 |

> 💡 **说明**: 项目中存在多个基础实体类,根据业务需求选择使用:
> - `Base`: 包含完整的审计字段,适用于需要完整审计追踪的场景
> - `BaseId`: 仅包含 ID 和时间字段,适用于简化场景
> - `BaseEntity`: 包含所有审计字段(包括 ID 和 Code),适用于需要详细审计的场景

---

#### 业务实体类

##### EntityName (表名: {{table_name}})

{{实体说明/功能描述}}

| 字段名 | 类型 | 说明 |
|--------|------|------|
| {{字段名}} | {{类型}} | {{说明}} |

---

### Feign 客户端 (远程服务调用)

#### 网点服务 (`NetworkFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylnetworkapi` |
| 路径前缀 | `/networkapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/web/servicequality/network/getNetworkAndUpperById` | GET | 根据网点ID查询网点及上级网点 | 入参: `id: Integer`, 返回: `Result<SqGetNetworkAndUpperVO>` |
| `/web/servicequality/staff/getStaffByCode` | GET | 根据员工code查询员工信息 | 入参: `staffCode: String`, 返回: `Result<SqStaffVO>` |
| `/web/css/network/getByIds` | POST | 批量查询网点对象 | 入参: `List<Integer>`, 返回: `Result<List<CssNetworkDetailVO>>` |
| `/web/servicequality/network/getNetworkByCode` | GET | 查询网点信息 | 入参: `code: String`, 返回: `Result<SqNetworkVO>` |

#### OPS 服务 (`OpsFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-jms-ops-pod-api` |
| 路径前缀 | `/ops/pod/opsPodTracking` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/qos/keywordList` | POST | 批量查询物流轨迹-内部 | 入参: `PodTrackingInnerQueryDTO`, 返回: `Result<List<PodTrackingListVO>>` |
| `/outer/qos/keywordList` | POST | 批量查询物流轨迹-外部 | 入参: `List<String>`, 返回: `Result<List<PodTrackingListVO>>` |

#### ChatBot 知识库服务 (`ChatBotKnowledgeApiFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `chatbotapi` |
| URL | `http://yl-jms-sqs-online-chatbot-api:8080` |
| 路径前缀 | `/sqsonlinechatbotapi/knowledge/im` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/match` | POST | 知识库匹配 | 入参: `ChatBotKnowledgeMatchDTO`, 返回: `Result<List<ChatBotKnowledgeMatchVO>>` |
| `/add` | POST | 新增知识 | 入参: `ChatBotKnowledgeAddDTO`, 返回: `Result<List<String>>` |
| `/delete` | POST | 删除知识 | 入参: `List<String>`, 返回: `Result<Boolean>` |
| `/drop_index` | POST | 删除索引 | 入参: `baseId: String`, 返回: `Result<Boolean>` |

#### 订单服务 (`OrderQueryFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-jms-workorder-api` |
| 路径前缀 | `/workorderapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/order/query` | POST | 订单查询 | 入参: `QueryOrderInfoByWaybillDTO`, 返回: `Result<OrderInfoQueryVO>` |
| `/callRecords/add` | POST | 新增通话记录 | 入参: `CallRecordsAddDTO`, 返回: `Result<CallRecordsVo>` |
| `/order/sensitive/query` | POST | 订单敏感信息查询 | 入参: `OrderSensitiveQueryDTO`, 返回: `Result<OrderSensitiveQueryVO>` |

#### BPO 用户服务 (`BpoUserFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-bpo-web-user` |
| 路径前缀 | `/user` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/getUserByCodes` | POST | 根据用户codes批量查询用户 | 入参: `List<String>`, 返回: `Result<List<OpsUserVO>>` |

#### CSS API 服务 (`CssApiFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-jms-css-api` |
| 路径前缀 | `/cssapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/sysSensitiveWord/page` | POST | 系统敏感词分页查询 | 入参: `SysSensitiveWordPageQueryDTO`, 返回: `Result<Page<SysSensitiveWordPageVO>>` |

#### 拼多多 IM 数据服务 (`PddImDataFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-jms-im-wechat-report` |
| 路径前缀 | `/imwechatreport` |

| 接口路径 | HTTP 方法 | 接口说明 | 参数/返回 |
|----------|-----------|----------|-----------|
| `/pdd/im/data` | POST | 拼多多 IM 数据上报 | 入参: `PddImDataDTO`, 返回: `Result<Boolean>` |

---

### Cache 缓存层

项目使用 Redis 作为缓存中间件,通过 `yl-redis` 组件进行封装。

| 缓存类 | Redis Key 前缀 | 功能 | 过期策略 |
|--------|----------------|------|----------|
| `LockAccountRedisUtil` | `lock:account:` | 账户锁定缓存 | 按需设置 |
| `RedisKeyEnum` | 多个前缀 | 枚举定义各类 Redis Key | 不同 Key 不同过期策略 |

**常用 Redis Key 前缀**:
- `sqs:session:` - 会话相关缓存
- `sqs:user:` - 用户相关缓存
- `sqs:network:` - 网点相关缓存
- `sqs:blacklist:` - 黑名单缓存
- `sqs:config:` - 配置缓存

---

### Task 定时任务

项目使用 XXL-Job 作为分布式定时任务调度框架。

#### 报表统计任务

| 任务类 | 功能 | 调度说明 |
|--------|------|----------|
| `OverallServiceReportTask` | 整体服务报表数据生成 | 定时统计整体服务数据 |
| `OverallServiceReportRefreshTask` | 整体服务报表数据刷新 | 定时刷新报表数据 |
| `OverallServiceReportDataImportGroupTableTask` | 整体服务报表数据导入团队表 | 定时导入数据 |
| `OverallServiceReportSyncBITask` | 整体服务报表同步到 BI | 定时同步数据到 BI 系统 |
| `ReportPersonalDataTask` | 个人报表数据生成 | 定时生成个人报表数据 |
| `ReportPersonalDayWeekMonthTask` | 个人日报周报月报数据生成 | 定时生成个人周期性报表 |
| `ReportPersonalChannelTask` | 个人渠道报表数据生成 | 定时生成个人渠道报表 |
| `ReportPersonalWorkOrderDayWeekMonthTask` | 个人工单日报周报月报数据生成 | 定时生成个人工单周期性报表 |
| `ReportDayWeekMonthTask` | 日报周报月报数据生成 | 定时生成周期性报表 |
| `ReportIncomingHourTask` | 进线小时报表数据生成 | 定时生成进线小时报表 |
| `ReportWaybillRepeatDayWeekMonthTask` | 重复进线报表数据生成 | 定时生成重复进线报表 |
| `ReportWaybillRepeatSessionDataNewTask` | 重复进线会话数据生成 | 定时生成重复进线会话数据 |
| `NetworkIndexReportTask` | 网点指标报表数据生成 | 定时生成网点指标报表 |

#### 数据刷新任务

| 任务类 | 功能 | 调度说明 |
|--------|------|----------|
| `RefreshReportDataTask` | 刷新报表数据 | 定时刷新报表数据 |
| `RefreshUserNetworkTask` | 刷新用户网点数据 | 定时刷新用户网点信息 |
| `RefreshUserRealNameTask` | 刷新用户真实姓名 | 定时刷新用户真实姓名 |
| `RefreshUserSumReceptionNumTask` | 刷新用户总接待数 | 定时刷新用户总接待数 |
| `RefreshServiceProviderPhoneTask` | 刷新服务商电话 | 定时刷新服务商电话 |
| `Refresh72HFCRTask` | 刷新 72 小时 FCR 数据 | 定时刷新 72 小时 FCR 数据 |
| `RefreshWaybillCollectionNodeConfigTask` | 刷新运单揽收网点配置 | 定时刷新运单揽收网点配置 |
| `RefreshBlackListInfoToRedisTask` | 刷新黑名单信息到 Redis | 定时刷新黑名单信息到 Redis |

#### 其他任务

| 任务类 | 功能 | 调度说明 |
|--------|------|----------|
| `Index24hFrcTask` | 24 小时 FCR 指标计算 | 定时计算 24 小时 FCR 指标 |
| `EvaltateTodayInitTask` | 今日评价初始化 | 定时初始化今日评价数据 |
| `KnowledgeDataPushChatBotTask` | 知识库数据推送到 ChatBot | 定时推送知识库数据到 ChatBot |
| `KnowledgeAnswerRefreshDataTask` | 知识库答案数据刷新 | 定时刷新知识库答案数据 |
| `ReportIndexDetailDataProcessTask` | 报表明细数据处理 | 定时处理报表明细数据 |
| `PlatformSessionAlarm` | 平台会话告警 | 监控平台会话并告警 |
| `RobotChannelReportTask` | 机器人渠道报表数据生成 | 定时生成机器人渠道报表 |
| `RobotHotQuestionReportTask` | 机器人热门问题报表数据生成 | 定时生成机器人热门问题报表 |
| `AgentStateReportTask` | 客服状态报表数据生成 | 定时生成客服状态报表 |
| `WorkOrderNumTask` | 工单数量统计 | 定时统计工单数量 |
| `ThirdSessionWaybillNoRefreshDataTask` | 第三方会话运单号数据刷新 | 定时刷新第三方会话运单号数据 |

---

### AOP 切面

| 切面类 | 注解 | 功能 | 应用场景 |
|--------|------|------|----------|
| `DistributedLockAspect` | `@DistributedLock` | 分布式锁切面 | 防止并发重复操作,保证数据一致性 |
| `LogProcessorAspect` | `@LogProcessor` | 日志处理切面 | 记录操作日志,审计追踪 |

**注解说明**:
- `@DistributedLock`: 用于需要分布式锁保护的方法,支持设置锁的 key、等待时间、超时时间等
- `@LogProcessor`: 用于需要记录操作日志的方法,支持自定义日志内容、操作类型等

---

### 消息中间件

#### RocketMQ

**概述**: 项目使用 **RocketMQ** 实现消息收发,使用 `yl-sqs-platform-rocketmq` 动态发布器。

| 配置项 | 说明 |
|--------|------|
| 框架 | RocketMQ |
| Starter | yl-sqs-platform-rocketmq 2.0.1.0-RELEASE |
| Name Server | 从配置文件获取 |

**Topic 动态发布器**:

| Topic 名称 | Tag | 发布器类 | 调用位置 | 消息类型 | 说明 |
|------------|-----|----------|----------|----------|------|
| `sqs-online-related-information-result` | - | `RocketMQDynamicPublisher` | `MessageProducer.sendSessionRelatedInformation()` | `SessionRelatedInformationVO` | 发送会话指标计算数据 |
| `sqs-online-create-close-evaluation-result` | - | `RocketMQDynamicPublisher` | `MessageProducer.sendSessionEventMessage()` | `SessionMessageVO` | 发送会话事件消息(会话创建、会话关闭、会话评价) |
| `sqs-online-chat-bot-knowledge` | - | `RocketMQDynamicPublisher` | `MessageProducer.sendChatBotKnowledgeBaseId()` | `Long` | 发送预发布知识库 ID |
| `sqs-online-session-index-detail-72h-fcr` | - | `RocketMQDynamicPublisher` | `MessageProducer.sendSessionIndexDetail72HFCR()` | `SessionIndexDetail` | 刷新 72H FCR 数据 |
| `sqs-online-session-index-detail` | - | `RocketMQDynamicPublisher` | `MessageProducer.sendSessionIndexDetail()` | `SessionIndexDetail` | 刷新报表数据 |
| `sqs-online-report-waybill-repeat` | - | `RocketMQDynamicPublisher` | `MessageProducer.sendReportWaybillRelatedSessionInfo()` | `ReportWaybillRepeatSessionMqDTO` | 重复进线报表数据计算 |

**消息消费者**:

项目使用 `MessageReceiver` 和 `RobotMessageReceiver` 来消费消息,具体 Topic 配置在 Apollo 配置中心管理。

---

### Elasticsearch 搜索引擎

**概述**: 项目使用 **Elasticsearch 7.16.2** 实现数据搜索和分析,主要用于会话记录、评价记录、报表数据等的快速检索和聚合查询。

| 配置项 | 说明 |
|--------|------|
| 框架 | Elasticsearch Java High Level REST Client 7.16.2 |
| 客户端类 | `RestHighLevelClient` |
| 工具类 | `ESDocHolder` (文档操作), `ESSearchHolder` (搜索查询) |

#### 索引信息

| 索引名称 | 常量定义 | 用途 | 索引模式 |
|----------|----------|------|----------|
| `sqs_online_customer_session` | `IM_CUSTOMER_SESSION_INDEX` | 客服会话记录索引 | 单索引 |
| `sqs_online_session_index_detail` | `IM_SESSION_INDEX_DETAIL_INDEX` | 会话指标详情索引 | 按月分索引 (`yyyyMM*`) |
| `sqs_online_customer_evaluation` | `IM_CUSTOMER_EVALUATION_INDEX` | 客户评价记录索引 | 单索引 |
| `sqs_online_customer_chat_record` | `IM_CUSTOMER_CHAT_RECORD_INDEX` | 客户聊天记录索引 | 按月分索引 (`yyyyMM*`) |
| `sqs_online_ai_work_order_summary_record` | `IM_AI_WORK_ORDER_SUMMARY_RECORD_INDEX` | AI 工单总结记录索引 | 按月分索引 (`yyyyMM*`) |
| `sqs_online_ai_work_order_recommend_record` | `IM_AI_WORK_ORDER_RECOMMEND_RECORD_INDEX` | AI 工单推荐记录索引 | 按月分索引 (`yyyyMM*`) |
| `sqs_online_report_waybill_repeat_session` | `REPORT_WAYBILL_REPEAT_SESSION` | 重复进线报表索引 | 单索引 |

---

### Config 配置类

| 配置类 | 功能 | 主要配置项 |
|--------|------|------------|
| `XxlJobConfig` | XXL-Job 配置 | 调度中心地址、执行器配置 |
| `RedissonConfig` | Redisson 配置 | Redis 连接配置、分布式锁配置 |
| `JacksonConfig` | Jackson 配置 | JSON 序列化配置 |
| `RestTemplateConfig` | RestTemplate 配置 | HTTP 客户端配置 |
| `ThreadPoolConfig` | 线程池配置 | 核心线程数、最大线程数、队列容量 |
| `WebMvcConfig` | Web MVC 配置 | 拦截器、跨域、静态资源等配置 |
| `MultipartSupportConfig` | 文件上传配置 | 文件大小限制、上传路径配置 |
| `IdGeneratorConfig` | ID 生成器配置 | 分布式 ID 生成配置 |
| `MybatisIdGenerator` | MyBatis ID 生成器 | MyBatis-Plus ID 生成策略配置 |
| `CozeAPIConfig` | Coze API 配置 | Coze AI 服务配置 |
| `ZkConfig` | Zookeeper 配置 | ZK 连接配置 |
| `DataSourceHealthConfig` | 数据源健康检查配置 | 数据源健康检查配置 |
| `CacheConfiguration` | 缓存配置 | Redis 缓存配置 |
| `SkillGroupConfig` | 技能组配置 | 技能组相关配置 |
| `DBJsonMapper` | 数据库 JSON 映射器 | 数据库字段与 JSON 对象映射 |
| `JsonMapper` | JSON 映射器 | JSON 序列化和反序列化配置 |
| `ApolloURLProvider` | Apollo URL 提供者 | Apollo 配置中心 URL 提供者 |

---

## 配置文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| `pom.xml` | 根目录 | Maven 依赖配置 |
| `application.yaml` | `src/main/resources/` | Spring Boot 主配置 |
| `bootstrap.yml` | `src/main/resources/` | Spring Cloud 启动配置 |
| `logback-spring.xml` | `src/main/resources/` | Logback 日志配置 |
| `app.properties` | `src/main/resources/META-INF/` | 应用属性 |
| `mapper/*.xml` | `src/main/resources/mapper/` | MyBatis XML 映射 |

---

## 外部依赖服务

### AI 服务

| 服务名 | 客户端类 | 用途 | 主要接口 |
|--------|----------|------|----------|
| Coze AI | `CozeService` | AI 对话服务 | `chat` - AI 对话接口 |

### Feign 远程服务调用清单

| 序号 | 服务名 | 客户端类 | 接口数量 |
|------|--------|----------|----------|
| 1 | 网点服务 | `NetworkFeignClient` | 4 |
| 2 | OPS 服务 | `OpsFeignClient` | 2 |
| 3 | ChatBot 知识库服务 | `ChatBotKnowledgeApiFeignClient` | 4 |
| 4 | 订单服务 | `OrderQueryFeignClient` | 3 |
| 5 | BPO 用户服务 | `BpoUserFeignClient` | 1 |
| 6 | CSS API 服务 | `CssApiFeignClient` | 1 |
| 7 | 拼多多 IM 数据服务 | `PddImDataFeignClient` | 1 |

> 详细接口地址和说明请参见 **Feign 客户端 (远程服务调用)** 章节

---

*文档更新时间: 2026-04-03 14:31:57*

---
