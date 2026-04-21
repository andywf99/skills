---
name: infra-graceful-batch
description: 用于批量接入 yl-sqs-platform-graceful-starter、改造线程池优雅关停、批量提交推送、合并到 uat、处理 pom 与优雅关停相关冲突，并生成 MR 链接与执行报告。适用于多仓库 Java/Spring Boot 项目的批量优雅启停接入和发布。
---

# 优雅启停批量作业

当用户要求批量接入优雅启停、重建 `feature/优雅上下线`、批量提交推送、合并 `uat`、生成 MR 链接、排查线程池优雅关停问题时，使用本技能。

优先复用 `scripts/` 下的批量脚本，不要重复手写同类 PowerShell 逻辑。

## 适用范围

- 多仓库批量接入 `yl-sqs-platform-graceful-starter`
- 批量改造 `ThreadPoolTaskExecutor`、`ExecutorService`、`ThreadPoolExecutor`、`ForkJoinPool`
- 批量提交并推送 `feature/优雅上下线`
- 批量合并到 `uat`
- 生成 `feature/优雅上下线 -> master` 的 MR 链接表，输出MR Markdown 文档

## 输入约定

默认从当前技能目录读取：

- `gits.txt`
- `projects.txt`，可选过滤
- `projects/`

如果仓库已存在于 `projects/`，优先复用本地仓库；不要重复克隆。

## 执行前检查

- 操作人需要具备全部目标仓库的 Git 拉取、推送、建分支、删分支权限
- `gits.txt` 是必需输入
- 项目名默认从 Git 地址动态推导；`projects.txt` 不是必需输入，如果存在，则只作为目标仓库过滤清单使用
- 本地批量操作前，目标仓库工作区必须干净
- 如果要合并到 `uat`，本地 `uat` 只能基于 `origin/uat` 开始，不要在分叉的本地 `uat` 上继续操作

## 可直接复用的脚本

- [scripts/batch_graceful_starter.ps1](scripts/batch_graceful_starter.ps1)
  - 用途：批量克隆、抓取最新远端、切换或重建 `feature/优雅上下线`
  - 典型场景：首次准备仓库、批量恢复 feature 分支、批量重建 feature 分支
  - 输入规则：默认读取 `gits.txt` 全量仓库并动态推导项目名；如果提供 `projects.txt`，则只处理其中列出的项目
- [scripts/build_uat_mr_links.ps1](scripts/build_uat_mr_links.ps1)
  - 用途：根据 Git 地址文件生成 MR Markdown 表格
  - 典型场景：批量生成 `feature/优雅上下线 -> master` 的 MR 链接；如果用户主动要求，再生成 `feature/优雅上下线 -> uat` 的 MR 链接
  - 输入规则：默认读取 `gits.txt` 全量仓库并动态推导项目名；如果提供 `projects.txt`，则只输出其中列出的项目

## 执行原则

### 1. 分支原则

- 功能分支固定为 `feature/优雅上下线`
- 除非用户明确要求，否则不要把 `uat` 快进或 merge 到 `feature/优雅上下线`
- Windows 下涉及中文分支名时，推送优先用 `git push -u origin HEAD`
- 需要合并到 `uat` 时，优先在干净工作区上把本地 `uat` 对齐到 `origin/uat`
- 如果只是为了生成 MR 或继续改 feature，不要先同步 `uat -> feature`

### 2. 依赖接入原则

根 `pom.xml` 需要确保存在：

```xml
<dependency>
    <groupId>com.yl</groupId>
    <artifactId>yl-sqs-platform-graceful-starter</artifactId>
    <version>1.0.20</version>
</dependency>
```

如果已存在，只保留一份，不要重复插入。

### 3. 线程池改造原则

#### `ThreadPoolTaskExecutor`

统一补齐：

- `setWaitForTasksToCompleteOnShutdown(true)`
- `setAwaitTerminationSeconds(...)`

默认规则：

- 普通 Spring Bean：使用 Apollo 配置
- 配置项：`graceful.executor.awaitTerminationSeconds`
- 默认值：`10`
- 如果某个线程池类最终没有使用 `graceful.executor.awaitTerminationSeconds`，则不要为了统一形式强行增加该配置或 `@Value` 字段

示例：

```java
@Value("${graceful.executor.awaitTerminationSeconds:10}")
private Integer awaitSeconds;
```

```java
executor.setAwaitTerminationSeconds(awaitSeconds);
```

#### `final` / `static final` 线程池

如果线程池是 `final` 或 `static final` 持有，默认直接写死 `10s`，不要强行改成 Apollo 注入。

#### 原生线程池 Bean

如果是 Spring 管理的：

- `ExecutorService`
- `ThreadPoolExecutor`
- `ForkJoinPool`

要补显式关闭逻辑：

- `shutdown()`
- `awaitTermination(...)`
- 必要时 `shutdownNow()`

如果是 Bean 冲突，优先保留已有业务语义，再补优雅关停。

#### 业务代码临时线程池

如果生命周期清晰且由当前类创建：

- 在使用完后显式 `shutdown()`
- 继续 `awaitTermination(...)`

如果线程池是长生命周期字段：

- 优先在 Spring Bean 中通过 `@PreDestroy` 收口

### 4. 校验原则

提交前至少做这些检查：

- `git diff --check`
- 检查是否仍存在硬编码 `setAwaitTerminationSeconds(10)`
- 允许保留硬编码 `10` 的场景：`final/static final` 线程池
- 检查是否有重复插入的 `awaitSeconds` 字段或重复 shutdown 配置
- 检查 `pom.xml` 中 starter version 和 dependency 是否重复
- 检查 `@Value("${graceful.executor.awaitTerminationSeconds:10}")` 是否误加到 `final/static final` 线程池场景
- 检查未使用 `graceful.executor.awaitTerminationSeconds` 的线程池类中，是否被错误引入了 `@Value` 字段或相关配置代码

## 批量工作流

### 步骤 1：准备仓库

1. 读取 `gits.txt`
2. 从 Git 地址动态推导目标项目名；如果存在 `projects.txt`，再用它做过滤
3. 优先执行 `scripts/batch_graceful_starter.ps1`
4. 本地不存在则克隆
5. 需要重建 feature 时：
   - 删除本地 `feature/优雅上下线`
   - 删除远端 `feature/优雅上下线`
   - 基于远程 `master` 重新创建该分支

### 步骤 2：批量改代码

1. 根 `pom.xml` 接入 graceful starter
2. 扫描 `ThreadPoolTaskExecutor`
3. 扫描原生线程池 Bean
4. 扫描业务代码里直接创建的线程池
5. 按规则补齐优雅关停

### 步骤 3：批量提交推送

对有改动的仓库：

1. `git add -A`
2. `git commit -m "feat: 优雅启停接入"`
3. `git push -u origin HEAD`

### 步骤 4：合并到 `uat`（非必须，推荐需用户确认，提示可能冲突需要手动操作）

在干净工作区执行：

1. `git checkout -B uat origin/uat`
2. 合并 `feature/优雅上下线`
3. 如仅 `pom.xml` 冲突，按下述规则自动解决
4. 如 Java 冲突仅是优雅关停相关改动，直接采用 `feature/优雅上下线` 版本
5. 如果仍有非优雅冲突，立即 `git merge --abort`
6. 输出 MR 链接给用户人工处理

### 步骤 5：输出结果

结果需要分三类输出：

- 已完成的仓库
- 无需变更的仓库
- 失败仓库

如果用户要求，还要额外输出：

- `feature/优雅上下线 -> uat` 的 MR 链接表
- 剩余冲突文件列表

生成 MR 表时，优先执行 `scripts/build_uat_mr_links.ps1`。

注意：

- `feature/优雅上下线 -> master` 的 MR 文档是默认收尾产物
- `feature/优雅上下线 -> uat` 的 MR 文档不是默认产物，只作为推荐项，在用户主动要求时才生成

### 步骤 6：默认收尾输出

当代码改动、提交、推送全部完成后，默认额外输出一份：

- `feature/优雅上下线 -> master` 的 MR 链接 Markdown 文档

推荐直接执行：

```powershell
.\scripts\build_uat_mr_links.ps1 -TargetBranch master -OutputFile .\master_mr_links.md
```

如果用户主动要求 `uat` 的 MR 文档，则再额外生成：

```powershell
.\scripts\build_uat_mr_links.ps1 -TargetBranch uat -OutputFile .\uat_mr_links.md
```

## 合并到UAT冲突处理规则

### `pom.xml`

`pom.xml` 冲突统一按以下规则：

1. 以 `uat` 当前 `pom` 为基准
2. 保留 `uat` 上已有的非优雅上下线改动
3. 确保 graceful starter 的版本属性存在
4. 确保 graceful starter 依赖存在
5. 如果 `uat` 已经存在 graceful starter，只保留一份

### Java 冲突

如果冲突块只涉及这些内容，可以直接采用 feature 版本：

- `awaitSeconds`
- `graceful.executor.awaitTerminationSeconds`
- `setWaitForTasksToCompleteOnShutdown`
- `setAwaitTerminationSeconds`
- `@PreDestroy`
- `shutdown/awaitTermination/shutdownNow`
- 原生线程池 Bean 的优雅关停包装

如果冲突块包含业务字段、业务方法、业务分支逻辑，则不要自动覆盖，保留给人工处理。

## 关键禁忌

- 不要未经用户确认把 `uat` 合回 `feature/优雅上下线`
- 不要因为 Windows 编码问题直接把中文分支名写进 `push` refspec
- 不要在有未提交改动时重置分支
- 不要对无法确认是“纯优雅关停冲突”的 Java 文件直接覆盖
- 不要在 merge 失败后把带冲突的工作区遗留给下一仓库，必须先 `git merge --abort`

## 已验证踩坑

- `git push origin feature/优雅上下线` 在 Windows 下可能遇到中文 refspec 编码问题，统一改用 `git push -u origin HEAD`
- 把 `uat` 快进到 `feature/优雅上下线` 会污染 feature 历史，后续 MR 难审，默认禁止
- `pom.xml` 冲突不能简单整文件取一边，必须保留 `uat` 上非优雅改动，同时确保 graceful starter 只保留一份
- 不是所有 Java 冲突都能自动取 feature；只有冲突块纯粹围绕优雅关停时才能自动覆盖
- `Application.java`、监听器、业务方法体、业务字段冲突默认视为人工处理范围
- 仅靠 `gits.txt` 就能推导项目名，因此 `projects.txt` 不应再被设计成强依赖

## 交付物

按用户要求可以产出：

- 执行总结
- 冲突仓库清单
- MR Markdown 表格
- 操作文档
- 默认生成的 `feature/优雅上下线 -> master` MR Markdown 文档
- 只有用户主动要求时才生成的 `feature/优雅上下线 -> uat` MR Markdown 文档
