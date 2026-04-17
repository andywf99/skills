# 排障指南

## 1. Model warning

如果看到下面告警：

```text
WARN  i.s.m.p.AbstractSerializableParameter - Illegal DefaultValue null for parameter type integer java.lang.NumberFormatException: For input string: ""
```

按以下顺序处理：

- 检查 `swagger-annotations`、`swagger-models` 是否落在 `1.5.20`。
- 检查 `@ApiModelProperty` 是否缺少 `example`。
- 能升级时，优先升级到 `1.5.21` 以消除该 warning。

## 2. Swagger 地址能打开，但返回的不是预期文档

- 不要先入为主加分组；文档说明默认 `swagger` 配置不需要加 group。
- 先确认是否请求到了错误服务或错误路径。

## 3. 聚合服务访问 Swagger 地址不通

- 检查服务是否注册到 Eureka。
- 检查 `appid` 是否与 Eureka 中的应用名一致；大小写不敏感，但拼写必须正确。
- 检查使用的 `domain` 是否对应正确国家和环境。

## 4. `actuator` 中没有 `swagger` 节点

如果访问 `/actuator` 时看不到类似下面的节点：

```json
{
  "_links": {
    "self": {
      "href": "http://localhost:8080/actuator",
      "templated": false
    },
    "swagger": {
      "href": "http://localhost:8080/actuator/swagger",
      "templated": false
    }
  }
}
```

优先检查：

```properties
management.endpoints.web.exposure.include=mapping,health,prometheus,swagger
swagger.enabled=true
```

如果使用 Apollo，优先检查 `common.bootstrap` 或实际生效的配置空间。

## 5. 聚合访问不到 Swagger，后台还报空指针

按下面顺序排查：

1. 检查项目是否引用 `yl-platform-web-starter-1.1.1-RELEASES.jar`。
   - 如果引用了，这个包里可能自带 `SwaggerConfig`。
   - 此时访问地址可能需要显式加 `group`，例如：

```text
http://demo-jmsph-apidoc-inner.jtexpress.com.cn/swagger/yl-jmsph-report-datacabin?group=平台接口
```

2. 检查是否存在：

```properties
springfox.documentation.auto-startup=false
```

- 如果有，改为 `true`，或直接删除该配置。

## 6. 用 Arthas 协助排查

### 6.1 确认是否引用 `jt-2.9.2`

```text
java -jar /opt/arthas-boot.jar
jad springfox.documentation.swagger2.endpoint.SwaggerEndpoint
```

### 6.2 确认 Swagger 开关是否开启

```text
java -jar /opt/arthas-boot.jar
vmtool -x 3 --action getInstances --className com.yl.common.base.config.SwaggerConfig --express 'instances[0].isEnabled'
```

## 7. 调试说明

- API 管理页在线调试需要先解决跨域问题。
- 原始文档提到需要安装调试插件，但插件下载与安装内容未导出到当前 Markdown；若用户明确需要插件方案，说明该部分原文缺失，并让用户补充附件或截图。