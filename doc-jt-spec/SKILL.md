---
name: doc-jt-spec
description: 将 PRD 需求文档转换为极兔概要设计文档。适用于用户要求生成 TRD、概要设计、技术方案，或提供 PRD 文档路径时。流程采用对话式 Review/Research/Planning，并把阶段结论落到 OpenSpec proposal/specs/design/tasks，最终输出极兔概要设计.md；保留严格阶段确认，但不要求用户打开 review.md/research.md/plan.md 文件交互。
---

# JT Spec

将 PRD 转换为可落地的极兔概要设计文档。流程保留 Review、Research、Planning 三个阶段，但阶段确认全部通过对话完成；OpenSpec 只作为结构化产物承接，不作为一开始就突兀创建的提案。

## 核心原则

- 不要一开始就创建 OpenSpec change。
- 先读取 PRD 和项目上下文，再通过对话完成 Review、Research、Planning。
- 不默认生成 `review.md`、`research.md`、`plan.md`；这些阶段的结论直接在聊天中给用户确认。
- 每个阶段都必须等待用户在对话中确认后才能进入下一阶段。
- OpenSpec 产物由 AI 维护，用户不需要打开文件确认。
- 严禁把没有证据的推断写成确定结论。
- 最终交付物仍是 `概要设计.md`，格式遵循极兔概要设计规范。

## 与 superpowers:brainstorming 的结合

吸收以下规则：

- 先探索上下文，再提问。
- 一次只问一个澄清问题。
- 优先问会影响方案边界、数据口径、接口契约、上线风险的问题。
- 在 Planning 阶段给出 2-3 个可选方案、取舍和推荐方案。
- 在对话中展示阶段结论，并等待用户确认。
- 不在方案确认前进入实现或生成最终 TRD。

不吸收以下规则：

- 不创建 `docs/superpowers/specs/...-design.md`。
- 不要求用户审阅 superpowers spec 文件。
- 不自动 commit。
- 不进入 superpowers `writing-plans`。

## 目录结构

```text
#12xxxxx 【业务需求】XXX/
├── assets/
├── 需求文档.docx
├── 需求文档.md
├── openspec/
│   └── changes/<change-id>/
│       ├── proposal.md
│       ├── specs/**/spec.md
│       ├── design.md
│       └── tasks.md
└── 概要设计.md
```

## Step 0：PRD 转 Markdown

当用户提供 `.docx` 或 `.doc`：

1. 根据 PRD 文件名创建需求目录。
2. 将原始 PRD 移入需求目录。
3. 使用脚本转换 Markdown：

```bash
scripts/word2md.bat "需求目录/需求文档.docx" "需求目录/需求文档.md"
```

4. 检查图片、表格、列表是否基本可读。
5. 后续优先读取 `需求文档.md`。

## Step 1：对话式 Review -> proposal.md

目标：评审 PRD 是否足够清楚，并确认需求边界。不要生成 `review.md`。

执行顺序：

1. 读取 PRD Markdown。
2. 如果当前目录是代码仓库，快速查看项目结构、README、已有 OpenSpec specs。
3. 在聊天中输出 Review 摘要：
   - 业务目标
   - 需求范围
   - 明确的业务规则
   - 不清楚、矛盾或缺失的信息
   - 数据、接口、权限、性能、安全、灰度、回刷风险
   - 是否阻塞进入 Research
4. 对阻塞问题逐个提问，一次只问一个。
5. 用户确认 Review 通过后，才创建或完善 OpenSpec `proposal.md`。

创建 change：

```bash
openspec new change <change-id> --description "<一句话需求摘要>"
openspec instructions proposal --change <change-id>
```

`proposal.md` 必须承接 Review 结论，包括 Why、What Changes、Capabilities、Impact。

## Step 2：对话式 Research -> specs/**/*.md + design.md

目标：结合代码证据深挖需求，把产品描述转成可验证的系统行为和技术事实。不要生成 `research.md`。

必须做代码证据核验：

- 枚举值必须从代码读取，不能凭语义猜测。
- 接口清单必须从 Controller、Feign 或接口定义读取。
- 字段落点必须从 Entity、DTO、VO、缓存 DTO 读取。
- 服务范围过滤必须检查业务码枚举和过滤逻辑。
- 审核、解约、导出、缓存刷新、异步任务、外部依赖必须检查是否受影响。
- Mapper/XML 文件必须以实际搜索结果为准，不能凭常见结构猜测。
- 所有“无”“无需”“自动包含”结论必须有代码证据或 PRD 明确依据；否则写为待确认。

在聊天中输出 Research 摘要：

- 功能点拆解
- 影响接口和间接链路
- 数据模型、枚举值和回刷范围
- 缓存、导出、审核、解约、灰度、权限、安全影响面
- 代码证据清单
- 待确认事项

用户确认 Research 通过后，才写入或完善：

```bash
openspec instructions specs --change <change-id>
openspec instructions design --change <change-id>
```

`specs/**/*.md` 必须描述系统 SHALL/MUST 行为和场景。`design.md` 必须记录代码证据、关键决策、风险、迁移和 Open Questions。

## Step 3：对话式 Planning -> design.md + tasks.md

目标：确认技术方案、上线策略和任务拆解。不要生成 `plan.md`。

在聊天中输出 Planning 摘要：

- 推荐方案和 1-2 个备选方案
- 方案取舍和推荐理由
- DDL/DML/回滚 SQL 草案
- 接口改造范围
- 缓存和历史数据处理策略
- 灰度、回滚、验证策略
- OpenSpec capability specs 列表
- 实施任务拆解

SQL 规则：

- 回刷 SQL 必须引用真实枚举值。
- 回刷前必须提供影响范围查询。
- 回刷后必须提供验证 SQL。
- 数据回滚不能简单全表更新，必须有备份表、回滚条件或明确影响范围。
- DDL 回滚必须说明对已发布代码的兼容风险。

用户确认 Planning 通过后，才写入或完善：

```bash
openspec instructions tasks --change <change-id>
```

`tasks.md` 中的文件路径必须来自真实代码搜索结果；找不到文件时写“待定位”，不要猜测路径。

## Step 4：OpenSpec 校验和语义审查

运行：

```bash
openspec validate <change-id> --strict --no-interactive
openspec status --change <change-id>
```

注意：OpenSpec strict 校验只代表格式有效，不代表业务正确。校验通过后仍必须做语义审查：

- PRD 需求是否全部进入 proposal/specs/design/tasks。
- 枚举值、状态值、接口路径、类名、字段名是否有代码证据。
- 回刷 SQL 是否引用真实枚举值。
- 接口清单是否漏掉审核、解约、导出、缓存刷新等间接链路。
- 是否存在无依据的“无/无需/自动”结论。
- tasks 中的文件路径是否来自真实代码搜索结果。

如果语义审查发现问题，修复 OpenSpec 产物并在聊天中说明，再继续生成 TRD。

## Step 4.5：最终对话校验

目标：在生成 `概要设计.md` 前，用 superpowers:brainstorming 的方式做最终一致性检查和疑问收口。

执行规则：

- 重新检查 PRD、OpenSpec、代码证据、SQL、接口清单、灰度/回滚/缓存/权限/安全是否一致。
- 只问会影响最终 TRD 正确性的阻塞问题。
- 一次只问一个问题，不要一次抛出大量问题。
- 非阻塞问题写入 OpenSpec `Open Questions` 和 `概要设计.md` 的待确认事项。
- 如果疑问会改变 DDL/DML、接口契约、灰度策略、回刷范围、权限/安全结论，必须在生成 TRD 前向用户确认。
- 在聊天中输出最终确认摘要，包含推荐方案、关键风险、待确认项、是否可以生成 `概要设计.md`。

不要执行：

- 不创建 `docs/superpowers/specs/...-design.md`。
- 不要求用户打开文件 review。
- 不自动 commit。
- 不进入 superpowers `writing-plans`。

用户确认最终校验通过后，进入 Step 5。

## Step 5：生成极兔概要设计

读取以下资料：

- PRD Markdown
- OpenSpec `proposal.md`
- OpenSpec `specs/**/*.md`
- OpenSpec `design.md`
- OpenSpec `tasks.md`
- 当前项目代码上下文

输出 `概要设计.md`，章节包括：

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

要求：

- 不留空章节。
- 不确定内容写入“待确认”，并说明影响。
- 数据结构必须说明唯一索引和幂等方案。
- 新增或变更类接口必须说明事务、并发控制、日志留痕。
- 涉及生产行为变化必须包含灰度开关和回滚方案；如判断无需灰度，必须说明证据。
- 涉及权限或敏感数据必须包含越权风险和脱敏方案。

## 交互规则

- 所有阶段确认都通过聊天完成，不要求用户打开文件。
- Review、Research、Planning 三个阶段都必须等待用户对话确认。
- 如果发现重大歧义、互斥需求、缺少核心业务规则，暂停并询问。
- 如果只是非关键缺口，继续生成，并在 OpenSpec `Open Questions` 和 `概要设计.md` 中列为待确认事项。
- 不要使用 `review.md`、`research.md`、`plan.md` 作为默认交互文件；仅在用户明确要求时生成。