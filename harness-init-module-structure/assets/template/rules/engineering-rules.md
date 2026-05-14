# Engineering Rules / 工程规则

本文件用于约束 Codex/Cursor/Claude Code 等编码代理在 `__MODULE_NAME__` 模块内的工程交付行为。
原则：能在仓库内执行的写成 MUST_DO；需要组织/平台配合的写成 MUST_REPORT。
优先级：如与 `__MODULE_NAME__` 模块的 `AGENTS.md`、`rules/agent-rules.md` 或其他更高优先级约束冲突，以模块内约束为准。

## 规则文件

| 文件 | 适用场景 | 加载方式 |
|---|---|---|
| engineering-rules.md | 工程通用规则（C 系列） | 本模块内按需加载 |
| java-backend-rules.md | Java 后端开发（J 系列） | 预留扩展，`__MODULE_NAME__` 模块当前尚未提供 |

```yaml
meta:
  name: engineering-rules
  version: v1.2.0
  scope: Spring Boot multi-module/multi-service Maven workspace
  sources:
    - engineering-rules (C series)
    - merged-into-current-module
  precedence:
    - module_local_constraints_override_imported_rules
    - security_and_data_safety_first
    - backward_compatibility_default
    - verifiable_and_rollbackable_delivery
    - code_quality_first

rules:
  - id: C001
    category: execution_contract_and_compatibility
    severity: BOTH
    triggers: [any_code_change, refactor, behavior_change, delivery]
    zh:
      title: 执行契约与兼容性
      must_do:
        - 最小化改动，只修改与需求直接相关的文件和逻辑。
        - 默认保持兼容，不破坏既有 API、消息协议、DB 字段语义。
        - 变更必须可验证，补测试或提供可执行验证步骤。
        - 涉及线上行为变化时优先提供开关或兼容写法，保证可回滚。
      must_report:
        - 需要压测、灰度、安全评审、数据回刷等协作项必须列为人工待办。
        - 若存在破坏性变更，必须在交付中显式标注影响与迁移路径。
      checklist:
        - 改动范围受控。
        - 兼容性声明明确。
        - 验证和回滚路径可执行。
    en:
      title: Execution contract and compatibility
      must_do:
        - Keep changes minimal and requirement-scoped.
        - Preserve API/message/schema compatibility by default.
        - Provide tests or executable verification steps.
        - Prefer feature flags or compatible rollout for rollback safety.
      must_report:
        - Report items requiring load test, canary, security review, or backfill.
        - Explicitly report breaking changes and migration path.
      checklist:
        - Scope controlled.
        - Compatibility declared.
        - Verification and rollback are actionable.

  - id: C002
    category: naming_conventions
    severity: MUST_DO
    triggers: [new_project, schema_change, redis_key_change, mq_change, es_change]
    zh:
      title: 命名规范（项目/DB/Redis/MQ/ES）
      must_do:
        - 项目名使用小写加中划线，如 `user-service`。
        - DB 库表字段使用小写加下划线，表名遵循"模块_功能"。
        - Redis Key 使用冒号分隔并保持可读唯一。
        - MQ 命名在仓库内保持一种风格一致（下划线或点分）。
        - ES 索引使用小写下划线，分区场景追加日期后缀。
      must_report: []
      checklist:
        - 命名无歧义、可追踪所属模块。
        - 无临时词、无特殊非法字符。
    en:
      title: Naming conventions (project/DB/Redis/MQ/ES)
      must_do:
        - Use lowercase kebab-case for project names.
        - Use lowercase snake_case for DB schema/table/column names.
        - Use colon-delimited readable Redis keys.
        - Keep one consistent MQ naming style per repository.
        - Use lowercase ES index names with date suffix when partitioned.
      must_report: []
      checklist:
        - Names are unambiguous and traceable.
        - No temporary or illegal symbols.

  - id: C003
    category: logging_exception_security
    severity: BOTH
    triggers: [error_handling_change, observability_change, auth_change, external_input]
    zh:
      title: 日志、异常与安全基线
      must_do:
        - 正确使用日志级别，异常必须记录堆栈。
        - 日志尽量包含 traceId/requestId 与业务主键。
        - 禁止输出敏感信息明文（密码、证件、银行卡、完整地址等）。
        - 外部输入必须校验，权限必须做资源归属校验，防越权。
      must_report:
        - 若现有日志体系缺少关键追踪字段，标记为"建议改进点"。
        - 涉及敏感数据新字段或新链路时，标记"需要安全评审/合规确认"。
      checklist:
        - 错误可定位、日志可追踪。
        - 敏感信息已脱敏。
        - 权限边界明确。
    en:
      title: Logging, exception, and security baseline
      must_do:
        - Use correct log levels and always log exception stack traces.
        - Include trace identifiers and business keys when possible.
        - Never log sensitive plaintext data.
        - Validate external input and enforce ownership-based authorization.
      must_report:
        - Report missing traceability fields in current logging system.
        - Report security/compliance review needs for sensitive data changes.
      checklist:
        - Failures are traceable.
        - Sensitive data is masked.
        - Authorization boundaries are explicit.

  - id: C004
    category: data_design_and_idempotency
    severity: BOTH
    triggers: [ddl_change, index_change, write_api, mq_consumer_change, transaction_change]
    zh:
      title: 数据设计、索引与幂等
      must_do:
        - 结构变更需提供 DDL（类型、长度上限、默认值、注释、索引）。
        - 高频查询条件必须有索引，组合索引满足最左前缀。
        - 写入类场景必须有幂等方案（唯一索引、乐观锁、幂等键或去重机制）。
        - 多表写操作必须纳入事务，并提供回滚验证方式。
      must_report:
        - 无法使用唯一索引时，必须说明原因与替代方案。
      checklist:
        - 字段长度上限有业务依据。
        - 索引与查询模式匹配。
        - 幂等与事务行为可验证。
    en:
      title: Data design, index, and idempotency
      must_do:
        - Provide DDL details for schema changes.
        - Ensure indexes for high-frequency query predicates.
        - Define idempotency for all retryable writes.
        - Use transactions for multi-table writes and verify rollback.
      must_report:
        - Report reason and fallback when unique index is not feasible.
      checklist:
        - Field length bounds are justified.
        - Indexes align with query patterns.
        - Idempotency and rollback are testable.

  - id: C005
    category: backfill_replay_and_fault_tolerance
    severity: BOTH
    triggers: [data_backfill, replay_job, batch_job, async_job]
    zh:
      title: 回刷重放与容错
      must_do:
        - 回刷/重放实现需可重跑，并支持分批、断点续跑、限速。
        - 输出统计日志（成功/失败/跳过/耗时）。
        - 异步/JOB 必须 try-catch，单条失败可跳过且记录明细。
      must_report:
        - 输出影响范围评估（对象、数据量、执行窗口、回滚/重跑策略）。
        - 无告警通道时，标记"需要接入告警/监控"的待办。
      checklist:
        - 任务不会因单条异常阻塞全批。
        - 失败可追溯、可补偿。
    en:
      title: Backfill/replay and fault tolerance
      must_do:
        - Make backfill/replay rerunnable with batching, checkpoint, and rate limit.
        - Emit structured stats logs for success/failure/skip/time.
        - Catch errors in async jobs and skip-record per-item failures.
      must_report:
        - Report impact scope, volume, execution window, and rollback/retry strategy.
        - Report alerting/monitoring integration TODO when channel is missing.
      checklist:
        - Single-record failure does not block full batch.
        - Failures are traceable and compensatable.

  - id: C006
    category: api_concurrency_transaction_audit
    severity: BOTH
    triggers: [api_add, api_change, contract_change, mq_ordering_issue]
    zh:
      title: API 设计、并发控制、事务与留痕
      must_do:
        - 新增/变更接口补齐最小文档（URL、方法、入参、出参、错误码、示例、幂等约定）。
        - 写接口必须显式并发方案（乐观锁/悲观锁/分布式锁）。
        - MQ 场景考虑重复投递与乱序（去重、幂等、状态机校验）。
        - 关键分支和状态流转输出 INFO 留痕日志。
      must_report:
        - 对跨服务契约变化给出兼容期与下线计划。
      checklist:
        - 接口行为和错误语义明确。
        - 并发冲突处理可复现验证。
        - 关键决策链路可审计。
    en:
      title: API, concurrency, transaction, and auditability
      must_do:
        - Add minimal API docs for new/changed endpoints.
        - Define explicit concurrency control for write APIs.
        - Handle MQ duplicate/out-of-order delivery explicitly.
        - Keep INFO audit logs for key state transitions.
      must_report:
        - Report compatibility window and deprecation plan for contract changes.
      checklist:
        - API/error semantics are explicit.
        - Concurrency handling is reproducible.
        - Decision path is auditable.

  - id: C007
    category: performance_and_capacity
    severity: BOTH
    triggers: [query_change, hot_path_change, cache_change, external_api_change]
    zh:
      title: 性能与容量约束
      must_do:
        - 避免 N+1、无索引全表扫、无界集合加载、无界缓存。
        - 批处理采用分页或流式处理。
        - 新查询需提供示例 SQL 与索引建议。
      must_report:
        - 输出压测与容量待确认项（QPS、P95/P99、资源上限）。
        - 对外/外域接口说明是否需要限流（如 Sentinel）。
      checklist:
        - 关键路径有性能风险说明。
        - 容量假设明确并可人工跟进。
    en:
      title: Performance and capacity
      must_do:
        - Avoid N+1, full scans without index, and unbounded loads/caches.
        - Use pagination or streaming for batch processing.
        - Provide sample SQL and index suggestions for new queries.
      must_report:
        - Report load-test/capacity TODOs (QPS, P95/P99, resource limits).
        - Report whether rate limiting is required for external-facing calls.
      checklist:
        - Hot-path risks are documented.
        - Capacity assumptions are explicit.

  - id: C008
    category: gray_release_rollback_and_mandatory_change_notes
    severity: BOTH
    triggers: [prod_release, config_change, db_change, job_change, dependency_change]
    zh:
      title: 灰度回滚与强制变更说明
      must_do:
        - 行为变化优先提供开关点，并说明默认值与生效范围。
        - DB 变更遵循"先加后用再清理"，避免不可逆改动。
        - 触发强制项时必须输出变更清单：对象、摘要、兼容性、上线步骤、回滚方案、验证方式。
      must_report:
        - 输出灰度观察指标清单（错误率、超时率、成功率、DB/ES 压力）。
        - 以下对象变更需明确人工执行项：MySQL/mADB/ES/ORACLE/鲲鹏SQL、Apollo、XXL-JOB、依赖服务（HTTP/RPC/MQ/第三方）。
      checklist:
        - 灰度路径和回滚路径清晰。
        - 变更清单完整且可执行。
    en:
      title: Gray release, rollback, and mandatory change notes
      must_do:
        - Prefer feature flags for behavior changes with clear default/scope.
        - Follow expand-migrate-cleanup for DB changes.
        - Produce mandatory change notes when trigger systems are touched.
      must_report:
        - Report canary watch metrics and manual execution checklist.
        - Report manual follow-ups for DB/config/job/dependency platform changes.
      checklist:
        - Rollout and rollback paths are explicit.
        - Change notes are complete and actionable.

  - id: C009
    category: sql_change_and_report_requirements
    severity: BOTH
    triggers: [sql_add, sql_modify, report_sql_change, db_change]
    zh:
      title: SQL 变更与 Report SQL 提交要求
      must_do:
        - 新增 SQL 必须提供完整、可执行的变更语句（含对象名、字段定义、索引、注释）。
        - report 相关 SQL 变更必须单独列出变更前后语句或等价 diff，保证可审阅。
        - SQL语句需满足生产执行安全要求，避免出现锁表变更语句。
        - 涉及大表或核心链路时，必须采用低风险策略（分批、限流、在线 DDL 或等价方案）。
      must_report:
        - 报告变更影响范围（库表、数据量级、锁风险、耗时预估）与发布顺序。
        - 若无法提供标准回滚脚本，必须报告原因及人工应急处置步骤。
      checklist:
        - SQL 变更语句完整且可直接执行。
        - report SQL 变更可追溯、可审计。
        - 生产发布、回滚、验证路径清晰。
    en:
      title: SQL changes and report SQL submission requirements
      must_do:
        - Provide complete executable SQL migration statements for new SQL.
        - List report SQL changes explicitly with before/after statements or equivalent diff.
        - SQL statements must meet production execution safety requirements and avoid table-locking change statements.
        - Use low-risk strategy for large tables or critical paths (batching, throttling, online DDL, or equivalent).
      must_report:
        - Report impact scope (schema objects, data volume, lock risk, time estimate) and rollout order.
        - If standard rollback script is unavailable, report reason and manual emergency procedure.
      checklist:
        - SQL migration statements are complete and directly executable.
        - Report SQL changes are traceable and auditable.
        - Production rollout, rollback, and verification paths are explicit.

  - id: C010
    category: logging
    severity: MUST_DO
    triggers: [new_logging, log_level_change, code_review]
    zh:
      title: Java 日志规约
      must_do:
        - 依赖 SLF4J 的 API，不直接使用日志系统（Log4j、Logback）的 API。
        - 所有日志文件至少保存 15 天；敏感操作日志留存不少于 6 个月。
        - 日志输出时，字符串变量之间的拼接使用占位符方式。
        - trace/debug/info 级别的日志输出，必须先做日志级别开关判断。
        - 避免重复打印日志，在 log4j.xml 中设置 additivity=false。
        - 异常日志必须包含案发现场信息和异常堆栈信息。
        - 生产环境禁止输出 debug 日志，有选择地输出 info 日志。
        - 用户输入参数错误的场景用 warn 日志级别，非必要不使用 error 级别。
      must_report:
        - 若现有日志体系缺少 traceId/requestId，标记为建议改进点。
      checklist:
        - 使用 SLF4J。
        - 占位符拼接。
        - 日志级别正确。
        - 异常堆栈完整。
    en:
      title: Java logging conventions
      must_do:
        - Use SLF4J API, not Log4j/Logback directly.
        - Keep logs for at least 15 days; sensitive operation logs for 6+ months.
        - Use placeholders for string concatenation in logs.
        - Check log level before trace/debug/info output.
        - Avoid duplicate logging; set additivity=false in log4j.xml.
        - Exception logs must include context and stack trace.
        - No debug logs in production; selective info logs.
        - Use warn for user input errors; use error sparingly.
      must_report:
        - Report if current logging lacks traceId/requestId.
      checklist:
        - Using SLF4J.
        - Placeholder concatenation.
        - Correct log level.
        - Complete exception stack.

  - id: C011
    category: security
    severity: MUST_DO
    triggers: [auth_change, data_access, external_input, api_change]
    zh:
      title: Java 安全规约
      must_do:
        - 隶属于用户个人的页面或功能，必须进行权限控制校验，防止水平权限越权。
        - 用户敏感数据禁止直接展示，必须做脱敏处理。
        - 用户输入的 SQL 参数严格使用参数绑定，禁止字符串拼接 SQL 语句。
        - 用户请求传入的任何参数必须做有效性验证。
        - 禁止向 HTML 页面输出未经安全过滤或未正确转义的用户数据。
        - 表单、AJAX 提交必须执行 CSRF 安全验证。
        - 使用短信、邮件、支付等平台资源时，必须实现正确的防重放机制。
        - 用户生成内容（UGC）场景必须实现防刷、违禁词过滤等风控策略。
        - 数据库递增 id 使用分布式 id，防止 id 遍历越权。
      must_report:
        - 涉及敏感数据新字段时，报告需要安全评审/合规确认。
        - 跨模块数据访问时，报告越权风险评估。
      checklist:
        - 权限校验完整。
        - 敏感数据脱敏。
        - SQL 参数绑定。
        - 参数有效性验证。
        - CSRF 验证。
    en:
      title: Java security conventions
      must_do:
        - Enforce permission control for user-specific pages/features to prevent horizontal privilege escalation.
        - Mask sensitive user data; never display in plaintext.
        - Use parameter binding for SQL; no string concatenation.
        - Validate all user input parameters.
        - Sanitize user data before output to HTML.
        - Implement CSRF validation for form/AJAX submissions.
        - Implement anti-replay for SMS/email/payment resources.
        - Implement rate limiting and content filtering for UGC.
        - Use distributed IDs instead of auto-increment to prevent ID enumeration.
      must_report:
        - Report security/compliance review needed for new sensitive data fields.
        - Report privilege escalation risk assessment for cross-module data access.
      checklist:
        - Permission check complete.
        - Sensitive data masked.
        - SQL parameter binding.
        - Parameter validation.
        - CSRF validation.

  - id: C012
    category: platform_integration
    severity: BOTH
    triggers: [new_integration, external_api, third_party_service]
    zh:
      title: Java 平台对接规范
      must_do:
        - 确认 IP 是否需加白名单。
        - 确认验签逻辑，双方验签失败需告警感知。
        - 确认参数长度，保证平台数据可以落库。
        - 确认平台文件是否需要转存，及需向平台告知文件有效期。
        - 确认双方 QPS 要求及批次限制。
        - 确认异常码是否需兼容。
        - 确认对方是否会重试、我方是否会补推。
        - 确认是否有唯一约束保证幂等性。
      must_report:
        - 输出平台对接清单与风险点。
        - 报告需要协调的平台配置项。
      checklist:
        - IP 白名单确认。
        - 验签逻辑完整。
        - 幂等性保证。
        - QPS 限制明确。
    en:
      title: Java platform integration
      must_do:
        - Confirm if IP whitelist is needed.
        - Confirm signature verification logic; alert on verification failure.
        - Confirm parameter length limits for database storage.
        - Confirm if platform files need to be transferred and file expiration.
        - Confirm QPS requirements and batch limits on both sides.
        - Confirm if error codes need compatibility.
        - Confirm if retry is enabled on either side.
        - Confirm unique constraint for idempotency.
      must_report:
        - Output platform integration checklist and risks.
        - Report platform configuration items requiring coordination.
      checklist:
        - IP whitelist confirmed.
        - Signature verification complete.
        - Idempotency guaranteed.
        - QPS limits clear.

completion_output_template:
  zh:
    title: 交付说明
    sections:
      - What changed（变更点）
      - Files touched（涉及文件）
      - Rules applied（应用的规则 ID）
      - How to test（测试命令/验证点）
      - Risks & rollback（风险与回滚）
      - MUST REPORT checklist（需要人工/平台跟进的事项）
  en:
    title: Delivery Notes
    sections:
      - What changed
      - Files touched
      - Rules applied
      - How to test
      - Risks and rollback
      - MUST REPORT checklist
```

## 按需加载规则

如后续补充 `rules/java-backend-rules.md`，Java 后端项目可在项目根目录创建 `CLAUDE.md` 并按下面方式引入：

```markdown
# Java Backend Project

## 规则引入
@./rules/java-backend-rules.md
```

