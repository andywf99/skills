---
name: 优雅启停接入
description: 该技能用于批量接入优雅启停依赖，从 projects.txt 和 gits.txt 读取项目信息，自动克隆项目、添加 yl-sqs-platform-graceful-starter 依赖；如果项目存在自定义线程池，则补充优雅关停改造并推送变更。
---

# 优雅启停接入

当用户说 **[批量优雅启停接入]** 时，按以下任务顺序执行：

---

## 任务 1：读取项目配置

**目标**：获取需要修改的项目列表和对应的 Git 地址。

**操作步骤**：
1. 读取当前工作目录下的 `projects.txt` 文件，获取项目名称列表
2. 读取当前工作目录下的 `gits.txt` 文件，获取项目对应的 Git clone 地址
3. 解析两个文件，建立项目名称与 Git 地址的映射关系

**文件格式示例**：

`projects.txt`:
```
project-a
project-b
project-c
```

`gits.txt`:
```
git@github.com:company/project-a.git
git@github.com:company/project-b.git
git@github.com:company/project-c.git
```

**验证**：确认所有项目都有对应的 Git 地址。

---

## 任务 2：克隆项目并切换分支

**目标**：将所有项目克隆到本地并切换到指定分支。

**操作步骤**：
1. 在当前工作目录下创建 `projects` 目录用于存放克隆的项目
2. 遍历项目列表，对每个项目执行：
   - 检查项目目录是否已存在
   - 如不存在，执行 `git clone <git_url>` 克隆项目
   - 切换到 `feature/优雅上下线` 分支
     - 如果分支不存在，创建并切换：`git checkout -b feature/优雅上下线`
     - 如果分支已存在，直接切换：`git checkout feature/优雅上下线`

**验证**：确认所有项目已成功克隆并处于 `feature/优雅上下线` 分支。

---

## 任务 3：检查并添加依赖

**目标**：检查项目是否已有优雅启停依赖，如无则添加。

**操作步骤**：
1. 找到项目的 Maven parent `pom.xml` 文件（通常位于项目根目录）
2. 检查是否已存在 `yl-sqs-platform-graceful-starter` 依赖
3. 如果已存在，将该项目标记为 **无需变更**
4. 如果不存在，执行以下修改：

### 3.1 添加 properties

在 `<properties>` 标签内添加版本号（如无 `<properties>` 标签则创建）：

```xml
<yl-sqs-platform-graceful-starter.version>2.0.1.0-RELEASE</yl-sqs-platform-graceful-starter.version>
```

### 3.2 添加 dependency

在 `<dependencies>` 标签内添加依赖：

```xml
<dependency>
    <groupId>com.yl</groupId>
    <artifactId>yl-sqs-platform-graceful-starter</artifactId>
    <version>${yl-sqs-platform-graceful-starter.version}</version>
</dependency>
```

**注意事项**：
- 如果是在 `dependencyManagement` 中添加，确保添加到正确的位置
- 保持 XML 格式缩进一致
- 不要破坏原有的 XML 结构

**验证**：使用 `mvn dependency:tree` 或检查 pom.xml 确认依赖已正确添加。

---

## 任务 4：验证依赖添加

**目标**：确认所有修改项目的依赖已正确添加。

**操作步骤**：
1. 对每个有变更的项目，重新读取 `pom.xml` 文件
2. 验证 `properties` 中包含 `yl-sqs-platform-graceful-starter.version`
3. 验证 `dependencies` 中包含 `yl-sqs-platform-graceful-starter` 依赖
4. 如验证失败，重新检查并修复

---

## 任务 5：检查并改造线程池

**目标**：识别项目中的自定义线程池，并补齐优雅关停策略。

**操作步骤**：
1. 扫描项目中的线程池实现，重点检查：
   - `ThreadPoolTaskExecutor` bean
   - `ExecutorService`、`ThreadPoolExecutor`、`ForkJoinPool`
   - 自定义 executor bean 或线程池封装类
2. 如果项目不存在自定义线程池，标记为 **无需线程池变更**
3. 如果存在 `ThreadPoolTaskExecutor`，补齐以下设置：
   - `waitForTasksToCompleteOnShutdown=true`
   - `awaitTerminationSeconds`
   - 如果项目已经把 graceful 超时时间外置配置化，优先复用现有配置，不要硬编码新的时间值
   - 如果项目通过 `graceful.properties` 或 Apollo 管理优雅关停超时，优先对齐 `graceful.executor.awaitTerminationSeconds`
4. 如果存在原生 `ExecutorService`、`ThreadPoolExecutor` 或 `ForkJoinPool`，补齐显式关闭逻辑：
   - 调用 `shutdown()`
   - 在有界超时时间内等待
   - 如果必须 `shutdownNow()`，记录排队任务日志并上报风险
5. 明确记录排队任务的业务策略：执行完成、告警后丢弃，或持久化后重放

**验证**：
1. 确认线程池改造不会破坏原有 bean 初始化与销毁流程
2. 确认在应用关闭时，线程池会等待在途任务或按既定策略处理队列任务

---

## 任务 6：验证依赖和线程池改造

**目标**：确认所有修改项目的依赖与线程池改造都已正确落地。

**操作步骤**：
1. 对每个有变更的项目，重新读取 `pom.xml` 与相关线程池代码文件
2. 验证 `properties` 中包含 `yl-sqs-platform-graceful-starter.version`
3. 验证 `dependencies` 中包含 `yl-sqs-platform-graceful-starter` 依赖
4. 如果修改了 `ThreadPoolTaskExecutor`，验证已设置 `waitForTasksToCompleteOnShutdown=true` 和 `awaitTerminationSeconds` awaitTerminationSeconds支持apollo配置，默认10s
5. 如果修改了原生线程池，验证存在显式关闭逻辑与超时等待
6. 如果项目使用 `graceful.properties` 或 Apollo，验证 `graceful.executor.awaitTerminationSeconds` 与线程池等待时间一致
7. 如验证失败，重新检查并修复

---

## 任务 7：推送变更到 Git 仓库

**目标**：将所有变更提交并推送到远程仓库。

**操作步骤**：
对每个有变更的项目执行：
1. `git add pom.xml <modified_files>`
2. `git commit -m "feat: 优雅启停接入"`
3. `git push origin feature/优雅上下线`

**错误处理**：
- 如果 push 失败，先执行 `git pull --rebase origin feature/优雅上下线` 解决冲突
- 解决冲突后重新提交

---

## 任务 8：合并到 UAT 分支

**目标**：将 `feature/优雅上下线` 分支合并到 `uat` 分支。

**操作步骤**：
对每个有变更的项目执行：
1. 切换到 `uat` 分支：`git checkout uat`
2. 拉取最新代码：`git pull origin uat`
3. 合并 `feature/优雅上下线` 分支：`git merge feature/优雅上下线`
4. 推送到远程：`git push origin uat`

**冲突处理**：
1. 如果合并时出现冲突，尝试自动修复：
   - 读取冲突文件，分析冲突内容
   - 对于 `pom.xml` 冲突，保留双方改动（保留原有依赖 + 新增的优雅启停依赖）
   - 对于线程池相关 Java / 配置文件冲突，优先保留已有业务语义，同时保留优雅关停逻辑
   - 使用 `git add <file>` 标记冲突已解决
   - 执行 `git commit` 完成合并
2. 如果冲突无法自动修复：
   - 执行 `git merge --abort` 取消合并
   - 将该项目记录到失败列表，标注"合并冲突无法自动解决"
   - 继续处理下一个项目

**注意事项**：
- 冲突修复时优先保留 pom.xml 中的 properties 和 dependencies
- 确保 XML 格式正确，标签闭合完整
- 合并成功后验证 pom.xml 结构完整性

---

## 执行总结

所有任务完成后，输出以下报告：

### 变更成功的项目列表

| 项目名称 | Git 地址 | 变更内容 | 状态 |
|---------|---------|---------|------|
| project-a | git@xxx | 依赖接入 + 线程池改造 | ✅ 已推送至 feature 和 uat 分支 |
| project-b | git@xxx | 仅依赖接入 | ✅ 已推送至 feature 和 uat 分支 |

### 无需变更的项目列表

| 项目名称 | Git 地址 | 原因 |
|---------|---------|------|
| project-c | git@xxx | 依赖已存在且无需线程池变更 |

### 失败项目列表（如有）

| 项目名称 | Git 地址 | 失败原因 |
|---------|---------|---------|
| project-d | git@xxx | 克隆失败 |
| project-e | git@xxx | 合并冲突无法自动解决：线程池关闭逻辑与现有实现冲突 |
