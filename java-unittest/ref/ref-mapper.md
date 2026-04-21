# MyBatis Mapper Mock 参考

## MyBatis-Plus ServiceImpl 继承类特殊处理

当被测类继承自 MyBatis-Plus 的 `ServiceImpl`（如 `ServiceImpl<Mapper, Entity>`）时，
调用 `this.update()`、`this.list()`、`this.getById()`、`this.save()` 等方法实际执行的是 `ServiceImpl` 的继承方法，
需要特殊处理才能在单元测试中 mock。

### 核心策略：spy + doReturn().when()

使用 `PowerMockito.spy()` 创建 spy 对象，只 mock 数据库相关方法，其他业务逻辑正常执行。

```java
// 【关键】使用 doReturn().when() 语法，避免调用被 spy 包装的方法
doReturn(null).when(service).getById(any());
doReturn(true).when(service).updateById(any(QualityFilingOa.class));
doReturn(Collections.emptyList()).when(service).list(any(LambdaQueryWrapper.class));
```

### 测试类模板

```java
@RunWith(PowerMockRunner.class)
@PrepareForTest({GrayUtils.class, JSON.class})  // 根据实际静态类调整
public class XxxServiceImplTest {

    private XxxServiceImpl service;

    @Mock
    private XxxMapper xxxMapper;  // 继承 ServiceImpl 后，注入的是 baseMapper

    @Before
    public void setUp() throws Exception {
        // 【关键】预热 MyBatis-Plus lambda 缓存，避免 LambdaUpdateWrapper 初始化失败
        TableInfoHelper.initTableInfo(
                new MapperBuilderAssistant(new MybatisConfiguration(), ""),
                XxxEntity.class
        );

        // 创建 spy 对象 - 只有被 spy 包装的对象，其继承方法才能被 mock
        service = PowerMockito.spy(new XxxServiceImpl());

        // 注入 mock baseMapper（ServiceImpl 的 baseMapper）
        ReflectionTestUtils.setField(service, "baseMapper", xxxMapper);

        // 【重要】如果需要 mock 静态方法（如 GrayUtils）
        PowerMockito.mockStatic(GrayUtils.class);
        PowerMockito.when(GrayUtils.isGray(any(GraySwitch.class))).thenReturn(false);
    }
}
```

### mock 数据库继承方法（如 this.update、this.list、this.getById）

```java
// 【语法】必须使用 doReturn().when()，不能用 when()
// 错误：when(service.getById(any())).thenReturn(entity);  // 会实际调用原方法
// 正确：doReturn(entity).when(service).getById(any());

// mock service 的 getById 方法（继承自 ServiceImpl）
doReturn(existingRecord).when(service).getById(any());

// mock service 的 updateById 方法（继承自 ServiceImpl）
doReturn(true).when(service).updateById(any(QualityFilingOa.class));

// mock service 的 list 方法（继承自 ServiceImpl）
doReturn(Collections.emptyList()).when(service).list(any(LambdaQueryWrapper.class));

// mock service 的 update 方法（继承自 ServiceImpl）
doReturn(true).when(service).update(any());
```

### 完整示例

```java
@RunWith(PowerMockRunner.class)
@PrepareForTest({GrayUtils.class, JSON.class})
public class QualityFilingOaServiceImpl_submitProxy_test {

    /** spy 对象 */
    private QualityFilingOaServiceImpl qualityFilingOaService;

    /** mock baseMapper */
    @Mock
    private QualityFilingOaMapper qualityFilingOaMapper;

    @Before
    public void setUp() throws Exception {
        // 关键：在测试方法执行前，手动初始化实体类的缓存
        TableInfoHelper.initTableInfo(
                new MapperBuilderAssistant(new MybatisConfiguration(), ""),
                QualityFilingOa.class
        );

        MockitoAnnotations.initMocks(this);
        // 创建 spy 对象
        qualityFilingOaService = PowerMockito.spy(new QualityFilingOaServiceImpl());
        // 注入 mock baseMapper
        ReflectionTestUtils.setField(qualityFilingOaService, "baseMapper", qualityFilingOaMapper);
    }

    @Test
    public void test_submitProxy_noMatchingData_returnFalse() {
        // Given
        QualityFilingOaSubmitProxyDTO dto = new QualityFilingOaSubmitProxyDTO();
        List<Long> ids = Arrays.asList(1L, 2L, 3L);
        dto.setIds(ids);

        // mock baseMapper.selectList 返回空列表
        when(qualityFilingOaMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Collections.emptyList());

        // When
        Boolean result = qualityFilingOaService.submitProxy(dto);

        // Then
        assertFalse("查询不到符合条件的数据时应返回false", result);
        verify(qualityFilingOaMapper, times(1)).selectList(any(LambdaQueryWrapper.class));
    }
}
```

### 关键要点

1. **`TableInfoHelper.initTableInfo()`** - 必须调用，否则 `LambdaUpdateWrapper` 初始化会失败
2. **`PowerMockito.spy()`** - 创建 spy 对象使继承方法可被 mock
3. **`doReturn().when()` 语法** - 必须使用此语法，禁止使用 `when().thenReturn()`
4. **`ReflectionTestUtils.setField(service, "baseMapper", mapper)`** - 注入 mock mapper
5. **`any()` vs `any(XxxWrapper.class)`** - 使用 `any()` 通配符更通用，避免类型匹配问题
6. **静态方法单独 mock** - `GrayUtils.isGray()` 等静态方法通过 `@PrepareForTest` + `PowerMockito.mockStatic()` mock

---

## JUnit 5 模式

### 依赖声明

```java
@ExtendWith(MockitoExtension.class)
class XxxMapperTest {
    @Mock
    private XxxMapper xxxMapper;

    @InjectMocks
    private XxxServiceImpl xxxService;

    @BeforeEach
    void setUp() {
        // 初始化设置，如需预热 lambda 缓存：
        // TableInfoHelper.initTableInfo(
        //     new MapperBuilderAssistant(new MybatisConfiguration(), ""),
        //     XxxEntity.class
        // );
    }

    @AfterEach
    void tearDown() {
        // 清理资源
    }
}
```

### 查询场景——必须覆盖三个分支（各自独立测试方法）

**记录存在**：
```java
@Test
void selectById_existingRecord_returnsEntity() {
    // Given
    User mockUser = new User();
    mockUser.setId(1L);
    mockUser.setUsername("admin");
    when(userMapper.selectById(1L)).thenReturn(mockUser);

    // When
    User result = userService.getById(1L);

    // Then
    assertNotNull(result);
    assertEquals("admin", result.getUsername());
}
```

**记录不存在（null）**：
```java
@Test
void selectById_notFound_returnsNull() {
    // Given
    when(userMapper.selectById(99L)).thenReturn(null);

    // When
    User result = userService.getById(99L);

    // Then
    assertNull(result);
}
```

**结果为空集合**：
```java
@Test
void selectList_noMatch_returnsEmptyList() {
    // Given
    when(userMapper.selectList(any())).thenReturn(Collections.emptyList());

    // When
    List<User> result = userService.list();

    // Then
    assertNotNull(result);
    assertTrue(result.isEmpty());
}
```

### 写操作——必须覆盖两个分支

**成功（影响行数=1）**：
```java
@Test
void updateById_recordExists_returnsSuccess() {
    // Given
    when(userMapper.updateById(any())).thenReturn(1);

    // When
    int rows = userMapper.updateById(new User());

    // Then
    assertEquals(1, rows);
}
```

**失败（影响行数=0，记录不存在）**：
```java
@Test
void updateById_recordNotFound_returnsZero() {
    // Given
    when(userMapper.updateById(any())).thenReturn(0);

    // When
    int rows = userMapper.updateById(new User());

    // Then
    assertEquals(0, rows);
}
```

### verify 必须验证到入参字段级别

```java
// 禁止——只验证调用次数，参数错误也通过
verify(userMapper, times(1)).insert(any());

// 必须——验证关键字段值正确
verify(userMapper, times(1)).insert(argThat(user ->
    "admin".equals(user.getUsername()) && Integer.valueOf(1).equals(user.getStatus())));
```

---

## JUnit 4 模式（通用）

### 依赖声明

```java
@RunWith(MockitoJUnitRunner.class)
public class XxxMapperTest {
    @Mock
    private XxxMapper xxxMapper;

    @InjectMocks
    private XxxServiceImpl xxxService;

    @Before
    public void setUp() {
        // 初始化设置
    }

    @After
    public void tearDown() {
        // 清理资源
    }
}
```

### 查询场景——必须覆盖三个分支（各自独立测试方法）

**记录存在**：
```java
when(userMapper.selectById(1L)).thenReturn(mockUser);
```

**记录不存在（null）**：
```java
when(userMapper.selectById(99L)).thenReturn(null);
```

**结果为空集合**：
```java
when(userMapper.selectList(any())).thenReturn(Collections.emptyList());
```

### 写操作——必须覆盖两个分支

**成功（影响行数=1）**：
```java
when(userMapper.updateById(any())).thenReturn(1);
```

**失败（影响行数=0，记录不存在）**：
```java
when(userMapper.updateById(any())).thenReturn(0);
```

### verify 必须验证到入参字段级别

```java
// 禁止——只验证调用次数，参数错误也通过
verify(userMapper, times(1)).insert(any());

// 必须——验证关键字段值正确
verify(userMapper, times(1)).insert(argThat(user ->
    "admin".equals(user.getUsername()) && Integer.valueOf(1).equals(user.getStatus())));
```

---

## 常见错误（PowerMock 专项）

**错误1**：
```
MybatisPlusException: can not find lambda cache for this property [status]
```
**解决**：在 `@Before` 中添加 `TableInfoHelper.initTableInfo()` 预热

**错误2**：
```
Misplaced or misused argument matcher
```
**原因**：在 `when(service.update(any()))` 中使用了 `any()` 匹配器，但实际调用了原方法
**解决**：必须使用 `doReturn().when()` 语法

**错误3**：
```
Mocking methods declared on non-public parent classes is not supported
```
**原因**：尝试 mock 继承自非公开父类的方法（如 `OrikaBeanMapper.map()`）
**解决**：无法 mock，需要通过 spy 包装真实对象或通过集成测试覆盖
