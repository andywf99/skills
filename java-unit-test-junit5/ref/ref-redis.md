# Redis 测试参考（JUnit 5）

Redis 操作测试规范和常见场景，包括缓存命中、未命中、过期等。

## 1. 基础配置

### 测试类结构

```java
package com.yl.cswot.service;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.data.redis.core.ValueOperations;

import java.util.concurrent.TimeUnit;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyLong;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.*;

/**
 * XxxService单元测试
 * 测试范围：包含 Redis 操作的业务逻辑
 */
@ExtendWith(MockitoExtension.class)
public class XxxServiceTest {

    @Mock
    private RedisTemplate<String, Object> redisTemplate;

    @Mock
    private ValueOperations<String, Object> valueOperations;

    @InjectMocks
    private XxxService xxxService;

    @BeforeEach
    public void setUp() {
        // Mock RedisTemplate 的 opsForValue() 方法
        when(redisTemplate.opsForValue()).thenReturn(valueOperations);
    }
}
```

## 2. 缓存读取场景

### 2.1 缓存命中

```java
@Test
public void test_getFromCache_cacheHit_returnCachedValue() {
    String cacheKey = "test:key";
    String expectedValue = "缓存值";

    // 模拟缓存命中
    when(valueOperations.get(cacheKey)).thenReturn(expectedValue);

    // 执行查询
    String result = xxxService.getDataFromCache(cacheKey);

    // 验证结果
    assertThat(result).isEqualTo(expectedValue);

    // 验证只查询了缓存，未查询数据库
    verify(valueOperations, times(1)).get(cacheKey);
    verify(valueOperations, never()).set(anyString(), any());
}
```

### 2.2 缓存未命中

```java
@Test
public void test_getFromCache_cacheMiss_queryDatabaseAndSetCache() {
    String cacheKey = "test:key";
    String dbValue = "数据库值";

    // 模拟缓存未命中（返回 null）
    when(valueOperations.get(cacheKey)).thenReturn(null);

    // 执行查询（会查询数据库并设置缓存）
    String result = xxxService.getDataFromCache(cacheKey);

    // 验证结果
    assertThat(result).isEqualTo(dbValue);

    // 验证查询了缓存，然后设置了缓存
    verify(valueOperations, times(1)).get(cacheKey);
    verify(valueOperations, times(1)).set(anyString(), any());
}
```

### 2.3 缓存空值

```java
@Test
public void test_getFromCache_cacheNullValue_returnNull() {
    String cacheKey = "test:key";

    // 模拟缓存中存储了空值（用于防止缓存穿透）
    when(valueOperations.get(cacheKey)).thenReturn("");

    // 执行查询
    String result = xxxService.getDataFromCache(cacheKey);

    // 验证结果
    assertThat(result).isNull();

    // 验证只查询了缓存，未查询数据库
    verify(valueOperations, times(1)).get(cacheKey);
}
```

## 3. 缓存写入场景

### 3.1 写入缓存

```java
@Test
public void test_setToCache_validParam_setSuccessfully() {
    String cacheKey = "test:key";
    String value = "缓存值";
    long expireTime = 3600L;

    // 执行写入缓存
    xxxService.setDataToCache(cacheKey, value, expireTime);

    // 验证调用了 Redis 设置方法
    verify(valueOperations, times(1)).set(cacheKey, value, expireTime, TimeUnit.SECONDS);
}

@Test
public void test_setToCache_withDefaultExpire_setSuccessfully() {
    String cacheKey = "test:key";
    String value = "缓存值";

    // 执行写入缓存（使用默认过期时间）
    xxxService.setDataToCache(cacheKey, value);

    // 验证调用了 Redis 设置方法
    verify(valueOperations, times(1)).set(eq(cacheKey), eq(value), anyLong(), any(TimeUnit.class));
}
```

### 3.2 批量写入

```java
@Test
public void test_setBatchToCache_validParams_setAllSuccessfully() {
    Map<String, Object> cacheMap = new HashMap<>();
    cacheMap.put("key1", "value1");
    cacheMap.put("key2", "value2");

    // 执行批量写入
    xxxService.setBatchDataToCache(cacheMap);

    // 验证每个 key 都被设置
    verify(valueOperations, times(1)).set("key1", "value1", anyLong(), any(TimeUnit.class));
    verify(valueOperations, times(1)).set("key2", "value2", anyLong(), any(TimeUnit.class));
}
```

## 4. 缓存删除场景

### 4.1 删除单个缓存

```java
@Test
public void test_deleteFromCache_validKey_deleteSuccessfully() {
    String cacheKey = "test:key";

    // 执行删除
    xxxService.deleteFromCache(cacheKey);

    // 验证调用了删除方法
    verify(redisTemplate, times(1)).delete(cacheKey);
}
```

### 4.2 批量删除

```java
@Test
public void test_deleteBatchFromCache_validKeys_deleteAllSuccessfully() {
    List<String> cacheKeys = Arrays.asList("key1", "key2", "key3");

    // 执行批量删除
    xxxService.deleteBatchFromCache(cacheKeys);

    // 验证调用了批量删除方法
    verify(redisTemplate, times(1)).delete(cacheKeys);
}
```

### 4.3 模糊删除

```java
@Test
public void test_deleteByPattern_validPattern_deleteAllMatchedKeys() {
    String pattern = "test:*";

    // 执行模糊删除
    xxxService.deleteByPattern(pattern);

    // 验证调用了 keys 和 delete 方法
    verify(redisTemplate, times(1)).keys(pattern);
    verify(redisTemplate, times(1)).delete(anyCollection());
}
```

## 5. 缓存过期场景

### 5.1 设置过期时间

```java
@Test
public void test_setExpire_validKeyAndTime_setSuccessfully() {
    String cacheKey = "test:key";
    long expireTime = 3600L;

    // 执行设置过期时间
    xxxService.setExpire(cacheKey, expireTime);

    // 验证调用了 expire 方法
    verify(redisTemplate, times(1)).expire(cacheKey, expireTime, TimeUnit.SECONDS);
}
```

### 5.2 获取剩余过期时间

```java
@Test
public void test_getExpire_validKey_returnRemainingTime() {
    String cacheKey = "test:key";
    long expectedExpire = 3600L;

    // 模拟返回过期时间
    when(redisTemplate.getExpire(cacheKey, TimeUnit.SECONDS)).thenReturn(expectedExpire);

    // 执行获取过期时间
    long result = xxxService.getExpire(cacheKey);

    // 验证结果
    assertThat(result).isEqualTo(expectedExpire);
}
```

## 6. 复杂场景

### 6.1 缓存预热

```java
@Test
public void test_cacheWarmUp_loadAllDataToCache() {
    // 准备测试数据
    Map<String, Object> warmUpData = new HashMap<>();
    warmUpData.put("key1", "value1");
    warmUpData.put("key2", "value2");

    // 执行缓存预热
    xxxService.cacheWarmUp(warmUpData);

    // 验证所有数据都被写入缓存
    verify(valueOperations, times(2)).set(anyString(), any(), anyLong(), any(TimeUnit.class));
}
```

### 6.2 缓存更新

```java
@Test
public void test_updateCache_validKeyAndUpdateValue_updateSuccessfully() {
    String cacheKey = "test:key";
    String oldValue = "旧值";
    String newValue = "新值";

    // 模拟缓存中存在旧值
    when(valueOperations.get(cacheKey)).thenReturn(oldValue);

    // 执行缓存更新
    xxxService.updateCache(cacheKey, newValue);

    // 验证先删除旧缓存，再设置新缓存
    verify(redisTemplate, times(1)).delete(cacheKey);
    verify(valueOperations, times(1)).set(cacheKey, newValue, anyLong(), any(TimeUnit.class));
}
```

### 6.3 分布式锁

```java
@Test
public void test_tryLock_validKey_lockSuccessfully() {
    String lockKey = "lock:test";

    // 模拟加锁成功
    when(redisTemplate.opsForValue().setIfAbsent(anyString(), any(), anyLong(), any(TimeUnit.class)))
        .thenReturn(true);

    // 执行加锁
    boolean result = xxxService.tryLock(lockKey);

    // 验证结果
    assertThat(result).isTrue();
}

@Test
public void test_tryLock_lockFailed_returnFalse() {
    String lockKey = "lock:test";

    // 模拟加锁失败
    when(redisTemplate.opsForValue().setIfAbsent(anyString(), any(), anyLong(), any(TimeUnit.class)))
        .thenReturn(false);

    // 执行加锁
    boolean result = xxxService.tryLock(lockKey);

    // 验证结果
    assertThat(result).isFalse();
}
```

## 7. 最佳实践

1. **Mock RedisTemplate**：禁止连接真实 Redis，使用 Mock 模拟所有操作
2. **覆盖缓存命中/未命中**：两种场景都要测试
3. **验证过期时间**：确保缓存设置了合理的过期时间
4. **测试缓存穿透保护**：测试空值缓存场景
5. **验证删除操作**：确保删除操作参数正确
6. **避免测试间干扰**：每个测试独立，使用不同的 key
