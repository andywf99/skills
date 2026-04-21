---
name: infra-openspec
description: 检查 Node.js 版本并安装 OpenSpec CLI
triggers:
  - 安装OpenSpec
  - 安装OpenSpec
  - 初始化OpenSpec
---

# 安装 OpenSpec CLI

按以下步骤检查环境并安装 OpenSpec CLI。

## 第1步：检查 Node.js 版本

执行：
```bash
node --version
```

**判断逻辑：**
- 版本 >= 20.19.0：展示当前版本，直接进入第2步
- 版本 < 20.19.0：提示用户「当前 Node.js 版本为 vX.X.X，OpenSpec 要求 >= 20.19.0，请访问 https://nodejs.org 更新后重新执行」，并停止

## 第2步：安装 OpenSpec CLI

执行：
```bash
npm install -g @fission-ai/openspec@latest
```

安装完成后进入第3步。

## 第3步：验证安装

执行：
```bash
openspec --version
```

- 输出版本号：提示用户「OpenSpec CLI 安装成功，版本：X.X.X」
- 报错未找到命令：提示用户「安装可能未生效，请检查 npm 全局路径是否在系统 PATH 中」
