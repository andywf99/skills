# Feign 客户端 Mock 参考

## 依赖声明

```java
@Mock
private OrderFeignClient orderFeignClient;
```

## 必须覆盖三个场景（各自独立测试方法）

### 场景一：正常调用返回 DTO

```java
UserOrderDTO dto = new UserOrderDTO();
dto.setOrderCount(5);
when(orderFeignClient.getUserOrders(1L)).thenReturn(dto);
// 调用后验证被测方法正确读取了 DTO 字段
assertThat(result.getTotalOrders()).isEqualTo(5);
// 纯查询场景豁免 verify，注释说明原因
```

### 场景二：Feign 调用抛出异常（服务不可用）

```java
when(orderFeignClient.getUserOrders(anyLong()))
    .thenThrow(FeignException.serviceUnavailable("order-service down", request, null, null));
assertThatThrownBy(() -> userService.getUserDetail(1L))
    .isInstanceOf(ServiceException.class)
    .hasMessageContaining("订单服务暂不可用");
```

### 场景三：Feign 返回 null（熔断降级）

```java
when(orderFeignClient.getUserOrders(anyLong())).thenReturn(null);
UserDetailVO result = userService.getUserDetail(1L);
// 断言降级时兜底值正确，而非 NPE
assertThat(result.getTotalOrders()).isZero();
```
