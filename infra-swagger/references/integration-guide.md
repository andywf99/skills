# 集成指南

## 1. 适用场景

- UAT 环境不能直接使用旧版 Swagger 页面，但仍需要前后端联调。
- 同一团队内接口管理工具不统一，需要统一 Swagger 数据出口。
- 需要把服务文档导入 API 管理平台。

## 2. 方案原理

- 目的：规避旧方案中域名带 `../` 的安全风险。
- 方式：禁用主应用中的 Swagger 直接暴露方式，通过 `actuator` 暴露 `swagger` 端点。
- 端口：文档说明要求通过服务的 `8070` 管理端口暴露。

## 3. 依赖调整

把旧版本 `io.springfox:2.9.2` 替换为 `jt-2.9.2`：

```xml
<!-- 暴露 endpoint 并屏蔽 api-docs 接口 -->
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger2</artifactId>
    <version>jt-2.9.2</version>
</dependency>
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-spring-web</artifactId>
    <version>jt-2.9.2</version>
</dependency>

<!-- 屏蔽 swagger-resources 相关接口 -->
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-swagger-common</artifactId>
    <version>jt-2.9.2</version>
</dependency>
```

## 4. `SwaggerConfig` 参考实现

按项目现有风格新增或调整配置类；至少替换成项目真实包名、服务信息和公共请求头。

```java
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import springfox.documentation.builders.ApiInfoBuilder;
import springfox.documentation.builders.ParameterBuilder;
import springfox.documentation.builders.PathSelectors;
import springfox.documentation.builders.RequestHandlerSelectors;
import springfox.documentation.schema.ModelRef;
import springfox.documentation.service.ApiInfo;
import springfox.documentation.service.Contact;
import springfox.documentation.service.Parameter;
import springfox.documentation.spi.DocumentationType;
import springfox.documentation.spring.web.plugins.Docket;
import springfox.documentation.swagger2.annotations.EnableSwagger2;

import java.util.ArrayList;
import java.util.List;

@Configuration
@EnableSwagger2
public class SwaggerConfig {

    @Value("${spring.application.name:}")
    private String applicationName;

    @Value("${spring.profiles.active:uat}")
    private String profiles;

    @Value("${swagger.enabled:true}")
    private boolean isEnabled;

    @Bean
    public Docket createRestApi() {
        return new Docket(DocumentationType.SWAGGER_2)
                .enable(isEnabled)
                .apiInfo(apiInfo())
                .select()
                .apis(RequestHandlerSelectors.basePackage("com.yl"))
                .paths(PathSelectors.any())
                .build()
                .globalOperationParameters(getParameterList());
    }

    private ApiInfo apiInfo() {
        return new ApiInfoBuilder()
                .title(applicationName)
                .description("Api Document, " + profiles)
                .termsOfServiceUrl("http://www.yl-scm.com/")
                .contact(new Contact("云路科技", "http://www.yl-scm.com", "XXX@yl-scm.com"))
                .version("3.0")
                .build();
    }

    private List<Parameter> getParameterList() {
        List<Parameter> pars = new ArrayList<>();

        ParameterBuilder tokenPar = new ParameterBuilder();
        tokenPar.name("authToken")
                .description("authToken")
                .modelRef(new ModelRef("string"))
                .parameterType("header")
                .required(false);

        ParameterBuilder routeNamePar = new ParameterBuilder();
        routeNamePar.name("routeName")
                .description("routeName")
                .modelRef(new ModelRef("string"))
                .parameterType("header")
                .required(false);

        pars.add(tokenPar.build());
        pars.add(routeNamePar.build());
        return pars;
    }
}
```

## 5. Controller 与模型注解补齐

如果任务要求补 Swagger 注解，按以下规则处理：

- Controller 类补 `@Api(tags = "业务名称")`；优先取类 JavaDoc 业务描述。
- Controller 对外接口方法补 `@ApiOperation(value = "接口业务描述")`；优先取方法 JavaDoc 首句，没有则使用方法名。
- 接口出入参涉及的 DTO/VO/Entity 补 `@ApiModel` 与字段级 `@ApiModelProperty`。
- `@ApiModel.description` 优先取类业务注释；没有业务注释时直接使用类名，不要把类名拆成空格。
- `@ApiModelProperty.value` 优先取字段 JavaDoc 或已有 `/** (value = "...") */`，没有则使用字段名。

## 6. 必要配置项

如果 `actuator` 中没有 `swagger` 节点，优先补齐以下配置：

```properties
management.endpoints.web.exposure.include=mapping,health,prometheus,swagger
swagger.enabled=true
```

本地启动时增加 VM 参数：

```text
-Dmanagement.server.port=8070
```

如果配置放在 Apollo，文档建议优先放在 `common.bootstrap`；若没有该空间，再放入实际使用的配置空间。

## 7. Swagger JSON 获取方式

### 方式一：本地或容器内直连

```text
http://localhost:8070/actuator/swagger
```

适合本地开发，或登录到容器后直接访问。

### 方式二：通过聚合服务访问

```text
http://${domain}/swagger/${appid}
```

- `appid`：Eureka 中注册的应用名称，不区分大小写。
- `domain`：聚合服务所属产品/环境域名。

文档中还给出旧的 Knife4j 页面地址：

```text
http://${ip}/apidoc/${appid}
```

如果两者都存在，优先使用 Swagger JSON 接口地址。

示例：

```text
https://demo-jms-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT
```

## 8. 推荐聚合域名

优先使用域名方式，不通时再看直连 IP。

| 产品 | TEST | UAT | 示例 |
| --- | --- | --- | --- |
| 中国 jms | `http://test-jms-apidoc.jms.com` | `http://demo-jms-apidoc-inner.jtexpress.com.cn` | `http://demo-jms-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 马来 jms | `http://test-jmsmy-apidoc.jms.com` | `http://demo-jmsmy-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsmy-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 印尼 jms | `http://test-jmsidn-apidoc.jms.com` | `http://demo-jmsidn-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsidn-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 埃及 jms | `http://test-jmseg-apidoc.jms.com` | `http://demo-jmseg-apidoc-inner.jtexpress.com.cn` | `http://demo-jmseg-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 沙特 jms | `http://test-jmssa-apidoc.jms.com` | `http://demo-jmssa-apidoc-inner.jtexpress.com.cn` | `http://demo-jmssa-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 墨西哥 jms | `http://test-jmsmx-apidoc.jms.com` | `http://demo-jmsmx-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsmx-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 巴西 jms | `http://test-jmsbr-apidoc.jms.com` | `http://demo-jmsbr-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsbr-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 新加坡 jms | `http://test-jmssg-apidoc.jms.com` | `http://demo-jmssg-apidoc-inner.jtexpress.com.cn` | `http://demo-jmssg-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 泰国 jms | `http://test-jmsth-apidoc.jms.com` | `http://demo-jmsth-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsth-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 菲律宾 jms | `http://test-jmsph-apidoc.jms.com` | `http://demo-jmsph-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsph-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 越南 jms | `http://test-jmsvn-apidoc.jms.com` | `http://demo-jmsvn-apidoc-inner.jtexpress.com.cn` | `http://demo-jmsvn-apidoc-inner.jtexpress.com.cn/swagger/FTEXPORT` |
| 柬埔寨 jms | `http://test-jmscb-apidoc.jms.com` | 无 UAT 域名 | 暂未提供 |
| 美国 JTI | `http://test-jtius-apidoc.jms.com` | `http://demo-jtius-apidoc-inner.jtexpress.com.cn` | 暂无 |
| 中国云毅系统 | `http://test-yms-apidoc.jms.com` | `http://demo-yms-apidoc-inner.jtexpress.com.cn` | `http://demo-yms-apidoc-inner.jtexpress.com.cn/swagger/FINANCIALMANAGEMENT` |
| 极兔国际-落地配 | `http://test-ldp-apidoc.jms.com` | `http://demo-ldp-apidoc-inner.jtexpress.com.cn` | 暂无 |
| 菲律宾驰钧网货平台 | `http://10.24.11.85:31440` | 暂无 | 暂无 |

## 9. 直连 IP 聚合地址

如果域名方式不通，可参考文档中的聚合服务地址：

- 中国 jms：`http://10.21.61.79:31809`
- 马来 jms：`http://10.99.72.106:30662`
- 印尼 jms：`http://10.84.17.207:30880`
- 埃及 jms：`http://10.43.7.181:31333`
- 沙特 jms：`http://10.48.7.158:30478`
- 墨西哥 jms：`http://10.44.7.17:31484`
- 巴西 jms：`http://10.46.7.83:30734`
- 新加坡 jms：`http://10.49.7.151:31009`
- 泰国 jms：`http://10.96.72.54:31297`
- 菲律宾 jms：`http://10.98.72.53:31357`
- 越南 jms：`http://10.97.72.102:32247`

## 10. API 管理页面

访问地址：

```text
https://tc.jtexpress.com.cn/?postApi=%2Fjt-api-doc%2F%23%2Fdoc-list#/portApi/postApi-sub/doc-list
```

使用域账号登录。页面异常时，优先确认本机已安装最新版 Chrome。

支持三种导入方式：

1. Swagger Json 导入
   - 导入 jt-swagger 生成的 Swagger JSON。
   - 也可导入本地生成的 Swagger JSON。
2. Swagger Url 导入
   - 适合固定地址复用。
   - 要确保当前浏览器网络可以访问该 URL。
3. 服务自动识别导入
   - 适合已经按 jt-swagger 规范接入的服务。
   - 可根据服务名自动推断 URL。
