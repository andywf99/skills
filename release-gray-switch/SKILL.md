---
name: release-gray-switch
description: "为 Java/Spring Boot 服务中的生产行为变更加上 gray switch 守护，并确保可以通过纯配置即时回滚。适用于提前识别发布风险、预置灰度开关和回滚路径，以及修改业务逻辑、添加影响既有流程的新逻辑、调整 API 语义/契约，或处理安全、性能、遗留逻辑变更时。"
---

# 灰度开关约束

## 目标

保证任何生产行为变更都必须受 gray switch 保护，并且能够仅通过配置回滚。

## 必需依赖

确保存在以下依赖：

```xml
<dependency>
   <groupId>com.yl</groupId>
   <artifactId>yl-jms-sqs-utils</artifactId>
   <version>${yl-jms-sqs-utils.version}</version>
</dependency>
```

## 灰度开关键规范

命名规范（强制）：

- `gray-switch.module.{module}.{feature}`

示例：

- `gray-switch.module.example.gray-test`
- `gray-switch.module.example.feature-toggle.enabled`
- `gray-switch.module.example.feature-toggle.condition`

条件示例：

- `#{#dto.code == 'X001'}`
- `#{['X001','X002'].contains(#dto.code)}`
- `#{#dto.codes.contains('X001')}`

配置规则：

- Apollo 配置可选。
- 如果未配置，开关默认开启。

## 强制规则（硬约束）

- 保留旧逻辑。
- 修改既有逻辑时，复制原始实现。
- 将旧方法重命名为带 `Old` 后缀。
- 用 `@Deprecated` 标记旧方法。
- 绝不允许删除旧逻辑，也不允许直接内联替换且不保留回退路径。
- 新逻辑必须受 gray switch 保护。
- gray 关闭时，旧逻辑必须仍然可执行。
- 回滚必须是纯配置、且立即生效。
- **禁止在灰度 if 开关中混用 `&&` 或业务逻辑**。灰度判断必须独立，不得与业务条件组合。

### 灰度开关条件规范（强制）

灰度开关的 `if` 条件必须保持纯粹，只包含 `GrayUtils.isGray()` 或其否定形式，禁止与业务逻辑混用。

**错误示例（禁止）：**

```java
// ❌ 禁止：灰度开关与业务条件用 && 组合
if (GrayUtils.isGray(...) && StringUtils.isNotEmpty(code)) {
    // 新逻辑
}

// ❌ 禁止：灰度开关与业务条件用 || 组合
if (!GrayUtils.isGray(...) || dataList.size() > 10) {
    // 旧逻辑
}

// ❌ 禁止：灰度开关嵌套在业务条件中
if (status == Status.ACTIVE && GrayUtils.isGray(...)) {
    // 新逻辑
}
```

**正确示例：**

```java
// ✅ 正确：灰度判断独立，业务逻辑在内层
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-a", "描述"))) {
    if (StringUtils.isNotEmpty(code)) {
        // 新逻辑
    }
}

// ✅ 正确：否定形式独立使用
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-b", "描述"))) {
    // 旧逻辑
} else {
    // 新逻辑
}

// ✅ 正确：灰度判断后用 else 分支处理业务
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-c", "描述"))) {
    // 新逻辑（可包含任意业务条件判断）
} else {
    // 旧逻辑
}
```

**原因：**
1. 灰度开关的职责是控制新旧逻辑切换，不应承担业务判断职责。
2. 混用会导致灰度关闭时无法完整回退到旧逻辑。
3. 独立的灰度判断便于快速定位和排查问题。
4. 配置回滚时逻辑清晰，不会产生意外的业务分支。

### 例外：简单新增逻辑（不需要创建新方法/类）

当新增逻辑足够简单时，可以直接在原方法中使用带 gray switch 的内联 `if` / `if-else`，不需要额外抽取新方法，也不需要创建 `*Old` 方法。

“简单逻辑”定义如下：

1. 完全新增的逻辑由 `if (GrayUtils.isGray(...))` 保护，且 `if` 代码块不超过 10 行。
2. 简单的 `get` / `set` 风格调整。
3. 不超过 5 行的小改动。

示例：

```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-a", "sample gray switch A"))) {
    if (StringUtils.isNotEmpty(idParam) && StringUtils.isNotEmpty(textParam) && textParam.length() >= 500) {
        String value = remoteClient.queryById(idParam).result();
        if (StringUtils.isNotEmpty(value)) {
            return value;
        }
    }
}
```

```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-b", "sample gray switch B"))) {
    // 旧逻辑
    processOld(dataList);
    return;
}
// 新逻辑在灰度开启时执行
if (!codeSet.contains(dataList.get(0).getCode())) {
    processNew(dataList);
}
```

```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-c", "sample gray switch C"))) {
    if (TypeEnum.TYPE_X.getId().equals(request.getTypeId())) {
        request.setCode(request.getSourceCode());
    }
}
```

```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-d", "sample gray switch D"))) {
    target.setUpdateTime(now);
}
```

```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-d", "sample gray switch D"))) {
    target.getvalue();
}
```

```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-e", "sample gray switch E"))) {
    // 新逻辑
    return newValue;
} else {
    // 旧逻辑
    return oldValue;
}
```

## 实现模式

模式 1：方法级灰度（AOP）

```java
import com.yl.sqs.gray.annotation.Gray;

@Gray(
        value = "gray-switch.module.example.gray-test",
        beanName = "springBeanName"
)
public Result test(DTO dto) {
   // New logic
}

@Deprecated
public Result testOld(DTO dto) {
   // Old logic copied from original implementation
}
```

模式 2：局部灰度（有返回值）

```java
Result result = GrayUtils.execute(
        GraySwitch.of("gray-switch.module.example.gray-test", "Legacy logic change"),
        dto,
        e -> {
           // New logic
           return processNew(e);
        },
        e -> {
           // Old logic
           return processOld(e);
        }
);
```

注意：

- `result` 可能为 `null`，调用方要处理 NPE 风险。

模式 3：局部灰度（无返回值）

```java
GrayUtils.execute(
        GraySwitch.of("gray-switch.module.example.gray-test", "Performance optimization"),
  () -> {
          // New logic
          },
          () -> {
          // Old logic
          }
          );
```

模式 4：条件灰度

```java
if (GrayUtils.isGray(
        GraySwitch.of("gray-switch.module.example.gray-test", "Fallback guard")
)) {
        // New logic
        } else {
        // Old logic
        }
```

模式 5：XML（MyBatis）灰度

```xml
<choose>
   <when test="@com.yl.sqs.gray.utils.GrayUtils@isGray(
    @com.yl.sqs.gray.common.GraySwitch@of(
      'gray-switch.module.sample.query-order',
      'Sample query order gray'
    ))">
      order by t1.create_time desc
   </when>
   <otherwise>
      order by t1.id desc
   </otherwise>
</choose>
```

## 执行步骤

1. 识别触发条件并确认该 skill 适用。
2. 确保依赖存在；如不存在则补上。
3. 将原始逻辑复制到 `Old` 方法，并用 `@Deprecated` 标记。
4. 按命名规范引入 gray switch key。
5. 用 gray switch 保护新逻辑，并确保 gray 关闭时旧逻辑仍然执行。
6. 确保回滚是纯配置、且能立即生效。
7. 为 gray 开启和关闭两种情况补充或更新测试。
8. 运行相关检查；如果未运行，要明确说明。

## 自检（必做）

在最终输出前，检查以下事项：

- 灰度依赖已存在
- gray switch key 符合命名规范
- 旧逻辑已保留且已废弃标记
- 新逻辑已受 gray switch 保护
- 回滚是纯配置且立即生效
- **灰度 if 条件未与业务逻辑混用 `&&` 或 `||`**

如果任一项不满足，拒绝生成代码。

## 最终原则

没有 gray switch，不允许合并。
没有回滚路径，不允许发布。
