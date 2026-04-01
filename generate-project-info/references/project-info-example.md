# yl-jms-sqs-online-api 项目框架文档

## 一、项目简介

这是一个**在线客服系统（SQS Online API）**，提供客户与客服的实时聊天、机器人自动回复、会话分配与管理、工单推送等核心功能。

### 核心能力

| 能力 | 描述 |
|------|------|
| 实时聊天 | WebSocket 实现坐席与客户双向通信 |
| 会话管理 | 会话创建、分配、转接、挂起、结束全生命周期管理 |
| 机器人服务 | 自动回复、知识库匹配、敏感词过滤、手机验证 |
| 消息队列 | RabbitMQ/RocketMQ 消息驱动，支持灰度切换 |
| 多渠道接入 | 支持菜鸟、抖音、拼多多、京东、快手、小红书等渠道 |

### 技术栈

| 类型 | 技术 |
|------|------|
| 基础框架 | Spring Boot 2.3.12.RELEASE |
| 微服务框架 | Spring Cloud Hoxton.SR9 |
| ORM | MyBatis-Plus 3.5.3.1 |
| 数据库 | MySQL 8.0.32 + Sharding-JDBC 5.4.1 |
| 缓存 | Redis (Redisson) |
| 消息队列 | RabbitMQ (Spring Cloud Stream) + RocketMQ |
| 配置中心 | Apollo 1.4.0 |
| 服务治理 | Eureka + OpenFeign + Hystrix + Ribbon |
| 定时任务 | XXL-Job 2.3.0 |
| 监控 | Prometheus + Micrometer |
| AI 服务 | Coze API 0.3.2 + Dify Java Client 1.1.9 |
| 其他 | MapStruct 1.5.3, Orika 1.5.2, Hutool 5.5.7, EasyExcel |

---

## 二、项目模块

### 2.1 模块架构图

```
yl-jms-sqs-online-api
├── controller/                    # 控制器层 - 接收 HTTP 请求
├── service/                       # 服务层 - 业务逻辑处理
│   ├── knowledge/                 # 知识库服务
│   └── process/                   # 流程处理服务
├── mapper/                        # 数据访问层 - MyBatis-Plus Mapper
│   ├── knowledge/                 # 知识库 Mapper
│   ├── process/                   # 流程 Mapper
│   └── assistant/                 # 助手 Mapper
├── model/                         # 数据模型层
│   ├── entity/                    # 实体类
│   │   ├── knowledge/             # 知识库实体
│   │   ├── process/               # 流程实体
│   │   └── assistant/             # 助手实体
│   ├── dto/                       # 入参对象
│   ├── vo/                        # 出参对象
│   └── enums/                     # 枚举类
├── feign/                         # 远程服务调用层
│   ├── waybill/                   # 运单服务
│   ├── network/                   # 网点服务
│   ├── customer/                  # 客户服务
│   ├── order/                     # 订单服务
│   ├── ops/                       # 运营服务
│   ├── sms/                       # 短信服务
│   ├── chatbot/                   # 聊天机器人服务
│   ├── transport/                 # 运输服务
│   ├── workorder/                 # 工单服务
│   ├── postalapi/                 # 邮政服务
│   ├── mschannel/                 # 渠道服务
│   ├── cssapi/                    # CSS API
│   └── third/                     # 第三方服务
├── cache/                         # 缓存管理层
│   ├── knowledge/                 # 知识库缓存
│   ├── process/                   # 流程缓存
│   ├── timeout/                   # 超时缓存
│   ├── verify/                    # 验证码缓存
│   ├── inbox/                     # 收件箱缓存
│   └── ai/                        # AI 缓存
├── task/                          # 定时任务层 - XXL-Job
├── listener/                      # 消息监听层
├── stream/                        # 消息流层 - Spring Cloud Stream
├── websocket/                     # WebSocket 通信层
├── aop/                           # AOP 切面
│   ├── annotation/                # 自定义注解
│   └── aspect/                    # 切面实现
├── config/                        # 配置类
├── base/                          # 基础组件
│   ├── config/                    # 基础配置
│   ├── constant/                  # 常量
│   ├── filter/                    # 过滤器
│   ├── interceptor/               # 拦截器
│   ├── model/                     # 基础模型
│   ├── util/                      # 基础工具类
│   ├── validation/                # 校验器
│   └── wrapper/                   # 包装器
└── util/                          # 工具类
```

### 2.2 包结构说明

| 包名 | 说明 | 主要内容 |
|------|------|----------|
| `controller` | 控制器层 | 接收 HTTP 请求，参数校验，调用 Service |
| `service` | 服务层 | 业务逻辑处理，事务管理 |
| `mapper` | 数据访问层 | MyBatis-Plus Mapper 接口，SQL 操作 |
| `model.entity` | 实体类 | 数据库表映射实体 |
| `model.dto` | 入参对象 | 接口入参封装 |
| `model.vo` | 出参对象 | 接口出参封装 |
| `model.enums` | 枚举类 | 业务枚举定义 |
| `feign` | 远程调用 | Feign 客户端接口 |
| `cache` | 缓存层 | Redis 缓存管理 |
| `task` | 定时任务 | XXL-Job 定时任务 |
| `stream` | 消息流 | Spring Cloud Stream 消息生产/消费 |
| `websocket` | WebSocket | 实时通信 |
| `aop` | 切面 | 分布式锁、操作日志等 |
| `config` | 配置 | Spring 配置类 |
| `base` | 基础组件 | 通用配置、常量、工具类 |
| `util` | 工具类 | 业务工具类 |

---

## 三、各模块详细说明

### 3.1 Controller 层

| 类名 | 路径前缀 | 功能 | 主要接口方法 |
|------|----------|------|-------------|
| `AgentController` | `/agent` | 坐席管理 | `agentLogin`, `agentLogout`, `agentSetState`, `sessionTransfer`, `sessionEnd`, `pushWorkOrder` |
| `UserController` | `/user` | 用户/访客管理 | `chatMsgListByUser`, `submitEvaluation`, `sessionEnd`, `sessionQueueExit` |
| `RobotController` | `/user/robot` | 机器人服务 | `userPhoneVerify`, `sensitiveVerification`, `sendNoWaybillInfo`, `matchTest` |
| `GuideController` | `/guide` | 引导服务 | 引导页、FAQ、欢迎语等 |
| `NotifyController` | `/notify` | 通知服务 | 消息通知推送 |
| `CustomerNotifyController` | `/customer/notify` | 客户通知 | 客户端消息通知 |
| `ThirdApiController` | `/third` | 第三方接口 | 第三方系统对接 |
| `BaseController` | - | 基础控制器 | 提供通用方法 |

---

### 3.2 Entity 实体类

#### 3.2.1 基础实体类继承体系

```
BaseId<T> (extends Model<T>)
    └── BaseEntity<T> (添加 createBy, updateBy 等字段)
            └── Base<T> (添加 isDelete, isEnable 字段)
```

**BaseId 字段**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID（雪花算法） |
| `createTime` | `LocalDateTime` | 创建时间 |
| `updateTime` | `LocalDateTime` | 更新时间 |

**BaseEntity 额外字段**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `createBy` | `String` | 创建人 code |
| `createByName` | `String` | 创建人名称 |
| `updateBy` | `String` | 修改人 code |
| `updateByName` | `String` | 修改人名称 |

**Base 额外字段**

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `isDelete` | `Integer` | 删除标记（2 未删除） |
| `isEnable` | `Integer` | 是否启用（1 启用，2 不启用） |

---

#### 3.2.2 Customer (客户信息) - 表名: `customer`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `account` | `String` | 用户账号 |
| `customerName` | `String` | 用户昵称 |
| `skillGroupId` | `Long` | 技能组 ID |
| `skillGroupName` | `String` | 技能组名称 |
| `openId` | `String` | 渠道对应的 openId |
| `isProxy` | `Boolean` | 是否代理用户 |
| `createTime` | `LocalDateTime` | 创建时间 |

---

#### 3.2.3 CustomerSession (会话信息) - 表名: `customer_session`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID（继承 BaseId） |
| `agentId` | `Long` | 坐席 ID |
| `realName` | `String` | 坐席名称 |
| `agentName` | `String` | 坐席昵称 |
| `account` | `String` | 坐席账号 |
| `customerId` | `Long` | 访客 ID |
| `customerName` | `String` | 访客昵称 |
| `customerPhone` | `String` | 访客手机号 |
| `customerPhoneEncrypted` | `String` | 访客手机号加密 |
| `serviceId` | `Long` | 服务商 ID |
| `serviceName` | `String` | 服务商名称 |
| `skillGroupId` | `Long` | 技能组 ID |
| `skillGroupCode` | `String` | 技能组 CODE |
| `skillGroupName` | `String` | 技能组名称 |
| `serviceNetworkType` | `String` | 网点类型 |
| `serviceNetworkId` | `Integer` | 网点 ID |
| `serviceNetworkCode` | `String` | 网点 Code |
| `serviceNetworkName` | `String` | 网点名称 |
| `financialCenterType` | `String` | 结算中心类型 |
| `financialCenterId` | `Integer` | 结算中心 ID |
| `financialCenterCode` | `String` | 结算中心 Code |
| `financialCenterName` | `String` | 结算中心名称 |
| `serviceAgencyId` | `Integer` | 代理区 ID |
| `serviceAgencyCode` | `String` | 代理区 Code |
| `serviceAgencyName` | `String` | 代理区名称 |
| `extraData` | `String` | 会话发起页 json |
| `extraSessionId` | `String` | 会话端关联的外部 sessionId |
| `waybillNo` | `String` | 运单号 |
| `isSuspend` | `Integer` | 是否挂起（1:是,2:否） |
| `state` | `Integer` | 会话状态 |
| `stateName` | `String` | 会话状态名称 |
| `startTime` | `LocalDateTime` | 会话开始时间 |
| `endTime` | `LocalDateTime` | 会话结束时间 |
| `sessionTime` | `BigInteger` | 会话时长（毫秒） |
| `queueStartTime` | `LocalDateTime` | 排队开始时间 |
| `queueEndTime` | `LocalDateTime` | 排队结束时间 |
| `queueTime` | `Long` | 排队时长（毫秒） |
| `currentMsgRoundsAuthor` | `Integer` | 上次消息发送者（1:坐席,2:用户） |
| `currentMsgRoundsTime` | `LocalDateTime` | 上次消息发送时间 |
| `msgRounds` | `Integer` | 消息轮次 |
| `firstReplyTime` | `Long` | 首次响应时长（毫秒） |
| `avgReplyTime` | `Long` | 平均响应时长（毫秒） |
| `satisfied` | `Boolean` | 是否已经推送过评价 |
| `satisfiedAgentInvite` | `Boolean` | 是否是坐席主动邀请的评价 |
| `endType` | `Integer` | 结束类型 |
| `formatDate` | `String` | 格式化后的日期 yyyy-MM-dd |
| `transferAgentId` | `Long` | 转接坐席 ID |
| `transferAgentName` | `String` | 转接坐席昵称 |
| `transferAccount` | `String` | 转接坐席账号 |
| `transferTime` | `LocalDateTime` | 转接时间 |
| `customerLevel` | `Integer` | 访客级别 |
| `sessionType` | `Integer` | 会话类型 |
| `preSessionId` | `Long` | 上一个会话 id |
| `isConvertAgent` | `Integer` | 是否机器人会话转人工（1:是 2:否） |
| `robotChatRecordState` | `Integer` | 机器人记录同步状态 |
| `refWorkOrder` | `Integer` | 是否映射工单（1:是 2:否） |
| `source` | `String` | 来源 |
| `serviceType` | `Integer` | 服务类型（1:上门取件 2:快递柜 3:驿站寄件） |
| `businessNo` | `String` | 业务单号 |
| `isHongKong` | `Integer` | 是否集运(香港) |
| `isTryConvertAgent` | `Integer` | 是否尝试转人工 |
| `targetServiceNetworkType` | `String` | 目标网点类型 |
| `targetServiceNetworkId` | `Integer` | 目标网点 ID |
| `targetServiceNetworkCode` | `String` | 目标网点 Code |
| `targetServiceNetworkName` | `String` | 目标网点名称 |
| `targetServiceAgencyId` | `Integer` | 目标代理区 ID |
| `targetServiceAgencyCode` | `String` | 目标代理区 Code |
| `targetServiceAgencyName` | `String` | 目标代理区名称 |
| `isSharedCustomerService` | `Integer` | 是否共享客服（1:是 2:否） |
| `existTaoTianWorkOrder` | `Integer` | 是否存在淘天工单 |
| `isUseOrderAssistant` | `Integer` | 是否使用录单小助手（1:是 2:否） |

---

#### 3.2.4 User (坐席用户) - 表名: `user`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `account` | `String` | 用户名 |
| `agentName` | `String` | 坐席名称 |
| `serviceId` | `Long` | 服务商 ID |
| `serviceName` | `String` | 服务商名称 |
| `serviceCode` | `String` | 服务商编码 |
| `isAgent` | `Integer` | 是否坐席 |
| `isAgentEnable` | `Integer` | 是否坐席启用 |
| `loginTime` | `LocalDateTime` | 上次登录时间 |
| `todayFirstLoginTime` | `LocalDateTime` | 今日首次登录时间 |
| `passWord` | `String` | 密码 |
| `phone` | `String` | 手机号码 |
| `certificate` | `String` | 身份证号 |
| `realName` | `String` | 真实姓名 |
| `gender` | `Integer` | 性别（1:男 2:女） |
| `email` | `String` | 邮箱地址 |
| `dataSource` | `String` | 数据来源 |
| `outId` | `String` | 外部 ID |
| `serviceNetworkType` | `String` | 网点类型 |
| `serviceNetworkId` | `Integer` | 网点 ID |
| `serviceNetworkCode` | `String` | 网点 Code |
| `serviceNetworkName` | `String` | 网点名称 |
| `financialCenterType` | `String` | 结算中心类型 |
| `financialCenterId` | `Integer` | 结算中心 ID |
| `financialCenterCode` | `String` | 结算中心 Code |
| `financialCenterName` | `String` | 结算中心名称 |

---

#### 3.2.5 SkillGroup (技能组) - 表名: `skill_group`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `skillGroupCode` | `String` | 技能组 code |
| `skillGroupName` | `String` | 技能组名称 |
| `skillGroupTag` | `String` | 技能组访客名称标签 |
| `skillGroupAvatar` | `String` | 技能组访客头像（文件相对路径） |
| `isGray` | `Integer` | 灰度（1:是, 2:否） |

---

#### 3.2.6 ServiceProvider (服务商) - 表名: `service_provider`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `isQuotaEnable` | `Integer` | 是否分流启用（1:分流 2:不分流） |
| `serviceName` | `String` | 服务商名称 |
| `serviceCode` | `String` | 服务商编码 |
| `contactPerson` | `String` | 联系人 |
| `contactNumber` | `String` | 联系电话 |
| `contactEmail` | `String` | 联系邮箱 |
| `corporateName` | `String` | 公司法人 |
| `corporateIdCard` | `String` | 法人身份证 |
| `accountBank` | `String` | 开户行 |
| `account` | `String` | 收款账号 |
| `socialCreditCode` | `String` | 统一社会信用代码 |
| `businessLicenseImg` | `String` | 营业执照图片 |
| `businessLicenseStartTime` | `Date` | 营业执照开始时间 |
| `businessLicenseEndTime` | `Date` | 营业执照结束时间 |
| `effectiveStartTime` | `Date` | 有效开始日期 |
| `effectiveEndTime` | `Date` | 有效结束日期 |

---

#### 3.2.7 ServiceProviderChannelDiversion (服务商渠道分流) - 表名: `service_provider_channel_diversion`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `skillGroupId` | `Long` | 技能组 ID |
| `skillGroupCode` | `String` | 技能组编码 |
| `skillGroupName` | `String` | 技能组名称 |
| `serviceProviderId` | `Long` | 服务商 ID |
| `serviceProviderCode` | `String` | 服务商编码 |
| `serviceProviderName` | `String` | 服务商名称 |
| `quota` | `Integer` | 分配份额（同一技能组总份额必须为100或0） |

---

#### 3.2.8 CustomerChatRecord (聊天记录) - 表名: `customer_chat_record`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 BaseId | - | 包含基础字段 |
| `guid` | `String` | 唯一标识 |
| `sessionId` | `Long` | 会话 ID |
| `customerId` | `Long` | 游客 ID |
| `customerName` | `String` | 游客昵称 |
| `agentId` | `Long` | 坐席 ID |
| `agentName` | `String` | 坐席昵称 |
| `msgType` | `Integer` | 消息内容类型 |
| `status` | `String` | 消息状态 |
| `msg` | `String` | 消息 |
| `srcType` | `Integer` | 消息来源类型 |
| `author` | `Integer` | 消息发送者 |
| `msgShowType` | `Integer` | 消息显示类型 |
| `fileName` | `String` | 文件名 |
| `fileSize` | `String` | 文件大小 |
| `evalStatus` | `Integer` | 评价状态（null:不可评价, 0:未评价, 1:点赞, 2:点踩） |
| `suggestReply` | `String` | 推荐回复 |

---

#### 3.2.9 CustomerEvaluation (客户评价) - 表名: `customer_evaluation`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 BaseId | - | 包含基础字段 |
| `sessionId` | `Long` | 会话 ID |
| `customerId` | `Long` | 游客 ID |
| `agentId` | `Long` | 坐席 ID |
| `account` | `String` | 坐席账号 |
| `agentName` | `String` | 坐席名称 |
| `serviceId` | `Long` | 服务商 ID |
| `serviceName` | `String` | 服务商名称 |
| `skillGroupId` | `Long` | 技能组 ID |
| `skillGroupCode` | `String` | 技能组 CODE |
| `skillGroupName` | `String` | 技能组名称 |
| `star` | `Integer` | 评价星级（1-5） |
| `suggestion` | `String` | 评价内容 |
| `resolved` | `Integer` | 是否解决（1:解决 2:未解决） |
| `endType` | `Integer` | 结束类型 |
| `waybillNo` | `String` | 运单号 |
| `serviceNetworkType` | `String` | 网点类型 |
| `serviceNetworkId` | `Integer` | 网点 ID |
| `serviceNetworkName` | `String` | 网点名称 |
| `serviceAgencyId` | `Integer` | 代理区 ID |
| `serviceAgencyName` | `String` | 代理区名称 |
| `tagCodes` | `String` | 评价星级标签编码（多个用英文逗号拼接） |
| `tagNames` | `String` | 评价星级标签名称（多个用英文逗号拼接） |
| `targetServiceNetworkType` | `String` | 目标网点类型 |
| `targetServiceNetworkId` | `Integer` | 目标网点 ID |
| `targetServiceNetworkCode` | `String` | 目标网点 Code |
| `targetServiceNetworkName` | `String` | 目标网点名称 |
| `targetServiceAgencyId` | `Integer` | 目标代理区 ID |
| `targetServiceAgencyCode` | `String` | 目标代理区 Code |
| `targetServiceAgencyName` | `String` | 目标代理区名称 |
| `isSharedCustomerService` | `Integer` | 是否共享客服（1:是 2:否） |

---

#### 3.2.10 UserOnlineState (坐席在线状态) - 表名: `user_online_state`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `agentId` | `Long` | 坐席编号（主键） |
| `state` | `Integer` | 坐席状态（1:接待中 2:忙碌中 3:离线中） |
| `updateTime` | `LocalDateTime` | 最后更新时间 |

---

#### 3.2.11 UserSkillGroup (坐席技能组关联) - 表名: `user_skill_group`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `userId` | `Long` | 用户编号 |
| `skillGroupId` | `Long` | 技能组 CODE |
| `skillGroupName` | `String` | 技能组名称 |
| `maxUsersCount` | `Integer` | 最大接入数（默认 10） |

---

#### 3.2.12 RobotBaseConfig (机器人基础配置) - 表名: `robot_base_config`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 BaseEntity | - | 包含基础字段 |
| `robotName` | `String` | 机器人名称 |
| `robotHeadImg` | `String` | 机器人头像 |
| `hitThreshold` | `Float` | 命中阈值 |
| `clarificationThreshold` | `Float` | 澄清阈值 |
| `sessionTimeout` | `Integer` | 会话超时结束（单位 s） |
| `clarificationMaxNumber` | `Integer` | 澄清最大次数 |
| `clarificationStartMessage` | `String` | 澄清开头话术 |
| `clarificationEndMessage` | `String` | 澄清结尾话术 |
| `topMax` | `Integer` | 推荐 top 最大个数 |
| `unrecognizedStartMessage` | `String` | 未识别开头话术 |
| `unrecognizedEndMessage` | `String` | 未识别结尾话术 |
| `interceptPromptLanguageOne` | `String` | 拦截提示语一 |
| `interceptPromptLanguageTwo` | `String` | 拦截提示语二 |
| `interceptPromptLanguageThree` | `String` | 拦截提示语三 |
| `verifyTime` | `Integer` | 手机号验证码的时间配置（单位 h） |

---

#### 3.2.13 ServiceConfig (服务配置) - 表名: `service_config`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `helloMsg` | `String` | 欢迎消息（已废弃） |
| `workingHoursStart` | `LocalTime` | 开始工作时间 |
| `workingHoursEnd` | `LocalTime` | 结束工作时间 |
| `workingHoursNotMsg` | `String` | 快递非工作时间段提示语 |
| `notAgentMsg` | `String` | 无坐席在线提示语 |
| `successMsg` | `String` | 分配成功提示语 |
| `replyOvertimeByAgentTime` | `Integer` | 坐席回复超时时间（秒，默认 5*60） |
| `replyOvertimeByAgentMsg` | `String` | 坐席回复超时提示语 |
| `replyOvertimeByUsersTime` | `Integer` | 用户回复超时时间（秒，默认 5*60） |
| `replyOvertimeByUsersMsg` | `String` | 用户回复超时提示语 |
| `replyCountdownByUsersTime` | `Integer` | 用户回复倒计时关闭（秒，默认 5*60） |
| `replyCountdownByUsersMsg` | `String` | 用户回复超时关闭提示音 |
| `agentEndSessionMsg` | `String` | 坐席主动结束会话提示语 |
| `usersEndSessionMsg` | `String` | 用户主动结束会话提示语 |
| `reconnectOvertimeByAgentsTime` | `Integer` | 坐席重连超时时间（秒，默认 5*60） |
| `reconnectOvertimeByUsersTime` | `Integer` | 用户重连超时时间（秒，默认 5*60） |
| `reconnectOvertimeByUsersMsg` | `String` | 用户重连超时提示语 |
| `queueMaxTimeout` | `Integer` | 用户排队超时剔除时间（秒，默认 12*60*60） |
| `queueFullMsg` | `String` | 排队队列已满提示语 |
| `queueMsg` | `String` | 排队中提示语（排队号：[[num]]） |
| `queueWaitMsg` | `String` | 排队靠后等待提示语 |
| `queueMaxLength` | `Integer` | 排队最大长度（默认 500） |
| `queueOverflowTimeout` | `Integer` | 排队溢出超时时间（秒） |
| `queueNetworkOverflowLength` | `Integer` | 网点排队溢出长度 |
| `queueCenterOverflowLength` | `Integer` | 中心排队溢出长度 |
| `queueAgentAreaOverflowLength` | `Integer` | 代理区排队溢出长度 |
| `collectWaybillMsg` | `String` | 收集运单话术 |
| `confirmWaybillPhoneMsg` | `String` | 确认收/寄件人手机尾号话术 |
| `queueTipTimeout` | `Integer` | 排队提醒超时时间 |
| `queueTipLastTimeout` | `Integer` | 排队提醒超时持续时间 |
| `privacyPolicyMsg` | `String` | 隐私政策 |
| `msgRecallEnable` | `Integer` | 消息撤回开关 |
| `msgRecallTimeout` | `Integer` | 消息撤回超时时间（秒） |
| `scriptRecommendationEnable` | `Integer` | 话术推荐状态（1:启用 2:禁用） |
| `scriptRecommendationSkillGroups` | `String` | 话术推荐技能组（多个用逗号隔开） |
| `subtotalWorkOrder` | `Integer` | 工单小计 |

---

#### 3.2.14 QuickReply (快捷回复) - 表名: `quick_reply`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `type` | `Integer` | 类型（默认企业类型） |
| `parentId` | `Long` | 父类 ID |
| `level` | `Integer` | 层级（1:分组 2:内容） |
| `content` | `String` | 内容 |
| `clickCount` | `Integer` | 点击量（默认 0） |

---

#### 3.2.15 EvaluationTag (评价标签) - 表名: `evaluation_tag`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `star` | `Integer` | 评价星级（1:一星 2:二星 3:三星 4:四星 5:五星） |
| `nominalName` | `String` | 评价标称 |
| `hint` | `String` | 提示语 |
| `tagCode` | `String` | 标签编码 |
| `tagName` | `String` | 标签名称 |
| `isExclusive` | `Integer` | 排他（1:是 2:否） |

---

#### 3.2.16 SensitiveWords (敏感词) - 表名: `sensitive_words`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `content` | `String` | 敏感词 |

---

#### 3.2.17 Inbox (收件箱) - 表名: `inbox`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | `String` | 名称（主键） |
| `offset` | `Long` | 偏移量 |

---

#### 3.2.18 GuideFaq (引导 FAQ) - 表名: `guide_faq`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `tabId` | `Long` | 栏目 ID |
| `problem` | `String` | 问题 |
| `solution` | `String` | 答案 |
| `sort` | `Integer` | 排序 |

---

#### 3.2.19 GuideTab (引导标签页) - 表名: `guide_tab`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 Base | - | 包含基础字段 |
| `name` | `String` | 栏目名称 |
| `sort` | `Integer` | 排序 |

---

#### 3.2.20 GuideWelcome (欢迎语) - 表名: `guide_welcome`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `content` | `String` | 内容 |
| `startTime` | `LocalDateTime` | 开始时间 |
| `endTime` | `LocalDateTime` | 结束时间 |
| `type` | `int` | 类型（1:默认 2:时段 3:例外） |
| `isEnable` | `int` | 是否启用（1:启用 2:不启用） |
| `createTime` | `LocalDateTime` | 创建时间 |
| `createBy` | `String` | 创建人 code |
| `createByName` | `String` | 创建人 name |

---

#### 3.2.21 GuideNotice (引导公告) - 表名: `guide_notice`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | `Long` | 主键 ID |
| `title` | `String` | 标题 |
| `content` | `String` | 内容 |
| `startTime` | `LocalTime` | 开始时间 |
| `endTime` | `LocalTime` | 结束时间 |
| `model` | `Integer` | 模式（1:隐藏 2:显示） |
| `isEnable` | `Integer` | 是否启用（1:启用 2:不启用） |
| `updateTime` | `LocalDateTime` | 修改时间 |
| `updateBy` | `String` | 修改人 code |
| `updateByName` | `String` | 修改人 name |

---

#### 3.2.22 KnowledgeBase (知识库基础) - 表名: `knowledge_base`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 BaseEntity | - | 包含基础字段 |
| `type` | `KnowledgeBaseType` | 知识库类型（PRO:生产,PRE:预发,OLD:历史） |
| `status` | `KnowledgeBaseStatus` | 知识库状态（LOADING:加载中,COMPLETE:加载完成,FAILED:加载失败） |

---

#### 3.2.23 Process (流程配置) - 表名: `process`

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 继承 BaseEntity | - | 包含基础字段 |
| `guid` | `String` | 唯一 ID |
| `processType` | `ProcessType` | 流程类型 |
| `rootName` | `String` | 根名称 |
| `name` | `String` | 名称 |
| `isEnable` | `Integer` | 启用/禁用 |

---

### 3.3 Feign 客户端 (远程服务调用)

#### 3.3.1 运单服务 (`WaybillFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylwaybillouterapi` |
| 路径前缀 | `/waybillouterapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/waybillDetailByNo` | GET | 根据运单号获取运单详情 | `waybillNo: String` | `Result<OmsWaybillDetailVO>` |
| `/common/get` | POST | 通用运单查询 | `WaybillDetailSearchDTO` | `Result<OmsWaybillDetailVO>` |
| `/css/getWaybillsByPhoneNum` | POST | 根据手机号查询运单列表 | `WaybillDetailByPhoneDTO` | `Result<Page<WaybillDetailByPhoneVO>>` |
| `/css/getWaybillsByPhoneNumNew` | POST | 根据手机号查询运单列表(新) | `WaybillDetailByPhoneDTO` | `Result<Page<WaybillDetailByPhoneVO>>` |

---

#### 3.3.2 网点服务 (`NetworkFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylnetworkapi` |
| 路径前缀 | `/networkapi/web` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/servicequality/network/getNetworkAndUpperById` | GET | 根据网点 ID 查询网点及上级网点 | `id: Integer` | `Result<SqGetNetworkAndUpperVO>` |
| `/servicequality/network/getNetworkAndUpperByCode` | GET | 根据网点 Code 查询网点及上级网点 | `code: String` | `Result<SqGetNetworkAndUpperVO>` |
| `/servicequality/network/getNetworkAgentByCodes` | POST | 查询虚拟代理区 | `codes: List<String>` | `Result<List<SqNetworkAgentVO>>` |
| `/servicequality/network/getNetworkByCode` | GET | 查询网点信息 | `code: String` | `Result<SqNetworkVO>` |
| `/css/network/getDetailById` | GET | 根据网点 ID 获取详细信息 | `id: Integer` | `Result<SqNetworkVO>` |
| `/servicequality/staff/getStaffPhoneByCodes` | POST | 收派员手机号查询 | `staffCodes: List<String>` | `Result<List<SqStaffVO>>` |

---

#### 3.3.3 客户服务 (`SysCustomerNicheFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylcustomerapi` |
| 路径前缀 | `/customerapi/niche` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/addH5` | POST | 添加商机客户 H5 | `SysCustomerNicheAddDTO` | `Result<SysCustomerNicheQueryVO>` |
| `/selectNicheByMobile` | POST | 通用手机号查询商机信息 | `SysCustomerNichePageDTO` | `Result<List<SysCustomerNicheQueryAllVO>>` |

---

#### 3.3.4 订单查询服务 (`OrderQueryFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `jms-order-query-api` |
| 路径前缀 | `/order-query-api` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/waybill/queryOrderInfo` | POST | 根据运单号获取订单信息 | `QueryOrderInfoByWaybillDTO` | `Result<List<OrderInfoQueryVO>>` |
| `/sqs/orderQuery/queryOrderByWaybillIds` | POST | 根据运单号批量查询订单 | `QueryOrderInfoByWaybillDTO` | `Result<List<OrderInfoQueryVO>>` |
| `/orderMarkExpand/queryOrderMark/{waybillNo}` | GET | 根据运单号获取订单标记信息 | `waybillNo: String` | `Result<List<OrderMarkVO>>` |

---

#### 3.3.5 工单服务 (`WorkOrderClientFeign`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylcssworkorderapi` |
| 路径前缀 | `/cssworkorderapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/workOrder/getRegularWorkOrder` | GET | 获取普通工单 | `waybillNo: String` | `Result<List<WorkOrderProblemRecordVO>>` |

---

#### 3.3.6 工单服务 V2 (`WorkOrderFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylcssworkorderapi` |
| 路径前缀 | `/cssworkorderapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/audioOrderInfo/queryByAudioIds` | GET | 根据音频 ID 查询工单 | `audioIds: List<Long>` | `Result<List<AudioWorkOrderDTO>>` |
| `/audioOrderInfo/hasWorkOrder` | GET | 是否有工单操作 | `audioId: String` | `Result<Boolean>` |
| `/workOrderInfo/information` | GET | 工单详情 | `workOrderNo: String` | `Result<WorkOrderDetailDTO>` |
| `/workOrder/imSave` | POST | IM 保存工单 | `IMWorkOrderAddDTO` | `Result<Boolean>` |
| `/workOrder/save` | POST | 录单或问题记录 | `WorkOrderAddDTO` | `Result<Boolean>` |
| `/workOrderType/page/workOrderSecondType` | POST | 分页查询二级工单类型 | `WorkOrderTypeSecondSearchDTO` | `Result<Page<WorkOrderTypeSecondVO>>` |
| `/workOrder/queryTransportation` | GET | 查询运输状态 | `waybillNo: String, historyType: Integer` | `Result<TransportationStatusVO>` |
| `/workOrder/getRegularWorkOrder` | GET | 获取普通工单 | `waybillNo: String` | `Result<List<WorkOrderProblemRecordVO>>` |

---

#### 3.3.7 CSS 服务 (`CssApiFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylcssapi` |
| 路径前缀 | `/cssapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/phoneCall/callPhone` | POST | 企微报表异常告警-电话 | `PhoneCallDTO` | `Result<Boolean>` |
| `/sysSensitiveWord/sensitiveVerification` | POST | 敏感词验证 | `Map<String, String>` | `Result<Boolean>` |
| `/dispatcherWorkOrder/checkExist` | POST | 派送员工单校验存在 | `DispatcherWorkOrderCheckDTO` | `Result<Boolean>` |
| `/networkAbnormalWaybill/checkIsTimeDelayByWaybill` | POST | 校验运单是否时效顺延 | `ExceptionDTO` | `Result<Boolean>` |
| `/networkAbnormalWaybill/isExceptionWaybill` | GET | 是否异常运单 | `waybillNo: String` | `Result<SecondaryAbnormalWaybillNoVO>` |

---

#### 3.3.8 运营查询服务 (`OpsQueryFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `opsscanqueryapi` |
| 路径前缀 | `/scanquery` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/external/search/fwzl/getZysmAndXzfjByWaybillNo` | POST | 批量查询物流轨迹 | `waybills: List<String>` | `Result<List<ZysmAndXzfjByWaybillNoVO>>` |

---

#### 3.3.9 运营 POD 服务 (`OpsFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-jms-ops-pod-api` |
| 路径前缀 | `/ops/pod/opsPodTracking` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/qos/keywordList` | POST | 批量查询物流轨迹-内部 | `PodTrackingInnerQueryDTO` | `Result<List<PodTrackingListVO>>` |
| `/outer/qos/keywordList` | POST | 批量查询物流轨迹-外部 | `keywordList: List<String>` | `Result<List<PodTrackingListVO>>` |

---

#### 3.3.10 短信服务 (`SmsSendFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylsms` |
| 路径前缀 | - |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/sms/v2/sendBatch` | POST | 发送短信 | `SmsSendDTO` | `Result<SmsSendVO>` |

---

#### 3.3.11 聊天机器人服务 (`ChatBotKnowledgeApiFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yl-jms-sqs-online-chatbot-api` |
| 路径前缀 | `/sqsonlinechatbotapi/knowledge/im` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/match` | POST | 知识库匹配 | `ChatBotKnowledgeMatchDTO` | `Result<List<ChatBotKnowledgeMatchVO>>` |
| `/add` | POST | 添加知识库 | `ChatBotKnowledgeAddDTO` | `Result<List<String>>` |
| `/delete` | POST | 删除知识库 | `extraIds: List<String>` | `Result<Boolean>` |
| `/drop_index` | POST | 删除索引 | `db: String` | `Result<Boolean>` |

---

#### 3.3.12 第三方回调服务 (`ThirdApiCallbackFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yljmssqsonlinethird` |
| 路径前缀 | `/sqsonlinethird/third/invoke` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/querySessionMessage` | POST | 查询访客与第三方机器人聊天记录 | `ThirdQuerySessionMsgDTO` | `Result<List<ThirdCustomerChatRecordVO>>` |
| `/sendWorkOrderMessage` | POST | 发送工单消息 | `ThirdSendWorkOrderMessageDTO` | `Result<Void>` |
| `/sendShopTaskMessage` | POST | 发送商家任务单消息 | `ThirdSendShopTaskMessageDTO` | `Result<Void>` |
| `/sendTaoTianWorkOrder` | POST | 发送淘天工单 | `SqsTaoTianWorkOrderPushDTO` | `Result<SqsTaoTianWorkOrderResultVO>` |
| `/sendTaoTianSessionDiagnosisResult` | POST | 发送淘天会话诊断结果 | `SqsTaoTianSessionDiagnosisResultPushDTO` | `Result<SqsTaoTianWorkOrderResultVO>` |

---

#### 3.3.13 渠道服务 (`MSChannelFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yljmschannelapi` |
| 路径前缀 | - |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/channelapi/api/wx/getMobileByOpenid` | GET | 根据 openId 获取手机号 | `openid: String` | `Result<String>` |

---

#### 3.3.14 邮政服务 (`CombineInfoFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylcsspostalapi` |
| 路径前缀 | `/csspostalapi/combineInfo` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/getHasPostalMap` | POST | 批量查询运单是否有工单 | `GetHasPostalMapDTO` | `Result<Map<String, Boolean>>` |

---

#### 3.3.15 运输服务 (`ShipmentFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yltransportwebcooperate` |
| 路径前缀 | `/transportcooperate` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/shipmentstate/queryByShipmentNo` | GET | 根据运单号查询运输状态 | `shipmentNo: String` | `Result<ShipmentStateVO>` |

---

#### 3.3.16 项目工单服务 (`ProjectWorkOrderFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `sqsplatformorderapi` |
| 路径前缀 | `/platformorderapi/projectWorkOrder` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/getPlatformWorkOrder` | GET | 获取平台工单 | `waybillNo: String` | `Result<List<WorkOrderProblemRecordVO>>` |

---

#### 3.3.17 订单敏感信息服务 (`CcmOrderSensitiveFeignClient`)

| 属性 | 值 |
|------|-----|
| 服务名 | `yljmsccmordersensitiveapi` |
| 路径前缀 | `/ccmordersensitiveapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/order/sensitive/query` | POST | 反查订单敏感信息 | `OrderSensitiveQueryDTO` | `Result<List<OrderSensitiveQueryVO>>` |

---

#### 3.3.18 通话记录服务 (`CallRecordsFeign`)

| 属性 | 值 |
|------|-----|
| 服务名 | `ylsqsproblemapi` |
| 路径前缀 | `/sqsproblemapi` |

| 接口路径 | HTTP 方法 | 接口说明 | 入参 | 返回 |
|----------|-----------|----------|------|------|
| `/callRecords/getCallRecord` | POST | 查询来电记录 | `CallRecordsAddDTO` | `Result<List<CallRecordsVO>>` |
| `/problemPiece/queryProblemPieceByWaybillNo` | GET | 根据运单号获取问题件记录 | `wayBillNo: String` | `Result<List<ProblemPieceInfoVO>>` |

---

### 3.4 Cache 缓存层

| 缓存类 | 功能 | 说明 |
|--------|------|------|
| `BaseCache` | 缓存基类 | 提供通用缓存方法 |
| `AgentTokenCache` | 坐席 Token 缓存 | 坐席登录 Token 管理 |
| `AgentSkillGroupCache` | 坐席技能组缓存 | 坐席与技能组关联 |
| `UserTokenCache` | 用户 Token 缓存 | 用户登录 Token |
| `UserOnlineCountCache` | 在线用户数缓存 | 在线人数统计 |
| `QueueSessionCache` | 排队会话缓存 | 排队信息 |
| `WebsocketSessionCache` | WebSocket 会话缓存 | WS 连接管理 |
| `RedissonClientCache` | Redisson 客户端缓存 | 分布式锁支持 |
| `GuideFaqCache` | 引导 FAQ 缓存 | FAQ 内容缓存 |
| `GuideHintCardCache` | 引导提示卡缓存 | 提示卡内容 |
| `GuideNoticeCache` | 引导公告缓存 | 公告内容 |
| `GuideQuickChannelCache` | 快捷渠道缓存 | 渠道信息 |
| `GuideTabCache` | 引导标签页缓存 | 标签页内容 |
| `GuideWelcomeCache` | 欢迎语缓存 | 欢迎语内容 |
| `RobotBaseConfigCache` | 机器人配置缓存 | 机器人基础配置 |
| `RobotEvaluationConfigCache` | 机器人评价配置缓存 | 评价配置 |
| `ServiceConfigCache` | 服务配置缓存 | 服务参数配置 |
| `ServiceNetworkCache` | 服务网点缓存 | 网点信息 |
| `ServiceNetworkAgencyCache` | 服务网点代理缓存 | 代理信息 |
| `TransferAgentKeywordCache` | 转接关键词缓存 | 转接关键词 |
| `RepeatJoinSessionCountCache` | 重复进线计数缓存 | 进线统计 |

---

### 3.5 Task 定时任务

| 任务类 | XXL-Job 名称 | 功能 |
|--------|-------------|------|
| `CleanRedisTask` | `cleanRedisTask` | 清理 Redis 缓存 |
| `AgentReconnectOvertimeTask` | - | 坐席重连超时处理 |
| `AgentReplyOvertimeTask` | - | 坐席回复超时处理 |
| `UserReconnectOvertimeTask` | - | 用户重连超时处理 |
| `UserReplyOvertimeTask` | - | 用户回复超时处理 |
| `CustomerQueueOverflowTimeoutTask` | - | 客户排队溢出超时处理 |
| `SessionQueueAllocationTask` | - | 会话排队分配 |
| `InboxClearTask` | - | 收件箱清理 |
| `KnowledgeTopRefreshTask` | - | 知识库热门刷新 |
| `SensitiveWordsInitTask` | - | 敏感词初始化 |

---

### 3.6 Stream 消息流

#### 3.6.1 概述

项目使用 **Spring Cloud Stream** + **RabbitMQ** / **RocketMQ** 实现消息驱动，支持灰度切换。

#### 3.6.2 Output（消息生产）

| Channel 名称 | Topic | 说明 |
|--------------|-------|------|
| `online-agent-result-output` | `sqs-online-online-agent` | 坐席消息广播 |
| `online-user-result-output` | `sqs-online-user-result` | 用户消息广播 |
| `user-queuing-timeout-output` | `sqs-online-user-queuing-timeout` | 用户排队超时 |
| `session-create-close-evaluation-result-output` | `sqs-online-create-close-evaluation-result` | 会话创建/关闭/评价 |
| `online-message-dump-oss-output` | `sqs-online-message-dump-oss` | 文件消息转存 OSS |
| `online-message-suggest-output` | `sqs-online-message-suggest` | 消息推荐 |
| `online-session-waybill-time-limit-output` | `sqs-online-session-waybill-time-limit` | 会话运单时效 |
| `online-ai-work-order-recommend-context-output` | `sqs-online-ai-work-order-recommend-context` | AI 工单推荐上下文 |

#### 3.6.3 Input（消息消费）

| Channel 名称 | Topic | 处理逻辑 |
|--------------|-------|----------|
| `user-queuing-timeout-input` | `sqs-online-user-queuing-timeout` | `sessionQueueService.customerQueueTimeout()` |
| `online-message-dump-oss-input` | `sqs-online-message-dump-oss` | `customerChatRecordService.dumpOss()` |
| `online-message-suggest-input` | `sqs-online-message-suggest` | `messageSuggestService.messageSuggest()` |
| `online-session-waybill-time-limit-input` | `sqs-online-session-waybill-time-limit` | `sessionWaybillTimeLimitCache.queryTransportationAndSet()` |
| `online-ai-work-order-recommend-context-input` | `sqs-online-ai-work-order-recommend-context` | `aiWorkOrderRecommendContextCache.get()` |

---

### 3.7 Config 配置类

| 配置类 | 功能 |
|--------|------|
| `MybatisPlusConfig` | MyBatis-Plus 配置 |
| `FeignAutoConfig` | Feign 自动配置 |
| `OrikaConfiguration` | Orika 对象映射配置 |
| `ValidatorConfiguration` | 校验器配置 |
| `RedissonConfig` | Redisson 分布式锁配置 |
| `RedisTemplateConfig` | Redis 模板配置 |
| `XxlJobConfig` | XXL-Job 定时任务配置 |
| `IdGeneratorConfig` | ID 生成器配置 |
| `CozeAPIConfig` | Coze AI 服务配置 |
| `DifyClientConfig` | Dify AI 服务配置 |
| `JacksonConfig` | JSON 序列化配置 |
| `RestTemplateConfig` | HTTP 客户端配置 |
| `WebMvcConfig` | Web MVC 配置 |

---

## 四、配置文件清单

| 文件 | 路径 | 用途 |
|------|------|------|
| `pom.xml` | 根目录 | Maven 依赖配置 |
| `application.yml` | `src/main/resources/` | Spring Boot 主配置 |
| `bootstrap.yml` | `src/main/resources/` | Spring Cloud 启动配置 |
| `logback-spring.xml` | `src/main/resources/` | Logback 日志配置 |
| `app.properties` | `src/main/resources/META-INF/` | Apollo 应用属性 |
| `mapper/*.xml` | `src/main/resources/mapper/` | MyBatis XML 映射 |

---

## 五、外部依赖服务

### 5.1 AI 服务

| 服务名 | 客户端类 | 用途 |
|--------|----------|------|
| Coze API | `CozeAPIConfig` | AI 对话服务 |
| Dify | `DifyClientConfig` | AI 应用服务 |

### 5.2 Feign 远程服务调用清单

| 序号 | 服务名 | 客户端类 | 用途 |
|------|--------|----------|------|
| 1 | `ylwaybillouterapi` | `WaybillFeignClient` | 运单服务 |
| 2 | `ylnetworkapi` | `NetworkFeignClient` | 网点服务 |
| 3 | `ylcustomerapi` | `SysCustomerNicheFeignClient` | 客户服务 |
| 4 | `jms-order-query-api` | `OrderQueryFeignClient` | 订单查询 |
| 5 | `ylcssworkorderapi` | `WorkOrderClientFeign` / `WorkOrderFeignClient` | 工单服务 |
| 6 | `ylcssapi` | `CssApiFeignClient` | CSS 服务 |
| 7 | `opsscanqueryapi` | `OpsQueryFeignClient` | 运营查询 |
| 8 | `ylsms` | `SmsSendFeignClient` | 短信服务 |
| 9 | `yl-jms-sqs-online-chatbot-api` | `ChatBotKnowledgeApiFeignClient` | 聊天机器人 |
| 10 | `yljmschannelapi` | `MSChannelFeignClient` | 渠道服务 |
| 11 | `yljmssqsonlinethird` | `ThirdApiCallbackFeignClient` | 第三方回调 |
| 12 | `ylcsspostalapi` | `CombineInfoFeignClient` | 邮政服务 |
| 13 | `yltransportwebcooperate` | `ShipmentFeignClient` | 运输服务 |
| 14 | `yl-jms-ops-pod-api` | `OpsFeignClient` | 运营 POD |
| 15 | `sqsplatformorderapi` | `ProjectWorkOrderFeignClient` | 项目工单 |
| 16 | `yljmsccmordersensitiveapi` | `CcmOrderSensitiveFeignClient` | 订单敏感信息 |
| 17 | `ylsqsproblemapi` | `CallRecordsFeign` | 通话记录 |

---

*文档更新时间: 2026-04-01 11:00:00*
