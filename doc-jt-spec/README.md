# Doc JT Spec 操作指引

## 一、功能概述

`doc-jt-spec` 是将 PRD 需求文档转换为极兔概要设计文档的技能，核心流程为：

- 对话式 Review → Research → Planning 三阶段，逐步确认需求边界和技术方案
- 阶段结论落到 OpenSpec 结构化产物（proposal/specs/design/tasks）
- 最终输出 `概要设计.md`，格式遵循极兔概要设计规范

与 `doc-prd-to-trd` 的区别：
- `doc-prd-to-trd`：PRD → TRD，一步到位，适合需求清晰、变更较小的场景
- `doc-jt-spec`：PRD → 对话式深挖 → OpenSpec 结构化 → 概要设计，适合需求复杂、需逐阶段确认的场景

---

## 二、使用方式

### 方式一：直接触发

在 Claude Code 中输入：

```
/doc-jt-spec <PRD文件路径或目录>
```

示例：
```
/doc-jt-spec prd_docs/需求文档.docx
```

### 方式二：自然语言触发

当用户要求"生成概要设计""生成 TRD""做技术方案"时自动激活。

---

## 三、流程概览

```
PRD 文档 (.docx/.doc)
    │
    ▼
Step 0: PRD 转 Markdown
    │   scripts/word2md.bat 转换
    │
    ▼
Step 1: 对话式 Review → proposal.md
    │   评审需求清晰度、边界、风险
    │   用户确认后创建 OpenSpec change
    │
    ▼
Step 2: 对话式 Research → specs/**/*.md + design.md
    │   代码证据核验、接口/数据/缓存/灰度影响面
    │   用户确认后写入 specs 和 design
    │
    ▼
Step 3: 对话式 Planning → design.md + tasks.md
    │   技术方案、DDL/DML、灰度/回滚/验证策略
    │   用户确认后写入 tasks
    │
    ▼
Step 4: OpenSpec 校验 + 语义审查
    │   格式校验 + 业务正确性人工审查
    │
    ▼
Step 4.5: 最终对话校验
    │   一致性检查、疑问收口
    │
    ▼
Step 5: 生成概要设计.md
```

每个阶段都必须等待用户在对话中确认后才能进入下一阶段。

---

## 四、阶段详解

### Step 0：PRD 转 Markdown

当用户提供 `.docx` 或 `.doc` 文件时：

1. 根据 PRD 文件名创建需求目录
2. 将原始 PRD 移入需求目录
3. 使用脚本转换：
   ```bash
   scripts/word2md.bat "需求目录/需求文档.docx" "需求目录/需求文档.md"
   ```
4. 后续优先读取 Markdown 版本

### Step 1：对话式 Review

评审维度：
- 业务目标是否清楚
- 需求范围是否明确
- 业务规则是否完整
- 数据/接口/权限/性能/安全/灰度/回刷风险是否识别
- 不清楚、矛盾或缺失的信息

输出 Review 摘要后，逐个提问阻塞问题（一次只问一个）。用户确认后创建 OpenSpec change 和 `proposal.md`。

### Step 2：对话式 Research

必须做代码证据核验：
- 枚举值从代码读取，不凭语义猜测
- 接口清单从 Controller/Feign 读取
- 字段落点从 Entity/DTO/VO 读取
- Mapper/XML 以实际搜索结果为准

输出 Research 摘要后，用户确认写入 `specs/**/*.md` 和 `design.md`。

### Step 3：对话式 Planning

输出内容：
- 推荐方案 + 1-2 个备选方案
- DDL/DML/回滚 SQL 草案
- 接口改造范围
- 缓存和历史数据处理策略
- 灰度、回滚、验证策略
- 实施任务拆解

SQL 规则：
- 回刷 SQL 必须引用真实枚举值
- 回刷前提供影响范围查询
- 回刷后提供验证 SQL
- DDL 回滚必须说明兼容风险

### Step 4：OpenSpec 校验

```bash
openspec validate <change-id> --strict --no-interactive
openspec status --change <change-id>
```

校验通过后做语义审查：需求覆盖率、代码证据完整性、SQL 正确性等。

### Step 4.5：最终对话校验

一致性检查 + 疑问收口，只问阻塞问题，非阻塞问题写入待确认事项。

### Step 5：生成概要设计

读取 PRD + OpenSpec 全部产物 + 项目代码上下文，输出 `概要设计.md`，章节包括：

1. 需求背景
2. 业务链路
3. AI Coding 记录
4. 数据结构
5. 数据回刷
6. 接口设计
7. 性能设计
8. 容错设计
9. 灰度设计
10. 安全设计
11. 发版信息

---

## 五、输出目录结构

```text
#12xxxxx 【业务需求】XXX/
├── assets/                     # 图片资源
├── 需求文档.docx               # 原始 PRD
├── 需求文档.md                 # 转换后的 Markdown
├── openspec/
│   └── changes/<change-id>/
│       ├── proposal.md         # 需求提案
│       ├── specs/**/spec.md    # 功能规格
│       ├── design.md           # 技术设计
│       └── tasks.md            # 实施任务
└── 概要设计.md                  # 最终交付物
```

---

## 六、核心原则

| 原则 | 说明 |
|------|------|
| 对话驱动 | 所有阶段确认通过聊天完成，不要求用户打开文件 |
| 逐步确认 | Review → Research → Planning 每步必须等用户确认 |
| 代码证据 | 枚举值、接口、字段必须从代码读取，禁止猜测 |
| 无空章节 | 概要设计不留空章节，不确定内容写"待确认" |
| 灰度必须 | 生产行为变化必须包含灰度开关和回滚方案 |
| 一问一答 | 阻塞问题逐个提问，不一次抛出大量问题 |

---

## 七、与其他 doc-* 技能的关系

```
doc-prd-batch          批量 PRD 预览 + 需求评审（不做 TRD）
    │
    ▼ 评审通过
doc-preview-to-trd     已预审 PRD → TRD（一步到位）
    │
    ▼ 需求复杂 / 需逐阶段确认
doc-jt-spec            PRD → 对话式深挖 → OpenSpec → 概要设计
    │
    ▼ 同类文档生成
doc-prd-to-trd         PRD → TRD（标准流程）
doc-flowchart          需求内容 → Mermaid 流程图
```

---

## 八、环境依赖

| 依赖 | 用途 | 安装方式 |
|------|------|---------|
| OpenSpec CLI | 结构化产物管理 | `/install-openspec` |
| Pandoc | Word → Markdown 转换 | 系统安装 |
| Python 3.8+ | word2md 脚本 | 系统自带 |

---

## 九、常见问题

### Q1: 与 doc-prd-to-trd 怎么选？

- 需求清晰、变更较小 → `doc-prd-to-trd`，一步生成 TRD
- 需求复杂、需逐阶段确认 → `doc-jt-spec`，对话式推进

### Q2: 可以跳过某个阶段吗？

不可以。每个阶段的输出是下一阶段的输入，但对话中可以快速确认跳过不阻塞的部分。

### Q3: OpenSpec 产物需要手动编辑吗？

不需要。OpenSpec 由 AI 维护，用户只需在对话中确认，不需要打开文件交互。

### Q4: 生成概要设计后还能修改吗？

可以。对概要设计提出修改意见，AI 会直接更新 `概要设计.md` 和对应的 OpenSpec 产物。

---

**文档版本**: v1.0
**更新时间**: 2026-04-25
**适用范围**: 极兔 PRD → 概要设计场景
