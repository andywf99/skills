# Feign 客户端测试参考（JUnit 5）

Feign 客户端测试规范和常见场景，包括正常返回、异常处理、降级等。

## 1. 基础配置

### 测试类结构

```java
package com.yl.cswot.feign;

import com.yl.cswot.feign.xxx.XxxFeignClient;
import com.yl.cswot.feign.xxx.dto.XxxRequest;
import com.yl.cswot.feign.xxx.dto.XxxResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * XxxService单元测试
 * 测试范围：包含 Feign 调用的业务逻辑
 */
@ExtendWith(MockitoExtension.class)
public class XxxServiceTest {

    @Mock
    private XxxFeignClient xxxFeignClient;

    @InjectMocks
    private XxxService xxxService;

    private XxxRequest request;

    @BeforeEach
    public void setUp() {
        request = new XxxRequest();
        request.setId(1L);
        request.setName("测试");
    }
}
```

## 2. 正常场景

### 2.1 成功调用并返回数据

```java
@Test
public void test_callFeign_validParam_returnSuccess() {
    // 准备返回数据
    XxxResponse response = new XxxResponse();
    response.setCode("200");
    response.setMessage("success");
    response.setData("测试数据");

    // 模拟 Feign 调用返回结果
    when(xxxFeignClient.callApi(any(XxxRequest.class))).thenReturn(response);

    // 执行业务方法
    String result = xxxService.doSomething(request);

    // 验证结果
    assertThat(result).isEqualTo("测试数据");

    // 验证 Feign 被调用
    verify(xxxFeignClient, times(1)).callApi(any(XxxRequest.class));
}

@Test
public void test_callFeign_returnList_handleCorrectly() {
    // 准备返回数据
    XxxResponse response = new XxxResponse();
    response.setData(Arrays.asList("数据1", "数据2"));

    // 模拟 Feign 调用返回结果
    when(xxxFeignClient.queryList(any())).thenReturn(response);

    // 执行业务方法
    List<String> result = xxxService.queryData(request);

    // 验证结果
    assertThat(result).isNotNull();
    assertThat(result).hasSize(2);
}
```

### 2.2 返回空数据

```java
@Test
public void test_callFeign_returnEmpty_handleCorrectly() {
    // 准备返回数据
    XxxResponse response = new XxxResponse();
    response.setData(Collections.emptyList());

    // 模拟 Feign 调用返回空列表
    when(xxxFeignClient.queryList(any())).thenReturn(response);

    // 执行业务方法
    List<String> result = xxxService.queryData(request);

    // 验证结果
    assertThat(result).isNotNull();
    assertThat(result).isEmpty();
}

@Test
public void test_callFeign_returnNull_handleCorrectly() {
    // 模拟 Feign 调用返回 null（降级场景）
    when(xxxFeignClient.callApi(any())).thenReturn(null);

    // 执行业务方法
    String result = xxxService.doSomething(request);

    // 验证结果（通常应该返回默认值或抛出异常）
    assertThat(result).isNull();
}
```

## 3. 异常场景

### 3.1 Feign 调用抛出异常

```java
@Test
public void test_callFeign_throwException_handleCorrectly() {
    // 模拟 Feign 调用抛出异常
    when(xxxFeignClient.callApi(any()))
        .thenThrow(new RuntimeException("Feign 调用失败"));

    // 执行业务方法并验证异常
    assertThatThrownBy(() -> xxxService.doSomething(request))
        .isInstanceOf(RuntimeException.class)
        .hasMessageContaining("Feign 调用失败");
}

@Test
public void test_callFeign_timeoutException_handleCorrectly() {
    // 模拟 Feign 超时异常
    when(xxxFeignClient.callApi(any()))
        .thenThrow(new feign.RetryableException("timeout", null));

    // 执行业务方法并验证异常处理
    assertThatThrownBy(() -> xxxService.doSomething(request))
        .isInstanceOf(feign.RetryableException.class);
}
```

### 3.2 业务异常处理

```java
@Test
public void test_callFeign_businessException_returnError() {
    // 准备返回数据（业务错误）
    XxxResponse response = new XxxResponse();
    response.setCode("500");
    response.setMessage("系统错误");

    // 模拟 Feign 调用返回错误响应
    when(xxxFeignClient.callApi(any())).thenReturn(response);

    // 执行业务方法
    String result = xxxService.doSomething(request);

    // 验证结果（通常应该返回错误信息或默认值）
    assertThat(result).isNull();
}
```

## 4. 参数验证

### 4.1 验证请求参数

```java
@Test
public void test_callFeign_verifyRequestParam() {
    // 模拟 Feign 调用
    when(xxxFeignClient.callApi(any())).thenReturn(new XxxResponse());

    // 执行业务方法
    xxxService.doSomething(request);

    // 验证请求参数
    verify(xxxFeignClient, times(1)).callApi(argThat(req ->
        req.getId().equals(1L) && req.getName().equals("测试")
    ));
}
```

## 5. 复杂场景

### 5.1 多次 Feign 调用

```java
@Test
public void test_multipleFeignCalls_allSuccess() {
    // 模拟第一次调用
    XxxResponse response1 = new XxxResponse();
    response1.setData("数据1");

    // 模拟第二次调用
    XxxResponse response2 = new XxxResponse();
    response2.setData("数据2");

    when(xxxFeignClient.callApi(any()))
        .thenReturn(response1)
        .thenReturn(response2);

    // 执行业务方法（会调用两次 Feign）
    xxxService.processMultipleCalls(request);

    // 验证调用次数
    verify(xxxFeignClient, times(2)).callApi(any());
}
```

### 5.2 Feign 调用链

```java
@Test
public void test_feignCallChain_allSuccess() {
    // 模拟第一个 Feign 调用
    XxxResponse response1 = new XxxResponse();
    response1.setData("下一步请求ID");

    when(xxxFeignClient.step1(any())).thenReturn(response1);

    // 模拟第二个 Feign 调用
    XxxResponse response2 = new XxxResponse();
    response2.setData("最终结果");

    when(xxxFeignClient.step2(any())).thenReturn(response2);

    // 执行业务方法（会依次调用两个 Feign）
    String result = xxxService.processChain(request);

    // 验证结果
    assertThat(result).isEqualTo("最终结果");

    // 验证两个 Feign 都被调用
    verify(xxxFeignClient, times(1)).step1(any());
    verify(xxxFeignClient, times(1)).step2(any());
}
```

### 5.3 重试场景

```java
@Test
public void test_feignCallWithRetry_successAfterRetry() {
    // 第一次调用失败，第二次调用成功
    XxxResponse response = new XxxResponse();
    response.setData("成功");

    when(xxxFeignClient.callApi(any()))
        .thenThrow(new RuntimeException("第一次失败"))
        .thenReturn(response);

    // 执行业务方法（包含重试逻辑）
    String result = xxxService.doSomethingWithRetry(request);

    // 验证结果
    assertThat(result).isEqualTo("成功");

    // 验证调用了两次
    verify(xxxFeignClient, times(2)).callApi(any());
}
```

## 6. 熔断降级

### 6.1 熔断开启

```java
@Test
public void test_circuitBreakerOpen_returnFallback() {
    // 模拟熔断器开启，直接返回降级数据
    String fallbackResult = xxxService.doSomethingWithFallback(request);

    // 验证降级结果
    assertThat(fallbackResult).isEqualTo("降级数据");

    // 验证 Feign 未被调用
    verify(xxxFeignClient, never()).callApi(any());
}
```

### 6.2 限流场景

```java
@Test
public void test_rateLimitException_handleCorrectly() {
    // 模拟限流异常
    when(xxxFeignClient.callApi(any()))
        .thenThrow(new RuntimeException("429 Too Many Requests"));

    // 执行业务方法
    String result = xxxService.doSomething(request);

    // 验证结果（通常应该返回限流提示或队列等待）
    assertThat(result).contains("限流");
}
```

## 7. 批量操作

```java
@Test
public void test_batchFeignCalls_allSuccess() {
    // 准备批量请求数据
    List<XxxRequest> requests = Arrays.asList(
        new XxxRequest(1L, "测试1"),
        new XxxRequest(2L, "测试2")
    );

    // 模拟批量调用返回
    XxxResponse response = new XxxResponse();
    response.setData(Arrays.asList("结果1", "结果2"));

    when(xxxFeignClient.batchCall(any())).thenReturn(response);

    // 执行批量业务方法
    List<String> results = xxxService.batchProcess(requests);

    // 验证结果
    assertThat(results).hasSize(2);
}
```

## 8. 最佳实践

1. **完整覆盖三种场景**：正常返回、返回 null、抛出异常
2. **验证参数字段**：使用 `argThat` 验证请求参数，禁止只用 `any()`
3. **异常处理**：验证异常类型和消息内容
4. **降级逻辑**：测试熔断、限流、降级场景
5. **避免真实网络调用**：使用 Mock 模拟所有 Feign 调用
6. **验证调用次数**：确保 Feign 调用次数符合预期
