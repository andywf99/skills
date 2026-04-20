# 静态方法 Mock 参考（JUnit 5 + Mockito）

使用 Mockito 3.4+ 的 `mockStatic()` 进行静态方法 Mock，替代 PowerMock。

## 1. 基础配置

### Maven 依赖

```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-inline</artifactId>
    <version>3.12.4</version>
    <scope>test</scope>
</dependency>
```

**注意**：`mockito-inline` 是必需的，它提供了静态方法Mock的能力。

### 完整模板

```java
package com.yl.cswot.xxx;

import com.yl.sqs.gray.utils.GrayUtils;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.MockedStatic;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * XxxService单元测试
 * 测试范围：包含静态方法调用的业务逻辑
 */
@ExtendWith(MockitoExtension.class)
public class XxxServiceTest {

    private MockedStatic<GrayUtils> mockedGrayUtils;

    @BeforeEach
    public void setUp() {
        // Mock 静态方法
        mockedGrayUtils = mockStatic(GrayUtils.class);
        mockedGrayUtils.when(() -> GrayUtils.isGray(any())).thenReturn(false);
    }

    @AfterEach
    public void tearDown() {
        // 必须关闭 MockedStatic，避免内存泄漏
        if (mockedGrayUtils != null) {
            mockedGrayUtils.close();
        }
    }

    @Test
    public void test_xxx_staticMock_callSuccessfully() {
        // 执行被测方法
        // ...

        // 验证静态方法被调用
        mockedGrayUtils.verify(() -> GrayUtils.isGray(any()), atLeastOnce());
    }
}
```

## 2. 常见静态类 Mock

### GrayUtils（灰度开关）

```java
private MockedStatic<GrayUtils> mockedGrayUtils;

@BeforeEach
public void setUp() {
    mockedGrayUtils = mockStatic(GrayUtils.class);
    mockedGrayUtils.when(() -> GrayUtils.isGray(any())).thenReturn(false);
}

@AfterEach
public void tearDown() {
    if (mockedGrayUtils != null) {
        mockedGrayUtils.close();
    }
}
```

### StringUtils（字符串工具类）

```java
private MockedStatic<StringUtils> mockedStringUtils;

@BeforeEach
public void setUp() {
    mockedStringUtils = mockStatic(StringUtils.class);
    mockedStringUtils.when(() -> StringUtils.isBlank("test")).thenReturn(false);
}

@AfterEach
public void tearDown() {
    if (mockedStringUtils != null) {
        mockedStringUtils.close();
    }
}
```

### LocalDateTime/LocalDate（时间类）

```java
private MockedStatic<LocalDateTime> mockedLocalDateTime;

@BeforeEach
public void setUp() {
    LocalDateTime fixedTime = LocalDateTime.of(2024, 1, 1, 12, 0);
    mockedLocalDateTime = mockStatic(LocalDateTime.class);
    mockedLocalDateTime.when(LocalDateTime::now).thenReturn(fixedTime);
}

@AfterEach
public void tearDown() {
    if (mockedLocalDateTime != null) {
        mockedLocalDateTime.close();
    }
}
```

### CollectionUtils/Objects（集合工具类）

```java
private MockedStatic<CollectionUtils> mockedCollectionUtils;

@BeforeEach
public void setUp() {
    mockedCollectionUtils = mockStatic(CollectionUtils.class);
    mockedCollectionUtils.when(() -> CollectionUtils.isEmpty(any())).thenReturn(true);
}

@AfterEach
public void tearDown() {
    if (mockedCollectionUtils != null) {
        mockedCollectionUtils.close();
    }
}
```

## 3. 多个静态方法 Mock

```java
@ExtendWith(MockitoExtension.class)
public class XxxServiceTest {

    private MockedStatic<GrayUtils> mockedGrayUtils;
    private MockedStatic<StringUtils> mockedStringUtils;

    @BeforeEach
    public void setUp() {
        mockedGrayUtils = mockStatic(GrayUtils.class);
        mockedGrayUtils.when(() -> GrayUtils.isGray(any())).thenReturn(false);

        mockedStringUtils = mockStatic(StringUtils.class);
        mockedStringUtils.when(() -> StringUtils.isBlank(any())).thenReturn(false);
    }

    @AfterEach
    public void tearDown() {
        if (mockedGrayUtils != null) {
            mockedGrayUtils.close();
        }
        if (mockedStringUtils != null) {
            mockedStringUtils.close();
        }
    }
}
```

## 4. 不同返回值设置

```java
// 固定返回值
mockedStatic.when(() -> GrayUtils.isGray(any())).thenReturn(true);

// 根据参数返回不同值
mockedStatic.when(() -> StringUtils.isBlank("test")).thenReturn(false);
mockedStatic.when(() -> StringUtils.isBlank("")).thenReturn(true);

// 抛出异常
mockedStatic.when(() -> XxxStatic.method(any()))
    .thenThrow(new RuntimeException("Test exception"));

// 调用真实方法
mockedStatic.when(() -> XxxStatic.method(any()))
    .thenCallRealMethod();
```

## 5. 验证静态方法调用

```java
@Test
public void test_verifyStaticMethodCalled() {
    // 执行被测方法
    service.doSomething();

    // 验证静态方法被调用
    mockedStatic.verify(() -> GrayUtils.isGray(any()), times(1));

    // 验证从未调用
    mockedStatic.verify(() -> GrayUtils.isGray(any()), never());

    // 验证至少调用一次
    mockedStatic.verify(() -> GrayUtils.isGray(any()), atLeastOnce());
}
```

## 6. 常见错误

### 错误1：未添加 mockito-inline 依赖

```
org.mockito.exceptions.base.MockitoException:
The used MockMaker does not support the creation of static mocks
```

**解决方案**：添加 `mockito-inline` 依赖。

### 错误2：未关闭 MockedStatic

```
Memory leak: MockedStatic not closed
```

**解决方案**：在 `@AfterEach` 中调用 `mockedStatic.close()`。

### 错误3：在测试类级别声明 MockedStatic

```java
// 错误做法
@ExtendWith(MockitoExtension.class)
public class XxxTest {
    private static MockedStatic<GrayUtils> mockedStatic = mockStatic(GrayUtils.class);
}
```

**解决方案**：在 `@BeforeEach` 中创建，`@AfterEach` 中关闭。

## 7. 最佳实践

1. **每次测试创建新的 MockedStatic**：避免测试间相互影响
2. **必须关闭 MockedStatic**：在 `@AfterEach` 中关闭，防止内存泄漏
3. **使用 try-with-resources**：如果只想在单个测试中使用

```java
@Test
public void test_withTryWithResources() {
    try (MockedStatic<GrayUtils> mockedStatic = mockStatic(GrayUtils.class)) {
        mockedStatic.when(() -> GrayUtils.isGray(any())).thenReturn(true);
        // 测试代码
    }
}
```

4. **verify 参数匹配**：使用 `any()` 或具体值，避免类型不匹配

```java
// 正确
mockedStatic.verify(() -> GrayUtils.isGray(any(GraySwitch.class)));

// 错误
mockedStatic.verify(() -> GrayUtils.isGray(any())); // 可能类型不匹配
```
