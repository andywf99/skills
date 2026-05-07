---
name: harness-subModule-local-init
description: 子模块本地初始化，克隆 codes/workspace 下的业务代码，初始化 code-overview.md。适用于子模块刚 clone 下来、业务代码未拉取的场景。
triggers:
- 用户要求"初始化子模块"或"拉取业务代码"
- 用户要求"clone 工作区代码"或"克隆业务代码"
- 用户提到"codes/workspace"为空或"本地初始化"
- 子模块刚 clone 下来，需要初始化工作环境
---

# Harness SubModule Local Init

子模块本地初始化，克隆 `codes/workspace` 下的业务代码仓库，初始化 `docs/architecture/code-overview.md`。

## 使用场景

当用户 clone 了子模块仓库后，`codes/workspace/` 目录通常是空的。本 skill 用于：

1. 读取 `AGENTS.md` 中的绑定项目代码信息
2. 让用户选择克隆方式（SSH 或 HTTP）
3. 克隆所有业务代码仓库到 `codes/workspace/`
4. 初始化 `docs/architecture/code-overview.md`（如果是预留值）

## 工作流程

### Step 1: 检查当前环境

确认当前在子模块目录下（存在 `AGENTS.md` 和 `codes/workspace/`）。

```bash
# 检查必要文件
ls AGENTS.md
ls codes/workspace/
```

### Step 2: 读取 AGENTS.md 绑定项目代码

解析 `AGENTS.md` 中的 `## 绑定项目代码` 章节，提取仓库列表：

| 序号 | 仓库名 | 层级 | 目录路径 |
|------|--------|------|----------|
| 1 | `yl-web-sqs-serviceonline` | 小前台 | `codes/workspace/yl-web-sqs-serviceonline` |
| ... | ... | ... | ... |

同时解析 `### 克隆业务代码` 章节获取 SSH 和 HTTP 克隆地址。

### Step 3: 选择克隆方式

询问用户选择克隆方式：

1. **SSH 方式**（推荐）- 使用 `ssh://git@code.jms.com:2222/...` 地址
2. **HTTP 方式** - 使用 `http://code.jms.com/...` 地址

```
请选择克隆方式：
1. SSH（推荐，需要配置 SSH 密钥）
2. HTTP（需要输入用户名密码）

请输入选项 [1/2]:
```

### Step 4: 克隆业务代码

进入 `codes/workspace/` 目录，逐个克隆仓库：

```bash
cd codes/workspace

# 根据用户选择的方式克隆
git clone {ssh_url 或 http_url} {repo-name}
```

**并行克隆**：多个仓库可并行克隆以提高效率。

### Step 5: 检查 code-overview.md

读取 `docs/architecture/code-overview.md`，检查是否为预留值（占位内容）。

**预留值特征**：
- 文档状态章节说明"当前文档是占位文件"
- 内容为空或只有模板结构
- 包含 `__MODULE_NAME__` 等占位符

如果是预留值，询问用户是否初始化：

```
检测到 docs/architecture/code-overview.md 为预留值。
是否初始化 code-overview.md？[Y/n]
```

### Step 6: 初始化 code-overview.md

如果用户确认，调用 `doc-whitepaper-tech` skill 为每个仓库生成 `project-info.md`，并汇总生成 `code-overview.md`。

**生成内容**：
- 仓库概览表
- 系统架构图（Mermaid）
- 各仓库分工详解
- 技术栈版本汇总
- 代码阅读顺序
- 排查入口建议

### Step 7: 输出工作总结

完成初始化后，输出工作总结：

```
✅ 子模块本地初始化完成

## 已完成工作

- 克隆了 N 个业务代码仓库到 codes/workspace/
- 初始化了 docs/architecture/code-overview.md

## 已克隆仓库

| 序号 | 仓库名 | 层级 | 路径 |
|------|--------|------|------|
| 1 | yl-web-sqs-serviceonline | 小前台 | codes/workspace/yl-web-sqs-serviceonline |
| ... | ... | ... | ... |

## 后续工作建议

1. 查看业务代码：cd codes/workspace/{repo-name}
2. 补充代码仓库内容：各仓库的 project-info.md 已生成
3. 如需修改绑定项目：使用 harness-change-project skill

## 可用工具

- harness-change-project - 修改子模块绑定的项目代码（新增/删除/修改仓库）
```

---

## 使用示例

### 示例 1: 完整初始化

```
用户: 初始化 online 子模块

Agent 执行:
1. 检查当前在 modules/online 目录
2. 读取 AGENTS.md，发现 6 个仓库
3. 询问克隆方式，用户选择 SSH
4. 并行克隆 6 个仓库到 codes/workspace/
5. 检测 code-overview.md 为预留值
6. 询问是否初始化，用户确认
7. 调用 doc-whitepaper-tech 生成各仓库 project-info.md
8. 汇总生成 code-overview.md
9. 输出工作总结
```

### 示例 2: 仅克隆代码

```
用户: 拉取 workorder 子模块的业务代码

Agent 执行:
1. 检查当前在 modules/workorder 目录
2. 读取 AGENTS.md，发现 3 个仓库
3. 询问克隆方式，用户选择 HTTP
4. 克隆 3 个仓库
5. 检测 code-overview.md 已有内容，跳过初始化
6. 输出工作总结
```

### 示例 3: 子模块已有部分代码

```
用户: 初始化 qt 子模块

Agent 执行:
1. 检查 codes/workspace/，发现已有 2 个仓库
2. 读取 AGENTS.md，应有 4 个仓库
3. 询问克隆方式
4. 仅克隆缺失的 2 个仓库
5. 输出工作总结
```

---

## AGENTS.md 解析示例

**绑定项目代码章节**：

```markdown
## 绑定项目代码

本模块关联以下业务代码仓库：

| 序号 | 仓库名 | 层级 | 目录路径 |
|------|--------|------|----------|
| 1 | `yl-web-sqs-serviceonline` | 小前台 | `codes/workspace/yl-web-sqs-serviceonline` |
| 2 | `yl-jms-sqs-online` | 中台 | `codes/workspace/yl-jms-sqs-online` |
```

**克隆业务代码章节**：

```markdown
### 克隆业务代码

```bash
# SSH 方式（推荐）
git clone ssh://git@code.jms.com:2222/yl/yl-web-sqs-serviceonline.git yl-web-sqs-serviceonline
git clone ssh://git@code.jms.com:2222/yl/yl-jms-sqs-online.git yl-jms-sqs-online

# HTTP 方式
git clone http://code.jms.com/yl/yl-web-sqs-serviceonline.git yl-web-sqs-serviceonline
git clone http://code.jms.com/yl/yl-jms-sqs-online.git yl-jms-sqs-online
```
```

---

## 注意事项

1. **检查已有仓库**：克隆前检查 `codes/workspace/` 下是否已存在同名目录，避免重复克隆

2. **并行克隆**：多个仓库可并行克隆，提高效率

3. **克隆失败处理**：如果某个仓库克隆失败，记录错误继续克隆其他仓库，最后汇总报告

4. **SSH 密钥检查**：如果用户选择 SSH 方式，可提示检查 SSH 密钥配置

5. **code-overview.md 初始化**：仅在文档为预留值时询问是否初始化，已有内容则跳过

6. **用户确认**：克隆和初始化操作需要用户确认

---

## 依赖

- `AGENTS.md` - 绑定项目代码信息
- `doc-whitepaper-tech` skill - 生成 project-info.md
- Git 命令行工具
- Read/Edit/Write 工具

---

## 相关 Skill

- `harness-change-project` - 修改子模块绑定的项目代码（新增/删除/修改仓库）
- `doc-whitepaper-tech` - 生成项目技术文档
