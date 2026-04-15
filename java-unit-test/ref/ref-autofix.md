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

**修复**：在 pom.xml 中添加 PowerMock 依赖（见 `ref-powermock.md`）。

### 错误2：NoClassDefFoundError（运行时类缺失）

**修复**：
1. 检查依赖 scope 是否为 `test`
2. 执行 `mvn clean install -DskipTests` 重新下载
3. 确认版本兼容性（PowerMock 2.0.9 + Spring Boot 2.0.x）

### 错误3：NoSuchMethodError（Mockito 版本冲突）

**修复**：检查是否混用了 `MockedStatic` 和 PowerMock，统一使用 PowerMock。

### 错误4：断言不匹配

**修复**：
1. 检查 Mock 返回值是否与业务逻辑一致
2. 检查被测方法是否被正确调用
3. 用 `verify()` 验证调用参数

### 错误5：NullPointerException（Mock 未注入）

**修复**：
1. 确认 `@InjectMocks` 注解在被测类上
2. 确认所有依赖都有 `@Mock` 注解
3. 确认使用 `@RunWith(PowerMockRunner.class)`

### 错误6：测试类未被扫描

**修复**：确认类命名符合规范（`XxxTest.java`）且位于 `src/test/java` 目录下。

### 错误7：Surefire fork 失败

**修复**：在 pom.xml 的 `maven-surefire-plugin` 中设置 `<forkCount>0</forkCount>`。

---

## 修复示例：MockedStatic → PowerMock

```java
// 修改前（错误）
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

// 修改后（正确）
@RunWith(PowerMockRunner.class)
@PrepareForTest({SessionUtil.class})
public class XxxTest {
    @Before
    public void setUp() {
        PowerMockito.mockStatic(SessionUtil.class);
    }
}
```
