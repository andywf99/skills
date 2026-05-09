---
name: gray-switch-clean
description: 清理 Java/Spring Boot 项目中的灰度开关旧代码，适用于下线 @Gray、GrayUtils.isGray、GrayUtils.execute、GraySwitch.of、MyBatis XML 灰度分支、旧方法和相关测试代码。执行前必须要求用户提供生产 Apollo 中 namespace 为 gray-switch 的配置内容；该 namespace 内存在的配置 key 一律不能清理。同时必须检查 git 提交记录，最近一个月内仍有提交记录的灰度开关一律不能清理。
---

# 灰度开关清理

## 硬性规则

执行任何代码删除前，必须同时满足以下条件：

1. 用户已提供生产 Apollo 的 `gray-switch` namespace 配置内容。
2. 待清理的灰度 key 不存在于生产 Apollo `gray-switch` namespace 配置中。
3. 待清理的灰度 key 及其相关灰度代码最近一个月内没有提交记录。
4. 用户确认扫描清单和清理范围。

任一条件不满足时，不清理对应灰度代码。无法判断时按“不清理”处理。

## 必要输入

开始前先收集：

- 项目路径或当前仓库根目录。
- 清理范围：模块、类、方法、灰度 key，或“扫描全项目”。
- 生产 Apollo `namespace=gray-switch` 的配置内容。

Apollo 配置可接受 `.properties`、YAML、JSON、表格复制文本或 key 列表。只要某个 key 出现在生产 `gray-switch` namespace 中，就加入保护名单，不允许清理。不要因为值是 `true`、`false`、空值或条件表达式而放行。

如果用户没有提供生产 Apollo 配置，先停止并询问：

```text
请先提供生产 Apollo 中 namespace=gray-switch 的配置内容。我会把其中出现的配置 key 作为保护名单，相关灰度代码不会被清理。
```

## 扫描流程

1. 确认仓库状态，记录当前分支和未提交变更。不要回滚用户已有改动。
2. 从用户提供的 Apollo 配置中提取保护 key 集合。
3. 在清理范围内扫描灰度代码：
   - `@Gray(...)`
   - `GrayUtils.isGray(...)`
   - `GrayUtils.execute(...)`
   - `GraySwitch.of("...")`
   - `GraySwitch.of('...')`
   - MyBatis XML 中的 `GrayUtils@isGray` / `GraySwitch@of`
   - `*Old`、`*Deprecated`、`@Deprecated` 等旧逻辑方法
   - 测试中的 `PowerMockito.mockStatic(GrayUtils.class)`、`@PrepareForTest({GrayUtils.class})`、灰度开关 mock
4. 对每个灰度 key 建立清单：key、描述、文件、行号、灰度模式、新逻辑位置、旧逻辑位置、测试覆盖位置。
5. 对每个 key 运行最近一个月 git 检查。

推荐命令：

```bash
git log --all --since="1 month ago" --name-only --grep="<gray-key>"
git log --all --since="1 month ago" -S"<gray-key>" -- .
git log --all --since="1 month ago" -G"GrayUtils|GraySwitch|@Gray|<methodName>Old" -- <related-file>
git blame --date=short -- <related-file>
```

判定规则：

- 只要 key 字符串、`@Gray` 注解、`GrayUtils` 分支、`GraySwitch.of` 调用、旧方法或相关测试在最近一个月内有提交，标记为“近期提交保护”，不清理。
- 如果仓库历史不完整、命令失败、文件无法 blame，标记为“无法确认提交年龄”，不清理。
- 如果同一灰度 key 分布在多个文件，任一文件命中保护条件则整个 key 不清理。

## 清理资格分类

扫描后必须先输出清单并等待用户确认，不要立即改代码：

```markdown
## 灰度清理扫描清单

### Apollo 保护名单
- `gray-switch.module.example.a`
- `gray-switch.module.example.b`

### 候选灰度开关

| key | 位置 | 模式 | Apollo保护 | 最近一月提交 | 处理建议 |
| --- | --- | --- | --- | --- | --- |
| gray-switch.module.example.a | XxxService.java:32 | isGray | 是 | 否 | 不清理：生产Apollo仍有配置 |
| gray-switch.module.example.c | XxxService.java:80 | @Gray | 否 | 是 | 不清理：最近一月有提交 |
| gray-switch.module.example.d | XxxMapper.xml:20 | XML choose | 否 | 否 | 可清理 |

请确认只清理“可清理”的灰度开关。
```

只有用户明确确认后，才可以修改“可清理”的项。

## 清理规则

### `@Gray` 方法级灰度

清理前：

```java
@Gray(value = "gray-switch.module.example.feature", beanName = "xxxBean")
public Result method(Request request) {
    return newLogic(request);
}

@Deprecated
public Result methodOld(Request request) {
    return oldLogic(request);
}
```

清理后：

```java
public Result method(Request request) {
    return newLogic(request);
}
```

操作：

- 删除 `@Gray` 注解。
- 删除只服务于该灰度的 `*Old` 方法。
- 删除不再使用的 `Gray` import。

### `GrayUtils.isGray` 条件分支

正向分支：

```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.example.feature", "desc"))) {
    newLogic();
} else {
    oldLogic();
}
```

清理为：

```java
newLogic();
```

反向分支：

```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.example.feature", "desc"))) {
    oldLogic();
    return;
}
newLogic();
```

清理为：

```java
newLogic();
```

含业务条件时，只移除灰度判断，保留真实业务条件：

```java
if (condition && GrayUtils.isGray(GraySwitch.of("key", "desc"))) {
    newLogic();
} else {
    oldLogic();
}
```

清理为：

```java
if (condition) {
    newLogic();
}
```

### `GrayUtils.execute`

保留新逻辑 lambda 或方法引用，删除旧逻辑 lambda：

```java
Result result = GrayUtils.execute(
        GraySwitch.of("gray-switch.module.example.feature", "desc"),
        request,
        e -> processNew(e),
        e -> processOld(e)
);
```

清理为：

```java
Result result = processNew(request);
```

如果 lambda 内有多行逻辑，内联时保持原有异常处理、返回值和副作用顺序。

### MyBatis XML 灰度

清理前：

```xml
<choose>
  <when test="@com.xxx.GrayUtils@isGray(@com.xxx.GraySwitch@of('gray-switch.module.example.feature','desc'))">
    <!-- new SQL -->
  </when>
  <otherwise>
    <!-- old SQL -->
  </otherwise>
</choose>
```

清理后保留 `<when>` 中的新 SQL，删除 `<choose>/<when>/<otherwise>` 包装和旧 SQL。保持 XML 缩进、转义字符和动态 SQL 语义。

### 测试代码

同步删除或改造只服务于旧灰度分支的测试代码：

- `@PrepareForTest({GrayUtils.class})`
- `PowerMockito.mockStatic(GrayUtils.class)`
- `PowerMockito.when(GrayUtils.isGray(...))`
- 灰度关闭路径的测试用例
- 只服务于旧逻辑的 mock 字段和断言

保留并更新新逻辑路径测试。不要因为清理灰度而降低有效业务覆盖。

### import、字段和依赖

清理后逐个检查引用再删除：

- `com.yl.sqs.gray.annotation.Gray`
- `com.yl.sqs.gray.utils.GrayUtils`
- `com.yl.sqs.gray.common.GraySwitch`
- 只被旧逻辑使用的字段、构造参数、mock、私有方法

如果同一文件仍有受保护或不可清理的灰度代码，必须保留相关 import 和依赖。

## 验证

优先运行最小必要验证：

```bash
mvn test -Dtest=<RelatedTest>
mvn -pl <module> test
mvn -pl <module> compile
```

如果项目不是 Maven，按项目已有构建工具执行等价验证。无法运行时，在最终报告中说明原因。

## 最终报告

完成后输出：

```markdown
## 灰度清理报告

### 已清理
| key | 文件 | 清理内容 |
| --- | --- | --- |

### 未清理
| key | 原因 |
| --- | --- |
| gray-switch.module.example.a | 生产 Apollo gray-switch namespace 仍有配置 |
| gray-switch.module.example.c | 最近一个月内有提交记录 |

### 验证
- 编译：
- 测试：
```

最终报告必须明确列出因 Apollo 保护和最近一月提交保护而跳过的灰度 key。
