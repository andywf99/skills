---
name: java-unittest
description: 为 Java/Spring Boot 项目生成单元测试，遵循阿里命名规范。自动检测 JUnit 版本（JUnit 4 或 JUnit 5），使用 Mockito + mockito-inline/PowerMock（JUnit 4）或 Mockito/MockedStatic（JUnit 5）。支持增量模式（git diff vs master）、commit 模式（指定 commit id 之后的所有变更）、本地模式（git diff HEAD 未提交变更）和全量模式（用户指定类名/方法名）。适用于用户要求生成单元测试、补覆盖率、审查测试代码的场景。
allowed-tools: ["Bash(mvn:*)", "Bash(git:*)", "Read", "Glob", "Grep", "Edit", "Write"]
---

# Java 单元测试生成规范

生成或审查 Java 单元测试时必须遵循本规范。根据用户输入判断工作模式：

- **增量模式**（默认）：用户未指定类名或方法名，且未使用 `local` / `commit` 参数时，对比当前分支与 master 分支的 diff，仅为变更代码生成测试。
- **commit 模式**：用户传入 `commit {commitId}`（如 `commit f6f19fe2`）时，对比指定 commit 之后到 HEAD 的所有变更，为这些变更代码生成测试。
- **本地模式**（`local`）：用户传入 `local` 参数（如 `/java-unit-test local`）时，对比工作区与 HEAD 的 diff，仅为本地未提交的变更代码生成测试。
- **全量模式**：用户指定了类名或方法名时，为该类/方法生成完整的单元测试，覆盖所有公共方法。

---

## 执行流程（严格按此顺序，禁止使用 Agent 工具）

### 步骤 0：检测 JUnit 版本和 Mock 框架（所有模式必执行）

在生成测试之前，必须先检测项目使用的 JUnit 版本和静态 Mock 框架。

**缓存机制**：检测结果自动缓存到项目级文件 `.claude/test-framework-cache.json`，后续调用直接读取缓存，跳过检测。

**缓存文件格式**：
```json
{
  "junitVersion": "4",
  "mockitoInline": false,
  "powermock": false,
  "jacocoIntegrated": true,
  "detectedAt": "2026-04-24T14:30:00"
}
```

**检测流程**（缓存不存在时执行）：

**1. 检测 JUnit 版本：**
- `Grep` 搜索 `pom.xml` 中是否包含 `junit-jupiter`（artifactId 为 `junit-jupiter` 或 `junit-jupiter-api`）。
- 存在 → **JUnit 5 模式**
- 不存在 → **JUnit 4 模式**

**2. 统一检测 `mockito-inline` 和 `powermock`：**

| JUnit 版本 | mockito-inline | powermock | 策略 |
|------------|----------------|-----------|------|
| JUnit 5 | 有 | - | `@ExtendWith` + `MockedStatic`，阅读 `ref/ref-static-mock.md` |
| JUnit 5 | 无 | - | 将 `mockito-inline` 依赖添加到 `pom.xml`，然后使用 `MockedStatic`，阅读 `ref/ref-static-mock.md` |
| JUnit 4 | 有 | - | `@RunWith(MockitoJUnitRunner)` + `MockedStatic`，阅读 `ref/ref-static-mock.md` |
| JUnit 4 | - | 有 | `@RunWith(PowerMockRunner)` + PowerMock，阅读 `ref/ref-powermock.md` |
| JUnit 4 | 有 | 有 | 优先 `MockedStatic`，不引入 PowerMock，阅读 `ref/ref-static-mock.md` |
| JUnit 4 | 无 | 无 | 阅读 `ref/ref-powermock.md`，将「POM 依赖」添加到 `pom.xml`，使用 PowerMock |

**3. JUnit 5 模式额外说明：**
- 使用 `@ExtendWith(MockitoExtension.class)` 替代 `@RunWith`
- 使用 `@BeforeEach` / `@AfterEach` 替代 `@Before` / `@After`
- 禁止 PowerMock，静态方法 Mock 统一使用 `mockStatic()` + `MockedStatic`
- `@Value` 字段注入使用 `ReflectionTestUtils.setField()`（JUnit 4 同样适用）

### 增量模式（用户未指定目标，非 local）

1. **获取变更文件**：`git diff --name-only master` 拿到变更文件列表，仅关注 Service/Controller/Component 类。
2. **获取变更内容**：`git diff master -- <文件>` 查看具体 diff，确定变更的方法。
3. **读取被测类**：用 `Read` 直接读取目标源文件，理解完整类结构和依赖。
4. **按需读取 ref**：根据被测类的依赖类型和步骤 0 的检测结果，用 `Read` 读取对应的 `ref/ref-xxx.md`。
5. **生成增量测试**：仅为 diff 中变更的方法生成测试，不测存量方法。
6. **运行验证**：`mvn clean test -Dtest=XxxTest`，失败则修复后重新运行。

### commit 模式（用户传入 `commit {commitId}`）

1. **校验 commit id**：`git rev-parse --verify {commitId}` 验证 commit id 是否存在。无效则提示用户检查并重新输入。
2. **获取变更文件**：`git diff --name-only {commitId} HEAD` 拿到该 commit 之后到 HEAD 的所有变更文件，仅关注 Service/Controller/Component 类。
   - 若无变更文件：提示用户「指定 commit {commitId} 之后无代码变更，无需生成测试」，**结束**。
3. **获取变更内容**：`git diff {commitId} HEAD -- <文件>` 查看具体 diff，确定变更的方法。
4. **读取被测类**：用 `Read` 直接读取目标源文件，理解完整类结构和依赖。
5. **按需读取 ref**：根据被测类的依赖类型和步骤 0 的检测结果，用 `Read` 读取对应的 `ref/ref-xxx.md`。
6. **生成增量测试**：仅为 {commitId}..HEAD 的 diff 中变更的方法生成测试，不测存量方法。
7. **运行验证**：`mvn clean test -Dtest=XxxTest`，失败则修复后重新运行。

### 本地模式（用户传入 `local` 参数）

1. **获取本地变更文件**：`git diff HEAD --name-only` 拿到工作区与 HEAD 的差异文件列表（包含已暂存和未暂存的变更），仅关注 Service/Controller/Component 类。
   - 若无变更，尝试 `git status --short` 确认是否有未跟踪的新文件，提醒用户确认是否需要为新增文件生成测试。
2. **获取变更内容**：`git diff HEAD -- <文件>` 查看具体 diff，确定变更的方法。
3. **读取被测类**：用 `Read` 直接读取目标源文件，理解完整类结构和依赖。
4. **按需读取 ref**：根据被测类的依赖类型和步骤 0 的检测结果，用 `Read` 读取对应的 `ref/ref-xxx.md`。
5. **生成增量测试**：仅为本地 diff 中变更的方法生成测试，不测存量方法。
6. **运行验证**：`mvn clean test -Dtest=XxxTest`，失败则修复后重新运行。

### 全量模式（用户指定了类名或方法名）

1. **定位目标文件**：用 `Glob` 搜索用户指定的类名（如 `**/XxxService.java`）。
2. **读取被测类**：用 `Read` 直接读取目标源文件，理解完整类结构。
3. **按需读取 ref**：根据被测类的依赖类型和步骤 0 的检测结果，用 `Read` 读取对应的 `ref/ref-xxx.md`。
4. **生成全量测试**：为所有公共方法（或用户指定的方法）生成完整测试，覆盖正常/边界/异常全场景。
5. **运行验证**：`mvn clean test -Dtest=XxxTest`，失败则修复后重新运行。

**禁止**：禁止使用 Agent/Explore 等子代理工具搜索项目，直接用 Glob/Grep/Read 获取信息。

---

## 1. 基础规范

### 框架与依赖

框架选择由步骤 0 检测结果自动决定，以下是各模式下的注解和约束速查：

| 模式 | 测试注解 | 生命周期 | 扩展/Runner | 静态 Mock | 参考文件 |
|------|----------|----------|-------------|-----------|----------|
| JUnit 5 | `org.junit.jupiter.api.Test` | `@BeforeEach` / `@AfterEach` | `@ExtendWith(MockitoExtension.class)` | `mockStatic()` + `MockedStatic` | `ref/ref-static-mock.md` |
| JUnit 4 + mockito-inline | `org.junit.Test` | `@Before` / `@After` | `@RunWith(MockitoJUnitRunner.class)` | `Mockito.mockStatic()` + `MockedStatic` | `ref/ref-static-mock.md` |
| JUnit 4 + PowerMock | `org.junit.Test` | `@Before` / `@After` | `@RunWith(PowerMockRunner.class)` | `PowerMockito.mockStatic()` | `ref/ref-powermock.md` |

**禁止项：**
- 禁止在同一测试类中混用 `MockedStatic` 和 PowerMock
- 禁止混用 JUnit 4 和 JUnit 5 注解
- 禁止连接真实依赖，依赖隔离仅用 Mockito

**通用规则：**
- 断言优先 AssertJ；禁止混用多种断言风格
- `@Value` 字段注入统一使用 `ReflectionTestUtils.setField()`

### 命名规范（阿里）

| 类型       | 规则                             | 示例                                |
|------------|----------------------------------|-------------------------------------|
| 测试类名   | 被测类名 + `Test`，大驼峰        | `DeviceUploadInfoServiceTest`       |
| 测试方法名 | `test_方法名_场景_预期结果`      | `test_upload_validParam_returnSuccess` |
| 测试变量   | 小驼峰，语义化                   | `expectedUploadResult`              |

禁止中文方法名、无意义命名（如 `test1`）。

### 方法与注释规范

- `public void` + `@Test`，**单方法只测一个逻辑点**，禁止多场景合并。
- 覆盖正常、边界、异常场景；每个 `throw` 语句必须有独立测试方法。
- 测试类 `/** */` 说明测试范围；测试方法 `/** */` 说明场景+覆盖行+验证点；关键行 `//` 说明 Mock/断言作用。

---

## 2. 断言强制要求

- **禁止弱断言**作为主要断言：`isNotNull()` / `isPositive()` / `isInstanceOf()` 禁止单独使用。
- 返回值断言**必须**比对具体业务期望值，注释中写出计算公式。
- 异常断言必须同时验证**类型和消息**：`.isInstanceOf(X.class).hasMessage("xxx")`。
- BigDecimal 比较用 `isEqualByComparingTo()`，禁止 `isEqualTo()`。

---

## 3. 外部依赖 Mock

根据被测代码实际依赖，**阅读对应参考文件**获取 Mock 模板和必测场景：

| 依赖类型       | 参考文件                     | 必测场景概要                                    |
|----------------|------------------------------|------------------------------------------------|
| 静态方法（JUnit 5 / JUnit 4 + mockito-inline） | `ref/ref-static-mock.md` | MockedStatic 配置、生命周期管理、常见静态类 |
| 静态方法（JUnit 4 + PowerMock）     | `ref/ref-powermock.md`      | PowerMock 配置、`@PrepareForTest`、常见静态类    |
| GraySwitch 灰度开关 | `ref/ref-gray-switch.md` | 灰度开启/关闭双场景、Controller 层统一拦截返回 |
| Mapper/MyBatis | `ref/ref-mapper.md`          | 存在/null/空集合 + 写操作成功/失败 + verify 字段 |
| Feign 客户端   | `ref/ref-feign.md`           | 正常返回 / 抛异常 / 返回 null（降级）            |
| Redis          | `ref/ref-redis.md`           | 缓存命中/未命中 + 中间对象 Mock                   |
| MQ             | `ref/ref-mq.md`              | Producer verify destination+消息体 / Consumer 幂等+异常 |

**通用规则**：
- 有 Mock 依赖的写操作，必须 `verify()` 校验调用次数和参数字段值（`argThat`），禁止只用 `any()`。
- 纯查询场景可豁免 verify，但需注释说明原因。

---

## 4. 边界值与精度

- 数值边界：`threshold-1`、`threshold` 各自独立测试方法。
- 字符串/null：null、`""`、`"  "` 各自独立覆盖。
- BigDecimal 计算：必须有触发舍入的用例。

---

## 5. 测试范围

- **增量模式**：仅为当前分支 vs master 的 diff 变更方法编写测试，不补测存量方法。存量依赖用 Mockito 模拟返回值。
- **commit 模式**：仅为指定 commit 之后到 HEAD 的 diff 变更方法编写测试，不补测存量方法。存量依赖用 Mockito 模拟返回值。
- **本地模式**：仅为工作区 vs HEAD 的 diff 变更方法编写测试（即本地未提交的变更），不补测已提交或存量方法。
- **全量模式**：为用户指定类的所有方法（或指定方法）生成完整测试，覆盖正常/边界/异常全场景。

---

## 6. JaCoCo 覆盖率

- 变更代码：行覆盖率 ≥ 90%，分支覆盖率 ≥ 90%。
- 未集成 JaCoCo 时，生成插件配置（v0.8.7）并说明插入位置。
- 报告命令：`mvn clean test jacoco:report`，路径：`target/jacoco-ut/index.html`。

---

## 7. 测试运行与验证

生成测试后执行以下步骤，详细错误处理方案见 `ref-autofix.md`：

1. **检测 Maven**：`mvn -v`，不存在则询问用户安装地址。
2. **运行测试**：`mvn clean test -Dtest=XxxTest`
3. **失败修复**：根据错误类型自动修复（依赖缺失/编译/运行时/断言），详见 `ref/ref-autofix.md`。
4. **覆盖率报告**：`mvn clean test jacoco:report`
5. **覆盖率不达标时循环补充**：解析 JaCoCo 报告，若行覆盖率 < 90% 或分支覆盖率 < 90%，定位未覆盖的类/方法/分支，针对性补充测试用例，重新运行步骤 2-4，直到覆盖率达标或确认无法覆盖（需注释说明原因）。

---

## 8. 输出要求

- 生成完整测试类（含全部 import），标注测试方法对应的 Git 变更行。
- 附带覆盖率说明（行 ≥ 90%、分支 ≥ 90%）。
- 未集成的依赖/插件，生成 POM 片段并标明插入位置。
- 注释全部中文。
- 附带测试运行命令 + JaCoCo 报告生成命令。
- 测试必须可运行且通过，否则提供修复方案。

---

## 自检清单

**结构与命名**：
- [ ] 增量模式仅覆盖 diff 变更方法；commit 模式仅覆盖指定 commit 之后的变更方法；本地模式仅覆盖本地未提交变更方法；全量模式覆盖用户指定类/方法的所有场景
- [ ] 命名符合阿里规范（`test_xxx_场景_预期`），无中文方法名
- [ ] 中文注释完整（类/方法/关键行），说明覆盖场景和验证点
- [ ] JUnit 版本与项目一致，未混用 JUnit 4 和 JUnit 5
- [ ] 静态 Mock 框架未混用（MockedStatic 与 PowerMock 二选一）

**断言质量**：
- [ ] 核心断言为具体业务期望值（非弱断言）
- [ ] 异常断言同时验证类型和消息
- [ ] 数值边界独立覆盖临界值 ±1，BigDecimal 用 `isEqualByComparingTo()`
- [ ] 每个 `throw` 有独立测试方法

**依赖 Mock**：
- [ ] 写操作有 `verify()` 校验参数字段（`argThat`），非仅 `any()`
- [ ] 各依赖类型按参考文件覆盖必测场景
- [ ] 静态 Mock 框架配置完整（根据检测版本）：
  - JUnit 5：`@ExtendWith(MockitoExtension.class)` + `mockStatic()` + `@AfterEach` 关闭
  - JUnit 4 + mockito-inline：`MockedStatic` + `try-with-resources` + `@After` 关闭
  - JUnit 4 + PowerMock：`@RunWith(PowerMockRunner.class)` + `@PrepareForTest` + `mockStatic`
- [ ] GraySwitch 灰度开关覆盖开启/关闭双场景，Controller 层验证不调用 Service

**验证**：
- [ ] 测试可运行且通过
- [ ] 覆盖率达标（行 ≥ 90%、分支 ≥ 90%）
- [ ] 已提供运行命令和报告路径


## 效率优化原则                                                                
                                                                                                         
1. **先运行现有测试**：在生成新测试前，先执行 `mvn test -Dtest=XxxTest`，检查是否已有测试用例及编译错误        
2. **检查现有覆盖**：用 `Grep` 快速搜索测试文件中是否已有目标方法的测试（如 `grep "test_queryTransportation"`）
3. **批量修复同类错误**：编译错误通常是同一类问题，应一次性批量替换而非逐个修复                          
4. **精确定位代码**：用 `Grep -n` 定位关键代码行号，再用 `Read offset/limit` 定向读取，避免分段读取大文件
5. **复用已有测试结构**：若测试类已存在，优先修复编译错误并补充缺失场景，而非重写整个测试类
