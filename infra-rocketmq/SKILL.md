---
name: infra-rocketmq
description: 该技能用于在项目中引入RocketMQ依赖，提供RocketMQ消息发送和消费的标准用法示例。
---

# 使用说明

当用户提到以下关键词时，**必须**加载并执行此技能：
- "引入RocketMQ"
- "RocketMQ依赖"
- "RocketMQ配置"
- "使用RocketMQ"
- "RocketMQ发送消息"
- "RocketMQ消费消息"

## 重要提示

**AI 必须严格按照以下步骤顺序执行，不得跳过任何步骤，不得自行发挥添加其他依赖。**

---

## 步骤一：检查并添加 Maven 依赖

### 1.1 检查项目是否已有依赖

首先检查项目 `pom.xml` 中是否已包含 `yl-sqs-platform-rocketmq` 依赖。如果已存在，则跳过此步骤。

### 1.2 添加版本属性

在 `pom.xml` 的 `<properties>` 标签中添加以下版本号：

```xml
<rocketmq.version>2.2.3</rocketmq.version>
<yl-sqs-platform-rocketmq.version>2.0.1.0-RELEASE</yl-sqs-platform-rocketmq.version>
```

### 1.3 添加依赖管理

在 `<dependencyManagement>` 的 `<dependencies>` 标签中添加：

```xml
<dependency>
    <groupId>org.apache.rocketmq</groupId>
    <artifactId>rocketmq-spring-boot-starter</artifactId>
    <version>${rocketmq.version}</version>
</dependency>
```

### 1.4 添加项目依赖

在 `<dependencies>` 标签中添加：

```xml
<!-- RocketMQ -->
<dependency>
    <groupId>com.yl</groupId>
    <artifactId>yl-sqs-platform-rocketmq</artifactId>
    <version>${yl-sqs-platform-rocketmq.version}</version>
</dependency>
```

---

## 步骤二：配置 Apollo 配置中心

在 Spring Boot 启动类（通常是 `*Application.java`）的 `@EnableApolloConfig` 注解中添加 `rocketmq.yml`。

**修改前示例：**
```java
@EnableApolloConfig(value = {"sqs.common", "dbConnection.yml", "application"})
```

**修改后示例：**
```java
@EnableApolloConfig(value = {"sqs.common", "dbConnection.yml", "application", "rocketmq.yml"})
```

> 注意：只需在 value 数组末尾追加 `"rocketmq.yml"`，保留其他已有配置。

---

## 使用示例

### 示例一：发送 RocketMQ 消息

```java
import com.yl.sqs.platform.rocketmq.publisher.RocketMQDynamicPublisher;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

@Slf4j
@Component
@RequiredArgsConstructor
public class WorkOrderMessageSender {

    private final RocketMQDynamicPublisher rocketMQDynamicPublisher;

    /**
     * 发送工单消息
     * @param dto 消息体
     */
    public void sendWorkOrderMessage(WorkOrderPayload dto) {
        String topic = "sqs-online-session-close-auto-work-order";
        rocketMQDynamicPublisher.syncSend(topic, dto);
        log.info("消息发送成功, topic: {}, payload: {}", topic, dto);
    }
}
```

**说明：**
| 组件 | 说明 |
|------|------|
| `RocketMQDynamicPublisher` | 公司封装的 RocketMQ 发送工具类，通过依赖注入使用 |
| `syncSend(topic, payload)` | 同步发送方法，第一个参数是 Topic 名称，第二个参数是消息体对象 |
| Topic | 消息主题，需要在 Apollo 的 `rocketmq.yml` 中预先配置 |

---

### 示例二：消费 RocketMQ 消息

```java
import com.yl.sqs.platform.rocketmq.annotation.RocketMQDynamicListener;
import com.yl.sqs.platform.rocketmq.model.Message;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Slf4j
@Service
public class WorkOrderMessageConsumer {

    @RocketMQDynamicListener("sqs-online-session-close-auto-work-order")
    public void receive(Message<WorkOrderPayload> message) {
        WorkOrderPayload payload = message.getPayload();
        log.info("收到消息: {}", payload);

        // TODO: 处理业务逻辑
        processWorkOrder(payload);
    }

    private void processWorkOrder(WorkOrderPayload payload) {
        // 业务处理逻辑
    }
}
```

**说明：**
| 组件 | 说明 |
|------|------|
| `@RocketMQDynamicListener` | 消费者监听注解，参数为 Topic 名称 |
| `Message<T>` | 消息包装类，通过 `getPayload()` 获取实际消息体 |
| AOP 限制 | 在该方法上调用同类其他方法时，AOP 代理会失效，如需事务等功能请通过其他类调用 |

---

## 常见问题

### Q1: 如何定义消息体对象？

消息体对象需要实现序列化接口，建议使用 Lombok 简化代码：

```java
import lombok.Data;
import java.io.Serializable;

@Data
public class WorkOrderPayload implements Serializable {
    private static final long serialVersionUID = 1L;

    private String workOrderId;
    private String orderNo;
    private Integer status;
}
```

### Q2: Topic 在哪里配置？

Topic 在 Apollo 配置中心的 `rocketmq.yml` 文件中配置，需要联系运维或项目负责人添加。

### Q3: 发送消息有几种方式？

`RocketMQDynamicPublisher` 提供以下发送方法：

#### 3.1 普通同步发送

```java
// 方式一：直接发送对象
SendResult result = rocketMQDynamicPublisher.syncSend("publisher-name", payload);

// 方式二：发送 Message 对象（可自定义 headers）
Message<WorkOrderPayload> message = MessageBuilder.withPayload(payload).build();
SendResult result = rocketMQDynamicPublisher.syncSend("publisher-name", message);
```

#### 3.2 延迟消息（按延迟级别）

RocketMQ 预设了 18 个延迟级别，对应的延迟时间如下：

| 级别 | 延迟时间 | 级别 | 延迟时间 |
|------|---------|------|---------|
| 1 | 1s | 10 | 6min |
| 2 | 5s | 11 | 7min |
| 3 | 10s | 12 | 8min |
| 4 | 30s | 13 | 9min |
| 5 | 1min | 14 | 10min |
| 6 | 2min | 15 | 20min |
| 7 | 3min | 16 | 30min |
| 8 | 4min | 17 | 1h |
| 9 | 5min | 18 | 2h |

```java
// 使用延迟级别发送
rocketMQDynamicPublisher.syncSendDelayLevel("publisher-name", payload, 3); // 延迟 10s
```

#### 3.3 延迟消息（按指定时间）

```java
// 指定延迟时间（毫秒）
rocketMQDynamicPublisher.syncSendDelayTime("publisher-name", payload, 5000L); // 延迟 5 秒
```

> **注意**：`delayLevel` 和 `delayTime` 不能同时使用，只能选择其一。

#### 方法汇总

| 方法 | 参数 | 说明 |
|------|------|------|
| `syncSend(publisherName, payload)` | 发送者名称, 消息对象 | 普通同步发送 |
| `syncSend(publisherName, message)` | 发送者名称, Message对象 | 普通同步发送，可自定义消息头 |
| `syncSendDelayLevel(publisherName, payload, delayLevel)` | 发送者名称, 消息对象, 延迟级别 | 按级别延迟发送 |
| `syncSendDelayLevel(publisherName, message, delayLevel)` | 发送者名称, Message对象, 延迟级别 | 按级别延迟发送，可自定义消息头 |
| `syncSendDelayTime(publisherName, payload, delayTime)` | 发送者名称, 消息对象, 延迟时间(ms) | 按时间延迟发送 |
| `syncSendDelayTime(publisherName, message, delayTime)` | 发送者名称, Message对象, 延迟时间(ms) | 按时间延迟发送，可自定义消息头 |

---

## 检查清单

完成配置后，请确认以下事项：

- [ ] `pom.xml` 的 properties 中已添加 rocketmq 版本号
- [ ] `pom.xml` 的 dependencyManagement 中已添加 rocketmq-spring-boot-starter
- [ ] `pom.xml` 的 dependencies 中已添加 yl-sqs-platform-rocketmq
- [ ] 启动类的 `@EnableApolloConfig` 中已添加 `rocketmq.yml`
- [ ] 执行 `mvn clean install` 验证依赖是否正确下载