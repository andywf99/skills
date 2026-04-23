# MockedStatic 静态方法 Mock 参考

使用 Mockito 3.4+ 的 `mockStatic()` 进行静态方法 Mock。**禁止**在同一测试类中混用 MockedStatic 和 PowerMock。

## POM 依赖

```xml
<!-- mockito-inline 替换 mockito-core，支持静态方法和 final 类的 Mock -->
<dependency>
    <groupId>org.mockito</groupId>
    <artifactId>mockito-inline</artifactId>
    <version>5.2.0</version>
    <scope>test</scope>
</dependency>
```

---

## JUnit 5 模式（@ExtendWith + @BeforeEach/@AfterEach）

### 完整模板

```java
@ExtendWith(MockitoExtension.class)
public class XxxServiceTest {

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

    @Test
    public void test_xxx_staticMock_callSuccessfully() {
        // ... 测试逻辑
        mockedGrayUtils.verify(() -> GrayUtils.isGray(any()), atLeastOnce());
    }
}
```

### try-with-resources（单测试方法独占）

```java
@Test
public void test_withTryWithResources() {
    try (MockedStatic<GrayUtils> mockedStatic = mockStatic(GrayUtils.class)) {
        mockedStatic.when(() -> GrayUtils.isGray(any())).thenReturn(true);
        // 测试代码
    }
}
```

---

## JUnit 4 模式（@RunWith + @Before/@After）

### 完整模板

```java
@RunWith(MockitoJUnitRunner.class)
public class XxxServiceImplTest {

    private MockedStatic<SessionUtil> sessionUtilMockedStatic;

    @Before
    public void setUp() {
        sessionUtilMockedStatic = Mockito.mockStatic(SessionUtil.class);
    }

    @After
    public void tearDown() {
        sessionUtilMockedStatic.close();
    }

    @Test
    public void test_commonQuery_validParam_returnFeignResult() {
        UserSessionVO mockUser = new UserSessionVO();
        mockUser.setServiceId(100L);
        sessionUtilMockedStatic.when(() -> SessionUtil.getUser()).thenReturn(mockUser);
        // ... 测试逻辑
    }
}
```

### try-with-resources（单测试方法独占）

```java
@Test
public void test_specificMethod_withStaticMock_returnExpected() {
    try (MockedStatic<SessionUtil> mockedStatic = Mockito.mockStatic(SessionUtil.class)) {
        mockedStatic.when(() -> SessionUtil.getUser()).thenReturn(mockUser);
        // ... 测试逻辑
    }
}
```

---

## 通用：多个静态类 Mock

**JUnit 5：**
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
        if (mockedGrayUtils != null) mockedGrayUtils.close();
        if (mockedStringUtils != null) mockedStringUtils.close();
    }
}
```

**JUnit 4：**
```java
@RunWith(MockitoJUnitRunner.class)
public class XxxServiceImplTest {
    private MockedStatic<SessionUtil> sessionUtilMock;
    private MockedStatic<GrayUtils> grayUtilsMock;

    @Before
    public void setUp() {
        sessionUtilMock = Mockito.mockStatic(SessionUtil.class);
        grayUtilsMock = Mockito.mockStatic(GrayUtils.class);
    }

    @After
    public void tearDown() {
        sessionUtilMock.close();
        grayUtilsMock.close();
    }
}
```

> **注意**：关闭顺序与开启顺序相反（后开的先关），避免依赖问题。

---

## 通用：常见静态类示例

```java
// SessionUtil
sessionUtilMock.when(() -> SessionUtil.getUser()).thenReturn(mockUser);

// GrayUtils
grayUtilsMock.when(() -> GrayUtils.isGray(any())).thenReturn(true);

// StringUtils
stringUtilsMock.when(() -> StringUtils.isBlank("test")).thenReturn(false);

// LocalDateTime
localDateTimeMock.when(LocalDateTime::now).thenReturn(fixedTime);

// UUID
uuidMock.when(() -> UUID.randomUUID()).thenReturn(someUUID);

// CollectionUtils
collectionUtilsMock.when(() -> CollectionUtils.isEmpty(any())).thenReturn(true);
```

---

## 通用：不同返回值设置

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
mockedStatic.when(() -> XxxStatic.method(any())).thenCallRealMethod();
```

---

## 通用：验证静态方法调用

```java
// 验证调用次数
mockedStatic.verify(() -> GrayUtils.isGray(any()), times(1));

// 验证从未调用
mockedStatic.verify(() -> GrayUtils.isGray(any()), never());

// 验证至少调用一次
mockedStatic.verify(() -> GrayUtils.isGray(any()), atLeastOnce());

// verify 参数匹配：使用 any(具体类.class) 更精确
mockedStatic.verify(() -> GrayUtils.isGray(any(GraySwitch.class)));
```

---

## 通用：常见错误

### 错误1：未添加 mockito-inline 依赖

```
The used MockMaker does not support the creation of static mocks
```

**解决**：添加 `mockito-inline` 依赖。

### 错误2：未关闭 MockedStatic

```
Memory leak: MockedStatic not closed
```

**解决**：在 `@After`（JUnit 4）或 `@AfterEach`（JUnit 5）中调用 `close()`。

### 错误3：在测试类级别声明 MockedStatic

```java
// 错误做法
private static MockedStatic<GrayUtils> mockedStatic = mockStatic(GrayUtils.class);
```

**解决**：在 `@Before`/`@BeforeEach` 中创建，`@After`/`@AfterEach` 中关闭。

---

## 与 PowerMock 的区别

| 对比项 | MockedStatic | PowerMock |
|--------|-------------------------------|-----------|
| JUnit 5 支持 | 支持 | 不支持 |
| JUnit 4 Runner | `MockitoJUnitRunner` | `PowerMockRunner` |
| 静态 Mock 开启 | `Mockito.mockStatic()` | `PowerMockito.mockStatic()` |
| 静态 Mock 关闭 | 需手动 `close()` | 自动管理 |
| 注解 | 无需 `@PrepareForTest` | 需要 `@PrepareForTest` |
| 依赖量 | 轻量（仅 mockito-inline） | 较重（多个 powermock 模块） |
| 社区维护 | 活跃 | 已停止维护 |
