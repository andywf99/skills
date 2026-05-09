---
name: integrate-jt-swagger
description: 为 Java/Spring Boot 服务按公司内部 jt-swagger 规范集成新版 Swagger 文档，使用 actuator 暴露 `swagger` 端点并支持通过聚合服务或 API 管理页面访问。用于用户提出“接入 swagger”“集成 jt-swagger”“暴露 actuator swagger”“UAT 环境查看 swagger”“导入 API 文档平台”“排查 swagger 地址不通、空指针、Model warning”“给 controller 补 Swagger 注解”“补 @ApiOperation / @ApiModel / @ApiModelProperty”等场景。
---

# JT Swagger 集成

按下面流程执行，优先做最小改动，不要顺手重构无关代码。

## 快速使用

- 先判断当前任务属于哪一类：新增接入、补齐访问地址、补齐 Controller/Model 注解、导入 API 管理平台、排查异常。
- 涉及落地改造时，先阅读 `references/integration-guide.md`。
- 涉及地址不通、空指针、告警或 `actuator/swagger` 未暴露时，阅读 `references/troubleshooting.md`。
- 如果用户没有给出明确环境值，保留待确认项：`spring.application.name`、公共请求头、聚合域名、Apollo 配置所在空间；扫描包默认按规范使用 `com.yl`。

## 标准流程

### 1. 识别当前服务

- 检查是否为 Java/Spring Boot 服务。
- 检查 `pom.xml` 中是否已有 `springfox` 相关依赖。
- 检查是否已有 `SwaggerConfig`、公共 Web Starter、Apollo/bootstrap 配置。
- 检查是否同时存在项目内 `SwaggerConfig` 与公共包 `com.yl.common.base.config.SwaggerConfig` 等旧配置类，提前评估是否会出现同名 Bean 冲突。
- 检查服务名是否已注册到 Eureka；聚合访问依赖应用名。
- 检查目标 controller 包和相关 DTO/VO/Entity 是否已有 `io.swagger.annotations` 注解，避免重复补充。

### 2. 接入 jt-swagger

- 将旧的 `io.springfox:2.9.2` 相关依赖替换为 `jt-2.9.2` 版本。
- 新增或调整 `SwaggerConfig`，至少包含：`swagger.enabled` 开关、`ApiInfo`、扫描包配置、必要的公共 Header。
- `SwaggerConfig` 统一使用以下约定：
  - 扫描包：`RequestHandlerSelectors.basePackage("com.yl")`。
  - 服务名配置：`@Value("${spring.application.name:}")`，冒号后保持空默认值，不臆造应用名。
  - 环境配置：`@Value("${spring.profiles.active:uat}")`，默认值使用小写 `uat`。
  - 公共 Header 可按项目需要补充，常见为 `authToken`、`routeName`。
- 暴露 `actuator` 的 `swagger` 端点，并确认管理端口可访问。

### 3. 补齐 Swagger 注解

当用户要求“给 controller 集成 Swagger / 补 Swagger 注解 / 补接口方法和出入参注解”时，按下面规则执行：

- Controller 类：目标包下每个 `@RestController` / `@Controller` 补 `@Api(tags = "业务名称")`；优先取类 JavaDoc 的业务描述，没有则使用类名去掉 `Controller` 后的名称或用户指定名称。
- Controller 方法：每个对外接口方法补 `@ApiOperation(value = "接口业务描述")`；优先取方法 JavaDoc 首句，没有则使用方法名。实现 Feign 接口的 `@Override` 方法也要补。
- 出入参模型：接口直接或间接涉及的 DTO/VO/Entity 补 `@ApiModel` 和字段级 `@ApiModelProperty`。
- `@ApiModel` 的 `description`：优先取类上的业务注释；如果没有业务注释，直接使用类名本身，不要把类名按大写字母拆成空格。
- `@ApiModelProperty` 的 `value`：字段自身注释优先，按下面顺序取值：
  - 先取字段正上方的 `/** ... */` JavaDoc、`/** (value = "...") */` 形式说明。
  - 再取字段正上方的 `// ...` 单行业务注释。
  - 如果字段自身没有任何业务注释，再进入翻译兜底逻辑。
- 字段翻译兜底逻辑：当字段自身没有可直接复用的中文说明时，先按字段名直译出一个基础中文，再参考项目内相同字段名在相近场景下的既有注释、`@ApiModelProperty`、JavaDoc 叫法做校正；这些历史叫法只能作为参考，不能不看上下文直接复用。
- 同名字段跨类处理时，必须结合当前类名、父类、所在 DTO/VO/Entity 语义、相邻字段、方法入参与出参场景综合判断。同一个字段名在不同类里可能表达不同含义，禁止仅凭字段名做全局唯一映射。
- 翻译时优先遵循项目统一术语，不要机械直译。例如 `networkCode` 已在项目中统一叫“网点编码”，则缺失说明时也必须补成“网点编码”，而不是“网络编码”或其它字面翻译。
- 如果同名字段在项目中存在多个不同注释，说明该字段名本身有多义性；此时不要选出现次数最多的注释直接套用，而要优先回到当前字段所属业务场景判断，必要时宁可采用贴近当前上下文的直接翻译，也不要误复用其它场景的业务名称。
- `id` 字段单独处理：如果字段名精确等于 `id`，则 `@ApiModelProperty` 只允许使用该字段自身的业务注释；如果字段没有业务注释，直接使用 `id`，不要从其它类或字段复用“破损件明细ID”“网点ID”等上下文词。
- `ids` 字段按与 `id` 相同的方式处理：如果字段名精确等于 `ids`，则 `@ApiModelProperty` 只允许使用该字段自身的业务注释；如果字段没有业务注释，直接使用 `ids`，不要把它统一翻译成“所属网点及以下子网点集合”或其它历史场景词。
- 如果批量补 Swagger 注解时遇到历史脏注释，如 `name = "..."`、`value = "..."`、`("...")`、嵌套引号或被拼坏的旧注解，不要原样写回；应以“合法的 Swagger 注解语法 + 清洗后的中文业务描述”重建注解，避免生成无法编译的 Java 代码。
- 不要改接口语义、请求路径、参数绑定方式或业务逻辑；只补 Swagger 相关 import 和注解。

### 4. 验证访问链路

- 本地或容器内优先验证 `http://localhost:8070/actuator/swagger`。
- 再验证聚合访问地址：`http://${domain}/swagger/${appid}`。
- 如果用户还需要平台化管理或在线调试，再引导导入 API 管理页面。

### 5. 处理已知特殊情况

- 如果项目依赖 `yl-platform-web-starter-1.1.1-RELEASES.jar`，留意是否需要 `group` 参数。
- 如果存在 `springfox.documentation.auto-startup=false`，改为 `true` 或移除该配置。
- 如果只出现 Model warning，优先检查 `swagger-annotations` / `swagger-models` 版本与注解示例值。
- 如果启动时报 `swaggerConfig` Bean 冲突，且项目内已有自己的 Swagger 配置类，同时公共包又带了旧的 `SwaggerConfig`，优先在启动类的 `@ComponentScan` 上通过 `excludeFilters` 排除旧配置类；默认不要先删除旧依赖或改大量代码。
- 如果启动时报 `Multiple Dockets with the same group name are not supported`，优先排查是否同时加载了两套 Swagger 配置；通常与上面的旧 `SwaggerConfig` 未排除是同一类问题。
- 如果接入 `jt-swagger` 后出现 `org.mapstruct.NullValuePropertyMappingStrategy`、`MappingConstants` 等 MapStruct 类导包失败，先执行 `mvn dependency:tree "-Dincludes=org.mapstruct:*"` 检查版本来源。重点关注 `io.springfox:springfox-swagger2:jt-2.9.2` 是否传递引入了 `org.mapstruct:mapstruct:1.2.0.Final`。
- 遇到 MapStruct 冲突时，最稳方案是两步同时做：
  - 在 `pom.xml` 中显式锁定 `org.mapstruct:mapstruct` 与 `org.mapstruct:mapstruct-processor` 为项目实际使用的同一版本。
  - 对 `springfox-swagger2` 排除其传递依赖的旧版 `org.mapstruct:mapstruct`，避免旧 API 抢占类路径。
- 不要把 MapStruct 导包失败误判成 Swagger 注解问题；本质通常是 `mapstruct` API 版本被传递依赖覆盖，而项目源码和 processor 版本不一致。

## 输出要求

- 落地改造时，只修改与 Swagger 接入、Swagger 注解补齐直接相关的文件。
- 在结果中说明依赖、配置类、配置项、注解覆盖范围、验证地址分别改了什么。
- 明确给出验证方式：本地地址、聚合地址、是否需要 `group`。
- 如果缺少环境信息，明确列出待业务方补充的值，不要臆造。
- 完成后优先运行 `mvn -q -DskipTests compile` 验证；如果沙箱 Maven 仓库权限受限，按审批流程请求外部执行。

