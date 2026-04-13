---
name: java-unit-test
description: Generates Java unit tests for Spring Boot projects following Alibaba naming, JUnit 5/Mockito, Git-diff-only coverage, and JaCoCo. Use when the user asks for unit tests, test generation, coverage, or when writing or reviewing Java/Spring Boot test code.
---

# Java 单元测试生成规范

生成或审查 Java 单元测试时，必须遵循本规范。仅针对「当前分支 vs 基线分支」的 Git diff 变更代码编写测试，不编写存量代码的测试。

---

## 1. 基础规范

### 框架与依赖

- 仅用 JUnit 4（`org.junit.Test`），注解用 `@Test` / `@Before` / `@After`，禁止 JUnit 5。
- 使用 java 8+ 日期时间 API
- 依赖：优先 `spring-boot-starter-test`；未集成时在 POM 中补充 JUnit 与 Mockito，版本与 Spring Boot 匹配。
- 断言：优先 AssertJ；简单场景可用 JUnit 原生断言；禁止混用多种断言风格。
- **静态方法 Mock**：优先使用 PowerMock（`powermock-module-junit4` + `powermock-api-mockito2`），禁止使用 Mockito 3.4+ 的 `MockedStatic`（与 JDK 8/Spring Boot 2.0 不兼容）。

### 测试范围与隔离

- 仅测单个单元（方法/类），不测集成逻辑；不测 getter/setter。
- 覆盖：正常、边界、异常场景；每个 `throw` 语句必须有至少一个独立测试方法对应。
- 依赖隔离：仅用 Mockito 隔离 DB/Redis/第三方接口，禁止连接真实依赖。

### 命名规范（阿里规范）

| 类型       | 规则                                                                 | 示例 |
|------------|----------------------------------------------------------------------|------|
| 测试类名   | 被测类名 + `Test`，大驼峰                                            | `DeviceUploadInfoServiceTest` |
| 测试方法名 | 英文小写 + 下划线，格式：`test_被测方法名_场景_预期结果`              | `test_upload_validParam_returnSuccess` |
| 测试变量   | 小驼峰，语义化                                                        | `expectedUploadResult`、`actualDeviceInfo` |

禁止：测试方法名含中文、无意义命名（如 `test1`、`testUpload1`）。

### 方法规范

- 测试方法：`public void` + `@Test`；**单方法只测一个逻辑点**——禁止将 `amount=null` 和 `amount=0` 两个场景合并写在同一个方法里，每个场景必须是独立的测试方法。
- 前置/后置：JUnit 5 用 `@BeforeEach` / `@AfterEach`，JUnit 4 用 `@Before` / `@After`。
- 禁用测试：`@Disabled` + 中文原因说明。

### 中文注释要求

- **测试类**：类上方 `/** */`，说明「测试范围 + 核心被测逻辑」。
- **测试方法**：方法上方 `/** */`（中文），说明「测试场景 + 覆盖代码行 + 验证点」。
- **关键行**：Mock 配置、断言、异常捕获等加单行 `//` 注释（中文），说明「作用/覆盖场景」。
- 禁止无意义注释（如「创建对象」「调用方法」）；注释需说明「为什么」「覆盖什么」。

---

## 2. Spring Boot + Mockito

- 优先：`@ExtendWith(MockitoExtension.class)` 纯 Mock，`@Mock` 标记依赖，`@InjectMocks` 注入被测类。
- 强依赖 `@Value` / `@Autowired` 时：`@SpringBootTest(classes = {被测类.class})` 最小化容器，`@MockBean` 替换依赖。
- 覆盖配置：`@TestPropertySource`。
- **静态方法 Mock 必须使用 PowerMock**：禁止使用 Mockito 3.4+ 的 `MockedStatic`，改用 `PowerMockito.mockStatic()`。
- **必须追加 `verify()` 验证**：当被测方法调用了 Mock 依赖时，除 `when...thenReturn` 外，必须用 `verify()` 验证依赖被以正确参数调用了正确次数；纯查询场景（只读 get）可豁免，但需注释说明原因。

```java
// 验证 save 被调用一次，且保存的金额与计算结果一致，防止业务逻辑绕过持久化
verify(orderRepository, times(1)).save(argThat(order ->
    order.getAmount().compareTo(new BigDecimal("113.00")) == 0));
```

---

### 2.1 PowerMock 静态方法 Mock 模板

**使用场景**：当被测代码调用了静态方法（如 `SessionUtil.getUser()`、`OtherUserUtils.isBPO()` 等），需要使用 PowerMock 进行 Mock。

**推荐 POM 依赖**（Spring Boot 2.0.x + JDK 8）：
```xml
<!-- PowerMock 核心依赖 -->
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit4</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito2</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
<!-- AssertJ 断言库（可选，但推荐） -->
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.9.1</version>
    <scope>test</scope>
</dependency>
```

**完整测试类模板**：
```java
package com.yl.jms.web.serviceonline.service.report.impl;

import com.yl.jms.web.serviceonline.utils.SessionUtil;
import com.yl.jms.web.serviceonline.model.vo.UserSessionVO;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.powermock.api.mockito.PowerMockito;
import org.powermock.core.classloader.annotations.PrepareForTest;
import org.powermock.modules.junit4.PowerMockRunner;

import java.util.HashMap;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.when;

/**
 * XxxService 单元测试
 * 测试范围：commonQuery 方法（鲲鹏明细通用查询业务逻辑）
 * 覆盖场景：正常查询参数填充、用户信息注入 paramsMap、Feign 调用透传
 */
@RunWith(PowerMockRunner.class)          // 使用 PowerMockRunner
@PrepareForTest({SessionUtil.class})    // 声明需要 Mock 的静态类
public class XxxServiceImplTest {

    @Mock
    private XxxFeignClient xxxFeignClient;

    @InjectMocks
    private XxxServiceImpl service;

    @Before
    public void setUp() {
        // 初始化静态 mock（PowerMock 方式）
        PowerMockito.mockStatic(SessionUtil.class);
    }

    /**
     * 测试 commonQuery 方法 - 正常查询场景
     * 覆盖代码行：XxxServiceImpl 第 28-37 行
     * 验证点：paramsMap 中被注入用户字段，且 Feign 调用使用正确的参数
     */
    @Test
    public void test_commonQuery_validParam_returnFeignResult() {
        // 模拟静态方法返回值
        UserSessionVO mockUser = new UserSessionVO();
        mockUser.setServiceId(100L);
        mockUser.setAccount("testUser001");
        PowerMockito.when(SessionUtil.getUser()).thenReturn(mockUser);

        Map<String, Object> paramsMap = new HashMap<>();
        paramsMap.put("pageNum", 1);

        when(xxxFeignClient.query(anyString(), any(Map.class)))
                .thenReturn(Result.success("data"));

        // 调用被测方法
        Result<Object> actualResult = service.commonQuery("quality", paramsMap);

        // 断言
        assertThat(actualResult.isSucc()).isTrue();
        assertThat(paramsMap).containsEntry("service_id", 100L);
        verify(xxxFeignClient, times(1)).query(eq("quality"), eq(paramsMap));
    }
}
```

**PowerMock 关键点**：
1. `@RunWith(PowerMockRunner.class)` 替代 `MockitoJUnitRunner`
2. `@PrepareForTest({静态类.class})` 声明需要 Mock 的静态工具类
3. `@Before` 中调用 `PowerMockito.mockStatic(静态类.class)` 初始化
4. 测试方法中使用 `PowerMockito.when(静态类.静态方法()).thenReturn(返回值)`
5. 不需要 `@After` 关闭 Mock（PowerMock 自动管理）
6. 禁止使用 `MockedStatic`（Mockito 3.4+ 特性，与老版本不兼容）

**常见静态类示例**：
```java
// SessionUtil
PowerMockito.when(SessionUtil.getUser()).thenReturn(mockUser);

// OtherUserUtils
PowerMockito.when(OtherUserUtils.isBPO()).thenReturn(true);

// GrayUtils（如需 Mock）
PowerMockito.when(GrayUtils.isGray()).thenReturn(true);
```

---

## 3. 断言强度强制要求（高风险，必须遵守）

### 3.1 禁止使用弱断言作为主要断言

以下断言**禁止单独使用**，因为它们无法验证任何业务逻辑：

```java
// 禁止——只要方法不抛异常就能通过，业务公式写错照样绿灯
assertThat(result).isNotNull();
assertThat(result).isPositive();
assertThat(result).isGreaterThan(BigDecimal.ZERO);
assertThat(result).isInstanceOf(SomeClass.class);
```

### 3.2 返回值断言必须对齐具体业务期望值

每个测试方法的核心断言**必须**比对具体期望值，并在注释中写出计算公式：

```java
// amount(100) × quantity(1) × (1 + taxRate_CN 0.13) = 113.00，验证 CN 税率公式正确
assertThat(result).isEqualByComparingTo(new BigDecimal("113.00"));
```

弱断言（`isNotNull` 等）只允许作为辅助验证，且必须同时存在一个强业务断言。

### 3.3 异常断言必须同时验证异常类型和消息

```java
// 禁止——只验证类型，消息写错也通过
assertThatThrownBy(() -> service.foo(null))
    .isInstanceOf(IllegalArgumentException.class);

// 必须——同时验证消息，防止异常分支被张冠李戴
assertThatThrownBy(() -> service.foo(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessage("xxx不能为空");
```

---

## 4. 边界值分析（BVA）规范

对每个数值型边界条件，**必须**覆盖以下测试点，每个点独立一个测试方法：

| 边界位置 | 必测点           | 示例（阈值 = 10）                                    |
|----------|-----------------|------------------------------------------------------|
| 临界下方 | threshold - 1   | `test_calculateTotal_quantity9_noBulkDiscount`       |
| 临界值   | threshold       | `test_calculateTotal_quantity10_applyBulkDiscount`   |
| 临界上方 | threshold + 1   | `test_calculateTotal_quantity11_applyBulkDiscount`（可选）|

对字符串/null 边界：null、空串 `""`、纯空白 `"  "` 必须各自独立覆盖。

---

## 5. 精度与舍入测试规范

当被测方法涉及 BigDecimal 或浮点计算时，**必须**包含：

1. 一个会触发舍入的用例（计算中间结果含超过精度的小数）：
```java
// 100.005 × 1 × 1.13 = 113.00565，HALF_UP 舍入后期望 113.01，验证舍入模式正确
BigDecimal result = service.calculateTotal(new BigDecimal("100.005"), "CN", 1);
assertThat(result).isEqualByComparingTo(new BigDecimal("113.01"));
```
2. BigDecimal 比较**必须**用 `isEqualByComparingTo()`，禁止用 `isEqualTo()`（会比较 scale 导致误判）。

---

## 6. 外部依赖 Mock 规范

### 6.1 Mapper（MyBatis）

**依赖声明：**
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserMapper userMapper;
    @InjectMocks
    private UserService userService;
}
```

**查询场景——必须分别覆盖「记录存在」「记录不存在（null）」「结果为空集合」三个分支：**
```java
// 覆盖"记录存在"分支
when(userMapper.selectById(1L)).thenReturn(mockUser);

// 覆盖"记录不存在"分支——null 与空集合在业务上语义不同，必须各自独立测试
when(userMapper.selectById(99L)).thenReturn(null);

// 覆盖"查询列表为空"分支
when(userMapper.selectList(any())).thenReturn(Collections.emptyList());
```

**写操作——必须覆盖「影响行数=1（成功）」「影响行数=0（失败）」两个分支：**
```java
// MyBatis 写操作返回影响行数，0 表示未命中记录，业务层通常需要分别处理
when(userMapper.updateById(any())).thenReturn(1); // 更新成功
when(userMapper.updateById(any())).thenReturn(0); // 更新失败（记录不存在）
```

**verify() 必须验证到入参字段级别，防止字段被篡改后写库：**
```java
// 禁止——只验证调用次数，参数错误也通过
verify(userMapper, times(1)).insert(any());

// 必须——验证关键字段值正确，覆盖"入参组装逻辑"
verify(userMapper, times(1)).insert(argThat(user ->
    "admin".equals(user.getUsername()) && Integer.valueOf(1).equals(user.getStatus())));
```

---

### 6.2 Feign 客户端

**依赖声明：**
```java
@Mock
private OrderFeignClient orderFeignClient;
```

**必须覆盖以下三个场景，每个场景独立一个测试方法：**

**场景一：正常调用返回 DTO**
```java
// 构造完整的响应对象，断言业务层对 DTO 字段的处理逻辑
UserOrderDTO dto = new UserOrderDTO();
dto.setOrderCount(5);
when(orderFeignClient.getUserOrders(1L)).thenReturn(dto);
// 调用后验证被测方法正确读取了 orderCount 字段
assertThat(result.getTotalOrders()).isEqualTo(5);
// 纯查询场景豁免 verify，注释说明原因：仅读取返回值，无写操作
```

**场景二：Feign 调用抛出异常（服务不可用）**
```java
// 模拟下游服务故障，验证被测方法的异常处理/降级逻辑
when(orderFeignClient.getUserOrders(anyLong()))
    .thenThrow(FeignException.serviceUnavailable("order-service down", request, null, null));
assertThatThrownBy(() -> userService.getUserDetail(1L))
    .isInstanceOf(ServiceException.class)
    .hasMessageContaining("订单服务暂不可用");
```

**场景三：Feign 返回 null（熔断降级）**
```java
// 熔断降级时 Feign 可能返回 null，验证业务层判空保护逻辑
when(orderFeignClient.getUserOrders(anyLong())).thenReturn(null);
UserDetailVO result = userService.getUserDetail(1L);
// 断言降级时订单数兜底为 0，而非 NPE
assertThat(result.getTotalOrders()).isZero();
```

---

### 6.3 Redis（RedisTemplate / StringRedisTemplate）

**依赖声明——必须同时 Mock RedisTemplate 和中间操作对象，否则链式调用 NPE：**
```java
@Mock
private RedisTemplate<String, String> redisTemplate;
@Mock
private ValueOperations<String, String> valueOperations;

@BeforeEach
void setUp() {
    // opsForValue() 返回的中间对象必须提前 Mock，否则 .get()/.set() 调用报 NPE
    when(redisTemplate.opsForValue()).thenReturn(valueOperations);
    userService = new UserService(userMapper, redisTemplate);
}
```

**必须覆盖「缓存命中」「缓存未命中」两个分支，每个分支独立一个测试方法：**

**场景一：缓存命中——不应查 DB，验证 Mapper 未被调用**
```java
// 模拟缓存有数据，被测方法应直接返回，不再穿透到 DB
when(valueOperations.get("user:1")).thenReturn("{\"id\":1,\"username\":\"admin\"}");
UserVO result = userService.getUserById(1L);
assertThat(result.getUsername()).isEqualTo("admin");
// 缓存命中时 Mapper 必须未被调用，验证短路逻辑正确
verify(userMapper, never()).selectById(anyLong());
```

**场景二：缓存未命中——应查 DB 并回写缓存，验证 key/TTL 正确**
```java
// 模拟缓存无数据，被测方法应查 DB 并将结果写入缓存
when(valueOperations.get("user:1")).thenReturn(null);
when(userMapper.selectById(1L)).thenReturn(mockUser);
UserVO result = userService.getUserById(1L);
assertThat(result.getUsername()).isEqualTo("admin");
// 验证缓存 key、value 序列化结果、TTL 三要素，防止配置错误导致缓存永不过期或 key 写错
verify(valueOperations, times(1))
    .set(eq("user:1"), anyString(), eq(30L), eq(TimeUnit.MINUTES));
```

**缓存删除场景——验证 key 正确**
```java
// 验证更新/删除操作后对应的缓存 key 被清除，防止缓存与 DB 数据不一致
verify(redisTemplate, times(1)).delete("user:1");
```

---

### 6.4 MQ（RocketMQ / RabbitMQ / Kafka）

> MQ 与其他外部依赖的核心差异：
> - **消费者是被动触发的**，测试时直接调用 Listener 处理方法，不需要启动容器。
> - **幂等性**是 MQ 独有的必测场景。
> - **Producer verify** 必须同时验证 destination（topic/exchange/queue）、消息体关键字段，仅验证调用次数毫无意义。

#### 生产者（Producer）

**RocketMQ：**
```java
@Mock
private RocketMQTemplate rocketMQTemplate;
@InjectMocks
private OrderService orderService;
```

**场景一：正常发送——verify 必须覆盖 destination + 消息体关键字段**
```java
// 禁止——只验证调用次数，topic 写错或消息体字段漏填也通过
verify(rocketMQTemplate, times(1)).syncSend(any(), any());

// 必须——同时验证 topic:tag 和消息体关键字段，防止消息路由错误
verify(rocketMQTemplate, times(1)).syncSend(
    eq("order-topic:create"),
    argThat((Message<?> msg) -> {
        OrderMessage body = (OrderMessage) msg.getPayload();
        return Objects.equals(body.getOrderId(), 1001L)
            && Objects.equals(body.getStatus(), "CREATED");
    }));
```

**场景二：发送失败（MQ 不可用）——验证业务层补偿/降级逻辑**
```java
// 模拟 MQ Broker 不可用，验证被测方法不抛异常且触发补偿逻辑（如写入失败表）
when(rocketMQTemplate.syncSend(anyString(), any(Message.class)))
    .thenThrow(new MessagingException("broker unavailable"));
assertThatThrownBy(() -> orderService.createOrder(mockOrder))
    .isInstanceOf(ServiceException.class)
    .hasMessageContaining("消息发送失败");
// 验证补偿动作：失败记录写入 DB
verify(failedMessageMapper, times(1)).insert(any());
```

**RabbitMQ：**
```java
@Mock
private RabbitTemplate rabbitTemplate;

// verify exchange + routingKey + 消息体
verify(rabbitTemplate, times(1)).convertAndSend(
    eq("order.exchange"),
    eq("order.create"),
    argThat((OrderMessage msg) -> Objects.equals(msg.getOrderId(), 1001L)));
```

**Kafka：**
```java
@Mock
private KafkaTemplate<String, String> kafkaTemplate;

// verify topic + key + value（key 用于分区路由，不可忽略）
verify(kafkaTemplate, times(1)).send(
    eq("order-topic"),
    eq("1001"),          // partition key，通常为 orderId
    argThat(value -> value.contains("\"orderId\":1001")));
```

---

#### 消费者（Consumer）

**核心原则：直接调用 Listener 的处理方法，不依赖 MQ 容器，不使用 `@SpringBootTest`。**

**RocketMQ Listener 结构：**
```java
@ExtendWith(MockitoExtension.class)
class OrderMessageListenerTest {

    @Mock
    private OrderService orderService;

    // 直接 new Listener，注入 Mock 依赖
    private OrderMessageListener listener;

    @BeforeEach
    void setUp() {
        listener = new OrderMessageListener(orderService);
    }
}
```

**场景一：正常消费——验证业务方法以正确入参被调用**
```java
/**
 * 测试 OrderMessageListener.onMessage-正常消费场景
 * 覆盖代码行：OrderMessageListener 第 35 行
 * 验证点：消息体反序列化正确，orderService.processOrder 以正确 orderId 被调用一次
 */
@Test
void test_onMessage_validMessage_callProcessOrderOnce() {
    OrderMessage msg = new OrderMessage();
    msg.setOrderId(1001L);
    msg.setStatus("CREATED");
    // 直接调用 Listener 方法，模拟 MQ 投递消息
    listener.onMessage(msg);
    // 验证业务方法被以正确 orderId 调用，而非 any()
    verify(orderService, times(1)).processOrder(
        argThat(order -> Objects.equals(order.getOrderId(), 1001L)));
}
```

**场景二：幂等性——同一消息 ID 重复投递，业务逻辑仅执行一次**
```java
/**
 * 测试 OrderMessageListener.onMessage-重复消费场景（幂等性）
 * 覆盖代码行：OrderMessageListener 第 28-32 行（幂等判断分支）
 * 验证点：msgId 相同的消息第二次投递时，业务方法不重复执行
 */
@Test
void test_onMessage_duplicateMessageId_processOrderCalledOnlyOnce() {
    OrderMessage msg = new OrderMessage();
    msg.setMsgId("MSG-20260318-001");
    msg.setOrderId(1001L);
    // 模拟幂等表中已存在该 msgId（第一次已消费）
    when(messageIdempotentMapper.exists("MSG-20260318-001")).thenReturn(true);
    // 第二次投递同一消息
    listener.onMessage(msg);
    // 验证幂等保护生效：业务方法不被重复调用
    verify(orderService, never()).processOrder(any());
}
```

**场景三：消费异常——验证异常处理/死信/告警逻辑**
```java
/**
 * 测试 OrderMessageListener.onMessage-业务处理异常场景
 * 覆盖代码行：OrderMessageListener 第 40-45 行（catch 块）
 * 验证点：业务方法抛出异常时，异常被捕获，告警通知被触发，不向 MQ 框架抛出异常
 */
@Test
void test_onMessage_processOrderThrowException_alarmTriggered() {
    OrderMessage msg = new OrderMessage();
    msg.setOrderId(1001L);
    // 模拟业务处理失败
    doThrow(new ServiceException("库存不足")).when(orderService).processOrder(any());
    // Listener 方法本身不应向外抛出异常（避免无限重试）
    assertThatNoException().isThrownBy(() -> listener.onMessage(msg));
    // 验证告警通知被触发，覆盖 catch 块中的告警逻辑
    verify(alarmService, times(1)).sendAlert(contains("库存不足"));
}
```

**场景四：消息体反序列化异常——格式错误的消息不崩溃**
```java
/**
 * 测试 OrderMessageListener.onMessage-消息体字段缺失场景
 * 覆盖代码行：OrderMessageListener 第 22-26 行（参数校验分支）
 * 验证点：orderId 为 null 的消息被拒绝处理，业务方法不被调用
 */
@Test
void test_onMessage_nullOrderId_processOrderNotCalled() {
    OrderMessage msg = new OrderMessage();
    msg.setOrderId(null); // 模拟上游字段缺失
    listener.onMessage(msg);
    // 非法消息应被丢弃，业务方法不被调用
    verify(orderService, never()).processOrder(any());
}
```

---

#### MQ 单测自检要点

- **Producer**：`verify()` 必须同时断言 destination（topic/exchange/routing key）和消息体关键字段，禁止只用 `any()`
- **Consumer**：直接 `new Listener(mockDependency)` 后调用方法，禁止通过 `@SpringBootTest` 启动容器触发监听
- **幂等性**：必须有重复消息 ID 的测试方法，验证 `verify(service, never())` 不被重复调用
- **消费异常**：验证异常被捕获（`assertThatNoException`），不向 MQ 框架抛出，避免无限重试

---

## 7. Git 增量测试（最高优先级）

- **仅**为「当前分支 vs 基线分支」的 Git diff 变更代码编写测试，不修改、不补测存量代码。
- 存量依赖仅用 Mockito 模拟返回值，不编写存量方法的测试用例。

---

## 8. JaCoCo 覆盖率

- 变更代码：行覆盖率 ≥ 90%，分支覆盖率 ≥ 85%。
- 覆盖所有分支（if/else、异常），禁止空测试或无断言凑覆盖率。
- 未集成 JaCoCo 时：在 POM 中生成 JaCoCo 插件配置（如版本 0.8.7），并输出增量覆盖率报告说明。
   ```
   <plugin>
                   <groupId>org.jacoco</groupId>
                   <artifactId>jacoco-maven-plugin</artifactId>
                   <version>0.8.7</version>
                   <executions>
                       <execution>
                           <id>jacoco-initialize</id>
                           <goals>
                               <goal>prepare-agent</goal>
                           </goals>
                       </execution>
                       <execution>
                           <id>jacoco-site</id>
                           <phase>test</phase>
                           <goals>
                               <goal>report</goal>
                           </goals>
                           <configuration>
                               <dataFile>target/jacoco.exec</dataFile>
                               <outputDirectory>target/jacoco-ut</outputDirectory>
                               <excludes>
                                   <exclude>**/dto/**</exclude>
                                   <exclude>**/vo/**</exclude>
                                   <exclude>**/enums/**</exclude>
                                   <exclude>**/model/**</exclude>
                               </excludes>
                           </configuration>
                       </execution>
                   </executions>
               </plugin>
   ```
**生成测试后必须提供：**

1. **JaCoCo 报告生成命令**（Maven 示例）：
   ```bash
   mvn clean test jacoco:report
   ```
   报告路径：`target/site/jacoco/index.html`。

2. **增量覆盖率查看说明**：打开上述 HTML，定位被测类，对照 Git diff 变更行，确认行覆盖率 ≥ 90%、分支覆盖率 ≥ 85%。

---

## 9. 单测必须可运行且通过

- 无语法错误：import 完整、注解正确、变量合法，能编译通过。
- 无运行时异常：Mock 配置准确、依赖模拟完整，避免 NPE、ClassNotFound 等。
- 无断言失败：断言与场景一致，执行后全部通过。

**若运行失败**：必须给出修复方案——失败原因、修改后的代码片段、修复逻辑说明（中文）。

---

## 9.1 自动运行测试与错误修复流程

**生成测试后必须执行以下步骤：**

### 步骤1：检测 Maven 环境

首先检查系统是否已安装 Maven：

```bash
mvn -v
```

**如果 mvn 命令不存在**：使用 AskUserQuestion 询问用户 Maven 安装地址

```
请提供 Maven 安装地址（例如：C:\apache-maven-3.8.6 或 /usr/local/maven）
```

### 步骤2：运行单元测试

使用以下命令运行测试：

```bash
mvn clean test
```

**可选：指定测试类运行（推荐用于快速验证）**

```bash
mvn clean test -Dtest=XxxServiceImplTest
```

### 步骤3：解析测试结果

**测试通过**：继续步骤4

**测试失败**：根据错误类型自动修复

#### 常见错误类型与自动修复方案

**错误1：编译错误 - 缺少依赖**

```
[ERROR] ... cannot find symbol: class PowerMockRunner
```

**修复方案**：在 pom.xml 中添加 PowerMock 依赖（已在第2.1节提供）

**错误2：NoClassDefFoundError - 运行时类缺失**

```
java.lang.NoClassDefFoundError: org/powermock/modules/junit4/PowerMockRunner
```

**修复方案**：
1. 检查 pom.xml 中 PowerMock 依赖的 scope 是否为 `test`
2. 执行 `mvn clean install -DskipTests` 重新下载依赖
3. 确认依赖版本兼容性（PowerMock 2.0.9 + Spring Boot 2.0.x）

**错误3：NoSuchMethodError - 方法签名不匹配**

```
java.lang.NoSuchMethodError: org.mockito.MockedStatic.when(Ljava/util/function/Function;)
```

**修复方案**：这是 Mockito 版本冲突，检查是否混用了 `MockedStatic` 和 PowerMock，统一使用 PowerMock 处理静态方法

**错误4：初始化错误 - MockStatic 未关闭**

```
The MockedStatic created by mockStatic is not thread-safe and you should not call when on multiple threads
```

**修复方案**：移除 `MockedStatic` 字段和 `@After` 中的 `close()` 调用，改用 PowerMock 的 `@Before` 初始化方式

**错误5：测试失败 - 断言不匹配**

```
test_xxx_validParam_returnSuccess() failed
Expecting: <actual> to be equal to: <expected> but was not.
```

**修复方案**：
1. 检查 Mock 返回值是否与业务逻辑一致
2. 检查被测方法是否被正确调用
3. 添加调试日志或使用 `verify()` 验证调用参数

**错误6：NullPointerException - Mock 未注入**

```
java.lang.NullPointerException at XxxServiceImpl.method()
```

**修复方案**：
1. 确认 `@InjectMocks` 注解在被测类上
2. 确认所有依赖都有 `@Mock` 注解
3. 检查是否使用了 `@RunWith(PowerMockRunner.class)` 而非 `MockitoJUnitRunner`

**错误7：测试类未被扫描 - 命名不规范**

```
No tests were executed for XxxServiceImpl.java
```

**修复方案**：确认测试类命名符合规范（`XxxTest.java`）且位于 `src/test/java` 目录下

**错误8：Surefire fork 失败**

```
The forked VM terminated without properly saying goodbye
```

**修复方案**：在 pom.xml 的 `maven-surefire-plugin` 中设置 `<forkCount>0</forkCount>`

### 步骤4：生成覆盖率报告（可选）

测试通过后生成 JaCoCo 覆盖率报告：

```bash
mvn clean test jacoco:report
```

报告位置：`target/jacoco-ut/index.html`

### 步骤5：验证覆盖率达标

打开报告 HTML，确认：
- 行覆盖率 ≥ 90%
- 分支覆盖率 ≥ 85%

---

## 9.2 自动修复示例

**场景：MockedStatic 与 PowerMock 混用导致错误**

**错误信息**：
```
java.lang.NoSuchMethodError: org.mockito.Mockito.mockStatic
```

**自动修复步骤**：

1. 识别错误：使用了 Mockito 3.4+ 的 `MockedStatic`，但项目依赖的是老版本 Mockito

2. 修改测试类：
```java
// 修改前（错误）
@RunWith(MockitoJUnitRunner.class)
public class XxxTest {
    private MockedStatic<SessionUtil> sessionUtilMock;

    @Before
    public void setUp() {
        sessionUtilMock = mockStatic(SessionUtil.class);
    }

    @After
    public void tearDown() {
        sessionUtilMock.close();
    }

    @Test
    public void test_xxx() {
        sessionUtilMock.when(SessionUtil::getUser).thenReturn(mockUser);
    }
}

// 修改后（正确）
@RunWith(PowerMockRunner.class)
@PrepareForTest({SessionUtil.class})
public class XxxTest {
    @Before
    public void setUp() {
        PowerMockito.mockStatic(SessionUtil.class);
    }

    @Test
    public void test_xxx() {
        PowerMockito.when(SessionUtil.getUser()).thenReturn(mockUser);
    }
}
```

3. 更新 pom.xml（如未添加）：
```xml
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-module-junit4</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
<dependency>
    <groupId>org.powermock</groupId>
    <artifactId>powermock-api-mockito2</artifactId>
    <version>2.0.9</version>
    <scope>test</scope>
</dependency>
```

4. 重新运行测试验证修复

---

## 10. 输出要求

- 生成完整测试类（含全部 import），并标注测试方法对应的 Git 变更行。
- 附带「覆盖率覆盖说明」，说明是否达到行 ≥ 90%、分支 ≥ 85%。
- 未集成依赖/插件时：生成 POM 片段（dependencies/plugins），并标明插入位置。
- 禁止为存量代码生成测试逻辑。
- 注释全部中文，且符合「中文注释强制要求」，注释覆盖所有测试方法与关键行。
- 必须附带：**测试运行命令** + **JaCoCo 报告生成命令**，保证可一键执行。
- 若无法一次通过，需提供修复方案。
- 测试方法名严格遵循：`test_被测方法名_场景_预期结果`，禁止中文命名。

---

## 测试方法命名示例

| 场景     | 示例 |
|----------|------|
| 正常     | `test_upload_validParam_returnSuccess` |
| 异常     | `test_upload_nullParam_throwIllegalArgumentException` |
| 边界     | `test_query_maxId_returnEmpty` |

---

## 注释示例

**测试类：**
```java
/**
 * DeviceUploadInfoService单元测试
 * 测试范围：upload/query/delete等核心业务方法
 * 覆盖场景：正常流程/参数异常/依赖异常
 */
```

**测试方法：**
```java
/**
 * 测试upload方法-参数为空场景
 * 覆盖代码行：DeviceUploadInfoService第45行
 * 验证点：入参为null时抛出IllegalArgumentException
 */
```

**关键行：**
```java
// 模拟Mapper返回空，覆盖“查询无数据”分支
when(deviceUploadInfoMapper.selectById(anyLong())).thenReturn(null);
// 断言异常类型和提示语，验证参数校验逻辑
assertThatThrownBy(() -> service.upload(null))
    .isInstanceOf(IllegalArgumentException.class)
    .hasMessage("上传参数不能为空");
```

---

## 执行清单（生成测试后自检）

**结构层面：**
- [ ] 仅覆盖 Git diff 变更代码，未动存量
- [ ] 测试类/方法/变量命名符合阿里规范，方法名为 `test_xxx_场景_预期`
- [ ] 类、方法、关键行均有中文注释且有意义
- [ ] 使用 JUnit 4 与 Mockito/PowerMock 一致，无混用
- [ ] 已提供测试运行命令与 JaCoCo 报告生成命令
- [ ] 已说明覆盖率是否达标（行 ≥ 90%、分支 ≥ 85%）
- [ ] 测试可本地运行且通过，否则已给出修复方案
- [ ] **PowerMock 检查**：静态方法 Mock 使用 PowerMock 而非 MockedStatic

**自动运行与验证（新增）：**
- [ ] 已检测 Maven 环境（`mvn -v`），如不存在已询问用户安装地址
- [ ] 已执行 `mvn clean test` 运行单元测试
- [ ] 如测试失败，已根据错误类型自动修复（依赖/编译/运行时/断言）
- [ ] 修复后已重新运行测试，确认全部通过
- [ ] 已生成 JaCoCo 覆盖率报告（`mvn clean test jacoco:report`）
- [ ] 已验证覆盖率达标（行 ≥ 90%、分支 ≥ 85%）
- [ ] 已提供测试报告路径（`target/jacoco-ut/index.html`）

**业务语义层面（防止"能跑但没用"）：**
- [ ] 每个测试方法只测一个逻辑点，禁止同一方法内出现多个 `assertThatThrownBy` 或多组参数
- [ ] 每个返回值断言是否为具体业务期望值（非 `isNotNull`/`isPositive` 等弱断言）
- [ ] 异常断言是否同时验证了异常类型和消息内容（`.isInstanceOf().hasMessage()`）
- [ ] 有 Mock 依赖的写操作方法，是否追加了 `verify()` 验证调用次数和参数
- [ ] 每个数值边界是否独立覆盖了「临界值-1」和「临界值」两个测试方法
- [ ] null、空串、纯空白三种边界是否各自有独立测试方法
- [ ] BigDecimal 计算是否有会触发舍入的用例，且使用 `isEqualByComparingTo()` 而非 `isEqualTo()`
- [ ] 每个 `throw` 语句是否有至少一个独立测试方法对应
- [ ] **PowerMock 使用**：静态方法 Mock 使用 `PowerMockito.when(类.方法())` 而非 `mockStatic().when(类::方法)`
- [ ] **PowerMock 配置**：测试类有 `@RunWith(PowerMockRunner.class)` 和 `@PrepareForTest({静态类.class})` 注解
- [ ] **PowerMock 初始化**：`@Before` 方法中调用 `PowerMockito.mockStatic(静态类.class)` 初始化

**外部依赖层面：**
- [ ] Mapper 查询是否覆盖了「记录存在」「null（不存在）」「空集合」三个分支（各自独立方法）
- [ ] Mapper 写操作是否覆盖了「影响行数=1」「影响行数=0」两个分支
- [ ] Mapper 写操作的 `verify()` 是否校验到关键字段值（用 `argThat`），而非只验证调用次数
- [ ] Feign 客户端是否覆盖了「正常返回 DTO」「抛出 FeignException」「返回 null（降级）」三个场景
- [ ] Redis 是否同时 Mock 了 `RedisTemplate` 和 `opsForValue()` 返回的中间操作对象（防 NPE）
- [ ] Redis 缓存是否覆盖了「缓存命中（verify Mapper never 调用）」「缓存未命中（verify Mapper 调用 + 缓存写入）」两个分支
- [ ] Redis 缓存写入的 `verify()` 是否同时验证了 key、value（anyString 可接受）、TTL 和时间单位
- [ ] MQ Producer 的 `verify()` 是否同时验证了 destination（topic/exchange/routing key）和消息体关键字段（禁止只用 `any()`）
- [ ] MQ Producer 发送失败场景是否覆盖，并验证补偿/降级逻辑
- [ ] MQ Consumer 是否直接 `new Listener(mockDep)` 后调用处理方法，而非启动 Spring 容器
- [ ] MQ Consumer 是否有**幂等性**测试方法（重复消息 ID，`verify(service, never())`）
- [ ] MQ Consumer 异常场景是否用 `assertThatNoException` 验证异常被捕获（不向框架抛出避免无限重试）
