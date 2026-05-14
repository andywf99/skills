---
name: java-jacoco-unittest-boost
description: 为 Maven Java/Spring Boot 项目执行全量单测补充。适用于用户要求先检查基线测试，基线失败时参考 /java-unittest 最多修复 10 次；基线正常后生成并解析 JaCoCo 报告，按固定 excludes 找出覆盖率不超过 90% 的类；只设置两个 agent，一个监控 agent 监督进度与约束，一个执行 agent 遍历 targets 并按 /java-unittest 逐类补测。单类优先尝试 100%，5 次后达不到 100% 但达到 90% 以上也视为通过。严格禁止修改业务代码和已提交单测代码，禁止生成未列出的文件。
---

# Java 全量单测补充

## 一句话流程

先跑通基线测试，再生成 JaCoCo 报告并筛出覆盖率不超过 90% 的未排除类，最后用“监控 agent + 执行 agent”逐类补测：单类先冲 100%，最多 5 次；5 次后 90% 以上算通过，低于 90% 算不通过。

未指定项目路径时，默认使用当前工作目录作为项目根目录。

## 硬性约束

- 严禁修改业务代码。
- 不能更改已提交的单测代码；严禁删除、移动、重命名、改后缀、重写、弱化断言或修改已有测试逻辑。
- 只允许新增必要的未提交测试文件，或在未提交的新测试文件中调整本轮生成内容。
- 失败的本轮新增测试不保留草稿，直接回退本轮新增内容，只在 `.claude/log/jacoco-unittest-agent-log.md` 记录原因。
- 如基线修复需要修改业务代码或已提交单测代码，视为不可修复。
- 只能设置两个 agent：一个监控 agent，一个执行 agent；禁止并发启动多个执行 agent。
- 除“允许生成的文件”中列出的运行产物和必要新增测试文件外，不能生成其他文件、目录、备份、草稿或额外报告。

## 允许生成的文件

所有运行产物只允许写入当前项目目录的 `.claude`：

```text
.claude/jacoco-unittest-targets.md
.claude/jacoco-unittest-progress.md
.claude/log/jacoco-unittest-agent-log.md
.claude/jacoco-report-summary.md
.claude/jacoco-report-data.md
.claude/jacoco-unittest-constraints.md
```

若 `.claude` 或 `.claude/log` 不存在，先创建。除上面列出的运行产物外，不得生成其他 `.claude` 文件或目录。

## 固定 excludes

生成目标清单时必须应用以下排除规则；命中 excludes 的类不进入目标清单、不补测：

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

## 执行阶段

### 阶段 1：基线测试检查

1. 先运行现有测试，确认基线能正常运行。
   - 单模块：`mvn test`
   - 多模块：`mvn -pl <module> -am test`
2. 基线通过，进入阶段 2。
3. 基线失败，参考 `/java-unittest` 的诊断和修复方式尝试修复。
4. 基线最多修复 10 次；每次修复后必须重新运行测试。
5. 连续 10 次仍不能正常运行，立即终止本 Skill，并提示：

```text
不能修复单测，已参考 /java-unittest 尝试修复 10 次，基线测试仍不能正常运行。
```

基线不可修复时，不生成目标清单，不启动执行 agent。

### 阶段 2：生成并解析 JaCoCo 报告

基线正常后，执行项目原生 JaCoCo 命令。没有特殊命令时使用：

```bash
mvn test jacoco:report
```

多模块项目可使用：

```bash
mvn -pl <module> -am test jacoco:report
```

解析 `target/site/jacoco/jacoco.xml`、`target/jacoco-ut/jacoco.xml` 或 POM 指定的 JaCoCo XML。

写入报告概要：

```text
.claude/jacoco-report-summary.md
```

写入解析明细：

```text
.claude/jacoco-report-data.md
```

明细至少包含：

```text
JaCoCo XML：
生成命令：

| 类路径 | 类名 | line% | branch% | instruction% | method% | class% | missedLines | coveredLines |
```

### 阶段 3：生成目标清单

从 `.claude/jacoco-report-data.md` 生成 `.claude/jacoco-unittest-targets.md`：

1. 读取 JaCoCo class/sourcefile 覆盖率数据。
2. 应用固定 excludes，命中排除规则的类跳过。
3. 对未排除类计算单类覆盖率。
4. 找出覆盖率不超过 90% 的未排除类。
5. 按源码路径自上而下排序。
6. 写入目标清单。

目标清单格式：

```text
项目根目录：
JaCoCo 报告：
阈值：> 90% 视为完成，<= 90% 进入补测

| 顺序 | 类路径 | 类名 | line% | branch% | instruction% | 是否排除 | 原因 |
```

### 阶段 4：生成约束摘要

启动执行 agent 前，必须生成或更新：

```text
.claude/jacoco-unittest-constraints.md
```

至少包含：

- 不能修改业务代码。
- 不能更改已提交的单测代码。
- 失败的本轮新增测试不保留草稿，直接回退本轮新增内容，只在 `.claude/log/jacoco-unittest-agent-log.md` 记录原因。
- 执行 agent 必须参考 `/java-unittest` 和项目已有单测结构。
- 单类优先尝试覆盖率 100%；5 次后达不到 100% 但达到 90% 以上也视为通过。
- 基线测试最多修复 10 次。
- 只允许生成本 Skill 列出的 `.claude` 运行产物和必要新增测试文件。

### 阶段 5：启动两个 agent

只设置两个 agent：

- 监控 agent：监督进度、约束、停止条件。
- 执行 agent：从上到下遍历 `.claude/jacoco-unittest-targets.md` 的每个 target 并补测。

监控 agent 只做监督，不修改代码。它必须检查：

- 目标清单、进度文件、日志是否按要求更新。
- 执行 agent 是否读取 `.claude/jacoco-unittest-constraints.md`。
- 执行 agent 是否参考 `/java-unittest` 和项目已有单测结构。
- 是否违反“不能修改业务代码、不能更改已提交单测代码”。
- 单类是否按规则处理：先尝试 100%，最多 5 次；5 次后 90% 以上通过，低于 90% 不通过。
- 目标清单未完成且未触发终止条件时，要求执行 agent 继续处理下一类。

执行 agent 必须：

- 逐个遍历 targets，不能跳序。
- 参考 `/java-unittest` 和项目已有单测结构。
- 优先新增测试文件；已有测试文件已提交时不得修改。
- 每个类开始前读取 `.claude/jacoco-unittest-constraints.md`，并在日志中写明“已读取约束”。
- 每完成一个类写入日志和约束自检。
- 生成测试导致编译失败且无法在本轮新增文件内修复时，记录为 `不通过`，回退本轮新增内容，继续下一个目标类。

### 阶段 6：单类处理规则

对每个 target：

1. 优先尝试把单类覆盖率提升到 100%。
2. 最多尝试 5 次。
3. 5 次内达到 100%，记录为 `通过`。
4. 5 次后未达到 100% 但达到 90% 以上，记录为 `通过`。
5. 5 次后仍低于 90%，记录为 `不通过`。
6. 只有当前类记录为 `通过` 或 `不通过` 后，才能处理下一个 target。

## 进度与日志格式

进度文件：

```text
.claude/jacoco-unittest-progress.md
```

格式：

```text
当前进度：已处理 x/y
监控 agent：
执行 agent：

| 顺序 | 类路径 | 状态 | line% | branch% | instruction% | 尝试次数 | 处理 agent | 说明 |
```

状态只允许：

```text
通过
不通过
```

日志文件：

```text
.claude/log/jacoco-unittest-agent-log.md
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

处理 5 个类、阶段性汇报、执行 agent 完成某个类，都不是终止条件。

## 完成前自检

- [ ] 基线测试已正常运行；若失败，已参考 `/java-unittest` 最多修复 10 次。
- [ ] JaCoCo 报告已生成并记录到 `.claude/jacoco-report-summary.md`。
- [ ] JaCoCo XML 已解析，明细数据已写入 `.claude/jacoco-report-data.md`。
- [ ] 已按固定 excludes 过滤类。
- [ ] 覆盖率不超过 90% 的未排除类已写入 `.claude/jacoco-unittest-targets.md`。
- [ ] 已生成 `.claude/jacoco-unittest-constraints.md`。
- [ ] 已只设置两个 agent：一个监控 agent，一个执行 agent。
- [ ] 执行 agent 每完成一个类都已写入 `.claude/log/jacoco-unittest-agent-log.md`。
- [ ] 每个目标类都已优先尝试 100%；5 次后未达 100% 但达到 90% 以上的已记录为通过，5 次后仍低于 90% 的已记录为不通过。
- [ ] 未修改业务代码。
- [ ] 未更改已提交的单测代码。
- [ ] 除列出的 `.claude` 运行产物和必要新增测试文件外，未生成其他文件。
