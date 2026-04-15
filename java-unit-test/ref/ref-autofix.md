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

### 错误3：NoSuchMethodError（Mockito 版本冲突）

**修复**：
1. 检查是否混用了 `MockedStatic` 和 PowerMock，**禁止混用**，统一使用项目选定的方案。
2. **mockito-inline 方案**：确认 mockito-inline 版本为 5.2.0。
3. **PowerMock 方案**：确认 PowerMock 2.0.9 与项目 Mockito 版本兼容。

### 错误4：断言不匹配

**修复**：
1. 检查 Mock 返回值是否与业务逻辑一致
2. 检查被测方法是否被正确调用
3. 用 `verify()` 验证调用参数

### 错误5：NullPointerException（Mock 未注入）

**修复**：
1. 确认 `@InjectMocks` 注解在被测类上
2. 确认所有依赖都有 `@Mock` 注解
3. 确认 Runner 正确：
   - **mockito-inline**：`@RunWith(MockitoJUnitRunner.class)`
   - **PowerMock**：`@RunWith(PowerMockRunner.class)`

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
