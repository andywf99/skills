# MQ Mock 参考

## 核心差异

- **Consumer 是被动触发的**，测试时直接调用 Listener 处理方法，不启动容器。
- **幂等性**是 MQ 独有的必测场景。
- **Producer verify** 必须同时验证 destination + 消息体关键字段。

---

## Producer

> **注意**：Producer 测试仅依赖 Mockito 的 `@Mock` / `when` / `verify`，与 JUnit 版本无关。
> 具体使用的测试注解（`@ExtendWith` 或 `@RunWith`）取决于项目检测到的 JUnit 版本，请参照下方 Consumer 部分的 JUnit 4/5 模板。

### RocketMQ

```java
@Mock
private RocketMQTemplate rocketMQTemplate;
```

**正常发送——verify 必须覆盖 destination + 消息体**：
```java
// 禁止：只验证调用次数
verify(rocketMQTemplate, times(1)).syncSend(any(), any());

// 必须：同时验证 topic:tag 和消息体关键字段
verify(rocketMQTemplate, times(1)).syncSend(
    eq("order-topic:create"),
    argThat((Message<?> msg) -> {
        OrderMessage body = (OrderMessage) msg.getPayload();
        return Objects.equals(body.getOrderId(), 1001L)
            && Objects.equals(body.getStatus(), "CREATED");
    }));
```

**发送失败（MQ 不可用）**：
```java
when(rocketMQTemplate.syncSend(anyString(), any(Message.class)))
    .thenThrow(new MessagingException("broker unavailable"));
assertThatThrownBy(() -> orderService.createOrder(mockOrder))
    .isInstanceOf(ServiceException.class)
    .hasMessageContaining("消息发送失败");
// 验证补偿动作
verify(failedMessageMapper, times(1)).insert(any());
```

### RabbitMQ

```java
@Mock
private RabbitTemplate rabbitTemplate;

verify(rabbitTemplate, times(1)).convertAndSend(
    eq("order.exchange"),
    eq("order.create"),
    argThat((OrderMessage msg) -> Objects.equals(msg.getOrderId(), 1001L)));
```

### Kafka

```java
@Mock
private KafkaTemplate<String, String> kafkaTemplate;

// verify topic + key + value
verify(kafkaTemplate, times(1)).send(
    eq("order-topic"),
    eq("1001"),
    argThat(value -> value.contains("\"orderId\":1001")));
```

---

## Consumer

**核心原则：直接调用 Listener 处理方法，不使用 `@SpringBootTest`。**

### JUnit 5 模式

```java
@ExtendWith(MockitoExtension.class)
class OrderMessageListenerTest {
    @Mock
    private OrderService orderService;
    private OrderMessageListener listener;

    @BeforeEach
    void setUp() {
        listener = new OrderMessageListener(orderService);
    }

    @AfterEach
    void tearDown() {
        // 清理资源、重置状态
    }

    // --- 场景一：正常消费 ---
    @Test
    void onMessage_validMessage_processOrder() {
        listener.onMessage(msg);
        verify(orderService, times(1)).processOrder(
            argThat(order -> Objects.equals(order.getOrderId(), 1001L)));
    }

    // --- 场景二：幂等性——重复消息 ID 不重复执行 ---
    @Test
    void onMessage_duplicateMessageId_skipProcessing() {
        when(messageIdempotentMapper.exists("MSG-001")).thenReturn(true);
        listener.onMessage(msg);
        verify(orderService, never()).processOrder(any());
    }

    // --- 场景三：消费异常——异常被捕获，不向 MQ 框架抛出 ---
    @Test
    void onMessage_processThrowsException_exceptionHandled() {
        doThrow(new ServiceException("库存不足")).when(orderService).processOrder(any());
        assertThatNoException().isThrownBy(() -> listener.onMessage(msg));
        verify(alarmService, times(1)).sendAlert(contains("库存不足"));
    }

    // --- 场景四：消息体字段缺失——非法消息被丢弃 ---
    @Test
    void onMessage_nullOrderId_messageDiscarded() {
        msg.setOrderId(null);
        listener.onMessage(msg);
        verify(orderService, never()).processOrder(any());
    }
}
```

### JUnit 4 模式

```java
@RunWith(MockitoJUnitRunner.class)
public class OrderMessageListenerTest {
    @Mock
    private OrderService orderService;
    private OrderMessageListener listener;

    @Before
    public void setUp() {
        listener = new OrderMessageListener(orderService);
    }

    @After
    public void tearDown() {
        // 清理资源、重置状态
    }

    // --- 场景一：正常消费 ---
    @Test
    public void onMessage_validMessage_processOrder() {
        listener.onMessage(msg);
        verify(orderService, times(1)).processOrder(
            argThat(order -> Objects.equals(order.getOrderId(), 1001L)));
    }

    // --- 场景二：幂等性——重复消息 ID 不重复执行 ---
    @Test
    public void onMessage_duplicateMessageId_skipProcessing() {
        when(messageIdempotentMapper.exists("MSG-001")).thenReturn(true);
        listener.onMessage(msg);
        verify(orderService, never()).processOrder(any());
    }

    // --- 场景三：消费异常——异常被捕获，不向 MQ 框架抛出 ---
    @Test
    public void onMessage_processThrowsException_exceptionHandled() {
        doThrow(new ServiceException("库存不足")).when(orderService).processOrder(any());
        assertThatNoException().isThrownBy(() -> listener.onMessage(msg));
        verify(alarmService, times(1)).sendAlert(contains("库存不足"));
    }

    // --- 场景四：消息体字段缺失——非法消息被丢弃 ---
    @Test
    public void onMessage_nullOrderId_messageDiscarded() {
        msg.setOrderId(null);
        listener.onMessage(msg);
        verify(orderService, never()).processOrder(any());
    }
}
```
