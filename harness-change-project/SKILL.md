---
name: harness-change-project
description: 修改子模块 AGENTS.md 中的绑定项目代码章节，支持新增、删除、修改项目。默认从 module-registry.yaml 获取 Git 地址，若不存在则要求用户提供。
triggers:
- 用户要求"新增项目"或"添加项目"到模块
- 用户要求"删除项目"或"移除项目"从模块
- 用户要求"修改项目"或"更新项目"信息
- 用户要求"绑定项目代码"或"关联仓库"
- 用户提到"AGENTS.md 项目列表"或"克隆业务代码"
---

# Harness Change Project

修改子模块 `AGENTS.md` 中的 `## 绑定项目代码` 和 `### 克隆业务代码` 章节，支持新增、删除、修改项目。

## 工作流程

### Step 1: 确认操作类型

首先确认用户要执行的操作类型：

1. **新增 (add)** - 添加新的项目到模块
2. **删除 (remove)** - 从模块移除已有项目
3. **修改 (update)** - 修改已有项目的信息（如层级、目录路径等）
4. **查看 (list)** - 列出当前模块绑定的所有项目

### Step 2: 确认目标模块

确认要操作的模块名称（如 `online`, `workorder`, `qt` 等）。

模块路径格式：`modules/{module-name}/`

### Step 3: 读取 module-registry.yaml

从 `skills/harness-change-project/assets/module-registry.yaml` 读取项目注册表，获取：

- `name`: 仓库名
- `display_name`: 模块显示名
- `repos`: 仓库列表
  - `id`: 仓库 ID
  - `name`: 仓库名
  - `web_url`: Web 页面地址
  - `http_url`: HTTP 克隆地址
  - `ssh_url`: SSH 克隆地址
  - `layer`: 层级（小前台/中台/第三方前台等）
  - `gray_namespace`: 灰度命名空间

### Step 4: 执行操作

#### 4.1 新增项目 (add)

1. 确认要添加的项目名称
2. 从 `module-registry.yaml` 查找项目信息：
   - 如果找到：获取 `http_url` 和 `ssh_url`
   - 如果未找到：要求用户提供 Git 地址（HTTP 和/或 SSH）
3. 确认项目的层级（layer）
4. 更新 `AGENTS.md`：
   - 在"绑定项目代码"表格中添加新行
   - 在"克隆业务代码"章节添加对应的 git clone 命令

#### 4.2 删除项目 (remove)

1. 确认要删除的项目名称
2. 检查该项目是否在当前模块的 AGENTS.md 中
3. 更新 `AGENTS.md`：
   - 从"绑定项目代码"表格中移除对应行
   - 从"克隆业务代码"章节移除对应的 git clone 命令
4. 重新编排表格序号

#### 4.3 修改项目 (update)

1. 确认要修改的项目名称
2. 确认要修改的字段（层级、目录路径等）
3. 更新 `AGENTS.md` 中对应的内容

#### 4.4 查看项目 (list)

1. 读取 `AGENTS.md` 中的"绑定项目代码"章节
2. 展示当前绑定的所有项目列表

### Step 5: 更新 AGENTS.md

根据操作类型更新 `modules/{module-name}/AGENTS.md` 文件。

**AGENTS.md 格式参考**：

```markdown
## 绑定项目代码

本模块关联以下业务代码仓库：

| 序号 | 仓库名 | 层级 | 目录路径 |
|------|--------|------|----------|
| 1 | `yl-web-sqs-serviceonline` | 小前台 | `codes/yl-web-sqs-serviceonline` |
| 2 | `yl-jms-sqs-online` | 中台 | `codes/yl-jms-sqs-online` |

### 克隆业务代码

```bash
# 进入模块目录
cd modules/{module-name}

# 克隆业务代码到工作区（HTTP 方式）
cd codes
git clone {http_url} {repo-name}

# 或使用 SSH 方式克隆（推荐）
git clone {ssh_url} {repo-name}

# 返回模块根目录
cd ../..
```
```

### Step 6: 确认变更

向用户展示变更内容，确认是否继续。

**重要**: 修改 AGENTS.md 后需要用户确认是否提交 Git 变更。

---

## 使用示例

### 示例 1: 新增项目（registry 中存在）

```
用户: 给 online 模块添加 yl-jms-sqs-online-new 项目

Agent 执行:
1. 读取 module-registry.yaml，查找 yl-jms-sqs-online-new
2. 找到项目信息：
   - http_url: http://code.jms.com/yl/yl-jms-sqs-online-new.git
   - ssh_url: ssh://git@code.jms.com:2222/yl/yl-jms-sqs-online-new.git
   - layer: 中台
3. 更新 AGENTS.md，添加新项目
4. 展示变更，等待用户确认
```

### 示例 2: 新增项目（registry 中不存在）

```
用户: 给 online 模块添加 custom-project 项目

Agent 执行:
1. 读取 module-registry.yaml，查找 custom-project
2. 未找到，询问用户：
   "项目 custom-project 不在注册表中，请提供：
    - HTTP 克隆地址
    - SSH 克隆地址（可选）
    - 层级（小前台/中台/第三方前台等）"
3. 用户提供信息后，更新 AGENTS.md
```

### 示例 3: 删除项目

```
用户: 从 online 模块移除 yl-jms-sqs-online-third 项目

Agent 执行:
1. 读取 online/AGENTS.md，确认项目存在
2. 从表格和克隆命令中移除该项目
3. 重新编排序号
4. 展示变更，等待用户确认
```

### 示例 4: 修改项目

```
用户: 修改 online 模块的 yl-jms-sqs-online 层级为"小前台+中台"

Agent 执行:
1. 读取 online/AGENTS.md，找到对应项目
2. 更新层级字段
3. 展示变更，等待用户确认
```

### 示例 5: 查看项目列表

```
用户: 查看 online 模块绑定的项目列表

Agent 执行:
1. 读取 online/AGENTS.md
2. 展示"绑定项目代码"表格内容
```

---

## module-registry.yaml 结构

```yaml
modules:
  - name: online           # 模块名
    display_name: 飞兔IM   # 显示名
    repos:
      - id: 6917
        name: yl-web-sqs-serviceonline
        web_url: http://code.jms.com/yl/yl-web-sqs-serviceonline
        http_url: http://code.jms.com/yl/yl-web-sqs-serviceonline.git
        ssh_url: ssh://git@code.jms.com:2222/yl/yl-web-sqs-serviceonline.git
        layer: 小前台
        gray_namespace: ""
```

---

## 层级类型

| 层级 | 说明 |
|------|------|
| 小前台 | 前端 Web 应用 |
| 中台 | 后端 API 服务 |
| 第三方前台 | 第三方集成前端 |
| 小前台+中台 | 前后端一体 |
| 中台+小前台 | 前后端一体 |

---

## 注意事项

1. **优先使用 module-registry.yaml**: 默认从注册表获取项目信息，确保信息一致性

2. **用户确认**: 修改 AGENTS.md 前必须向用户展示变更内容并获得确认

3. **Git 操作需许可**: 如果用户要求提交变更，需要显式许可

4. **序号重排**: 删除项目后需要重新编排表格序号

5. **保持格式一致**: 更新 AGENTS.md 时保持现有格式风格

6. **同时更新两个章节**:
   - "绑定项目代码"表格
   - "克隆业务代码"命令块

---

## 依赖

- `skills/harness-change-project/assets/module-registry.yaml` - 项目注册表
- Read/Edit 工具
