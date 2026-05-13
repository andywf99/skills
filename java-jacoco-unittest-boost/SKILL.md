---
name: java-jacoco-unittest-boost
description: 为 Maven 构建的 Java/Spring Boot 项目执行基于 JaCoCo 的单元测试补充专项。适用于用户要求按 pom.xml 中 jacoco-maven-plugin 原生 include/exclude 规则扫描未排除类，可临时向 JaCoCo execution configuration 合并通用 excludes，支持单模块/多模块项目，按源码目录顺序逐类补充单测、单类覆盖率达到 90%、最多重试 5 次、只新增或补充测试代码且不修改业务代码的场景；每个类的单测生成规范参考 java-unittest skill。
---

# Java JaCoCo 单测补充专项

## 核心原则

以项目 `pom.xml` 中 `jacoco-maven-plugin` 的原生配置为唯一覆盖率依据，按源码目录自上而下逐类补充单元测试。对每个未排除目标类执行“补充用例 -> Maven 测试 -> JaCoCo 覆盖率校验”的闭环，单类覆盖率达到 90% 后才进入下一个类；最多重试 5 次，仍未达标则记录并跳过。

若用户未指定项目路径，默认使用当前工作目录作为项目根目录。

## 必须遵守

- 严禁修改业务代码、生产配置、接口契约、SQL、资源文件等非测试内容；唯一例外是可临时调整 `pom.xml` 中 `jacoco-maven-plugin` 的覆盖率统计 excludes，且必须在交付记录中说明并按用户要求还原或保留。
- 临时 JaCoCo excludes 默认在任务结束前还原；只有用户明确要求保留时才保留在 `pom.xml`。
- 严禁删除、重写、弱化原有单元测试；优先新增独立补充测试类，确需复用现有测试类时只允许追加 import、字段和测试方法，不改写已有断言与逻辑。
- 仅处理 `jacoco-maven-plugin` 配置中未排除的 Java 类；排除类、测试类、生成代码和非统计类直接跳过。
- 必须按项目文件目录自上而下的顺序处理目标类，不跳类、不调序、不批量无序推进。
- 单类覆盖率达标线为 90%。若 JaCoCo 配置指定了 rule/counter/covered ratio，则按项目原生 rule 判定；未指定时默认以 `LINE >= 90%` 为达标主判定，`BRANCH`、`INSTRUCTION` 作为辅助记录。无分支类的 `BRANCH` 可记为 `N/A`，不得因此判失败。
- 单类最多执行 5 轮补充与验证。第 5 轮后仍未达 90%，记录类路径、覆盖率数据和未覆盖点，然后继续下一类。
- 每个类文件的单测生成、Mock 策略、命名、断言和依赖隔离规范，优先参考 `java-unittest` skill；如其脚本可用，优先复用其框架检测、测试执行和覆盖率解析脚本。
- 禁止通过空跑测试、无断言测试、mock 被测类自身、降低覆盖率阈值、扩大 excludes 排除真实业务类、反射调用无业务意义私有方法等方式刷覆盖率。

## 执行流程

### 1. 解析 JaCoCo 配置

1. 定位项目根目录和主 `pom.xml`。
2. 识别 Maven 结构：若当前目录是聚合父工程，读取 `<modules>`，优先选择包含 `src/main/java` 的业务 module；若用户指定 module，则只处理指定 module。多模块命令优先使用 `mvn -pl <module> -am ...`。
3. 读取原始 POM；若插件配置来自父 POM 或 profile，执行 Maven effective POM 辅助确认，但最终仍以项目实际 Maven 构建生效配置为准。
4. 提取 `jacoco-maven-plugin` 的 `includes`、`excludes`、`rules`、`limits`、`report` 输出目录、`prepare-agent` 配置和 profile 激活条件。
5. 记录覆盖率维度：优先读取 `rules.limit.counter` 与 `rules.limit.value`，常见包括 `LINE`、`BRANCH`、`INSTRUCTION`、`METHOD`、`CLASS`。
6. 若 `jacoco-maven-plugin` 的 `<executions>` -> `<execution>` -> `<configuration>` 未完整包含通用排除规则，允许临时合并下方 `<excludes>`，用于过滤配置类、DTO、实体、Feign、枚举、VO/PO/Model 等不纳入专项补测的代码；该改动属于覆盖率统计临时配置，不属于业务代码变更。
7. 合并 excludes 时必须保留已有 excludes，只追加缺失项，不重复添加，不覆盖用户原有配置，不大面积重排 XML；若不存在 `<excludes>`，只在目标 execution 的 `<configuration>` 下新增该节点。
8. 若项目没有 JaCoCo 配置，不擅自新增插件；先向用户说明无法按本专项执行，除非用户明确要求接入 JaCoCo。

临时补充的通用 excludes：

```xml
<excludes>
    <exclude>**/*Configuration.class</exclude>
    <exclude>**/*Config.class</exclude>
    <exclude>**/*DTO.class</exclude>
    <exclude>**/*Dto.class</exclude>
    <exclude>**/*Entity.class</exclude>
    <exclude>**/*Feign.class</exclude>
    <exclude>**/*Enum.class</exclude>
    <exclude>**/*PO.class</exclude>
    <exclude>**/*Topic.class</exclude>
    <exclude>**/po/**</exclude>
    <exclude>**/vo/**</exclude>
    <exclude>**/dto/**</exclude>
    <exclude>**/entity/**</exclude>
    <exclude>**/enums/**</exclude>
    <exclude>**/feign/**</exclude>
    <exclude>**/annotation/**</exclude>
    <exclude>**/constants/**</exclude>
    <exclude>**/exception/**</exclude>
    <exclude>**/model/**</exclude>
    <exclude>**/filter/**</exclude>
    <exclude>**/configuration/**</exclude>
    <exclude>**/config/**</exclude>
    <exclude>**/aspect/**</exclude>
    <exclude>**/constant/**</exclude>
    <exclude>**/configs/**</exclude>
</excludes>
```

### 2. 生成目标类清单

1. 扫描 `src/main/java` 下所有 `.java` 文件。
2. 按文件系统路径字典序排序，保持目录自上而下顺序。
3. 将路径转换为 JaCoCo 类名匹配格式，严格应用 include/exclude 规则。
4. 排除明显不应处理的文件：测试文件、`target/`、生成目录、`package-info.java`、`module-info.java`、枚举常量容器、纯常量类、接口类；如果 JaCoCo 原生配置仍统计其中某类，则记录原因后按实际可测性处理。
5. 输出本轮目标类清单，后续必须逐类处理。
6. 将目标清单和处理进度记录到 `.codex/jacoco-unittest-progress.md`；若目录不存在则创建。长任务恢复时先读取该文件，继续处理第一个未完成目标类。

进度文件建议格式：

```text
项目根目录：
模块：
JaCoCo excludes 状态：未修改/已临时合并/已还原/用户要求保留
当前进度：已处理 x/y

| 顺序 | 类路径 | 状态 | line% | branch% | instruction% | 轮次 | 说明 |
```

### 3. 逐类补充单测

对每个目标类按顺序执行：

1. 读取目标类、同包现有测试类、相关依赖和已有测试风格。
2. 检测项目测试框架：JUnit 4/JUnit 5、Mockito、mockito-inline、PowerMock、Spring Test、AssertJ 等。
3. 按 `java-unittest` 规范设计补充用例，覆盖正常业务、边界值、空值、异常抛出、条件分支、外部依赖异常、幂等或状态变更等核心路径。
4. 优先新增 `被测类名 + Test` 或 `被测类名 + CoverageTest`；如果已有测试类存在且风格稳定，可只追加新的补充测试方法。
5. Mock 所有外部依赖，禁止连接真实 DB、Redis、MQ、HTTP、文件系统生产路径或第三方服务。
6. 写操作必须 `verify()` 关键依赖调用次数和核心字段；异常断言必须校验类型和关键消息；业务返回值断言必须比较具体期望值。

### 4. 验证覆盖率

每轮补充后运行项目原生命令，尽量限定测试范围以节省时间，但覆盖率报告必须能映射到单类：

```bash
mvn test jacoco:report
```

如项目已有专用 profile 或报告路径，使用项目原有命令，例如：

```bash
mvn -Pcoverage test jacoco:report
mvn -pl <module> -am test jacoco:report
```

解析 `target/site/jacoco/jacoco.xml`、`target/jacoco-ut/jacoco.xml` 或 POM 配置指定的 XML 报告。按 JaCoCo class/sourcefile 节点定位当前目标类，计算并记录 line、branch、instruction 覆盖率和未覆盖行。

覆盖率判定优先级：

1. 若 POM 中配置了 JaCoCo `rules`，按配置的 counter 与 minimum/coveredratio 判定单类是否达标。
2. 若 POM 未配置 rule，默认以当前类 `LINE >= 90%` 判定达标。
3. `BRANCH` 与 `INSTRUCTION` 必须记录；当类没有可统计分支时，`BRANCH` 记为 `N/A`。
4. 覆盖率报告无法定位到当前类时，不判定达标，先排查报告路径、模块、class 文件名映射和 excludes。

### 5. 达标与重试

对当前类执行最多 5 轮：

```text
for attempt in 1..5:
  补充缺口用例
  运行测试和 JaCoCo 报告
  解析当前类覆盖率
  if 当前类覆盖率 >= 90%:
    记录到达标清单
    break
if 5 轮后仍未达标:
  记录到未达标清单
  继续下一个目标类
```

重试时只针对未覆盖方法、分支和异常路径补充测试。不得为了覆盖率修改生产代码，不得删除已有测试，不得降低断言质量。

每处理完一个类都更新 `.codex/jacoco-unittest-progress.md`。每处理完 5 个类或阶段性暂停时，向用户汇报一次：

```text
已处理：x/y
当前类：
达标：
未达标：
临时 JaCoCo excludes：
下一类：
```

## 与 java-unittest 的协作

需要生成每个类的具体测试代码时，读取并遵循 `java-unittest` skill，尤其是：

- JUnit 4/JUnit 5 与 Mock 框架检测策略。
- Mockito、mockito-inline、PowerMock、静态方法 Mock 的选择。
- 阿里命名规范：测试类名、`test_方法名_场景_预期` 方法名、语义化变量名。
- 断言质量要求：禁止弱断言，异常断言同时验证类型与消息，BigDecimal 使用 `isEqualByComparingTo()`。
- 外部依赖 Mock 要求：Mapper、Feign、Redis、MQ、灰度开关、静态工具类等按项目已有风格隔离。
- 测试失败时的编译错误、依赖缺失、Mock 注入失败、断言不匹配等分类修复流程。

如 `java-unittest/scripts` 可用，优先使用：

```bash
python <java-unittest>/scripts/detect_framework.py <projectRoot>
python <java-unittest>/scripts/scan_dependencies.py <projectRoot> <targetFile.java>
python <java-unittest>/scripts/parse_test_result.py <projectRoot> --tests "<TestClass>"
python <java-unittest>/scripts/parse_coverage.py <projectRoot> --threshold 90
```

脚本输出与项目实际 JaCoCo 原生报告不一致时，以项目 Maven/JaCoCo 原生报告为准。

## 记录输出

工作结束或阶段性暂停时，必须给出以下结果：

### 单元测试达标类清单

记录所有覆盖率达到 90% 的类：

```text
类全路径 | 测试类路径 | line% | branch% | instruction% | 达标轮次
```

### 单元测试未达标类记录

记录 5 轮后仍未达标的类：

```text
类全路径 | line% | branch% | instruction% | 未覆盖方法/行号 | 未达标原因 | 已补充测试说明
```

### 最终 JaCoCo 报告

记录最终测试命令、报告 XML/HTML 路径、整体覆盖率、临时 JaCoCo excludes 是否已加入/是否已还原，以及仍需人工决策的问题。

若临时修改过 `pom.xml`，默认在最终交付前还原该 excludes 改动；若用户明确要求保留，则记录“用户要求保留”。

## 完成前自检

- [ ] 已解析并遵循项目 `jacoco-maven-plugin` 原生 include/exclude/rule 配置。
- [ ] 如临时补充 JaCoCo excludes，已记录 POM 变更状态；默认已还原，或已记录用户明确要求保留。
- [ ] 多模块项目已定位实际业务 module，并使用正确的 Maven `-pl/-am` 命令。
- [ ] 已维护 `.codex/jacoco-unittest-progress.md` 进度文件，可断点续跑。
- [ ] 已按 `src/main/java` 目录顺序逐类处理，未跳类、未调序。
- [ ] 只新增或追加测试代码，未修改业务代码，未删除或弱化原有测试。
- [ ] 每个已处理类都有测试运行结果和单类 JaCoCo 覆盖率记录。
- [ ] 达标类覆盖率达到 90%；未达标类已经完成 5 次以内重试并记录原因。
- [ ] 最终输出包含达标清单、未达标记录和 JaCoCo 整体报告路径。
