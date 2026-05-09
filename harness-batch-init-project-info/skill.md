---
name: harness-batch-init-project-info
description: 克隆业务代码仓库，调用 doc-whitepaper-tech skill 生成 project-info.md 技术文档，创建分支并推送到远程。适用于初始化模块技术文档、新项目接入、批量生成项目文档等场景。
triggers:
- 用户要求"克隆业务代码并初始化模块技术结构"
- 用户要求"生成项目文档"或"生成 project-info.md"
- 用户要求"批量生成项目技术文档"
- 用户说"初始化项目信息"
---

# Harness Batch Init Project Info

克隆业务代码仓库，调用 `doc-whitepaper-tech` skill 生成 `project-info.md` 技术文档，创建分支并推送到远程。

## 工作流程

### Step 1: 确认模块信息

从 `AGENTS.md` 的"绑定项目代码"章节获取仓库列表，或让用户提供：

1. **模块路径**: 默认当前工作目录
2. **工作区路径**: 默认 `codes/workspace/`
3. **仓库列表**: 从 AGENTS.md 解析或用户指定

**解析 AGENTS.md 示例**：

```markdown
| 序号 | 仓库名 | 层级 | 目录路径 |
|------|--------|------|----------|
| 1 | `yl-web-sqs-serviceonline` | 小前台 | `codes/workspace/yl-web-sqs-serviceonline` |
```

### Step 2: 克隆业务代码

检查 `codes/workspace/` 目录，克隆缺失的仓库：

```bash
cd {module-path}/codes/workspace

# 按仓库列表逐个克隆（可并行执行）
git clone {repo-url} {repo-name}
```

**并行克隆**: 多个仓库可并行克隆以提高效率。

### Step 3: 检查现有文档

检查每个仓库是否已存在 `project-info.md`：

```bash
ls {repo-path}/project-info.md
```

- 如果存在：询问用户是否覆盖
- 如果不存在：继续生成

### Step 4: 调用 doc-whitepaper-tech skill 生成文档

**对每个仓库调用 `doc-whitepaper-tech` skill**：

```
Skill: doc-whitepaper-tech
Args: {repo-path}
```

该 skill 会自动：
1. 扫描项目结构（Controller/Service/Mapper/Feign 等）
2. 提取技术栈版本（从 pom.xml）
3. 分析业务领域
4. 生成完整的 `project-info.md`

**并行执行**: 多个仓库可并行调用 Agent 执行分析。

### Step 5: 更新 code-overview.md

更新模块的 `docs/architecture/code-overview.md`，添加：

1. **仓库概览表**：列出所有仓库
2. **系统架构图**：使用 Mermaid 展示调用关系
3. **各仓库分工详解**：定位、职责、技术栈
4. **技术栈版本汇总**：版本对比表
5. **代码阅读顺序**：建议的阅读路径
6. **排查入口建议**：按问题类型给出排查起点

### Step 6: 创建分支并提交

```bash
cd {repo-path}
git checkout -b feature/project-info-build
git add project-info.md
git commit -m "新增 project-info.md 项目技术文档

- 项目概述与技术栈版本
- 目录结构说明
- 核心模块（Controller/Service/Mapper/Feign）
- 业务领域与外部依赖
- 配置说明

Co-Authored-By: Claude Opus 4.7 <noreply@anthropic.com>"
```

**重要**: commit 操作需要用户许可。

### Step 7: 推送到远程

```bash
git push -u origin feature/project-info-build
```

**重要**: push 操作需要用户许可。

---

## 使用示例

### 示例 1: 完整流程

```
用户: 克隆业务代码，并初始化模块整体技术结构和分工

Agent 执行:
1. 读取 AGENTS.md 获取仓库列表
2. 克隆 6 个仓库到 codes/workspace/
3. 并行调用 doc-whitepaper-tech skill 为每个仓库生成文档
4. 更新 code-overview.md
5. 创建分支并提交（需用户许可）
6. 推送到远程（需用户许可）
```

### 示例 2: 仅生成文档（代码已存在）

```
用户: 生成如果单仓文档没有生成，就生成

Agent 执行:
1. 检查各仓库是否存在 project-info.md
2. 为缺失的仓库调用 doc-whitepaper-tech skill
3. 创建分支并提交
```

### 示例 3: 指定仓库

```
用户: 为 yl-jms-sqs-online 生成项目文档

Agent 执行:
1. 检查仓库是否存在
2. 克隆（如不存在）
3. 调用 doc-whitepaper-tech skill 生成文档
4. 创建分支并提交
```

---

## 输出内容

### project-info.md 结构（由 doc-whitepaper-tech 生成）

| 章节 | 内容 |
|------|------|
| 项目概述 | 名称、版本、描述、核心功能 |
| 技术栈 | 框架版本、中间件、工具库、内部依赖 |
| 目录结构 | 完整目录树 |
| 核心模块 | Controller/Service/Mapper/Feign 列表及功能 |
| 业务领域 | 核心业务场景、枚举类型 |
| 外部依赖 | Feign 调用的服务列表 |
| 数据库表 | 从 Mapper 推断的表名及说明 |
| 配置说明 | Apollo Namespace、关键配置项 |

### code-overview.md 结构

| 章节 | 内容 |
|------|------|
| 仓库概览 | 表格列出所有仓库 |
| 系统架构 | Mermaid 架构图 |
| 仓库分工详解 | 每个仓库的定位、职责、技术栈 |
| 技术栈版本汇总 | 版本对比表 |
| 代码阅读顺序 | 建议的阅读路径 |
| 排查入口建议 | 按问题类型给出排查起点 |

---

## 并行执行策略

为提高效率，采用以下并行策略：

### 克隆阶段

```bash
# 并行克隆多个仓库
git clone repo1 &
git clone repo2 &
git clone repo3 &
wait
```

### 文档生成阶段

使用 Agent 工具并行分析多个仓库：

```
Agent 1: 分析 repo1 → 生成 project-info.md
Agent 2: 分析 repo2 → 生成 project-info.md
Agent 3: 分析 repo3 → 生成 project-info.md
```

### Git 操作阶段

```bash
# 并行创建分支和提交
(cd repo1 && git checkout -b feature/project-info-build && git add . && git commit -m "...") &
(cd repo2 && git checkout -b feature/project-info-build && git add . && git commit -m "...") &
wait
```

---

## 注意事项

1. **复用 doc-whitepaper-tech skill**: 不重复实现文档生成逻辑，直接调用现有 skill

2. **Git 操作需用户许可**: commit 和 push 操作必须获得用户许可

3. **并行提高效率**: 克隆、分析、Git 操作尽可能并行执行

4. **生成中文文档**: 所有文档使用中文撰写

5. **文档末尾添加元信息**:
   - 生成时间（通过 `date` 命令获取）
   - 项目路径

---

## 依赖

- **doc-whitepaper-tech skill**: 用于生成 project-info.md
- Git 命令行工具
- Read/Edit/Write 工具
- Agent 工具（用于并行分析项目结构）
