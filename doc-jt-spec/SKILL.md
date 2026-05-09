---
name: doc-jt-spec-v2
description: 将 PRD 转换为极兔概要设计文档的新版流程。先用 superpowers 式对话逐项收口 Review/Research/Planning 的所有设计影响问题，再把已确认结论落到 OpenSpec proposal/specs/design/tasks，最后生成概要设计.md。适用于用户要求生成 TRD、概要设计、技术方案，或提供 PRD 文档路径时，尤其适合业务口径多、接口/DDL/灰度/权限需要逐项确认的需求。
---

# JT Spec V2

## 工作目录

当前会话的工作目录为 `{{WORKING_DIRECTORY}}`，后续所有文件路径、目录结构、脚本执行均基于此目录，不再使用相对路径或临时路径。

## 设计目标

`doc-jt-spec-v2` 的主导流程是 **superpowers 式对话收口**，OpenSpec 只是承接和校验已确认结论的结构化产物。

核心原则：

1. **先问清楚，再写 OpenSpec。** Review、Research、Planning 阶段可以生成阶段文件方便 CLI 查看完整内容，但不创建 OpenSpec 产物，直到该阶段所有设计影响问题逐项收口。
2. **阶段文件服务对话，不替代确认。** `review.md`、`research.md`、`plan.md` 只是阶段草稿/快照；用户不需要打开文件确认，阶段通过仍必须在聊天中用 `AskUserQuestion` 完成。
3. **OpenSpec 不驱动需求。** OpenSpec 只记录已经确认的 Why / What / SHALL / Design / Tasks，不把未确认问题推进成文档结论。
4. **待确认默认阻塞。** 会影响业务行为、接口契约、DDL/DML、回刷、灰度、权限、安全、事务、外部依赖、测试验收的事项，必须通过 `AskUserQuestion` 逐项确认。
5. **一次只问一个问题。** 每个问题都用 `AskUserQuestion`，提供 2-4 个业务选项，第一个选项是推荐项并标注“推荐”。
6. **最终 TRD 不偷懒。** 只有真正不影响最终设计正确性的外部事项，才允许留为“待确认”，并必须写明非阻塞原因。

## 强制 AskUserQuestion 规则

凡是以下事项未确认，必须调用 `AskUserQuestion`，不能用普通文本询问，也不能直接写入文档：

- 业务范围、端口范围、角色范围、数据范围。
- 业务规则、校验规则、失败口径、部分成功/全部失败口径。
- 接口路径、接口入参/出参、Feign 契约、外部系统字段。
- DDL 字段、字段类型、默认值、索引、唯一约束、ES mapping。
- DML/回刷范围、备份、验证 SQL、回滚 SQL。
- 缓存策略、异步任务、消息队列、下载/导出链路。
- 事务边界、并发控制、幂等方案。
- 灰度开关、回滚策略、发版顺序。
- 权限、安全、脱敏、越权风险。
- 测试验收标准。

`AskUserQuestion` 要求：

- 每次只调用一次。
- 每次只问一个问题。
- options 必须 2-4 个。
- 第一个 option 必须是推荐项，label 中包含“推荐”。
- 选项必须是业务含义明确的选择，不要只给“是/否”。
- 允许用户用工具自带 Other 输入自定义，不要伪造“其他”选项。
- 用户回答后，必须更新当前阶段结论，再判断是否继续问下一个问题。

## 待确认分级

### 阻塞待确认

满足任一条件即为阻塞：

- 会改变系统行为。
- 会改变接口契约。
- 会改变数据库/ES/缓存结构。
- 会改变回刷、回滚或灰度策略。
- 会改变权限、安全或敏感数据处理。
- 会改变事务一致性或失败口径。
- 会改变测试验收标准。

阻塞待确认必须逐项提问收口，禁止写入最终 TRD 后继续推进。

### 非阻塞待确认

必须同时满足：

- 不改变已确认主方案。
- 不影响代码结构和接口契约。
- 不影响 DDL/DML/ES/回刷/回滚。
- 不影响权限、安全、灰度、测试验收。
- 只是外部排期、字段最终命名、上线窗口等执行层细节。

非阻塞待确认可以写入 Open Questions 和概要设计，但必须标注：

- 为什么非阻塞。
- 当前推荐默认值或占位方案。
- 后续由谁确认。
- 如果最终结果不同，影响范围是什么。

## 目录结构

```text
{{WORKING_DIRECTORY}}/
├── assets/
├── 需求文档.docx
├── 需求文档.md
├── stage/
│   ├── review.md
│   ├── research.md
│   └── plan.md
├── openspec/
│   └── changes/<change-id>/
│       ├── proposal.md
│       ├── specs/**/spec.md
│       ├── design.md
│       └── tasks.md
└── 概要设计.md
```

## Step 0：PRD 转 Markdown

1. 检查 `{{WORKING_DIRECTORY}}` 下是否存在 `需求文档.docx`（或 `.doc`）。
2. 如果未找到，退出执行，用 `AskUserQuestion` 提示用户："当前工作目录下缺少 `需求文档.docx` 必要文件，请确认文件是否已放置到 `{{WORKING_DIRECTORY}}` 目录下。"
3. 如果找到，使用脚本转换 Markdown：

```bash
scripts/word2md.bat "{{WORKING_DIRECTORY}}/需求文档.docx" "{{WORKING_DIRECTORY}}/需求文档.md"
```

4. 检查图片、表格、列表是否基本可读。
5. 后续优先读取 `{{WORKING_DIRECTORY}}/需求文档.md`。

不要在 Step 0 创建 OpenSpec change。

## 阶段文件规则

大需求需要阶段文件承载完整上下文，避免 CLI 对话摘要过长或信息丢失。

必须生成：

- `{{WORKING_DIRECTORY}}/stage/review.md`：Review 阶段完整评审快照。
- `{{WORKING_DIRECTORY}}/stage/research.md`：Research 阶段完整代码证据和影响面。
- `{{WORKING_DIRECTORY}}/stage/plan.md`：Planning 阶段完整方案、SQL、任务拆解。

阶段文件规则：

1. 阶段文件可以在对应阶段中持续更新，但只能记录“已确认事实”和“待确认草稿”。
2. 阶段文件不是用户确认入口；用户不需要打开文件确认，所有确认仍必须通过聊天和 `AskUserQuestion` 完成。
3. 每次阶段文件更新后，聊天中只输出简短摘要和文件路径，避免 CLI 被长文本刷屏。
4. 当用户要求“展开/查看完整内容”时，读取对应阶段文件并分段展示。
5. 阶段通过前，阶段文件中不能把阻塞待确认写成确定结论。
6. 阶段通过后，必须把用户已确认的答案回写阶段文件，形成“已确认版本”。

阶段文件建议结构：

```text
# <阶段名>

## 1. 阶段结论摘要
## 2. 已确认事实
## 3. 代码/PRD 证据
## 4. 阻塞待确认项
## 5. 已收口问题清单
## 6. 非阻塞待确认项及原因
## 7. 下一阶段输入
```

## Step 1：Superpowers Review（对话确认 + review.md，不写 OpenSpec）

目标：确认 PRD 的业务边界和阻塞疑问。

必须执行：

1. 读取 PRD Markdown。
2. 快速查看项目结构、README/CLAUDE、核心 Controller/Service/Entity/DTO/VO/Mapper。
3. 写入或更新 `{{WORKING_DIRECTORY}}/stage/review.md`，完整记录：
   - 业务目标。
   - 需求范围。
   - 明确规则。
   - 矛盾、缺失、不清楚的信息。
   - 数据、接口、权限、性能、安全、灰度、回刷风险。
   - 阻塞问题清单。
   - 已收口问题清单。
4. 在聊天中只输出 Review 简短摘要、`{{WORKING_DIRECTORY}}/stage/review.md` 路径、当前要确认的一个阻塞问题。
5. 对阻塞问题逐项 `AskUserQuestion`。
6. 每个回答后更新 Review 结论并回写 `{{WORKING_DIRECTORY}}/stage/review.md`。
7. 当且仅当所有阻塞问题收口后，才能发起 Review 阶段通过确认。

Review 阶段禁止：

- 禁止创建 OpenSpec change。
- 禁止写 proposal.md。
- 禁止把未确认范围写成确定结论。
- 禁止一次性把多个阻塞问题列给用户让用户自行回答。

Review 通过确认问题也必须用 `AskUserQuestion`。

## Step 2：Superpowers Research（对话确认 + research.md，不写 OpenSpec）

目标：用代码证据把 PRD 转成可验证系统行为。

必须核验：

- 枚举值：从 enum 或常量读取。
- 接口路径：从 Controller/Feign 读取。
- DTO/VO/Entity 字段落点。
- Mapper/XML/SQL 真实文件。
- ES mapping 或 ES 查询字段。
- 缓存、Redis key、消息队列、异步任务。
- 导出/下载/回刷/审核/解约/满意度/短信等间接链路。
- 权限和数据范围过滤。
- 灰度开关和现有回滚方式。

`{{WORKING_DIRECTORY}}/stage/research.md` 必须完整记录：

- 功能点拆解。
- 影响接口和间接链路。
- 数据模型、枚举值、状态值、回刷范围。
- 缓存、ES、导出、短信、审核、权限、安全影响面。
- 代码证据清单，带文件路径和行号。
- 阻塞待确认清单。
- 已收口问题清单。
- 非阻塞待确认草稿及非阻塞原因。

聊天中只输出 Research 简短摘要、`{{WORKING_DIRECTORY}}/stage/research.md` 路径、当前要确认的一个阻塞问题。

Research 阶段门禁：

1. 阻塞待确认逐项 `AskUserQuestion`。
2. 用户回答后更新 Research 结论并回写 `{{WORKING_DIRECTORY}}/stage/research.md`。
3. 不能用“后续待确认”跳过接口契约、字段落点、枚举、SQL、灰度、权限、安全等问题。
4. 所有阻塞问题收口后，输出“已收口问题清单”。
5. 如仍有非阻塞待确认，逐项说明为什么非阻塞。
6. 用 `AskUserQuestion` 请求 Research 通过确认。

Research 通过前禁止：

- 禁止创建或完善 OpenSpec specs/design。
- 禁止生成概要设计。

## Step 3：Superpowers Planning（对话确认 + plan.md，不写 OpenSpec）

目标：确认技术方案、SQL、接口、灰度、回滚、任务拆解。

`{{WORKING_DIRECTORY}}/stage/plan.md` 必须完整记录：

- 推荐方案。
- 1-2 个备选方案。
- 取舍和推荐理由。
- 接口设计草案。
- DTO/VO/Entity/Mapper/Service 改造范围。
- DDL/DML/ES mapping 草案。
- 影响范围查询、备份、验证 SQL、回滚 SQL。
- 事务边界、并发控制、幂等。
- 缓存和历史数据策略。
- 灰度和回滚策略。
- 权限、安全、脱敏。
- 测试和验收标准。
- 实施任务拆解草案。
- 阻塞待确认清单。
- 已收口问题清单。

聊天中只输出 Planning 简短摘要、`{{WORKING_DIRECTORY}}/stage/plan.md` 路径、当前要确认的一个阻塞问题。

Planning 阶段必须逐项确认：

- 主方案选择。
- 字段设计与默认值。
- 回刷范围与回滚策略。
- 接口契约。
- 事务/一致性失败口径。
- 短信/外部依赖失败口径。
- 缓存策略。
- 灰度开关。
- 权限和安全口径。
- 测试验收标准。

Planning 通过前必须输出并回写 `{{WORKING_DIRECTORY}}/stage/plan.md`：

- 已收口问题清单。
- 剩余非阻塞待确认清单及非阻塞原因。
- 最终推荐方案摘要。

Planning 通过确认必须用 `AskUserQuestion`。

## Step 4：一次性生成 OpenSpec 产物

只有 Review、Research、Planning 全部通过后，才创建 OpenSpec change。

执行：

```bash
openspec new change <change-id> --description "<一句话需求摘要>"
openspec instructions proposal --change <change-id>
openspec instructions specs --change <change-id>
openspec instructions design --change <change-id>
openspec instructions tasks --change <change-id>
```

写入规则：

### proposal.md

承接已确认的 Review 结论：

- Why。
- What Changes。
- New/Modified Capabilities。
- Impact。

### specs/**/*.md

描述已确认系统行为：

- 使用 SHALL/MUST。
- 每个 Requirement 必须有 `#### Scenario`。
- 不把未确认问题写成 SHALL。

### design.md

记录已确认技术设计：

- Context。
- Goals / Non-Goals。
- Decisions。
- Alternatives。
- Risks / Trade-offs。
- Migration Plan。
- Open Questions（仅允许非阻塞待确认，并说明原因）。

### tasks.md

- 使用 `- [ ]` checkbox。
- 文件路径必须来自真实代码搜索结果。
- 找不到路径写“待定位”，不要猜测。

## Step 5：OpenSpec 校验与语义审查

运行：

```bash
openspec validate <change-id> --strict --no-interactive
openspec status --change <change-id>
```

语义审查必须检查：

- PRD 需求是否全部进入 proposal/specs/design/tasks。
- 所有阻塞待确认是否已在聊天中收口。
- specs 是否只包含已确认 SHALL/MUST。
- design 的 Open Questions 是否全部非阻塞且有原因。
- 枚举、状态、接口路径、类名、字段名是否有代码证据。
- SQL 是否引用真实枚举值。
- tasks 文件路径是否来自真实搜索结果。

如果发现阻塞问题：

1. 暂停生成概要设计。
2. 用 `AskUserQuestion` 逐项确认。
3. 回写 OpenSpec。
4. 重新校验。

## Step 6：最终对话校验

目标：生成 `概要设计.md` 前最后一次 superpowers 式收口。

必须输出最终确认摘要：

- 推荐方案。
- 已收口问题清单。
- 剩余非阻塞待确认清单及非阻塞原因。
- 关键风险。
- 是否可以生成概要设计。

必须用 `AskUserQuestion` 请求最终通过确认。

如果用户选择“补充/调整”，必须回到对应阶段更新结论和 OpenSpec，再重新校验。

## Step 7：生成极兔概要设计.md

读取：

- PRD Markdown。
- Review/Research/Planning 已确认结论。
- OpenSpec proposal/specs/design/tasks。
- 代码证据。

输出章节：

1. 需求背景。
2. 业务链路。
3. AI Coding 记录。
4. 数据结构。
5. 数据回刷。
6. 接口设计。
7. 性能设计。
8. 容错设计。
9. 灰度设计。
10. 安全设计。
11. 发版信息。
12. 详细设计补充。
13. 测试用例。
14. 待确认事项。

文档要求：

- 不留空章节。
- 不留阻塞待确认项。
- 待确认事项只允许非阻塞项，并说明非阻塞原因、推荐默认方案、后续确认人、变化影响。
- 数据结构必须说明字段、类型、默认值、索引、幂等方案。
- SQL 必须包含 DDL、影响范围、备份、DML、验证、回滚风险。
- 接口必须说明路径、方法、入参、出参、异常、日志、事务、并发控制。
- 涉及生产行为变化必须有灰度开关和回滚方案。
- 涉及权限或敏感数据必须有越权风险和脱敏方案。
- 测试用例必须覆盖正向、边界、异常、回滚、权限、数据一致性。

## 执行检查清单

在每个阶段结束前自检：

- 是否还有会影响最终 TRD 的未确认问题？
- 是否使用 `AskUserQuestion` 一次一个问题收口？
- 是否把“暂列待确认”在最终校验再次询问？
- 是否有代码证据支撑枚举、字段、接口、SQL、路径？
- 是否过早写了 OpenSpec？如果 Review/Research/Planning 未全部通过，则这是错误。
- 是否把 OpenSpec 当作承接产物而不是推动需求？
- 是否在最终文档中留下了阻塞待确认？如果有，必须停止并提问。

## 禁止事项

- 禁止一开始创建 OpenSpec change。
- 禁止在 Review/Research/Planning 未通过前写 proposal/specs/design/tasks。
- 禁止用普通文本代替 `AskUserQuestion`。
- 禁止一次问多个阻塞问题。
- 禁止把影响设计正确性的事项写成“待确认”后继续生成。
- 禁止没有代码证据就断言“无需改造”“自动包含”“无影响”。
- 禁止为了完成文档而跳过用户确认。
- 禁止自动 commit。
