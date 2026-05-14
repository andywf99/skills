# Harness Batch Update

批量更新所有 harness 子模块的工具。

## 功能

- **查看状态**：检查所有子模块的 git 状态
- **批量拉取**：拉取所有子模块的最新代码
- **批量推送**：推送所有子模块的本地提交
- **批量提交**：提交所有子模块的改动
- **执行脚本**：在所有子模块中执行命令
- **更新文件**：批量更新文件内容

## 使用方法

### 1. 列出所有子模块

```bash
python skills/harness-batch-update/scripts/batch-update.py list
```

### 2. 查看 Git 状态

```bash
python skills/harness-batch-update/scripts/batch-update.py git-status
```

输出示例：
```
Git Status Summary (42 modules)
============================================================

✅ Clean (35): online, networkim, qt, ...

📝 Modified (3):
   - workorder
     M AGENTS.md
   - arbitration
     M .harness/harness-overview.md

⬆️  Ahead of remote (2):
   - claim (+1 commits)
   - postal (+2 commits)

⬇️  Behind remote (2):
   - sqsweb (-3 commits)
   - wdsqsweb (-1 commits)
```

### 3. 批量拉取

```bash
python skills/harness-batch-update/scripts/batch-update.py git-pull
```

### 4. 批量推送

```bash
python skills/harness-batch-update/scripts/batch-update.py git-push
```

### 5. 批量提交

```bash
python skills/harness-batch-update/scripts/batch-update.py batch-commit --message "更新配置文件"
```

### 6. 执行脚本

```bash
# 在所有子模块执行 npm install
python skills/harness-batch-update/scripts/batch-update.py run-script --script "npm install"

# 在所有子模块执行 mvn clean
python skills/harness-batch-update/scripts/batch-update.py run-script --script "mvn clean"
```

### 7. 更新文件

```bash
# 更新所有子模块的 .gitignore
python skills/harness-batch-update/scripts/batch-update.py update-file \
  --file .gitignore \
  --content "# IDE
.idea/
.claude/

# 业务代码工作区
codes/"
```

## 注意事项

1. **确认范围**：执行批量操作前，会显示受影响的模块列表
2. **错误处理**：单个模块失败不会中断整个批量操作
3. **结果汇总**：操作完成后显示成功/失败统计
4. **父仓库更新**：子模块更新后，需要在父仓库提交新的 commit 引用

## 示例场景

### 场景 1：每日同步

```bash
# 拉取所有子模块最新代码
python skills/harness-batch-update/scripts/batch-update.py git-pull

# 更新父仓库的子模块引用
git add modules/
git commit -m "更新子模块到最新版本"
git push
```

### 场景 2：批量更新配置

```bash
# 更新所有子模块的 .gitignore
python skills/harness-batch-update/scripts/batch-update.py update-file \
  --file .gitignore \
  --content "$(cat templates/.gitignore)"

# 提交改动
python skills/harness-batch-update/scripts/batch-update.py batch-commit \
  --message "更新 .gitignore 配置"

# 推送到远程
python skills/harness-batch-update/scripts/batch-update.py git-push
```

### 场景 3：检查未提交改动

```bash
# 查看状态
python skills/harness-batch-update/scripts/batch-update.py git-status

# 输出会显示哪些模块有未提交的改动
```
