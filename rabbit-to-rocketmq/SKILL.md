---
name: rabbit-to-rocketmq
description: 该技能用于将 Spring Cloud Stream RabbitMQ 迁移到 RocketMQ，支持灰度切换，实现平滑过渡。
---

# 使用说明

当用户提到以下关键词时，**必须**加载并执行此技能：
- "RabbitMQ切RocketMQ"
- "RabbitMQ切换RocketMQ"
- "Stream迁移RocketMQ"
- "RabbitMQ迁移"

## 前置条件

执行本技能前，请确保项目已完成 RocketMQ 依赖引入。如果未完成，请先执行 `use-rocketmq` 技能。

---

## 迁移工作流程

### 第一步：探索项目结构

在开始迁移前，必须先了解项目现有的 MQ 配置：

1. **查找 Stream 接口定义**
   ```
   搜索 InputInterface.java 和 OutputInterface.java
   ```
   确认所有需要迁移的 input/output 名称。

2. **检查是否已有灰度工具**
   ```
   搜索 RocketMQGrayUtils.java
   搜索 RocketMQDynamicPublisher
   ```
   如果项目中已存在这些类，直接复用；如果不存在，需要创建。

3. **查找消费者代码**
   ```
   搜索 @StreamListener 注解
   ```
   找到所有消费者方法。

4. **查找生产者代码**
   ```
   搜索 @EnableBinding 注解
   搜索 MessageProducer 或类似命名
   ```
   找到所有生产者类。

### 第二步：按用户提供的映射表执行迁移

用户会提供类似以下的映射关系：
```
input/output 名称, 类型, RocketMQ Topic
sqs-smart-workbench-question-answer-record-notice-input, 消费者, sqs-smart-qa-record
sqs-smart-workbench-question-answer-record-notice-output, 生产者, sqs-smart-qa-record
```

### 第三步：修改代码

按照"步骤二"和"步骤三"的模板修改代码。

### 第四步：验证

1. 检查编译是否通过
2. 检查所有消费者是否添加了 `@RocketMQDynamicListener` 注解
3. 检查所有生产者是否使用了 `RocketMQGrayUtils.gray()` 方法

---

## 迁移概述

本迁移方案采用**灰度切换**策略，保留原有 RabbitMQ 代码，新增 RocketMQ 代码，通过配置开关控制使用哪种消息队列，实现平滑过渡。

### 迁移架构

```
                    ┌─────────────────┐
                    │   业务代码       │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ RocketMQGrayUtils│  ← 灰度切换工具
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │ RocketMQ │   │ RabbitMQ │   │  双写    │
        └──────────┘   └──────────┘   └──────────┘
```

---

## 步骤一：创建灰度切换工具类

在项目中创建 `RocketMQGrayUtils` 工具类，用于控制 RocketMQ 和 RabbitMQ 的灰度切换。

```java
package com.yl.sqs.claimworkorder.api.utils;

import com.yl.sqs.gray.common.GraySwitch;
import com.yl.sqs.gray.utils.GrayUtils;
import org.apache.rocketmq.client.producer.SendResult;
import org.apache.rocketmq.client.producer.SendStatus;

import java.util.function.Supplier;

/**
 * RocketMQ/RabbitMQ 灰度切换工具
 */
public class RocketMQGrayUtils {

    /**
     * 灰度发送消息
     *
     * @param topic  Topic 名称
     * @param rocket RocketMQ 发送逻辑
     * @param rabbit RabbitMQ 发送逻辑
     * @return 发送结果
     */
    public static Boolean gray(String topic, Supplier<SendResult> rocket, Supplier<Boolean> rabbit) {
        String key = "gray-switch.rocketmq." + topic;

        boolean hasEnableRocketOrRabbit = false;
        boolean result = false;

        // RocketMQ 开关
        if (GrayUtils.isGray(GraySwitch.of(key + ".rocket", "RocketMQ 灰度开关", false))) {
            hasEnableRocketOrRabbit = true;
            if (rocket.get().getSendStatus() == SendStatus.SEND_OK) {
                result = true;
            }
        }

        // RabbitMQ 开关
        if (GrayUtils.isGray(GraySwitch.of(key + ".rabbit", "RabbitMQ 灰度开关", true))) {
            hasEnableRocketOrRabbit = true;
            if (rabbit.get()) {
                result = true;
            }
        }

        // 如果两个开关都未开启，则双写
        if (!hasEnableRocketOrRabbit) {
            Boolean b = rocket.get().getSendStatus() == SendStatus.SEND_OK;
            Boolean b1 = rabbit.get();
            result = b && b1;
        }

        return result;
    }
}
```

---

## 步骤二：修改生产者代码

### 2.1 修改前（原始 RabbitMQ 代码）

```java
@Component
@Slf4j
@EnableBinding(value = {OutputInterface.class})
public class ClaimMessageProducer {

    @Autowired
    private OutputInterface outputInterface;

    public void sendMessage(MessageDTO messageInfo) {
        Message<MessageDTO> message = MessageBuilder.withPayload(messageInfo).build();
        log.info("sendMessage message:[{}]", JSON.toJSONString(message));
        boolean send = outputInterface.sendMessage().send(message);
        log.info("sendMessage result:{}", send);
    }
}
```

### 2.2 修改后（支持灰度切换）

```java
@Component
@Slf4j
@EnableBinding(value = {OutputInterface.class})
public class ClaimMessageProducer {

    @Autowired
    private OutputInterface outputInterface;

    @Resource
    private RocketMQDynamicPublisher rocketMQDynamicPublisher;

    /**
     * 普通消息发送
     */
    public void sendMessage(MessageDTO messageInfo) {
        Message<MessageDTO> message = MessageBuilder.withPayload(messageInfo).build();
        log.info("sendMessage message:[{}]", JSON.toJSONString(message));

        String topic = "sqs-claim-message";

        Boolean result = RocketMQGrayUtils.gray(topic,
                () -> rocketMQDynamicPublisher.syncSend(topic, messageInfo),
                () -> outputInterface.sendMessage().send(message));

        log.info("sendMessage result:{}", result);
    }

    /**
     * 延迟消息发送
     */
    public void sendDelayMessage(MessageDTO messageInfo, Integer delayTime) {
        Message<MessageDTO> message = MessageBuilder.withPayload(messageInfo)
                .setHeader("x-delay", delayTime)
                .build();
        log.info("sendDelayMessage message:[{}]", JSON.toJSONString(message));

        String topic = "sqs-claim-delay-message";

        Boolean result = RocketMQGrayUtils.gray(topic,
                () -> rocketMQDynamicPublisher.syncSendDelayTime(topic, messageInfo, delayTime.longValue()),
                () -> outputInterface.sendDelayMessage().send(message));

        log.info("sendDelayMessage result:{}", result);
    }
}
```

---

## 步骤三：修改消费者代码

### 3.1 修改前（原始 RabbitMQ 代码）

```java
@Slf4j
@Component
@EnableBinding(InputInterface.class)
public class ClaimMessageListener {

    @Autowired
    private IAsyncService iAsyncService;

    @StreamListener(InputInterface.MESSAGE_INPUT)
    public void acceptMessage(Message<MessageDTO> entityMessage) {
        MessageDTO dto = entityMessage.getPayload();
        log.info("收到消息: {}", dto);

        // 业务处理
        iAsyncService.process(dto);
    }
}
```

### 3.2 修改后（同时支持 RocketMQ 和 RabbitMQ）

在原有消费者方法上添加 `@RocketMQDynamicListener` 注解，实现同时监听两个消息队列：

```java
@Slf4j
@Component
@EnableBinding(InputInterface.class)
public class ClaimMessageListener {

    @Autowired
    private IAsyncService iAsyncService;

    /**
     * 同时监听 RocketMQ 和 RabbitMQ
     * 注意：RocketMQ 消息体类型需要与 RabbitMQ 一致
     */
    @RocketMQDynamicListener("sqs-claim-message")
    @StreamListener(InputInterface.MESSAGE_INPUT)
    public void acceptMessage(Message<MessageDTO> entityMessage) {
        MessageDTO dto = entityMessage.getPayload();
        log.info("收到消息: {}", dto);

        // 业务处理
        iAsyncService.process(dto);
    }
}
```

---

## 步骤四：配置灰度开关

在 Apollo 配置中心添加灰度开关配置：

### 4.1 配置格式

```yaml
gray-switch:
  rocketmq:
    # Topic 名称
    sqs-claim-message:
      rocket: false  # RocketMQ 开关，false 表示关闭
      rabbit: true   # RabbitMQ 开关，true 表示开启
    sqs-claim-delay-message:
      rocket: false
      rabbit: true
```

### 4.2 切换策略

| 阶段 | rocket 开关 | rabbit 开关 | 说明 |
|------|------------|------------|------|
| 初始状态 | false | true | 仅使用 RabbitMQ |
| 灰度验证 | true | true | 双写，同时发送到两个队列 |
| 切换阶段 | true | false | 仅使用 RocketMQ |
| 完成迁移 | true | false | 可移除 RabbitMQ 代码 |

---

## 迁移对照表

### Stream 名称与 Topic 映射

根据用户提供的映射关系，AI 需要自动转换：

| RabbitMQ Stream | 类型 | RocketMQ Topic |
|-----------------|------|----------------|
| `xxx-output` | 生产者 | `topic-name` |
| `xxx-input` | 消费者 | `topic-name` |

### 生产者转换模板

```java
// 转换前
outputInterface.xxxOutput().send(message);

// 转换后
RocketMQGrayUtils.gray("topic-name",
    () -> rocketMQDynamicPublisher.syncSend("topic-name", payload),
    () -> outputInterface.xxxOutput().send(message));
```

### 消费者转换模板

```java
// 转换前
@StreamListener(InputInterface.XXX_INPUT)
public void consume(Message<T> message) { ... }

// 转换后
@RocketMQDynamicListener("topic-name")
@StreamListener(InputInterface.XXX_INPUT)
public void consume(Message<T> message) { ... }
```

---

## 注意事项

### 1. 消息体类型一致性

RocketMQ 和 RabbitMQ 的消费者方法接收的消息体类型必须一致：

```java
// 正确：两者都使用相同的 DTO
@RocketMQDynamicListener("topic")
@StreamListener(InputInterface.XXX)
public void consume(Message<MessageDTO> message) { }

// 错误：RocketMQ 用 DTO，RabbitMQ 用 String
@RocketMQDynamicListener("topic")
public void consumeRocket(Message<MessageDTO> message) { }

@StreamListener(InputInterface.XXX)
public void consumeRabbit(Message<String> message) { }  // 类型不一致！
```

### 2. 延迟消息

RabbitMQ 使用 `x-delay` header 实现延迟，RocketMQ 使用 `syncSendDelayTime` 或 `syncSendDelayLevel` 方法：

```java
// RabbitMQ 延迟
Message<MessageDTO> message = MessageBuilder.withPayload(dto)
    .setHeader("x-delay", 10000)  // 10秒延迟
    .build();

// RocketMQ 延迟
rocketMQDynamicPublisher.syncSendDelayTime("topic", dto, 10000L);
```

### 3. AOP 失效问题

`@RocketMQDynamicListener` 注解的方法在同一类内部调用时 AOP 会失效，如需事务等功能请通过其他类调用。

### 4. 消息确认机制

RabbitMQ 需要手动 ACK/NACK，RocketMQ 会自动重试：

```java
// RabbitMQ 手动确认
Channel channel = message.getHeaders().get(AmqpHeaders.CHANNEL, Channel.class);
Long deliveryTag = message.getHeaders().get(AmqpHeaders.DELIVERY_TAG, Long.class);
channel.basicAck(deliveryTag, false);

// RocketMQ 抛出异常即可触发重试
throw new RuntimeException("处理失败");
```

### 5. 关键类和注解说明

| 类/注解 | 包路径 | 用途 |
|--------|-------|------|
| `RocketMQGrayUtils` | 项目 utils 包 | 生产者灰度切换工具 |
| `RocketMQDynamicPublisher` | `com.yl.sqs.dynamic_rocketmq.core` | RocketMQ 消息发送器 |
| `@RocketMQDynamicListener` | `com.yl.sqs.dynamic_rocketmq.annotation` | 消费者灰度监听注解 |
| `GrayUtils` | `com.yl.sqs.gray.utils` | 灰度开关判断工具 |
| `GraySwitch` | `com.yl.sqs.gray.common` | 灰度开关配置模型 |

### 6. 迁移过程中的常见问题

**问题1：找不到 RocketMQDynamicPublisher**
- 原因：未引入 `yl-sqs-platform-rocketmq` 依赖
- 解决：检查 pom.xml 中是否添加了依赖

**问题2：消费者收不到 RocketMQ 消息**
- 原因：Apollo 中未配置 RocketMQ 相关配置
- 解决：在 `rocketmq.yml` 中配置 nameserver 等信息

**问题3：灰度开关不生效**
- 原因：配置 key 格式错误
- 解决：确保配置 key 格式为 `gray-switch.rocketmq.{topic}.rocket`

**问题4：消息序列化失败**
- 原因：消息体类型不一致或缺少无参构造函数
- 解决：确保 DTO 类有无参构造函数，且 RocketMQ 和 RabbitMQ 使用相同类型

---

## 检查清单

完成迁移后，请确认以下事项：

- [ ] 已创建 `RocketMQGrayUtils` 灰度切换工具类
- [ ] 生产者已添加 `RocketMQDynamicPublisher` 注入
- [ ] 生产者发送方法已改为 `RocketMQGrayUtils.gray()` 方式
- [ ] 消费者已添加 `@RocketMQDynamicListener` 注解
- [ ] Apollo 中已配置灰度开关
- [ ] 延迟消息类型已正确转换
- [ ] 消息体类型保持一致

---

## 完整示例

### 迁移需求示例

```
rabbit stream,type,rocket topic
css-fastclaim-add-arbitration-output,生产者,sqs-claim-add-arbitration
css-fastclaim-add-arbitration-input,消费者,sqs-claim-add-arbitration
css-fastclaim-add-claimdetail-output,生产者,sqs-claim-add-detail
css-fastclaim-add-claimdetail-input,消费者,sqs-claim-add-detail
```

### 生产者代码示例

```java
// 发送仲裁消息（延迟消息）
public void sendArbitratioMessage(FastClaimMessageDTO messageInfo, Integer networkType) {
    Integer delayTime = networkType == 1 ? arbitrationDelayTime : arbiAgentDelayTime;
    Message<FastClaimMessageDTO> message = MessageBuilder.withPayload(messageInfo)
            .setHeader("x-delay", delayTime)
            .build();
    log.info("sendArbitratioMessage message:[{}]", JSON.toJSONString(message));

    boolean send = RocketMQGrayUtils.gray("sqs-claim-add-arbitration",
            () -> rocketMQDynamicPublisher.syncSendDelayTime("sqs-claim-add-arbitration", messageInfo, delayTime.longValue()),
            () -> outputInterface.sendArbitratioMessage().send(message));

    log.info("sendArbitratioMessage message.result:{}", send);
}

// 发送理赔明细消息（延迟消息）
public void sendClaimDetailMessage(FastClaimMessageDTO messageInfo) {
    Message<FastClaimMessageDTO> message = MessageBuilder.withPayload(messageInfo)
            .setHeader("x-delay", 10000)
            .build();
    log.info("sendClaimDetailMessage message:[{}]", JSON.toJSONString(message));

    Boolean result = RocketMQGrayUtils.gray("sqs-claim-add-detail",
            () -> rocketMQDynamicPublisher.syncSend("sqs-claim-add-detail", messageInfo),
            () -> outputInterface.sendClaimDetailMessage().send(message));

    log.info("sendClaimDetailMessage result:{}", result);
}
```

### 消费者代码示例

```java
/**
 * 消费极速理赔新增仲裁消息
 */
@RocketMQDynamicListener("sqs-claim-add-arbitration")
@StreamListener(InputInterface.CLAIM_ADD_ARBITRATION_INPUT)
public void acceptAddArbitration(Message<FastClaimMessageDTO> entityMessage) {
    FastClaimMessageDTO addDTO = entityMessage.getPayload();
    log.info("ClaimMessageListener.acceptAddArbitration-监听到的数据:{}", JsonUtils.toJson(addDTO));

    // 业务处理
    iAsyncService.addArbitrationByClaim(addDTO.getFastClaimWorkOrder(), addDTO.getDto());
}

/**
 * 消费极速理赔新增线上理赔消息
 */
@RocketMQDynamicListener("sqs-claim-add-detail")
@StreamListener(InputInterface.CLAIM_ADD_CLAIMDETAIL_INPUT)
public void acceptAddClaimDetail(Message<String> entityMessage) {
    FastClaimMessageDTO addDTO = JsonUtils.toBean(entityMessage.getPayload(), FastClaimMessageDTO.class);
    log.info("ClaimMessageListener.acceptAddClaimDetail-监听到的数据:{}", JsonUtils.toJson(addDTO));

    // 业务处理
    iAsyncService.addClaimDetailByClaim(addDTO.getFastClaimWorkOrder(), addDTO.getDto());
}
```