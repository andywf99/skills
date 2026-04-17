# 单元测试自动修复指南（JUnit 5）

测试运行失败的常见错误类型和自动修复方案。

## 1. 依赖缺失错误

### 错误类型：`ClassNotFoundException`

```
ERROR] XxxTest.test_xxx ? Undefined class: org.junit.jupiter.api.Test
[ERROR] XxxTest.test_xxx ? Undefined class: org.junit.jupiter.api.BeforeEach
[ERROR] XxxTest.test_xxx ? Undefined class: org.mockito.Mock
```

**修复方案**：添加缺失的依赖到 POM

```xml
<!-- JUnit 5 -->
<dependency>
    <groupId>org.junit.jupiter</groupId>
    <artifactId>junit-jupiter</artifactId>
    <version>5.8.2</version>
    <scope>test</scope>
</dependency>

<!-- Mockito -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-core</artifactId>
    <version>3.12.4</version>
    <scope>test</scope>
</dependency>

<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-junit-jupiter</artifactId>
    <version>3.12.4</version>
    <scope>test</scope>
</dependency>

<!-- AssertJ -->
<dependency>
    <groupId>org.assertj</groupId>
    <artifactId>assertj-core</artifactId>
    <version>3.21.0</version>
    <scope>test</scope>
</dependency>
```

### 错误类型：`NoClassDefFoundError: MockedStatic`

**修复方案**：添加 mockito-inline 依赖

```xml
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-inline</artifactId>
    <version>3.12.4</version>
    <scope>test</scope>
</dependency>
```

## 2. 编译错误

### 错误类型：`package xxx does not exist`

```
[ERROR] XxxTest.java:[10,26] 找不到符号
  符号:   类 GrayUtils
  位置: 程序包 com.yl.sqs.gray.utils
```

**修复方案**：添加正确的 import

```java
// 添加缺失的 import
import com.yl.sqs.gray.utils.GrayUtils;
```

### 错误类型：`cannot find symbol: method when()`

**修复方案**：添加静态导入

```java
// 添加这些静态导入
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
```

### 错误类型：`MockedStatic<GrayUtils> 类型不存在`

**修复方案**：导入 GrayUtils 类

```java
import com.yl.sqs.gray.utils.GrayUtils;
import org.mockito.MockedStatic;
```

## 3. 运行时错误

### 错误类型：`NullPointerException`

**原因1：@Value 字段未注入**

```
java.lang.NullPointerException
    at XxxService.checkType(XxxService.java:139)
```

**修复方案**：使用 ReflectionTestUtils 注入字段

```java
@BeforeEach
public void setUp() {
    ReflectionTestUtils.setField(xxxService, "fieldName", value);
}
```

**原因2：MockedStatic 未正确设置**

```
java.lang.NullPointerException
    at XxxService.mqHandler(XxxService.java:186)
```

**修复方案**：确保 MockedStatic 正确设置

```java
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

**原因3：Mapper 未注入**

**修复方案**：手动设置 MyBatis-Plus 的 baseMapper

```java
@BeforeEach
public void setUp() {
    try {
        java.lang.reflect.Field field = xxxService.getClass().getSuperclass()
            .getDeclaredField("baseMapper");
        field.setAccessible(true);
        field.set(xxxService, xxxMapper);
    } catch (Exception e) {
        throw new RuntimeException("Failed to set baseMapper", e);
    }
}
```

### 错误类型：`UnnecessaryStubbingException`

```
org.mockito.exceptions.misusing.UnnecessaryStubbingException:
Please remove unnecessary stubbings or use 'lenient' strictness.
```

**修复方案**：使用 lenient() 或移除不必要的 stub

```java
// 方案1：使用 lenient
@BeforeEach
public void setUp() {
    lenient().when(dependency.someMethod()).thenReturn(value);
}

// 方案2：移除不必要的 stub
// 删除测试中未使用的 when().thenReturn() 语句
```

### 错误类型：`WrongTypeOfReturnValue`

```
org.mockito.exceptions.misusing.WrongTypeOfReturnValue:
String cannot be returned by getById()
getById() should return XxxEntity
```

**修复方案**：修正返回值类型

```java
// 错误
when(xxxMapper.getById(1L)).thenReturn("string");

// 正确
when(xxxMapper.getById(1L)).thenReturn(new XxxEntity());
```

## 4. 断言错误

### 错误类型：断言失败

```
org.opentest4j.AssertionFailedError:
expecting:
 <"actual">
to be equal to:
 <"expected">
but was not.
```

**修复方案**：修正期望值或检查业务逻辑

```java
// 检查期望值是否正确
assertThat(result).isEqualTo("correct-expected-value");

// 或者检查业务逻辑是否有问题
```

### 错误类型：弱断言警告

```
警告：核心断言为弱断言，应使用具体期望值
```

**修复方案**：使用具体期望值

```java
// 错误（弱断言）
assertThat(result).isNotNull();

// 正确（具体期望值）
assertThat(result).isEqualTo("expected-value");
```

## 5. Mock 配置错误

### 错误类型：`NotAMockException`

```
org.mockito.exceptions.misusing.NotAMockException:
Argument should be a mock, but is: class java.lang.Class
```

**修复方案**：正确使用 any()

```java
// 错误
when(xxxService.method(Class.class)).thenReturn(value);

// 正确
when(xxxService.method(any(Class.class))).thenReturn(value);
```

### 错误类型：`MissingMethodInvocationException`

```
org.mockito.exceptions.misusing.MissingMethodInvocationException:
when() requires an argument which has to be 'a method call on a mock'
```

**修复方案**：确保 when() 中的对象是 Mock

```java
// 错误：xxxService 不是 Mock，是真实对象
when(xxxService.method()).thenReturn(value);

// 正确：先创建 Mock
@Mock
private XxxService xxxService;

@BeforeEach
public void setUp() {
    when(xxxService.method()).thenReturn(value);
}
```

## 6. JUnit 版本冲突

### 错误类型：JUnit 4 和 JUnit 5 混用

```
ERROR: org.junit.platform.commons.JUnitException:
TestEngine with ID 'junit-vintage' failed to discover tests
```

**修复方案**：统一使用 JUnit 5

```java
// 删除 JUnit 4 import
// import org.junit.Test;  // 删除
// import org.junit.Before; // 删除

// 使用 JUnit 5 import
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.extension.ExtendWith;
```

## 7. 自动修复步骤

生成测试后，按以下步骤自动修复：

1. **运行测试**：`mvn clean test -Dtest=XxxTest`
2. **识别错误类型**：根据错误信息判断是依赖、编译还是运行时错误
3. **应用修复方案**：按照上述方案修复
4. **重新运行**：验证修复是否成功
5. **重复直到通过**：如果仍有错误，继续修复

## 8. 常见修复命令

### 更新 Maven 依赖
```bash
mvn clean install -DskipTests
```

### 强制重新编译
```bash
mvn clean compile test-compile
```

### 运行单个测试
```bash
mvn test -Dtest=XxxTest#testMethod
```

### 跳过失败的测试
```bash
mvn test -Dmaven.test.failure.ignore=true
```

### 生成覆盖率报告
```bash
mvn clean test jacoco:report
```
