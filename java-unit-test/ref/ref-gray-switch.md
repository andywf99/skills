# GraySwitch 灰度开关 Mock 参考

## 适用场景

当被测代码使用 `GrayUtils.isGray(GraySwitch.of(...))` 判断灰度开关状态时，需要使用 PowerMock 进行 Mock。

## GraySwitch 常用场景

| 场景 | GraySwitch Key 示例 | GraySwitch Desc 示例 |
|------|---------------------|----------------------|
| 二级异常类型分页 URL 回填 | `gray-switch.cssapi.secondaryAbnormalTypePageUrl` | 二级异常类型分页URL回填 |
| 二级异常类型新增 | `gray-switch.cssapi.secondaryAbnormalTypeAdd` | 二级异常类型新增线上申请字段 |
| 二级异常类型编辑 | `gray-switch.cssapi.secondaryAbnormalTypeEdit` | 二级异常类型编辑线上申请字段 |
| 二级异常类型批量新增 | `gray-switch.cssapi.secondaryAbnormalTypeBatchAdd` | 二级异常类型批量新增优化 |
| 操作指引 API 开关 | `gray-switch.module.operation-guide.api-enabled` | 操作指引配置功能 |

## 测试类模板

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

## Controller 层灰度开关测试

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

1. **必须声明 `@PrepareForTest({GrayUtils.class})`** - 灰度开关基于 `PowerMock`，必须声明需要 Mock 的静态类
2. **`@Before` 中调用 `PowerMockito.mockStatic(GrayUtils.class)`** - 全局初始化 GrayUtils Mock
3. **`PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(true/false)`** - 使用 `any()` 匹配任意 GraySwitch 对象
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
