---
name: java-unittest
description: 为 Java/Spring Boot 项目生成单元测试，遵循阿里命名规范。自动检测 JUnit 版本（JUnit 4 或 JUnit 5），使用 Mockito + mockito-inline/PowerMock（JUnit 4）或 Mockito/MockedStatic（JUnit 5）。支持增量模式（git diff vs master）、commit 模式（指定 commit id 之后的所有变更）、本地模式（git diff HEAD 未提交变更）和全量模式（用户指定类名/方法名）。适用于用户要求生成单元测试、补覆盖率、审查测试代码的场景。
allowed-tools: ["Bash(mvn:*)", "Bash(git:*)", "Bash(python:scripts/*)", "Read", "Glob", "Grep", "Edit", "Write"]
---

# Java 单元测试生成规范

生成或审查 Java 单元测试时必须遵循本规范。根据用户输入判断工作模式：

- **增量模式**（默认）：用户未指定类名或方法名，且未使用 `local` / `commit` 参数时，对比当前分支与 master 分支的 diff，仅为变更代码生成测试。
- **commit 模式**：用户传入 `commit {commitId}`（如 `commit f6f19fe2`）时，对比指定 commit 之后到 HEAD 的所有变更，为这些变更代码生成测试。
- **本地模式**（`local`）：用户传入 `local` 参数（如 `/java-unit-test local`）时，对比工作区与 HEAD 的 diff，仅为本地未提交的变更代码生成测试。
- **全量模式**：用户指定了类名或方法名时，为该类/方法生成完整的单元测试，覆盖所有公共方法。

---

## 执行流程

### 步骤 0：检测 JUnit 版本和 Mock 框架

生成测试前必须检测项目使用的 JUnit 版本和静态 Mock 框架。使用 `scripts/detect_framework.py` 脚本自动完成检测，结果自动缓存到 `.claude/test-framework-cache.json`（7 天有效期）。

**执行方式**：
```bash
python scripts/detect_framework.py {projectRoot}
```

脚本输出 JSON，包含以下字段：
- `junitVersion`: "4" 或 "5"
- `mockitoInline`: 是否存在 mockito-inline
- `powermock`: 是否存在 PowerMock
- `jacocoIntegrated`: 是否集成 JaCoCo
- `mockStrategy`: 框架策略标识

**根据 `mockStrategy` 字段确定后续方案**：

| mockStrategy | JUnit 版本 | Mock 方案 | 参考文件 |
|---|---|---|---|
| `ExtendWith_MockedStatic` | JUnit 5 | `@ExtendWith` + `MockedStatic` | `ref/ref-static-mock.md` |
| `ExtendWith_MockedStatic_NeedInline` | JUnit 5 | 需添加 `mockito-inline` 依赖，然后使用 `MockedStatic` | `ref/ref-static-mock.md` |
| `RunWith_MockedStatic` | JUnit 4 | `@RunWith(MockitoJUnitRunner)` + `MockedStatic` | `ref/ref-static-mock.md` |
| `RunWith_PowerMock` | JUnit 4 | `@RunWith(PowerMockRunner)` + PowerMock | `ref/ref-powermock.md` |
| `RunWith_PowerMock_NeedDeps` | JUnit 4 | 需添加 POM 依赖，使用 PowerMock | `ref/ref-powermock.md` |

**JUnit 5 通用规则**：
- 使用 `@ExtendWith(MockitoExtension.class)` 替代 `@RunWith`
- 使用 `@BeforeEach` / `@AfterEach` 替代 `@Before` / `@After`
- 禁止 PowerMock，静态方法 Mock 统一使用 `mockStatic()` + `MockedStatic`
- `@Value` 字段注入使用 `ReflectionTestUtils.setField()`

### 增量模式（用户未指定目标，非 local）

1. **采集变更**：
   ```bash
   python scripts/collect_changes.py --mode diff --base master {projectRoot}
   ```
   脚本自动执行 `git diff`，过滤测试类，解析变更方法，输出结构化 JSON。若 `files` 为空则提示用户并结束。

2. **扫描依赖**：
   ```bash
   python scripts/scan_dependencies.py {projectRoot} file1.java file2.java ...
   ```
   将步骤 1 输出中的文件路径传入，脚本自动识别依赖类型并输出需要的 `ref/ref-xxx.md` 列表。去重后一次性 `Read` 所需 ref 文件。

3. **批量读取被测类**：用 `Read` 并行读取所有目标源文件，理解完整类结构和依赖。

4. **批量生成测试**：为所有被测类生成增量测试（仅为 diff 中变更的方法），一次生成完毕。

5. **运行验证**：
   ```bash
   python scripts/parse_test_result.py {projectRoot} --tests "Class1Test,Class2Test,Class3Test"
   ```
   脚本自动运行 `mvn test`，解析输出，分类错误，输出结构化错误报告。根据 `category` 和 `priority` 字段逐个修复后重跑。

6. **覆盖率检查**：
   ```bash
   python scripts/parse_coverage.py {projectRoot} --threshold 90
   ```
   脚本自动运行 `mvn test jacoco:report`，解析 XML 报告，输出未覆盖的方法和行号。针对性补充测试用例，循环直到达标。

### commit 模式（用户传入 `commit {commitId}`）

1. **采集变更**：
   ```bash
   python scripts/collect_changes.py --mode commit --base {commitId} {projectRoot}
   ```
   脚本自动校验 commit id 有效性，执行 `git diff {commitId}..HEAD`，过滤测试类，解析变更方法。若 `files` 为空则提示用户「指定 commit {commitId} 之后无代码变更，无需生成测试」，结束。

2. **扫描依赖**：
   ```bash
   python scripts/scan_dependencies.py {projectRoot} file1.java file2.java ...
   ```

3. **批量读取被测类**：用 `Read` 并行读取所有目标源文件，理解完整类结构和依赖。

4. **批量生成测试**：为所有被测类生成增量测试（仅为 {commitId}..HEAD 的 diff 中变更的方法），一次生成完毕。

5. **运行验证**：
   ```bash
   python scripts/parse_test_result.py {projectRoot} --tests "Class1Test,Class2Test,Class3Test"
   ```

6. **覆盖率检查**：
   ```bash
   python scripts/parse_coverage.py {projectRoot} --threshold 90
   ```

### 本地模式（用户传入 `local` 参数）

1. **采集变更**：
   ```bash
   python scripts/collect_changes.py --mode local {projectRoot}
   ```
   脚本自动执行 `git diff HEAD`，过滤测试类，解析变更方法。同时检查未跟踪的新文件（`untracked` 字段），提醒用户确认是否需要为新增文件生成测试。

2. **扫描依赖**：
   ```bash
   python scripts/scan_dependencies.py {projectRoot} file1.java file2.java ...
   ```

3. **批量读取被测类**：用 `Read` 并行读取所有目标源文件，理解完整类结构和依赖。

4. **批量生成测试**：为所有被测类生成增量测试（仅为本地 diff 中变更的方法），一次生成完毕。

5. **运行验证**：
   ```bash
   python scripts/parse_test_result.py {projectRoot} --tests "Class1Test,Class2Test,Class3Test"
   ```

6. **覆盖率检查**：
   ```bash
   python scripts/parse_coverage.py {projectRoot} --threshold 90
   ```

### 全量模式（用户指定了类名或方法名）

1. **定位目标文件**：用 `Glob` 在 `src/main/java` 下搜索用户指定的类名（如 `Glob src/main/java/**/XxxService.java`）。

2. **扫描依赖**：
   ```bash
   python scripts/scan_dependencies.py {projectRoot} targetFile.java
   ```
   脚本自动识别依赖类型并输出需要的 `ref/ref-xxx.md` 列表，去重后一次性 `Read` 所需 ref 文件。

3. **读取被测类**：用 `Read` 直接读取目标源文件，理解完整类结构。

4. **生成全量测试**：为所有公共方法（或用户指定的方法）生成完整测试，覆盖正常/边界/异常全场景。

5. **运行验证**：
   ```bash
   python scripts/parse_test_result.py {projectRoot} --tests "XxxTest"
   ```

6. **覆盖率检查**：
   ```bash
   python scripts/parse_coverage.py {projectRoot} --threshold 90
   ```

信息获取优先使用 `scripts/` 下的脚本，脚本无法覆盖的场景再用 Glob/Grep/Read 获取信息。

---

## 1. 基础规范

### 框架与依赖

框架选择由步骤 0 检测结果自动决定：

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

- `public void` + `@Test`，单方法只测一个逻辑点，禁止多场景合并
- 覆盖正常、边界、异常场景；每个 `throw` 语句必须有独立测试方法
- 测试类 `/** */` 说明测试范围；测试方法 `/** */` 说明场景+覆盖行+验证点；关键行 `//` 说明 Mock/断言作用

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
- 报告命令：`mvn test jacoco:report`，路径：`target/jacoco-ut/index.html`。

---

## 7. 测试运行与验证

生成测试后使用脚本自动运行和解析，详细错误处理方案见 `ref-autofix.md`：

1. **运行测试并解析结果**：
   ```bash
   python scripts/parse_test_result.py {projectRoot} --tests "Class1Test,Class2Test,Class3Test"
   ```
   脚本自动检测 Maven、运行 `mvn test`、解析输出、分类错误。

2. **失败修复**：根据脚本输出的 `category` 和 `priority` 字段，按优先级修复：
   - `missing_dependency` / `compilation_error`：添加缺失依赖，详见 `ref/ref-autofix.md`
   - `class_not_found` / `method_not_found`：检查 Mockito 版本冲突
   - `mock_not_injected`：检查 Mock 注入和初始化
   - `assertion_mismatch`：调整断言值
   - 修复后仅重跑失败类：`python scripts/parse_test_result.py {projectRoot} --tests "XxxTest" --no-clean`

3. **覆盖率检查**：
   ```bash
   python scripts/parse_coverage.py {projectRoot} --threshold 90
   ```
   脚本自动运行 `mvn test jacoco:report`，解析 XML 报告。

4. **覆盖率不达标时循环补充**：根据脚本 `belowThreshold` 字段中未覆盖的方法和行号，针对性补充测试用例，然后用 `python scripts/parse_coverage.py {projectRoot} --threshold 90 --no-run` 重新验证，直到覆盖率达标或确认无法覆盖（需注释说明原因）。

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
