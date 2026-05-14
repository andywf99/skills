---
name: doc-jt-spec-v2
description: 将 PRD 转换为极兔概要设计文档的新版流程。先用 superpowers 式对话逐项收口 Review/Research/Pseudocode/Planning 的所有设计影响问题，再把已确认结论落到 OpenSpec proposal/specs/design/tasks，最后生成概要设计.md。适用于用户要求生成 TRD、概要设计、技术方案，或提供 PRD 文档路径时，尤其适合业务口径多、接口/DDL/灰度/权限需要逐项确认的需求。
---

# JT Spec V2

## 工作目录与输出目录

当前会话的代码工作目录为 `{{WORKING_DIRECTORY}}`，用于扫描代码、运行命令、读取项目结构和定位真实文件路径。

文档输出目录为 `{{OUTPUT_DIRECTORY}}`，必须位于项目主目录的 `docs/demand` 下新建的独立需求文件夹中。所有由本 skill 生成、复制、转换或维护的文档产物都必须写入 `{{OUTPUT_DIRECTORY}}`，不要散落到 `{{WORKING_DIRECTORY}}`、临时目录或仓库根目录。

输出目录命名规则：

- 如果用户提供 PRD 文件路径，默认使用 PRD 文件名去掉扩展名作为目录名。
- 如果用户未提供 PRD 文件路径，默认使用需求标题、用户给出的 change-id 或简短需求名作为目录名。
- 目录名应去除 Windows 不支持的路径字符，并避免过长。
- 示例：`<项目主目录>/docs/demand/<需求名称>/`。

`{{WORKING_DIRECTORY}}` 与 `{{OUTPUT_DIRECTORY}}` 的职责必须分离：

- 代码扫描、编译、测试、OpenSpec CLI 执行上下文默认基于 `{{WORKING_DIRECTORY}}`。
- PRD Markdown、阶段文件、OpenSpec 产物、概要设计文档必须基于 `{{OUTPUT_DIRECTORY}}`。
- OpenSpec change 可以存放在 `{{OUTPUT_DIRECTORY}}/openspec/changes/<change-id>/`，不要默认写入代码仓库根目录的 `openspec/`，除非用户明确要求使用仓库现有 OpenSpec 目录。

## 设计目标

`doc-jt-spec-v2` 的主导流程是 **superpowers 式对话收口**，OpenSpec 只是承接和校验已确认结论的结构化产物。

核心原则：

1. **先问清楚，再写 OpenSpec。** Review、Research、Pseudocode、Planning 阶段可以生成阶段文件方便 CLI 查看完整内容，但不创建 OpenSpec 产物，直到该阶段所有设计影响问题逐项收口。
2. **阶段文件服务对话，不替代确认。** `review.md`、`research.md`、`pseudocode.md`、`plan.md` 只是阶段草稿/快照；用户不需要打开文件确认，阶段通过仍必须在聊天中用 `AskUserQuestion` 完成。
3. **伪代码是实现桥梁。** `pseudocode.md` 必须把已确认需求、代码证据、接口契约、数据落点、异常口径、灰度回滚、测试场景转换成接近代码实现的流程描述，供 Planning、OpenSpec tasks 和最终概要设计复用。
4. **OpenSpec 不驱动需求。** OpenSpec 只记录已经确认的 Why / What / SHALL / Design / Tasks，不把未确认问题推进成文档结论。
5. **待确认默认阻塞。** 会影响业务行为、接口契约、DDL/DML、回刷、灰度、权限、安全、事务、外部依赖、测试验收的事项，必须通过 `AskUserQuestion` 逐项确认。
6. **一次只问一个问题。** 每个问题都用 `AskUserQuestion`，提供 2-4 个业务选项，第一个选项是推荐项并标注“推荐”。
7. **最终 TRD 不偷懒。** 只有真正不影响最终设计正确性的外部事项，才允许留为“待确认”，并必须写明非阻塞原因。

## AskUserQuestion 使用规则

凡是以下事项未确认，必须调用 `AskUserQuestion`；如果当前运行模式或宿主环境没有暴露 `AskUserQuestion`/`request_user_input` 工具，则用普通聊天提出一个简短问题替代，但仍必须遵守“一次只问一个问题”和“先收口再落文档”的原则。

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
{{OUTPUT_DIRECTORY}}/
├── assets/
├── 需求文档.docx
├── 需求文档.md
├── stage/
│   ├── review.md
│   ├── research.md
│   ├── pseudocode.md
│   └── plan.md
├── openspec/
│   └── changes/<change-id>/
│       ├── proposal.md
│       ├── specs/**/spec.md
│       ├── design.md
│       └── tasks.md
└── 概要设计.md
```

## Step 0：准备输出目录与 PRD Markdown

1. 根据用户提供的 PRD 路径、需求标题或当前任务名确定 `{{OUTPUT_DIRECTORY}}`。
2. 创建 `{{OUTPUT_DIRECTORY}}`、`{{OUTPUT_DIRECTORY}}/assets`、`{{OUTPUT_DIRECTORY}}/stage`。
3. 如果用户提供 `.docx` 或 `.doc` 路径，将原始文件复制到 `{{OUTPUT_DIRECTORY}}/需求文档.docx`。
4. 如果用户未提供 PRD 文件，检查 `{{OUTPUT_DIRECTORY}}` 下是否存在 `需求文档.docx`、`需求文档.doc` 或 `需求文档.md`。
5. 如果仍未找到 PRD，停止流程并询问用户提供 PRD 文件路径或 Markdown 内容。
6. 如果存在 Word 文档，转换为 Markdown：

```bash
scripts/word2md.bat "{{OUTPUT_DIRECTORY}}/需求文档.docx" "{{OUTPUT_DIRECTORY}}/需求文档.md"
```

7. 检查图片、表格、列表是否基本可读。
8. 后续优先读取 `{{OUTPUT_DIRECTORY}}/需求文档.md`。

不要在 Step 0 创建 OpenSpec change。

## 阶段文件规则

大需求需要阶段文件承载完整上下文，避免 CLI 对话摘要过长或信息丢失。

必须生成：

- `{{OUTPUT_DIRECTORY}}/stage/review.md`：Review 阶段完整评审快照。
- `{{OUTPUT_DIRECTORY}}/stage/research.md`：Research 阶段完整代码证据和影响面。
- `{{OUTPUT_DIRECTORY}}/stage/pseudocode.md`：Pseudocode 阶段完整伪代码、规则流、异常流、文件级改造草案和测试伪代码。
- `{{OUTPUT_DIRECTORY}}/stage/plan.md`：Planning 阶段完整方案、SQL、任务拆解。

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
2. 快速查看项目结构、README/CLAUDE/AGENTS、核心 Controller/Service/Entity/DTO/VO/Mapper。
3. 写入或更新 `{{OUTPUT_DIRECTORY}}/stage/review.md`，完整记录：
   - 业务目标。
   - 需求范围。
   - 明确规则。
   - 矛盾、缺失、不清楚的信息。
   - 数据、接口、权限、性能、安全、灰度、回刷风险。
   - 阻塞问题清单。
   - 已收口问题清单。
4. 在聊天中只输出 Review 简短摘要、`{{OUTPUT_DIRECTORY}}/stage/review.md` 路径、当前要确认的一个阻塞问题。
5. 对阻塞问题逐项 `AskUserQuestion`。
6. 每个回答后更新 Review 结论并回写 `{{OUTPUT_DIRECTORY}}/stage/review.md`。
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

`{{OUTPUT_DIRECTORY}}/stage/research.md` 必须完整记录：

- 功能点拆解。
- 影响接口和间接链路。
- 数据模型、枚举值、状态值、回刷范围。
- 缓存、ES、导出、短信、审核、权限、安全影响面。
- 代码证据清单，带文件路径和行号。
- 阻塞待确认清单。
- 已收口问题清单。
- 非阻塞待确认草稿及非阻塞原因。

聊天中只输出 Research 简短摘要、`{{OUTPUT_DIRECTORY}}/stage/research.md` 路径、当前要确认的一个阻塞问题。

Research 阶段门禁：

1. 阻塞待确认逐项 `AskUserQuestion`。
2. 用户回答后更新 Research 结论并回写 `{{OUTPUT_DIRECTORY}}/stage/research.md`。
3. 不能用“后续待确认”跳过接口契约、字段落点、枚举、SQL、灰度、权限、安全等问题。
4. 所有阻塞问题收口后，输出“已收口问题清单”。
5. 如仍有非阻塞待确认，逐项说明为什么非阻塞。
6. 用 `AskUserQuestion` 请求 Research 通过确认。

Research 通过前禁止：

- 禁止创建或完善 OpenSpec specs/design。
- 禁止生成概要设计。

## Step 2.5：生成详细伪代码（pseudocode.md，不写 OpenSpec）

目标：在 Research 已经有代码证据后，把“需求要改什么”和“代码应该怎么改”转换成可执行、可审查、可复用的伪代码。伪代码必须保持通用，不写入某个具体需求的固定业务口径；每次执行时根据当次 PRD 和代码证据生成。

`{{OUTPUT_DIRECTORY}}/stage/pseudocode.md` 必须尽量覆盖以下维度；如果某一维度不适用，必须写“不适用”并说明原因，不能直接省略。

1. **入口维度伪代码**
   - Controller、Facade、Job、MQ Consumer、定时任务、导入导出、回调接口等所有可能入口。
   - 每个入口写明触发条件、关键入参、鉴权/数据范围、调用链、返回/异常口径。
   - 如果同一需求有多个入口，分别写伪代码，不要合并成模糊描述。

2. **业务规则伪代码**
   - 主流程、分支流程、边界条件、互斥条件、优先级、短路返回、默认值处理。
   - 校验规则要写到字段级、状态级、枚举级，不只写“增加校验”。
   - 对既有规则的新增、绕过、替换、顺序调整必须单独标注。

3. **数据字段映射伪代码**
   - DTO/VO/BO/Entity/DO/ES Document/Excel VO 等对象之间的字段流转。
   - 新增字段、复用字段、派生字段、默认值、空值、历史数据兼容。
   - 写明字段来源和最终落点，不能只写“字段透传”。

4. **持久化与查询伪代码**
   - Mapper/XML/Repository 查询条件、插入、更新、批量处理、分页、排序。
   - DDL/DML/ES mapping/回刷/备份/验证/回滚相关伪代码。
   - 如果不涉及数据结构变更，也要写明“不涉及”以及依据。

5. **外部依赖伪代码**
   - Feign/RPC/HTTP/消息/缓存/第三方系统调用。
   - 请求参数、返回字段、超时、重试、降级、fallback、幂等键、日志。
   - 外部依赖异常时的业务口径必须明确：拦截、放行、重试、补偿或人工处理。

6. **异常、降级与补偿伪代码**
   - 参数异常、业务异常、依赖异常、数据库异常、部分成功、重复请求、并发冲突。
   - 失败后是否回滚、是否继续、是否告警、是否记录操作日志。
   - 对用户可见错误码/错误文案/接口响应结构要给出伪代码级描述。

7. **灰度、开关与回滚伪代码**
   - 开关 key、默认值、命中条件、关闭后行为、灰度范围。
   - 新旧逻辑切换点，回滚后是否需要兼容已产生数据。
   - 涉及生产行为变化时必须写；不涉及时说明原因。

8. **事务、并发与幂等伪代码**
   - 事务边界、锁粒度、唯一约束、幂等键、重复提交处理。
   - 异步链路和多系统链路要写明最终一致性方案。
   - 如果沿用既有事务机制，需要引用代码证据。

9. **文件级改造伪代码**
   - 按真实文件路径列出每个文件预期新增/修改的方法、类、字段或配置。
   - 每个文件下写“修改前关键行为”和“修改后伪代码”。
   - 找不到真实路径时写“待定位”，不要猜测路径。

10. **测试伪代码**
    - 单元测试、集成测试、接口测试、SQL 验证、灰度开关验证、回滚验证。
    - 覆盖正向、边界、异常、权限、并发、历史数据兼容、外部依赖失败。
    - 每个测试场景写 Given/When/Then 或等价结构。

`pseudocode.md` 建议结构：

```text
# 详细伪代码

## 1. 输入依据
## 2. 总体调用链伪代码
## 3. 入口维度伪代码
## 4. 业务规则伪代码
## 5. 数据字段映射伪代码
## 6. 持久化与查询伪代码
## 7. 外部依赖伪代码
## 8. 异常、降级与补偿伪代码
## 9. 灰度、开关与回滚伪代码
## 10. 事务、并发与幂等伪代码
## 11. 文件级改造伪代码
## 12. 测试伪代码
## 13. 不适用项说明
## 14. 待确认项
```

伪代码阶段门禁：

1. 只能基于已确认的 Review/Research 结论和真实代码证据生成。
2. 伪代码中出现的新字段、新接口、新枚举、新开关、新异常口径，如果尚未确认，必须列入阻塞待确认并逐项提问。
3. 伪代码通过后，必须回写 `{{OUTPUT_DIRECTORY}}/stage/pseudocode.md` 的已确认版本。
4. 用 `AskUserQuestion` 请求 Pseudocode 阶段通过确认。

## Step 3：Superpowers Planning（对话确认 + plan.md，不写 OpenSpec）

目标：基于 `research.md` 和 `pseudocode.md` 确认技术方案、SQL、接口、灰度、回滚、任务拆解。

`{{OUTPUT_DIRECTORY}}/stage/plan.md` 必须完整记录：

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
- 由 `pseudocode.md` 推导出的实施任务拆解草案。
- 阻塞待确认清单。
- 已收口问题清单。

聊天中只输出 Planning 简短摘要、`{{OUTPUT_DIRECTORY}}/stage/plan.md` 路径、当前要确认的一个阻塞问题。

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

Planning 通过前必须输出并回写 `{{OUTPUT_DIRECTORY}}/stage/plan.md`：

- 已收口问题清单。
- 剩余非阻塞待确认清单及非阻塞原因。
- 最终推荐方案摘要。

Planning 通过确认必须用 `AskUserQuestion`。

## Step 4：一次性生成 OpenSpec 产物

只有 Review、Research、Pseudocode、Planning 全部通过后，才创建 OpenSpec change。

OpenSpec 产物路径：

```text
{{OUTPUT_DIRECTORY}}/openspec/changes/<change-id>/
```

执行 OpenSpec CLI 时，优先在 `{{OUTPUT_DIRECTORY}}/openspec` 或该目录的父目录中执行；如果 CLI 只支持仓库级 OpenSpec，则先生成到临时/仓库级目录，再复制最终产物到 `{{OUTPUT_DIRECTORY}}/openspec/changes/<change-id>/`，并在最终说明中写明实际校验位置。

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

必须同时包含“最终修改伪代码”和“详细执行任务”两部分：

- 使用 `- [ ]` checkbox 编写可执行任务。
- 文件路径必须来自真实代码搜索结果。
- 找不到路径写“待定位”，不要猜测。
- 每个任务应能映射到 `pseudocode.md` 中的一个或多个伪代码块。
- 每个任务尽量包含修改文件、修改点、验收方式。
- 涉及 SQL、ES、缓存、消息、导出、回刷、灰度、权限、外部依赖时，必须单独列任务。

`tasks.md` 建议结构：

```text
# Tasks

## 1. 最终修改伪代码

### 1.1 总体调用链
### 1.2 入口与校验
### 1.3 数据落点与查询
### 1.4 外部依赖与异常降级
### 1.5 灰度、回滚、幂等
### 1.6 测试伪代码

## 2. 详细执行任务

- [ ] 1. 修改 <真实文件路径>：<具体改造点>；验收：<验证方式>
- [ ] 2. 修改 <真实文件路径>：<具体改造点>；验收：<验证方式>
- [ ] 3. 补充测试 <真实文件路径或待定位>：<测试场景>；验收：<执行命令或断言>

## 3. 发布与回滚任务

- [ ] 配置灰度开关/回滚开关：<key、默认值、关闭后行为>
- [ ] 执行 SQL/ES/回刷/缓存处理：<如不涉及则写不涉及及依据>
- [ ] 验证生产行为：<验证口径>
```

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
- tasks 是否包含最终修改伪代码和详细执行任务。
- tasks 中的执行任务是否能映射回 `pseudocode.md`。
- 枚举、状态、接口路径、类名、字段名是否有代码证据。
- SQL 是否引用真实枚举值。
- tasks 文件路径是否来自真实搜索结果。

如果发现阻塞问题：

1. 暂停生成概要设计。
2. 用 `AskUserQuestion` 逐项确认。
3. 回写阶段文件和 OpenSpec。
4. 重新校验。

## Step 6：最终对话校验

目标：生成 `概要设计.md` 前最后一次 superpowers 式收口。

必须输出最终确认摘要：

- 推荐方案。
- 已收口问题清单。
- 剩余非阻塞待确认清单及非阻塞原因。
- 关键风险。
- 最终伪代码摘要。
- 是否可以生成概要设计。

必须用 `AskUserQuestion` 请求最终通过确认。

如果用户选择“补充/调整”，必须回到对应阶段更新结论、伪代码和 OpenSpec，再重新校验。

## Step 7：生成极兔概要设计.md

读取：

- PRD Markdown。
- Review/Research/Pseudocode/Planning 已确认结论。
- OpenSpec proposal/specs/design/tasks。
- 代码证据。

输出到：

```text
{{OUTPUT_DIRECTORY}}/概要设计.md
```

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
13. 关键伪代码。
14. 测试用例。
15. 待确认事项。

文档要求：

- 不留空章节。
- 不留阻塞待确认项。
- 待确认事项只允许非阻塞项，并说明非阻塞原因、推荐默认方案、后续确认人、变化影响。
- 数据结构必须说明字段、类型、默认值、索引、幂等方案。
- SQL 必须包含 DDL、影响范围、备份、DML、验证、回滚风险。
- 接口必须说明路径、方法、入参、出参、异常、日志、事务、并发控制。
- 涉及生产行为变化必须有灰度开关和回滚方案。
- 涉及权限或敏感数据必须有越权风险和脱敏方案。
- 关键伪代码必须来自 `{{OUTPUT_DIRECTORY}}/stage/pseudocode.md` 和 OpenSpec `tasks.md`，不能临时重新编造。
- 测试用例必须覆盖正向、边界、异常、回滚、权限、数据一致性。

## 执行检查清单

在每个阶段结束前自检：

- 是否所有生成文件都写入 `{{OUTPUT_DIRECTORY}}`？
- 是否还有会影响最终 TRD 的未确认问题？
- 是否使用 `AskUserQuestion` 一次一个问题收口？
- 是否把“暂列待确认”在最终校验再次询问？
- 是否有代码证据支撑枚举、字段、接口、SQL、路径？
- 是否已生成并确认 `pseudocode.md`？
- 是否过早写了 OpenSpec？如果 Review/Research/Pseudocode/Planning 未全部通过，则这是错误。
- 是否把 OpenSpec 当作承接产物而不是推动需求？
- 是否在 tasks.md 中包含最终修改伪代码和详细执行任务？
- 是否在最终文档中留下了阻塞待确认？如果有，必须停止并提问。

## 禁止事项

- 禁止把本次或历史具体需求的业务口径写死到模板中。
- 禁止一开始创建 OpenSpec change。
- 禁止在 Review/Research/Pseudocode/Planning 未通过前写 proposal/specs/design/tasks。
- 禁止用普通文本代替可用的 `AskUserQuestion`。
- 禁止一次问多个阻塞问题。
- 禁止把影响设计正确性的事项写成“待确认”后继续生成。
- 禁止没有代码证据就断言“无需改造”“自动包含”“无影响”。
- 禁止为了完成文档而跳过用户确认。
- 禁止将生成产物散落在 `{{WORKING_DIRECTORY}}` 或临时目录。
- 禁止自动 commit。
