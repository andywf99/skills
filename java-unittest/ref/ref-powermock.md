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

### 基础模板（需要 Mock 静态方法）

```java
@RunWith(PowerMockRunner.class)
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

### 从 MockitoJUnitRunner 迁移模板（不需要 Mock 静态方法）

当测试类原本使用 `@RunWith(MockitoJUnitRunner.Silent.class)`，需要改为 PowerMockRunner 时：

```java
import org.mockito.junit.MockitoJUnitRunner;
import org.powermock.core.classloader.annotations.PowerMockIgnore;
import org.powermock.modules.junit4.PowerMockRunner;
import org.powermock.modules.junit4.PowerMockRunnerDelegate;

@RunWith(PowerMockRunner.class)
@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)  // 委托给 MockitoJUnitRunner
@PowerMockIgnore({"com.alibaba.fastjson.*", "javax.xml.*", "org.xml.*", "org.w3c.*"})  // 忽略 FastJSON
public class XxxServiceImplTest {

    @InjectMocks
    private XxxServiceImpl service;

    @Mock
    private XxxMapper xxxMapper;

    // 无需 @Before 中调用 PowerMockito.mockStatic()，因为不需要 Mock 静态方法
}
```

**关键配置说明**：

| 注解 | 作用 | 必需 |
|------|------|------|
| `@RunWith(PowerMockRunner.class)` | 使用 PowerMock 运行器 | 是 |
| `@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)` | 委托给 MockitoJUnitRunner，保持 Mockito 初始化行为 | 是（从 MockitoJUnitRunner 迁移时） |
| `@PowerMockIgnore({...})` | 忽略指定包，避免类加载器冲突 | 是（使用 FastJSON 时） |
| `@PrepareForTest({Xxx.class})` | 声明需要 Mock 的静态类 | 是（需要 Mock 静态方法时） |

## FastJSON 兼容配置

PowerMock 的类加载器与 FastJSON 的 ASM 序列化器冲突，会报错：
```
com.alibaba.fastjson.JSONException: create asm serializer error
```

**解决方案**：添加 `@PowerMockIgnore` 忽略 FastJSON 相关包：

```java
@PowerMockIgnore({"com.alibaba.fastjson.*", "javax.xml.*", "org.xml.*", "org.w3c.*"})
```

## UnnecessaryStubbing 错误处理

当 Mockito 检测到未使用的 stub 时会报错：
```
Unnecessary Mockito stubbings
```

**解决方案**：使用 `MockitoJUnitRunner.Silent.class` 作为委托：

```java
@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)
```

## 关键要点

1. `@RunWith(PowerMockRunner.class)` 替代 `MockitoJUnitRunner`
2. `@PrepareForTest({静态类.class})` 声明所有需要 Mock 的静态工具类
3. `@Before` 中调用 `PowerMockito.mockStatic(静态类.class)` 初始化
4. 测试方法中使用 `PowerMockito.when(静态类.静态方法()).thenReturn(返回值)`
5. 不需要 `@After` 关闭 Mock（PowerMock 自动管理）
6. **禁止**使用 `MockedStatic`（Mockito 3.4+ 特性，与老版本不兼容）
7. **从 MockitoJUnitRunner 迁移时**：必须使用 `@PowerMockRunnerDelegate` + `@PowerMockIgnore`

## 常见静态类示例

```java
// SessionUtil
PowerMockito.when(SessionUtil.getUser()).thenReturn(mockUser);

// OtherUserUtils
PowerMockito.when(OtherUserUtils.isBPO()).thenReturn(true);

// GrayUtils
PowerMockito.when(GrayUtils.isGray()).thenReturn(true);
```

## 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|----------|
| `JSONException: create asm serializer error` | PowerMock 类加载器与 FastJSON ASM 冲突 | 添加 `@PowerMockIgnore({"com.alibaba.fastjson.*", ...})` |
| `Unnecessary Mockito stubbings` | Mockito 严格模式检测到未使用的 stub | 使用 `@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)` |
| `ClassNotFoundException: PowerMockRunnerDelegate` | 包名错误 | 使用 `org.powermock.modules.junit4.PowerMockRunnerDelegate` |
| `NullPointerException` in `@Before` | Mockito 未初始化 | 添加 `@PowerMockRunnerDelegate(MockitoJUnitRunner.class)` |
| `NoClassDefFoundError: org/jacoco/agent/rt/internal_xxx/Offline` | JaCoCo offline 模式与 PowerMock 不兼容 | 见下方 JaCoCo 兼容配置 |

## JaCoCo 与 PowerMock 兼容配置

**问题**：JaCoCo 的 `instrument` goal（offline 模式）会修改字节码，与 PowerMock 的类加载器冲突，导致测试失败。

**解决方案**：修改 `pom.xml`，使用 `prepare-agent` 替代 `instrument`：

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.7</version>
    <executions>
        <execution>
            <id>jacoco-prepare-agent</id>
            <goals>
                <goal>prepare-agent</goal>
            </goals>
        </execution>
        <execution>
            <id>jacoco-report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
        </execution>
    </executions>
</plugin>
```

**测试类配置**：

```java
@RunWith(PowerMockRunner.class)
@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)
@PrepareForTest({GrayUtils.class})
@PowerMockIgnore({"com.alibaba.fastjson.*", "javax.xml.*", "org.xml.*", "org.w3c.*", "org.jacoco.*"})
public class XxxServiceImplTest {
    // 测试代码
}
```

**注意事项**：
1. 禁止在测试类中使用 `@AfterClass` 调用 JaCoCo 的 `dump` 方法（如 `org.jacoco.agent.rt.RT`）
2. 使用 `prepare-agent` 模式后，覆盖率报告路径为 `target/site/jacoco/index.html`
