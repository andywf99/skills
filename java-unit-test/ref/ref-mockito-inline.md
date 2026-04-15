# Mockito-Inline + MockedStatic 静态方法 Mock 参考

## 适用场景

当项目依赖 `mockito-inline` 时，使用 Mockito 3.4+ 原生提供的 `MockedStatic` 进行静态方法 Mock。**禁止**在此方案中使用 PowerMock。

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

## 测试类模板

### 方式一：@Before/@After 管理（推荐，多测试方法共享）

```java
@RunWith(MockitoJUnitRunner.class)
public class XxxServiceImplTest {

    @Mock
    private XxxFeignClient xxxFeignClient;

    @InjectMocks
    private XxxServiceImpl service;

    // 每个需要 Mock 的静态类声明一个 MockedStatic 字段
    private MockedStatic<SessionUtil> sessionUtilMockedStatic;

    @Before
    public void setUp() {
        // 在 @Before 中开启静态 Mock
        sessionUtilMockedStatic = Mockito.mockStatic(SessionUtil.class);
    }

    @After
    public void tearDown() {
        // 必须在 @After 中关闭，防止泄漏影响其他测试类
        sessionUtilMockedStatic.close();
    }

    @Test
    public void test_commonQuery_validParam_returnFeignResult() {
        // 模拟静态方法返回值
        UserSessionVO mockUser = new UserSessionVO();
        mockUser.setServiceId(100L);
        sessionUtilMockedStatic.when(() -> SessionUtil.getUser()).thenReturn(mockUser);

        // ... 测试逻辑
    }
}
```

### 方式二：try-with-resources（单测试方法独占）

```java
@Test
public void test_specificMethod_withStaticMock_returnExpected() {
    UserSessionVO mockUser = new UserSessionVO();
    mockUser.setServiceId(100L);

    try (MockedStatic<SessionUtil> mockedStatic = Mockito.mockStatic(SessionUtil.class)) {
        mockedStatic.when(() -> SessionUtil.getUser()).thenReturn(mockUser);

        // ... 测试逻辑
    } // 自动关闭
}
```

## 多个静态类 Mock

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

## 关键要点

1. 使用 `@RunWith(MockitoJUnitRunner.class)`，**不使用** `PowerMockRunner`。
2. `Mockito.mockStatic(类.class)` 开启静态 Mock，返回 `MockedStatic` 对象。
3. **必须关闭** `MockedStatic`，推荐 `@After` 中调用 `close()` 或使用 `try-with-resources`。
4. 设置返回值语法：`mockedStatic.when(() -> 静态类.方法()).thenReturn(值)`。
5. 验证调用：`mockedStatic.verify(() -> 静态类.方法(参数))`。
6. `mockito-inline` 同时支持 Mock final 类和 final 方法，无需额外配置。

## 常见静态类示例

```java
// SessionUtil
sessionUtilMock.when(() -> SessionUtil.getUser()).thenReturn(mockUser);

// OtherUserUtils
otherUserUtilsMock.when(() -> OtherUserUtils.isBPO()).thenReturn(true);

// GrayUtils
grayUtilsMock.when(() -> GrayUtils.isGray()).thenReturn(true);

// UUID
uuidMock.when(() -> UUID.randomUUID()).thenReturn(someUUID);
```

## 与 PowerMock 的区别

| 对比项 | mockito-inline + MockedStatic | PowerMock |
|--------|-------------------------------|-----------|
| Runner | `MockitoJUnitRunner` | `PowerMockRunner` |
| 静态 Mock 开启 | `Mockito.mockStatic()` | `PowerMockito.mockStatic()` |
| 静态 Mock 关闭 | 需手动 `close()` | 自动管理 |
| 注解 | 无需 `@PrepareForTest` | 需要 `@PrepareForTest` |
| 新构造函数 Mock | 支持（`MockedConstruction`） | 支持（`whenNew`） |
| 依赖量 | 轻量（仅 mockito-inline） | 较重（多个 powermock 模块） |
| 社区维护 | 活跃 | 已停止维护 |
