---
name: harness-init-module-structure
description: 创建新的 harness 模块子模块，初始化目录结构、推送到 GitLab、添加为 submodule。支持简单初始化和完整工作流程。
---

# Harness Init Module Structure

创建完整的 harness 模块工作流程：初始化结构 → 创建 GitLab 项目 → 推送代码 → 添加为 submodule。

## 工作流程

### Step 1: 收集必要信息

如果用户未提供以下信息，需要询问：

1. **模块名称**（如 `workorder`, `online`, `qt`）
   - 用作目录名和 submodule 名称
   - 小写字母，无空格，需要时用连字符

2. **显示名称**（如 `普通工单`, `飞兔IM`, `质检`）
   - 中文业务模块名称

3. **GitLab 项目地址**（可选，未提供时自动生成）
   - 格式：`http://code.jms.com/ai-coding/sqs-harness-module-{module-name}.git`
   - 未提供时使用默认地址

4. **关联业务仓库**（可选）
   - 要绑定的业务代码仓库列表
   - 格式：`repo_name,repo_url` 或仅 `repo_name`（URL 从 module-registry.yaml 获取）

### Step 2: 初始化 Harness 结构

```powershell
powershell -ExecutionPolicy Bypass -File .\skills\harness-init-module-structure\scripts\init-harness-module-structure.ps1 -TargetDir .\modules\{module-name} -ModuleName {module-name}
```

### Step 3: 创建 GitLab 项目（如不存在）

使用 GitLab API 创建项目：

```bash
curl --request POST "http://code.jms.com/api/v4/projects" \
  --header "PRIVATE-TOKEN: {token}" \
  --header "Content-Type: application/json" \
  --data "{
    \"name\": \"sqs-harness-module-{module-name}\",
    \"namespace_id\": 3396,
    \"visibility\": \"private\",
    \"initialize_with_readme\": false
  }"
```

如无 API token，可通过 Web 表单手动创建。

### Step 4: 推送到 GitLab

```bash
cd modules/{module-name}
git init
git add -A
git commit -m "init {module-name} harness module structure"
git remote add origin {gitlab-url}
git branch -M master
git push -u origin master
```

### Step 5: 添加为 Submodule

```bash
cd {harness-root}
git submodule add {gitlab-url} modules/{module-name}
git config -f .gitmodules submodule.{module-name}.branch master
```

### Step 6: 更新 AGENTS.md（如提供了业务仓库）

如果提供了业务仓库，更新 `modules/{module-name}/AGENTS.md` 的绑定项目代码章节。

### Step 7: 提交并推送

```bash
git add .gitmodules modules/{module-name}
git commit -m "添加 {module-name} 子模块"
git push
```

---

## 使用示例

### 示例 1: 简单初始化（仅提供模块名）

用户: "初始化 workorder 模块"

Agent 执行:
1. 检查 `modules/workorder` 是否存在
2. 运行初始化脚本
3. 完成（不推送 GitLab，不添加 submodule）

### 示例 2: 完整工作流程（模块名 + GitLab 地址）

用户: "创建 workorder 子模块，GitLab 地址 http://code.jms.com/ai-coding/sqs-harness-module-workorder.git"

Agent 执行:
1. 初始化 harness 结构
2. 创建 GitLab 项目（如需要）
3. 推送到 GitLab
4. 添加为 submodule
5. 提交并推送到父仓库

### 示例 3: 完整工作流程 + 业务仓库绑定

用户: "创建 online 子模块，关联仓库 yl-web-sqs-serviceonline, yl-jms-sqs-online"

Agent 执行:
1. 初始化 harness 结构
2. 创建 GitLab 项目
3. 推送到 GitLab
4. 添加为 submodule
5. 更新 AGENTS.md 绑定业务仓库
6. 提交并推送所有变更

---

## 注意事项

- 默认目标目录为 harness 根目录下的 `modules/{module-name}`
- GitLab `ai-coding` 组 ID 为 `3396`
- 所有 submodule 默认跟踪 `master` 分支
- 如果 `modules/` 下已存在同名模块，需用户确认后才可覆盖
- 如果 `.gitmodules` 中已注册该 submodule，跳过添加步骤
- 业务仓库 URL 从 `module-registry.yaml` 获取（仅提供仓库名时）

---

## 初始化后的目录结构

```
modules/{module-name}/
├── AGENTS.md
├── .module-manifest.yaml
├── .gitignore
├── .harness/
│   ├── directory-layout.md
│   ├── harness-overview.md
│   └── runtime-lifecycle.md
├── rules/
│   ├── agent-rules.md
│   └── engineering-rules.md
├── codes/
├── docs/
│   ├── domain/
│   │   └── TechWhitepaper.md
│   └── memory/
│       ├── demand/
│       ├── summary/
│       └── memory.md
└── skills/
    ├── {module-name}-analyst/
    ├── {module-name}-operator/
    └── {module-name}-reviewer/
```
