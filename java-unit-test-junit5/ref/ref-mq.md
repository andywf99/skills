# MQ 测试参考（JUnit 5）

消息队列测试规范，包括 Spring Cloud Stream、RocketMQ、RabbitMQ 等场景。

## 1. Producer 测试（消息发送）

### 1.1 基础配置

```java
package com.yl.cswot.stream;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * XxxProducer单元测试
 * 测试范围：消息发送
 */
@ExtendWith(MockitoExtension.class)
public class XxxProducerTest {

    @Mock
    private MessageChannel messageChannel;

    @InjectMocks
    private XxxProducer xxxProducer;
}
```

### 1.2 发送消息成功

```java
@Test
public void test_sendMessage_validParam_sendSuccessfully() {
    // 准备测试数据
    String payload = "测试消息";

    // 模拟发送成功
    when(messageChannel.send(any(Message.class))).thenReturn(true);

    // 执行发送
    boolean result = xxxProducer.sendMessage(payload);

    // 验证结果
    assertThat(result).isTrue();

    // 验证发送方法被调用
    verify(messageChannel, times(1)).send(any(Message.class));
}

@Test
public void test_sendMessage_verifyMessageContent() {
    // 准备测试数据
    XxxPayload payload = new XxxPayload();
    payload.setId(1L);
    payload.setContent("测试内容");

    // 模拟发送成功
    when(messageChannel.send(any(Message.class))).thenReturn(true);

    // 执行发送
    xxxProducer.sendMessage(payload);

    // 捕获消息内容
    ArgumentCaptor<Message<XxxPayload>> messageCaptor = ArgumentCaptor.forClass(Message.class);
    verify(messageChannel).send(messageCaptor.capture());

    // 验证消息内容
    Message<XxxPayload> capturedMessage = messageCaptor.getValue();
    assertThat(capturedMessage.getPayload()).isNotNull();
    assertThat(capturedMessage.getPayload().getId()).isEqualTo(1L);
    assertThat(capturedMessage.getPayload().getContent()).isEqualTo("测试内容");
}
```

### 1.3 发送消息失败

```java
@Test
public void test_sendMessage_sendFailed_returnFalse() {
    // 模拟发送失败
    when(messageChannel.send(any(Message.class))).thenReturn(false);

    // 执行发送
    boolean result = xxxProducer.sendMessage("测试消息");

    // 验证结果
    assertThat(result).isFalse();
}

@Test
public void test_sendMessage_throwException_handleCorrectly() {
    // 模拟发送抛出异常
    when(messageChannel.send(any(Message.class)))
        .thenThrow new RuntimeException("MQ 连接失败"));

    // 执行发送并验证异常处理
    assertThatThrownBy(() -> xxxProducer.sendMessage("测试消息"))
        .isInstanceOf(RuntimeException.class)
        .hasMessageContaining("MQ 连接失败");
}
```

### 1.4 批量发送

```java
@Test
public void test_sendBatchMessages_validParams_sendAllSuccessfully() {
    // 准备测试数据
    List<String> messages = Arrays.asList("消息1", "消息2", "消息3");

    // 模拟全部发送成功
    when(messageChannel.send(any(Message.class))).thenReturn(true);

    // 执行批量发送
    int successCount = xxxProducer.sendBatchMessages(messages);

    // 验证结果
    assertThat(successCount).isEqualTo(3);

    // 验证发送方法被调用3次
    verify(messageChannel, times(3)).send(any(Message.class));
}
```

## 2. Consumer 测试（消息消费）

### 2.1 基础配置

```java
package com.yl.cswot.stream;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

/**
 * XxxListener单元测试
 * 测试范围：消息消费处理
 */
@ExtendWith(MockitoExtension.class)
public class XxxListenerTest {

    @Mock
    private XxxService xxxService;

    @InjectMocks
    private XxxListener xxxListener;
}
```

### 2.2 正常消费

```java
@Test
public void test_handleMessage_validMessage_processSuccessfully() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);
    message.setContent("测试消息");

    // 模拟业务处理成功
    doNothing().when(xxxService).processMessage(any(XxxMessage.class));

    // 执行消费
    xxxListener.handleMessage(message);

    // 验证业务方法被调用
    verify(xxxService, times(1)).processMessage(argThat(msg ->
        msg.getId().equals(1L) && msg.getContent().equals("测试消息")
    ));
}
```

### 2.3 消息幂等性

```java
@Test
public void test_handleMessage_duplicateMessage_ignoreSecondProcess() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);
    message.setMessageId("msg-001");

    // 模拟第一次处理成功
    when(xxxService.isProcessed("msg-001")).thenReturn(true);

    // 执行消费
    xxxListener.handleMessage(message);

    // 验证业务处理方法未被调用（已处理过）
    verify(xxxService, never()).processMessage(any(XxxMessage.class));
}

@Test
public void test_handleMessage_firstTime_processAndRecord() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);
    message.setMessageId("msg-001");

    // 模拟未处理过
    when(xxxService.isProcessed("msg-001")).thenReturn(false);
    doNothing().when(xxxService).processMessage(any(XxxMessage.class));
    doNothing().when(xxxService).markAsProcessed("msg-001");

    // 执行消费
    xxxListener.handleMessage(message);

    // 验证处理并标记
    verify(xxxService, times(1)).processMessage(message);
    verify(xxxService, times(1)).markAsProcessed("msg-001");
}
```

### 2.4 异常处理

```java
@Test
public void test_handleMessage_processException_shouldRequeue() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);

    // 模拟业务处理抛出异常
    doThrow(new RuntimeException("处理失败"))
        .when(xxxService).processMessage(any(XxxMessage.class));

    // 执行消费并验证异常
    assertThatThrownBy(() -> xxxListener.handleMessage(message))
        .isInstanceOf(RuntimeException.class);

    // 验证业务方法被调用
    verify(xxxService, times(1)).processMessage(message);
}

@Test
public void test_handleMessage_businessException_ignoreAndContinue() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);

    // 模拟业务异常（不需要重试）
    doThrow(new BusinessException("业务异常，不重试"))
        .when(xxxService).processMessage(any(XxxMessage.class));

    // 执行消费
    xxxListener.handleMessage(message);

    // 验证异常被捕获，不抛出（根据实际业务逻辑调整）
}
```

## 3. RocketMQ 特定场景

### 3.1 事务消息

```java
@Test
public void test_sendTransactionMessage_validParam_sendSuccessfully() {
    // 准备测试数据
    TransactionMessage message = new TransactionMessage();
    message.setId(1L);

    // 模拟发送事务消息成功
    when(rocketMQTemplate.sendMessageInTransaction(
        any(), any(), any()
    )).thenReturn(new SendResult(SendStatus.SEND_OK));

    // 执行发送
    SendResult result = xxxProducer.sendTransactionMessage(message);

    // 验证结果
    assertThat(result.getSendStatus()).isEqualTo(SendStatus.SEND_OK);
}
```

### 3.2 延迟消息

```java
@Test
public void test_sendDelayMessage_validParam_sendSuccessfully() {
    // 准备测试数据
    DelayMessage message = new DelayMessage();
    message.setId(1L);
    message.setDelayLevel(3); // 延迟级别

    // 模拟发送延迟消息成功
    when(rocketMQTemplate.syncSend(any(), any(), anyLong())).thenReturn(new SendResult(SendStatus.SEND_OK));

    // 执行发送
    SendResult result = xxxProducer.sendDelayMessage(message);

    // 验证结果
    assertThat(result.getSendStatus()).isEqualTo(SendStatus.SEND_OK);

    // 验证延迟级别被正确设置
    verify(rocketMQTemplate, times(1)).syncStart(any(), argThat(msg ->
        msg.getDelayTimeLevel() == 3
    ), anyLong());
}
```

## 4. Spring Cloud Stream 场景

### 4.1 多 Output 绑定

```java
@Test
public void test_sendToMultipleOutputs_validParams_sendAllSuccessfully() {
    // 准备测试数据
    String message = "测试消息";

    // 模拟多个输出通道
    MessageChannel output1 = mock(MessageChannel.class);
    MessageChannel output2 = mock(MessageChannel.class);

    when(output1.send(any(Message.class))).thenReturn(true);
    when(output2.send(any(Message.class))).thenReturn(true);

    // 执行发送到多个输出
    xxxProducer.sendToMultipleOutputs(message);

    // 验证两个输出都被调用
    verify(output1, times(1)).send(any(Message.class));
    verify(output2, times(1)).send(any(Message.class));
}
```

### 4.2 条件路由

```java
@Test
public void test_conditionalRoute_conditionMatch_sendToCorrectOutput() {
    // 准备测试数据
    RoutingMessage message = new RoutingMessage();
    message.setType("A");

    // 模拟路由判断
    MessageChannel outputA = mock(MessageChannel.class);
    when(outputA.send(any(Message.class))).thenReturn(true);

    // 执行条件路由发送
    xxxProducer.sendWithRouting(message);

    // 验证发送到正确的输出
    verify(outputA, times(1)).send(any(Message.class));
    verify(outputB, never()).send(any(Message.class));
}
```

## 5. 消息重试场景

```java
@Test
public void test_handleMessageWithRetry_retryWithinLimit_successAfterRetry() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);

    // 第一次失败，第二次成功
    doThrow(new RuntimeException("第一次失败"))
        .doNothing()
        .when(xxxService).processMessage(any(XxxMessage.class));

    // 执行消费（包含重试逻辑）
    xxxListener.handleMessageWithRetry(message);

    // 验证重试了两次
    verify(xxxService, times(2)).processMessage(message);
}

@Test
public void test_handleMessageWithRetry_exceedRetryLimit_shouldDiscard() {
    // 准备测试数据
    XxxMessage message = new XxxMessage();
    message.setId(1L);

    // 始终失败
    doThrow(new RuntimeException("持续失败"))
        .when(xxxService).processMessage(any(XxxMessage.class));

    // 执行消费
    xxxListener.handleMessageWithRetry(message);

    // 验证重试了指定次数（如3次）
    verify(xxxService, times(3)).processMessage(message);
}
```

## 6. 最佳实践

### Producer 测试
1. **验证消息内容**：使用 `ArgumentCaptor` 捕获并验证消息体
2. **验证 destination**：确保消息发送到正确的 topic/queue
3. **测试发送失败**：验证失败处理逻辑
4. **避免真实连接**：使用 Mock 模拟 MessageChannel

### Consumer 测试
1. **测试幂等性**：验证重复消息的处理
2. **测试异常处理**：验证不同异常的处理策略
3. **验证业务调用**：使用 `argThat` 验证参数
4. **测试重试机制**：验证重试次数和最终结果

### 通用规则
1. **禁止真实 MQ 连接**：使用 Mock 模拟所有 MQ 操作
2. **验证消息格式**：确保消息序列化/反序列化正确
3. **测试并发场景**：如有需要，测试并发消费
4. **验证事务**：测试事务消息的提交和回滚
