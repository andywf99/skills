# PowerMock 静态方法 Mock 参考

## 适用场景

当被测代码调用了静态方法（如 `SessionUtil.getUser()`、`OtherUserUtils.isBPO()`、`GrayUtils.isGray()` 等），需要使用 PowerMock 进行 Mock。

## POM 依赖

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

## 测试类模板

```java
@RunWith(PowerMockRunner.class)          // 使用 PowerMockRunner
@PrepareForTest({SessionUtil.class})     // 声明需要 Mock 的静态类
public class XxxServiceImplTest {

    @Mock
    private XxxFeignClient xxxFeignClient;

    @InjectMocks
    private XxxServiceImpl service;

    @Before
    public void setUp() {
        PowerMockito.mockStatic(SessionUtil.class);
    }

    @Test
    public void test_commonQuery_validParam_returnFeignResult() {
        // 模拟静态方法返回值
        UserSessionVO mockUser = new UserSessionVO();
        mockUser.setServiceId(100L);
        PowerMockito.when(SessionUtil.getUser()).thenReturn(mockUser);

        // ... 测试逻辑
    }
}
```

## 关键要点

1. `@RunWith(PowerMockRunner.class)` 替代 `MockitoJUnitRunner`
2. `@PrepareForTest({静态类.class})` 声明所有需要 Mock 的静态工具类
3. `@Before` 中调用 `PowerMockito.mockStatic(静态类.class)` 初始化
4. 测试方法中使用 `PowerMockito.when(静态类.静态方法()).thenReturn(返回值)`
5. 不需要 `@After` 关闭 Mock（PowerMock 自动管理）
6. **禁止**使用 `MockedStatic`（Mockito 3.4+ 特性，与老版本不兼容）

## 常见静态类示例

```java
// SessionUtil
PowerMockito.when(SessionUtil.getUser()).thenReturn(mockUser);

// OtherUserUtils
PowerMockito.when(OtherUserUtils.isBPO()).thenReturn(true);

// GrayUtils
PowerMockito.when(GrayUtils.isGray()).thenReturn(true);
```
