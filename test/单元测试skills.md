---
name: java-unit-test-jdk8-springboot20-cn
description: 为运行在 JDK 8 和 Spring Boot 2.0.x 或同类老版本技术栈上的 Java Maven 项目创建、修复和验证单元测试。适用于新增 Service 或 Controller 单元测试、在不修改业务代码的前提下处理 GrayUtils 或 LoginUserUtils 等静态依赖、配置老项目 Surefire，以及为非 fork 测试运行生成 JaCoCo 覆盖率报告。
---

# Java 单元测试 JDK8 Spring Boot 2.0 通用模板

## 适用场景

当项目满足以下多数条件时，直接使用本模板：

- JDK：`1.8`
- Spring Boot：`2.0.1.RELEASE` 或同类较老的 `2.0.x`
- JUnit：`4.x`
- Mockito：来自 `spring-boot-starter-test` 的老版本
- Maven Surefire：`2.21.0` 左右
- 需要在本地、CI 或 K8s 中执行单元测试并生成 JaCoCo 覆盖率报告

## 核心结论

- 默认优先 `JUnit4 + Mockito`
- 不要默认用 `JUnit5`
- 不要默认引入 `mockito-inline`
- 不要默认引入 `PowerMock`
- 不要为了单元测试修改业务代码
- 优先在测试侧构造上下文和注入依赖
- 如果 Surefire fork 不稳定，优先 `forkCount=0 + JaCoCo 离线插桩 + @AfterClass dump(false)`

## 首先检查

开始写单测前，先确认真实运行环境，不要凭感觉判断：

- `mvn -v`
- `java -version`
- `JAVA_HOME`
- `pom.xml` 中的 Spring Boot、Surefire、JaCoCo 版本
- IDEA 或 CI 实际使用的 Maven JRE

原则：

- “以为是 JDK8”不等于“测试真跑在 JDK8”
- 本地、IDE、CI、K8s 使用的 JDK 不一致时，单测结论通常不可信

## 总体策略

### 1. 单元测试只测业务逻辑

默认只验证单个类或单个方法的业务逻辑，不验证完整系统联调结果。

以下内容默认都要隔离：

- 数据库
- Redis
- MQ
- Feign / HTTP / RPC
- 其他 Service / DAO
- Apollo / 配置中心
- 登录上下文 / 请求上下文 / 线程上下文

### 2. 优先顺序

优先级从高到低：

1. 普通 Mockito Mock
2. 在测试里构造真实上下文对象
3. 通过测试侧注入配置 / Bean / Request
4. 调整 Maven 构建配置
5. PowerMock

结论：

- 前 4 步能解决时，不要使用 PowerMock
- 非必要，不要为了单测改业务代码

### 3. Service 层默认写法

默认优先：

- `@RunWith(MockitoJUnitRunner.Silent.class)`
- `@Mock`
- `@InjectMocks`
- `ReflectionTestUtils.invokeMethod(...)`

禁止：

- `@SpringBootTest`
- 真实 Feign
- 真实 Apollo
- 真实数据库
- 把现有集成测试直接当单测跑
- 修改业务代码

### 4. Controller 层默认写法

默认优先：

- `@WebMvcTest`
- `MockMvc`
- `@MockBean`

Controller 单测重点：

- 参数解析
- HTTP 状态码
- JSON 结构
- 异常映射

不要在 Controller 单测里验证深层业务逻辑。

## 静态依赖处理原则

遇到 `GrayUtils`、`LoginUserUtils`、`ThreadLocalContext` 等静态依赖时，先不要直接上 PowerMock。

按以下顺序处理：

1. 看源码或反编译字节码
2. 找它真实读取的上下文来源
3. 在测试里构造该上下文
4. 只有完全找不到入口时，再考虑更重的方案

### GrayUtils 推荐处理方式

如果项目使用 `com.yl.sqs.gray.utils.GrayUtils`，优先在测试侧注入灰度源，而不是修改业务代码。

示例：

```java
@Mock
private GrayApolloUtils grayApolloUtils;

private void mockGray(boolean enabled) {
    when(grayApolloUtils.getApolloBooleanValue(
            "gray-switch.some.key", false
    )).thenReturn(enabled);
    new GrayUtils().setEnvironment(grayApolloUtils);
}
```

### LoginUserUtils / 请求上下文类推荐处理方式

如果最终依赖 `RequestContextHolder`，优先构造请求上下文：

```java
MockHttpServletRequest request = new MockHttpServletRequest();
RequestContextHolder.setRequestAttributes(new ServletRequestAttributes(request));
```

再按项目约定写入 header 或 attribute。

## 私有方法测试策略

如果公开入口链路太重，但目标只是覆盖某一个私有辅助方法中的复杂业务分支，可以直接通过反射调用私有方法，降低测试成本。

示例：

```java
AssessmentQueryPageDTO queryDTO = ReflectionTestUtils.invokeMethod(service, "getAssessmentQueryPageDTO", dto);
```

使用条件：

- 公开入口会引入大量无关依赖
- 你只想验证某个核心业务分支
- 使用反射能明显降低构造成本

## 推荐 POM 依赖

适合当前技术栈的最小测试依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-test</artifactId>
    <scope>test</scope>
</dependency>

<dependency>
    <groupId>org.jacoco</groupId>
    <artifactId>org.jacoco.agent</artifactId>
    <version>0.8.7</version>
    <classifier>runtime</classifier>
    <scope>test</scope>
</dependency>
```

说明：

- `spring-boot-starter-test`：提供 JUnit4、Mockito、Spring Test
- `org.jacoco.agent`：用于离线插桩场景下的覆盖率数据采集

不建议默认添加：

- `mockito-inline`
- `powermock-module-junit4`
- `powermock-api-mockito2`

## 推荐 Surefire 配置

对于当前这类老项目，推荐使用如下配置：

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-surefire-plugin</artifactId>
    <configuration>
        <skipTests>false</skipTests>
        <forkCount>0</forkCount>
        <systemPropertyVariables>
            <jacoco-agent.destfile>${project.build.directory}/jacoco.exec</jacoco-agent.destfile>
        </systemPropertyVariables>
        <excludes>
            <exclude>**/BaseTest.java</exclude>
            <exclude>**/ProjectWorkOrderFeignTest.java</exclude>
        </excludes>
    </configuration>
</plugin>
```

说明：

- `skipTests=false`：确保 K8s / CI 执行 `mvn test` 时不会默认跳过测试
- `forkCount=0`：避免老项目在 fork JVM 时崩溃
- `jacoco-agent.destfile`：让 JaCoCo 执行数据写到固定位置
- `excludes`：过滤测试父类和依赖外部环境的集成测试

## 推荐 JaCoCo 配置

当前版本组合下，推荐 JaCoCo 离线插桩：

```xml
<plugin>
    <groupId>org.jacoco</groupId>
    <artifactId>jacoco-maven-plugin</artifactId>
    <version>0.8.7</version>
    <executions>
        <execution>
            <id>jacoco-instrument</id>
            <phase>process-classes</phase>
            <goals>
                <goal>instrument</goal>
            </goals>
        </execution>
        <execution>
            <id>jacoco-restore</id>
            <phase>test</phase>
            <goals>
                <goal>restore-instrumented-classes</goal>
            </goals>
        </execution>
        <execution>
            <id>jacoco-report</id>
            <phase>test</phase>
            <goals>
                <goal>report</goal>
            </goals>
            <configuration>
                <dataFile>${project.build.directory}/jacoco.exec</dataFile>
                <outputDirectory>${project.build.directory}/jacoco-ut</outputDirectory>
            </configuration>
        </execution>
    </executions>
</plugin>
```

### 为什么不用 prepare-agent + fork

因为这类老项目常见问题是：

- Surefire fork 启动崩溃
- `mvn test` 能编译但测试 JVM 起不来
- JaCoCo 报告目录有了，但目标类仍然 `0%`

因此默认优先：

- `forkCount=0`
- 离线插桩
- 测试类 `@AfterClass dump(false)`

## 非 fork 模式下必须补的 JaCoCo 刷盘代码

如果 `forkCount=0`，建议在测试类末尾加：

```java
@AfterClass
public static void dumpJacocoExecutionData() throws Exception {
    Class<?> rtClass = Class.forName("org.jacoco.agent.rt.RT");
    Object agent = rtClass.getMethod("getAgent").invoke(null);
    agent.getClass().getMethod("dump", boolean.class).invoke(agent, false);
}
```

作用：

- 在 `report` 执行前主动把 execution data 写入 `target/jacoco.exec`
- 避免 `jacoco-sessions.html` 显示 `No execution data available`

## Service 单测推荐模板

```java
@RunWith(MockitoJUnitRunner.Silent.class)
public class XxxServiceImplTest {

    @InjectMocks
    private XxxServiceImpl service;

    @Mock
    private XxxDependencyA dependencyA;

    @Mock
    private XxxDependencyB dependencyB;

    @Mock
    private GrayApolloUtils grayApolloUtils;

    @AfterClass
    public static void dumpJacocoExecutionData() throws Exception {
        Class<?> rtClass = Class.forName("org.jacoco.agent.rt.RT");
        Object agent = rtClass.getMethod("getAgent").invoke(null);
        agent.getClass().getMethod("dump", boolean.class).invoke(agent, false);
    }

    @Test
    public void targetMethod_shouldReturnExpectedResult_whenConditionMatched() {
        Dto dto = new Dto();
        when(dependencyA.query(any())).thenReturn(buildMockData());
        when(grayApolloUtils.getApolloBooleanValue("gray-switch.some.key", false)).thenReturn(true);
        new GrayUtils().setEnvironment(grayApolloUtils);

        Result result = ReflectionTestUtils.invokeMethod(service, "targetMethod", dto);

        assertNotNull(result);
        assertEquals("expected", result.getSomeField());
        verify(dependencyA).query(any());
    }
}
```

## 针对业务分支的测试设计原则

当你只想覆盖某段分支逻辑时，优先覆盖以下场景：

1. 正常路径
   例如命中灰度开关并返回授权数据

2. 特定输入路径
   例如指定 `networkId`，且该值在授权范围内

3. 异常路径
   例如指定 `networkId` 不在授权范围内，抛出业务异常

断言维度优先包括：

- 返回值
- 集合内容
- 异常码和异常信息
- 依赖调用次数
- 某个依赖是否未被调用

## 测试失败排障顺序

单元测试失败时，按以下顺序处理：

1. 先确认 JDK、Spring Boot、Surefire、JaCoCo 版本
2. 确认失败是来自当前测试，还是来自别的测试类被扫描执行
3. 确认是否真的需要 Spring 容器
4. 确认依赖是否能通过普通 Mockito Mock
5. 遇到静态方法时，先找上下文入口，不要直接上 PowerMock
6. 覆盖率异常时，先看 `target/jacoco.exec`
7. 再看 `target/jacoco-ut/jacoco-sessions.html`
8. 最后打开目标类 HTML 页面，确认不是 `0%`

## 覆盖率验证标准

生成报告后，至少检查三层：

1. `target/jacoco.exec` 是否存在且大小正常
2. `target/jacoco-ut/jacoco-sessions.html` 是否存在 session
3. 目标类 HTML 页面是否有绿色覆盖，而不是全 `0%`

不要只看：

- `BUILD SUCCESS`
- `jacoco-ut` 目录存在
- 首页报告生成成功

这些都不足以证明覆盖率真实有效。

## 最终默认建议

遇到当前这类项目时，统一按下面的默认策略执行：

- JDK8 项目：先用 `JUnit4 + Mockito`
- Spring Boot 2.0.x：避免默认使用 JUnit5 和 mockito-inline
- 静态依赖：优先找真实上下文入口
- 单测生成：优先只改测试和 Maven 配置，不改业务代码
- 覆盖率：优先 `forkCount=0 + JaCoCo 离线插桩 + @AfterClass dump(false)`
- K8s 执行：确保 `mvn test` 能直接跑测试和出覆盖率报告
