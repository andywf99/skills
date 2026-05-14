---
name: java-jacoco-unittest-boost
description: 为 Maven Java/Spring Boot 项目执行全量单测补充。适用于用户要求先检查现有测试基线是否正常、基线失败时参考 /java-unittest 最多修复 10 次、基线正常后生成 JaCoCo 报告、按固定 excludes 过滤类、找出单类覆盖率不超过 90% 的目标类并记录到当前项目 .claude 目录、再由监督 agent 管理多个子 agent 按 /java-unittest 逐类补测的场景；单类优先尝试覆盖率 100%，5 次达不到 100% 但达到 90% 以上也视为通过；严格禁止修改业务代码和已提交的单测代码。
---

# Java 全量单测补充

## 核心目标

对当前 Maven Java 项目执行全量单测补充：先保证现有测试基线能正常运行，再基于 JaCoCo 报告和固定排除规则找出单类覆盖率不超过 90% 的类，记录到当前项目 `.claude` 目录，由监督 agent 管理多个子 agent 逐类补测。

未指定项目路径时，默认使用当前工作目录作为项目根目录。

## 硬性约束

- 严禁修改业务代码。
- 不能更改已提交的单测代码。严禁删除、移动、重命名、改后缀、重写、弱化断言或修改已有测试逻辑。
- 只允许新增未提交的测试文件，或在未提交的新测试文件中调整本轮生成内容。
- 如需修复基线测试，只能参考 `/java-unittest` 的诊断思路处理测试运行问题；若修复需要修改业务代码或已提交单测代码，视为不可修复。
- 目标类筛选必须基于 JaCoCo 报告和本 Skill 固定 excludes。
- 命中 excludes 的类不进入目标清单；未命中 excludes 且单类覆盖率不超过 90% 的类必须进入目标清单。
- 子 agent 每完成一个类都必须更新当前项目 `.claude` 下的日志和进度。
- 单个目标类优先尝试覆盖率 100%；最多尝试 5 次。5 次内达到 100% 立即记录为 `通过`；5 次后未达到 100% 但达到 90% 以上，也记录为 `通过`；5 次后仍低于 90%，记录为 `不通过`。

## 输出文件

所有运行产物写入当前项目目录的 `.claude` 下：

```text
.claude/jacoco-unittest-targets.md
.claude/jacoco-unittest-progress.md
.claude/jacoco-unittest-agent-log.md
.claude/jacoco-report-summary.md
.claude/jacoco-report-data.md
.claude/jacoco-unittest-constraints.md
```

若 `.claude` 不存在，先创建。

## 约束防忘

启动子 agent 前，必须生成或更新约束摘要文件：

```text
.claude/jacoco-unittest-constraints.md
```

约束摘要至少包含：

- 不能修改业务代码。
- 不能更改已提交的单测代码。
- 子 agent 必须参考 `/java-unittest` 和项目已有单测结构。
- 单类优先尝试覆盖率 100%；5 次后达不到 100% 但达到 90% 以上也视为通过。
- 基线测试最多修复 10 次。
- 所有目标、进度、日志写入当前项目 `.claude` 目录。

每个子 agent 开始处理类前，必须先读取 `.claude/jacoco-unittest-constraints.md` 并在日志中写明“已读取约束”。每完成一个类，必须在 `.claude/jacoco-unittest-agent-log.md` 写入约束自检结果。监督 agent 如果发现约束自检缺失，必须要求补齐，不允许继续分配下一类。

## 固定 excludes

生成 JaCoCo 目标类清单时必须应用以下排除规则：

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

## 执行流程

### 1. 基线测试检查

1. 先运行项目现有测试，确认基线能正常运行。
   - 单模块优先使用：`mvn test`
   - 多模块使用实际业务 module：`mvn -pl <module> -am test`
2. 如果基线测试通过，继续生成 JaCoCo 报告。
3. 如果基线测试失败，参考 `/java-unittest` 的测试诊断和修复方式尝试修复。
4. 基线测试最多修复 10 次；每次修复后必须重新运行测试。
5. 修复 10 次仍不能正常运行时，立即终止本 Skill，并提示用户：

```text
不能修复单测，已参考 /java-unittest 尝试修复 10 次，基线测试仍不能正常运行。
```

6. 基线不可修复时，不生成目标清单，不启动子 agent 补测。

### 2. 生成 JaCoCo 报告

基线测试正常后，执行项目原生 JaCoCo 报告命令。优先使用项目已有 profile 或脚本；没有特殊命令时使用：

```bash
mvn test jacoco:report
```

多模块项目可使用：

```bash
mvn -pl <module> -am test jacoco:report
```

解析 `target/site/jacoco/jacoco.xml`、`target/jacoco-ut/jacoco.xml` 或项目 POM 中指定的 JaCoCo XML 报告路径。解析后的 JaCoCo 明细数据必须存入当前项目 `.claude` 目录。

将报告概要写入：

```text
.claude/jacoco-report-summary.md
```

将解析后的明细数据写入：

```text
.claude/jacoco-report-data.md
```

明细数据至少包含：

```text
JaCoCo XML：
生成命令：

| 类路径 | 类名 | line% | branch% | instruction% | method% | class% | missedLines | coveredLines |
```

### 3. 生成目标清单

根据 `.claude/jacoco-report-data.md` 生成目标清单：

1. 读取已解析的 JaCoCo class/sourcefile 覆盖率数据。
2. 应用固定 excludes，命中排除规则的类直接跳过。
3. 对未排除类计算单类覆盖率。
4. 找出单类覆盖率不超过 90% 的类。
5. 按源码路径自上而下排序。
6. 写入：

```text
.claude/jacoco-unittest-targets.md
```

目标清单格式：

```text
项目根目录：
JaCoCo 报告：
阈值：> 90% 视为完成，<= 90% 进入补测

| 顺序 | 类路径 | 类名 | line% | branch% | instruction% | 是否排除 | 原因 |
```

### 4. 启动监督 agent 与子 agent

如果工具环境支持子 agent，必须启动一个监督 agent。监督 agent 负责：

- 读取 `.claude/jacoco-unittest-targets.md`。
- 读取和维护 `.claude/jacoco-unittest-progress.md`。
- 监督多个子 agent 按目标清单逐类工作。
- 检查每个子 agent 是否参考 `/java-unittest` 生成测试。
- 检查是否违反“不能修改业务代码、不能更改已提交单测代码”。
- 检查每个子 agent 开始前是否读取 `.claude/jacoco-unittest-constraints.md`。
- 检查每个类完成后的日志是否包含约束自检结果。
- 检查每个类是否已优先尝试 100%；若 5 次后未达 100%，是否达到 90% 以上；只有达到 100%、或 5 次后达到 90% 以上、或 5 次后仍低于 90% 并记录不通过，才允许进入下一个类。
- 目标清单未完成且未触发终止条件时，要求继续执行。

监督 agent 不修改代码，只做调度、检查和记录。

子 agent 工作规则：

- 每个子 agent 处理一个或多个目标类，但同一时间不得有两个子 agent 修改同一个测试文件。
- 子 agent 必须参考 `/java-unittest` 和项目已有单测结构。
- 优先新增测试文件；若已有测试文件已提交，不得修改。
- 每完成一个类，必须记录日志。
- 开始处理类前，必须读取 `.claude/jacoco-unittest-constraints.md`，并在日志中写明“已读取约束”。
- 单类优先尝试覆盖率 100%，最多尝试 5 次。
- 5 次内达到 100%，记录为 `通过`。
- 5 次后未达到 100% 但达到 90% 以上，记录为 `通过`，继续下一个目标类。
- 5 次后仍低于 90%，记录为 `不通过`，继续下一个目标类。
- 生成测试导致编译失败且无法在本轮新增文件内修复时，记录为 `不通过`，回退本轮新增内容，继续下一个目标类。

### 5. 日志与进度

进度文件：

```text
.claude/jacoco-unittest-progress.md
```

格式：

```text
当前进度：已处理 x/y
监督 agent：
当前子 agent：

| 顺序 | 类路径 | 状态 | line% | branch% | instruction% | 尝试次数 | 处理 agent | 说明 |
```

状态只允许：

```text
通过
不通过
```

子 agent 日志：

```text
.claude/jacoco-unittest-agent-log.md
```

每完成一个类追加：

```text
时间：
agent：
类路径：
状态：通过/不通过
尝试次数：
测试文件：
覆盖率：
说明：
约束自检：
- 未修改业务代码：是/否
- 未更改已提交单测：是/否
- 失败新增测试已回退：是/否/不适用
- 已参考 /java-unittest：是/否
- 已参考项目已有单测结构：是/否
- 覆盖率处理满足规则：是/否
```

## 终止条件

只有以下情况可以终止本 Skill：

- 基线测试连续 10 次修复后仍不能正常运行。
- JaCoCo 报告无法生成，且无法在不修改业务代码和已提交单测代码的前提下修复。
- 目标清单为空。
- 目标清单全部处理完成。
- 用户明确要求停止。

处理 5 个类、阶段性汇报、某个子 agent 完成任务，都不是终止条件。

## 完成前自检

- [ ] 基线测试已正常运行；若失败，已参考 `/java-unittest` 最多修复 10 次。
- [ ] JaCoCo 报告已生成并记录到 `.claude/jacoco-report-summary.md`。
- [ ] JaCoCo XML 已解析，明细数据已写入 `.claude/jacoco-report-data.md`。
- [ ] 已按固定 excludes 过滤类。
- [ ] 覆盖率不超过 90% 的未排除类已写入 `.claude/jacoco-unittest-targets.md`。
- [ ] 已启动监督 agent 或等价监督任务。
- [ ] 已生成 `.claude/jacoco-unittest-constraints.md`。
- [ ] 子 agent 每完成一个类都已写入 `.claude/jacoco-unittest-agent-log.md`。
- [ ] 每个子 agent 开始前已读取约束，每个类完成后已写入约束自检。
- [ ] 每个目标类都已优先尝试 100%；5 次后未达 100% 但达到 90% 以上的已记录为通过，5 次后仍低于 90% 的已记录为不通过。
- [ ] 未修改业务代码。
- [ ] 未更改已提交的单测代码。
