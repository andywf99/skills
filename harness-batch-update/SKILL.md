---
name: harness-batch-update
description: Use when a user wants to batch update all harness submodules, including pulling latest changes, updating common files, running scripts across all modules, or synchronizing configurations.
---

# Harness Batch Update

Use this skill to perform batch operations across all harness submodules in the `modules/` directory.

## Supported Operations

### 1. Update Submodules to Latest

Pull latest changes from remote for all submodules:

```bash
git submodule update --remote
```

### 2. Batch Git Operations

Execute git commands across all submodules:

- `git pull` - Pull latest changes
- `git status` - Check status of all modules
- `git push` - Push all local commits
- `git branch` - List branches

### 3. Batch File Operations

- Update common files (e.g., `.gitignore`, `.harness/*.md / rules/*.md`)
- Add new files to all modules
- Remove files from all modules
- Replace content in files across all modules

### 4. Batch Script Execution

Run a script or command in each submodule directory.

## Workflow

### Step 1: Identify Operation Type

Ask the user what operation they want to perform:

1. **Update submodules** - Pull latest from remote
2. **Batch git command** - Run git command in all modules
3. **Batch file operation** - Add/update/remove files
4. **Batch script execution** - Run custom script
5. **Custom operation** - Describe what you need

### Step 2: Confirm Scope

Show the list of affected modules and ask for confirmation:

```
Found 42 submodules in modules/:
- online
- networkim
- qt
- workorderhub
...
```

### Step 3: Execute Operation

Run the batch operation with progress reporting.

### Step 4: Report Results

Show summary of successful/failed operations.

## Usage Examples

### Example 1: Pull Latest Changes

```
User: "更新所有子模块到最新版本"
```

Agent will:
1. Run `git submodule update --remote`
2. Report which modules were updated
3. Ask if user wants to commit the updates to parent repo

### Example 2: Batch Git Status

```
User: "查看所有子模块状态"
```

Agent will:
1. Run `git status` in each module
2. Show modules with uncommitted changes
3. Show modules that are ahead/behind remote

### Example 3: Update Common File

```
User: "更新所有子模块的 .gitignore 文件"
```

Agent will:
1. Read the new `.gitignore` content
2. Write to all modules
3. Commit and push changes

### Example 4: Run Custom Script

```
User: "在所有子模块执行 npm install"
```

Agent will:
1. Run `npm install` in each module
2. Report success/failure for each module

## Batch Script

Use the provided `batch-update.py` script for complex operations:

```bash
python skills/harness-batch-update/scripts/batch-update.py <operation> [options]

# Examples:
python skills/harness-batch-update/scripts/batch-update.py git-status
python skills/harness-batch-update/scripts/batch-update.py git-pull
python skills/harness-batch-update/scripts/batch-update.py run-script "npm install"
python skills/harness-batch-update/scripts/batch-update.py update-file .gitignore "content"
```

## Safety Checks

- Always show affected modules before executing
- Ask for confirmation before destructive operations
- Create backups before bulk file replacements
- Report errors but continue with remaining modules
- Provide rollback instructions if needed

## Notes

- Default modules directory is `modules/`
- Failed operations don't stop the batch process
- Results are summarized at the end
- Parent repo updates (submodule commit references) are handled separately
