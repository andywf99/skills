# 自动运行测试与错误修复参考

## 执行步骤

### 步骤1：检测 Maven 环境

```bash
mvn -v
```

如果 mvn 命令不存在，询问用户 Maven 安装地址。

### 步骤2：运行测试

```bash
mvn clean test -Dtest=XxxServiceImplTest
```

### 步骤3：解析结果并修复

运行测试后，Maven 会在控制台输出测试结果。根据输出判断测试状态并应用对应修复。

#### 读取 Maven 测试输出

Maven 测试输出关键信息：

```
Tests run: 5, Failures: 1, Errors: 2, Skipped: 0
```

- **Failures**：断言失败，说明业务逻辑或 Mock 返回值与预期不符。
- **Errors**：运行时异常，说明测试代码本身或依赖配置有问题（如 ClassNotFoundException、NullPointerException）。
- **Skipped**：被跳过的测试，通常是条件注解或配置问题。

每个失败/错误的测试都会输出具体的异常堆栈，重点关注以下几类信息：

1. **异常类型**：如 `AssertionError`、`NoClassDefFoundError`、`NoSuchMethodError`、`NullPointerException` 等。
2. **异常消息**：通常会指明缺失的类、方法或不匹配的值。
3. **堆栈中的 Caused by**：嵌套异常的根因，优先查看最内层的 `Caused by`。

#### 识别错误类型

根据异常类型快速定位到对应的修复方案：

| 异常类型 | 对应修复方案 |
|---|---|
| `cannot find symbol` / 编译错误 | 错误1：缺少依赖 |
| `NoClassDefFoundError` | 错误2：运行时类缺失 |
| `NoSuchMethodError` | 错误3：Mockito 版本冲突 |
| `AssertionError` | 错误4：断言不匹配 |
| `NullPointerException` | 错误5：Mock 未注入 |
| `Surefire fork` 相关 | 错误7：Surefire fork 失败 |

#### 应用修复

1. 从 Maven 输出中提取失败的测试类名和方法名。
2. 根据异常类型匹配上方表格中的修复方案。
3. 按照对应方案修改代码或 pom.xml。
4. 重新执行步骤2验证修复是否生效。
5. 如果仍有失败，重复步骤3直到全部通过。

#### 多错误处理

当一次运行出现多个错误时，建议按以下优先级逐个修复：

1. **编译错误 / NoClassDefFoundError**：优先解决，否则后续测试无法运行。
2. **NoSuchMethodError**：版本冲突会导致连锁错误，优先解决。
3. **NullPointerException（Mock 未注入）**：修复后通常能一次性解决多个测试方法。
4. **AssertionError**：最后处理，需要在 Mock 和业务逻辑都正确的前提下调整断言。

### 步骤4：生成覆盖率报告

```bash
mvn clean test jacoco:report
```

报告路径：`target/jacoco-ut/index.html`

---

## 常见错误与自动修复方案

### 错误1：缺少依赖（cannot find symbol）

**修复**：根据项目使用的静态 Mock 框架添加对应依赖：
- **mockito-inline 方案**：在 pom.xml 中添加 `mockito-inline` 依赖（见 `ref-mockito-inline.md`）。
- **PowerMock 方案**：在 pom.xml 中添加 PowerMock 依赖（见 `ref-powermock.md`）。

### 错误2：NoClassDefFoundError（运行时类缺失）

**修复**：
1. 检查依赖 scope 是否为 `test`
2. 执行 `mvn clean install -DskipTests` 重新下载
3. 确认版本兼容性：
   - **mockito-inline**：5.2.0 与 Spring Boot 2.x 兼容
   - **PowerMock**：2.0.9 + Spring Boot 2.0.x

> **JUnit 5 注意**：如果项目使用 JUnit 5，确保 `mockito-inline` 版本为 4.x 以上。JUnit 5 + mockito-inline 需要配合 `mockito-junit-jupiter` 依赖，否则运行时可能出现 `NoClassDefFoundError: org/junit/jupiter/api/extension/Extension`。

### 错误3：NoSuchMethodError（Mockito 版本冲突）

**修复**：
1. 检查是否混用了 `MockedStatic` 和 PowerMock，**禁止混用**，统一使用项目选定的方案。
2. **mockito-inline 方案**：确认 mockito-inline 版本为 5.2.0。
3. **PowerMock 方案**：确认 PowerMock 2.0.9 与项目 Mockito 版本兼容。

> **JUnit 5 注意**：JUnit 5 环境下不应出现 `@RunWith` 注解。如果测试类使用了 `@RunWith(MockitoJUnitRunner.class)`，需替换为 `@ExtendWith(MockitoExtension.class)`，并确保引入了 `mockito-junit-jupiter` 依赖。混用 `@RunWith` 和 JUnit 5 注解是导致 `NoSuchMethodError` 的常见原因。

### 错误4：断言不匹配

**修复**：
1. 检查 Mock 返回值是否与业务逻辑一致
2. 检查被测方法是否被正确调用
3. 用 `verify()` 验证调用参数

### 错误5：NullPointerException（Mock 未注入）

**修复**：
1. 确认 `@InjectMocks` 注解在被测类上
2. 确认所有依赖都有 `@Mock` 注解
3. 确认 Runner/Extension 正确：
   - **mockito-inline**：`@RunWith(MockitoJUnitRunner.class)`
   - **PowerMock**：`@RunWith(PowerMockRunner.class)`

> **JUnit 5 修复**：JUnit 5 不使用 `@RunWith`。确认测试类使用 `@ExtendWith(MockitoExtension.class)`，而不是 `@RunWith(MockitoJUnitRunner.class)`。如果误用了 `@RunWith`，Mock 对象不会被自动初始化，导致所有 `@Mock` 字段为 null，进而引发 NullPointerException。正确写法：
> ```java
> @ExtendWith(MockitoExtension.class)
> class XxxServiceImplTest {
>     @InjectMocks
>     private XxxServiceImpl xxxService;
>     @Mock
>     private DependencyService dependencyService;
> }
> ```

### 错误6：测试类未被扫描

**修复**：确认类命名符合规范（`XxxTest.java`）且位于 `src/test/java` 目录下。

### 错误7：Surefire fork 失败

**修复**：在 pom.xml 的 `maven-surefire-plugin` 中设置 `<forkCount>0</forkCount>`。

---

## 修复示例：框架方案转换

### 方案 A：PowerMock → mockito-inline（当项目使用 mockito-inline 时）

```java
// 修改前（PowerMock 方案，与 mockito-inline 冲突）
@RunWith(PowerMockRunner.class)
@PrepareForTest({SessionUtil.class})
public class XxxTest {
    @Before
    public void setUp() {
        PowerMockito.mockStatic(SessionUtil.class);
    }
}

// 修改后（mockito-inline 方案）
@RunWith(MockitoJUnitRunner.class)
public class XxxTest {
    private MockedStatic<SessionUtil> sessionUtilMock;

    @Before
    public void setUp() {
        sessionUtilMock = Mockito.mockStatic(SessionUtil.class);
    }

    @After
    public void tearDown() {
        sessionUtilMock.close();
    }
}
```

### 方案 B：mockito-inline → PowerMock（当项目使用 PowerMock 时）

```java
// 修改前（MockedStatic 方案，与 PowerMock 冲突）
@RunWith(MockitoJUnitRunner.class)
public class XxxTest {
    private MockedStatic<SessionUtil> sessionUtilMock;

    @Before
    public void setUp() {
        sessionUtilMock = mockStatic(SessionUtil.class);
    }

    @After
    public void tearDown() {
        sessionUtilMock.close();
    }
}

// 修改后（PowerMock 方案）
@RunWith(PowerMockRunner.class)
@PrepareForTest({SessionUtil.class})
public class XxxTest {
    @Before
    public void setUp() {
        PowerMockito.mockStatic(SessionUtil.class);
    }
}
```
