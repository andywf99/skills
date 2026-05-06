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
import org.powermock.modules.junit4.PowerMockRunner;
import org.powermock.modules.junit4.PowerMockRunnerDelegate;

@RunWith(PowerMockRunner.class)
@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)  // 委托给 MockitoJUnitRunner
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
| `@PrepareForTest({Xxx.class})` | 声明需要 Mock 的静态类 | 是（需要 Mock 静态方法时） |

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
7. **从 MockitoJUnitRunner 迁移时**：必须使用 `@PowerMockRunnerDelegate`
8. **有副作用的静态类**：必须配合 `@SuppressStaticInitializationFor` 抑制静态初始化块

## @SuppressStaticInitializationFor — 抑制静态初始化块

### 问题场景

`PowerMockito.mockStatic(XxxUtil.class)` 在创建 mock 对象时，会先加载目标类，触发其静态初始化块 `<clinit>`。如果该初始化块包含网络请求、文件 IO、数据库连接等副作用（如 `YlFileUtil` 会在 `<clinit>` 中调用 `FileAutoConfiguration.init()` 连接文件服务），在 Jenkins 等无外网访问的 CI 环境中会抛异常导致测试失败。**本地开发环境可能因能连通外部服务而不报错，容易遗漏。**

典型报错：
```
YlFilePullException: YlFileUtil no reachable pullApi,please check network params:[unknown]
    at com.jt.file.pull.PullApiUtil.loopRequest(PullApiUtil.java:77)
    at com.jt.file.FileAutoConfiguration.appSlotRole(FileAutoConfiguration.java:370)
    at com.jt.file.FileAutoConfiguration.init(FileAutoConfiguration.java:198)
    at com.jt.file.YlFileUtil.reachInitFromStatic(YlFileUtil.java:1585)
    at com.jt.file.YlFileUtil.<clinit>(YlFileUtil.java:36)
```

### 解决方案

使用 `@SuppressStaticInitializationFor` 注解，让 PowerMock 跳过目标类的静态初始化代码，只创建空壳 mock 对象。

### 用法

```java
@RunWith(PowerMockRunner.class)
@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)
@PrepareForTest({YlFileUtil.class, MD5Utils.class})
@SuppressStaticInitializationFor("com.jt.file.YlFileUtil")   // 全限定类名
@PowerMockIgnore({"javax.management.*", "javax.net.ssl.*"})
public class XxxServiceImplTest {

    @Before
    public void setUp() {
        // mockStatic 不再触发 YlFileUtil 的 <clinit>
        PowerMockito.mockStatic(YlFileUtil.class);
        PowerMockito.when(YlFileUtil.upload(any(), anyLong(), anyString(),
                anyString(), anyString(), any(FileLifeEnum.class),
                anyString(), anyString(), anyString())).thenReturn("http://mock-url/file.mp3");
    }
}
```

### 何时必须使用

对以下类型的静态类使用 `mockStatic()` 时，**必须**配合 `@SuppressStaticInitializationFor`：

| 静态类特征 | 示例 | 是否必须 |
|-----------|------|---------|
| `<clinit>` 中有网络请求 | `YlFileUtil`（连接文件服务） | **是** |
| `<clinit>` 中有数据库连接 | 某些连接池工具类 | **是** |
| `<clinit>` 中读取外部配置/文件 | 某些 Config 加载类 | **是** |
| `<clinit>` 中仅初始化常量/缓存 | `GrayUtils`、`SessionUtil` | 否 |
| 纯工具方法，无 `<clinit>` 副作用 | `MD5Utils`、`JsonUtils` | 否 |

### 注意事项

1. `@SuppressStaticInitializationFor` 的值是**全限定类名**字符串，不是 `.class` 引用
2. 可以同时指定多个类：`@SuppressStaticInitializationFor({"com.jt.file.YlFileUtil", "com.xxx.ConfigHolder"})`
3. 抑制后该类的 `static final` 常量字段为默认值（`null`/`0`/`false`），需要通过 `when()` 设置 Mock 返回值
4. 只需对有副作用的类添加此注解，不要对不需要的类滥用

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
| `Unnecessary Mockito stubbings` | Mockito 严格模式检测到未使用的 stub | 使用 `@PowerMockRunnerDelegate(MockitoJUnitRunner.Silent.class)` |
| `ClassNotFoundException: PowerMockRunnerDelegate` | 包名错误 | 使用 `org.powermock.modules.junit4.PowerMockRunnerDelegate` |
| `NullPointerException` in `@Before` | Mockito 未初始化 | 添加 `@PowerMockRunnerDelegate(MockitoJUnitRunner.class)` |
| `NoClassDefFoundError: org/jacoco/agent/rt/internal_xxx/Offline` | JaCoCo offline 模式与 PowerMock 不兼容 | 见下方 JaCoCo 兼容配置 |
| `YlFilePullException` / 静态初始化连接外部服务失败 | `mockStatic()` 触发目标类 `<clinit>`，执行了网络请求等副作用 | 使用 `@SuppressStaticInitializationFor` 抑制静态初始化 |

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
public class XxxServiceImplTest {
    // 测试代码
}
```

**注意事项**：
1. 禁止在测试类中使用 `@AfterClass` 调用 JaCoCo 的 `dump` 方法（如 `org.jacoco.agent.rt.RT`）
2. 使用 `prepare-agent` 模式后，覆盖率报告路径为 `target/site/jacoco/index.html`
