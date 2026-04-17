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
- `@ApiModelProperty` 的 `value`：优先取字段 JavaDoc 或已有 `/** (value = "...") */` 形式说明；没有说明时使用字段名。
- 不要改接口语义、请求路径、参数绑定方式或业务逻辑；只补 Swagger 相关 import 和注解。

### 4. 验证访问链路

- 本地或容器内优先验证 `http://localhost:8070/actuator/swagger`。
- 再验证聚合访问地址：`http://${domain}/swagger/${appid}`。
- 如果用户还需要平台化管理或在线调试，再引导导入 API 管理页面。

### 5. 处理已知特殊情况

- 如果项目依赖 `yl-platform-web-starter-1.1.1-RELEASES.jar`，留意是否需要 `group` 参数。
- 如果存在 `springfox.documentation.auto-startup=false`，改为 `true` 或移除该配置。
- 如果只出现 Model warning，优先检查 `swagger-annotations` / `swagger-models` 版本与注解示例值。

## 输出要求

- 落地改造时，只修改与 Swagger 接入、Swagger 注解补齐直接相关的文件。
- 在结果中说明依赖、配置类、配置项、注解覆盖范围、验证地址分别改了什么。
- 明确给出验证方式：本地地址、聚合地址、是否需要 `group`。
- 如果缺少环境信息，明确列出待业务方补充的值，不要臆造。
- 完成后优先运行 `mvn -q -DskipTests compile` 验证；如果沙箱 Maven 仓库权限受限，按审批流程请求外部执行。
