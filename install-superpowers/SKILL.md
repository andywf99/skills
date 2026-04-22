---
name: install-superpowers
description: 安装 Claude Code Superpowers 插件，通过官方插件源全局安装。
triggers:
  - 安装superpowers
  - 安装 superpowers
  - 安装Superpowers插件
  - 安装Claude Code插件
---

# 安装 Claude Code Superpowers 插件

## 第1步：检查运行环境

本插件仅支持 Claude Code CLI，需先确认当前环境。

执行：

```bash
which claude 2>/dev/null && claude --version
```

**判断逻辑：**
- 命令成功输出版本号：当前为 Claude Code 环境，继续执行第2步
- 命令失败（未找到 claude 命令）：**停止执行**，提示用户「Superpowers 插件仅支持 Claude Code CLI，当前环境未检测到 claude 命令，请先安装 Claude Code」

## 第2步：检查是否已安装

执行：

```bash
claude plugins list 2>/dev/null | grep superpowers
```

- 输出中包含 `superpowers`：提示用户「Superpowers 插件已安装，跳过安装步骤」，**结束**
- 未找到：继续执行第3步

## 第3步：安装插件

执行：

```bash
claude plugin install superpowers@claude-plugins-official --global
```

安装完成后进入第4步。

## 第4步：验证安装

执行：

```bash
claude plugins list 2>/dev/null | grep superpowers
```

- 输出中包含 `superpowers`：提示用户「Superpowers 插件安装成功」
- 未找到：提示用户「安装后验证失败，请重启 Claude Code 后再试」
