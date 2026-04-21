# GraySwitch 灰度开关 Mock 参考

## 适用场景

当被测代码使用 `GrayUtils.isGray(GraySwitch.of(...))` 判断灰度开关状态时，需要 Mock 静态方法。JUnit 5 使用 `MockedStatic`，JUnit 4 使用 `PowerMock`。

## GraySwitch 常用场景

| 场景 | GraySwitch Key 示例 | GraySwitch Desc 示例 |
|------|---------------------|----------------------|
| 二级异常类型分页 URL 回填 | `gray-switch.cssapi.secondaryAbnormalTypePageUrl` | 二级异常类型分页URL回填 |
| 二级异常类型新增 | `gray-switch.cssapi.secondaryAbnormalTypeAdd` | 二级异常类型新增线上申请字段 |
| 二级异常类型编辑 | `gray-switch.cssapi.secondaryAbnormalTypeEdit` | 二级异常类型编辑线上申请字段 |
| 二级异常类型批量新增 | `gray-switch.cssapi.secondaryAbnormalTypeBatchAdd` | 二级异常类型批量新增优化 |
| 操作指引 API 开关 | `gray-switch.module.operation-guide.api-enabled` | 操作指引配置功能 |

## JUnit 5 模式（MockedStatic）

JUnit 5 使用 Mockito 的 `mockStatic()` 配合 `MockedStatic<GrayUtils>` 来 Mock 灰度开关静态方法。需要在 `@BeforeEach` 中打开 Mock，在 `@AfterEach` 中关闭。

### 测试类模板

```java
@ExtendWith(MockitoExtension.class)
public class XxxServiceImplTest {

    @Mock
    private XxxMapper baseMapper;

    @InjectMocks
    private XxxServiceImpl service;

    private MockedStatic<GrayUtils> grayUtilsMock;

    @BeforeEach
    public void setUp() {
        // 初始化 GrayUtils 静态 Mock
        grayUtilsMock = mockStatic(GrayUtils.class);
    }

    @AfterEach
    public void tearDown() {
        // 必须关闭 MockedStatic，避免影响其他测试
        grayUtilsMock.close();
    }

    @Test
    public void test_xxx_graySwitchEnabled_success() {
        // Given - 灰度开关开启（返回 true）
        grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true);

        // When
        Result<?> result = service.xxx(param);

        // Then - 验证灰度开启时的业务逻辑
        assertTrue(result.isSucc());
    }

    @Test
    public void test_xxx_graySwitchDisabled_returnOldLogic() {
        // Given - 灰度开关关闭（返回 false）
        grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(false);

        // When
        Result<?> result = service.xxx(param);

        // Then - 验证灰度关闭时走旧逻辑或返回特定提示
        assertFalse(result.isSucc());
    }
}
```

### Service 层灰度开关测试

```java
@ExtendWith(MockitoExtension.class)
public class SecondaryAbnormalTypeServiceImplTest {

    @Mock
    private SecondaryAbnormalTypeMapper mapper;

    @InjectMocks
    private SecondaryAbnormalTypeServiceImpl service;

    private MockedStatic<GrayUtils> grayUtilsMock;

    @BeforeEach
    void setUp() {
        grayUtilsMock = mockStatic(GrayUtils.class);
    }

    @AfterEach
    void tearDown() {
        grayUtilsMock.close();
    }

    @Test
    void test_pageUrl_grayOn_returnsNewUrl() {
        // Given - 灰度开关开启
        grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true);
        when(mapper.selectPage(any(), any())).thenReturn(new Page<>());

        // When
        Result<Page<SecondaryAbnormalTypeVO>> result = service.pageUrl(new QueryDTO());

        // Then - 走新逻辑，URL 回填
        assertTrue(result.isSucc());
        verify(mapper, times(1)).selectPage(any(), any());
    }

    @Test
    void test_pageUrl_grayOff_returnsOldResult() {
        // Given - 灰度开关关闭
        grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(false);

        // When
        Result<Page<SecondaryAbnormalTypeVO>> result = service.pageUrl(new QueryDTO());

        // Then - 走旧逻辑，不调用新方法
        assertFalse(result.isSucc());
        verify(mapper, never()).selectPage(any(), any());
    }
}
```

### Controller 层灰度开关测试

Controller 层通常在每个方法入口处统一判断灰度开关：

```java
@ExtendWith(MockitoExtension.class)
public class XxxControllerTest {

    @Mock
    private IXxxService xxxService;

    private XxxController controller;

    private MockedStatic<GrayUtils> grayUtilsMock;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
        controller = new XxxController();
        ReflectionTestUtils.setField(controller, "xxxService", xxxService);
        grayUtilsMock = mockStatic(GrayUtils.class);
    }

    @AfterEach
    void tearDown() {
        grayUtilsMock.close();
    }

    @Test
    void test_page_graySwitchEnabled_callService() {
        // Given - 灰度开关开启
        grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true);
        Page<XxxVO> mockPage = new Page<>(1, 10);
        when(xxxService.page(any(XxxQueryDTO.class))).thenReturn(mockPage);

        // When
        Result<Page<XxxVO>> result = controller.page(new XxxQueryDTO());

        // Then
        assertTrue(result.isSucc());
        verify(xxxService, times(1)).page(any(XxxQueryDTO.class));
    }

    @Test
    void test_page_graySwitchDisabled_returnForbidden() {
        // Given - 灰度开关关闭
        grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(false);

        // When
        Result<Page<XxxVO>> result = controller.page(new XxxQueryDTO());

        // Then - 灰度关闭时直接返回禁用，不调用 Service
        assertFalse(result.isSucc());
        assertEquals(ResultCodeEnum.INTERFACE_FORBIDDEN.getCode(), result.getCode());
        verify(xxxService, never()).page(any());
    }
}
```

## JUnit 4 模式（PowerMock）

### 测试类模板

```java
@RunWith(PowerMockRunner.class)
@PrepareForTest({GrayUtils.class})   // 灰度开关必需声明 GrayUtils
public class XxxServiceImplTest {

    @Mock
    private XxxMapper baseMapper;

    @InjectMocks
    private XxxServiceImpl service;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        // 初始化 GrayUtils 静态 Mock
        PowerMockito.mockStatic(GrayUtils.class);
    }

    @Test
    public void test_xxx_graySwitchEnabled_success() {
        // Given - 灰度开关开启（返回 true）
        PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true);

        // When
        Result<?> result = service.xxx(param);

        // Then - 验证灰度开启时的业务逻辑
        assertTrue(result.isSucc());
    }

    @Test
    public void test_xxx_graySwitchDisabled_returnOldLogic() {
        // Given - 灰度开关关闭（返回 false）
        PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(false);

        // When
        Result<?> result = service.xxx(param);

        // Then - 验证灰度关闭时走旧逻辑或返回特定提示
        assertFalse(result.isSucc());
    }
}
```

### Controller 层灰度开关测试

Controller 层通常在每个方法入口处统一判断灰度开关：

```java
@RunWith(PowerMockRunner.class)
@PrepareForTest({GrayUtils.class})
public class XxxControllerTest {

    @Mock
    private IXxxService xxxService;

    private XxxController controller;

    @Before
    public void setUp() {
        MockitoAnnotations.initMocks(this);
        controller = new XxxController();
        ReflectionTestUtils.setField(controller, "xxxService", xxxService);
        PowerMockito.mockStatic(GrayUtils.class);
    }

    @Test
    public void test_page_graySwitchEnabled_callService() {
        // Given - 灰度开关开启
        PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true);
        Page<XxxVO> mockPage = new Page<>(1, 10);
        when(xxxService.page(any(XxxQueryDTO.class))).thenReturn(mockPage);

        // When
        Result<Page<XxxVO>> result = controller.page(new XxxQueryDTO());

        // Then
        assertTrue(result.isSucc());
        verify(xxxService, times(1)).page(any(XxxQueryDTO.class));
    }

    @Test
    public void test_page_graySwitchDisabled_returnForbidden() {
        // Given - 灰度开关关闭
        PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(false);

        // When
        Result<Page<XxxVO>> result = controller.page(new XxxQueryDTO());

        // Then - 灰度关闭时直接返回禁用，不调用 Service
        assertFalse(result.isSucc());
        assertEquals(ResultCodeEnum.INTERFACE_FORBIDDEN.getCode(), result.getCode());
        verify(xxxService, never()).page(any());
    }
}
```

## 关键要点

### JUnit 5（MockedStatic）

1. **使用 `mockStatic(GrayUtils.class)`** - 通过 Mockito 的 `mockStatic()` 创建静态 Mock，无需额外 Runner
2. **`@BeforeEach` 中打开，`@AfterEach` 中关闭** - `MockedStatic` 必须显式 `close()`，否则会泄漏到其他测试
3. **使用 lambda 语法 Stub** - `grayUtilsMock.when(() -> GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true/false)`
4. **需要 mockito-inline 依赖** - JUnit 5 Mock 静态方法需要 `mockito-inline` 或 Mockito 5.x+（内置 inline mock maker）

### JUnit 4（PowerMock）

1. **必须声明 `@PrepareForTest({GrayUtils.class})`** - 灰度开关基于 `PowerMock`，必须声明需要 Mock 的静态类
2. **`@Before` 中调用 `PowerMockito.mockStatic(GrayUtils.class)`** - 全局初始化 GrayUtils Mock
3. **`PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true/false)`** - 使用 `any()` 匹配任意 GraySwitch 对象

### 通用要点

4. **灰度开关测试应成对覆盖** - 每个使用灰度开关的方法都应测试开启/关闭两种场景
5. **注意 Controller 层统一拦截** - Controller 的灰度开关通常在入口处统一判断，关闭时直接返回 `Result.error(ResultCodeEnum.INTERFACE_FORBIDDEN)`

## 常见灰度开关 Key 模式

```java
// CSS API 灰度开关 Key 模式
"gray-switch.cssapi.{业务模块}{操作}"        // 如 gray-switch.cssapi.secondaryAbnormalTypePageUrl
"gray-switch.module.{模块名}.api-enabled"   // 如 gray-switch.module.operation-guide.api-enabled

// GraySwitch 创建方式
GraySwitch.of("gray-switch.cssapi.xxx", "描述")
```

## 必测场景汇总

| 被测类类型 | 必测场景 |
|-----------|---------|
| Service 层 | 灰度开启 → 新逻辑执行<br>灰度关闭 → 旧逻辑执行或跳过 |
| Controller 层 | 灰度开启 → 调用 Service<br>灰度关闭 → 返回 INTERFACE_FORBIDDEN，不调用 Service |
| 批量操作 | 灰度开启 → 走新批量逻辑<br>灰度关闭 → 循环调用旧单条逻辑 |
