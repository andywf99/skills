---
name: release-gray-switch-v2
description: "基于本地 git diff 检测变更，为 Java/Spring Boot 服务中的生产行为变更加上 gray switch 守护。新逻辑放灰度 if 分支，原逻辑放 else 分支，确保可以通过纯配置即时回滚。适用于提前识别发布风险、预置灰度开关和回滚路径，以及修改业务逻辑、添加影响既有流程的新逻辑、调整 API 语义/契约，或处理安全、性能、遗留逻辑变更时。"
---

# 灰度开关约束 V2（本地变更检测模式）

## 目标

通过检测本地 git diff 变更，自动识别代码修改点，为所有生产行为变更加上 gray switch 保护，确保仅通过配置即可回滚。

## 核心流程：本地变更检测 → 灰度包裹

1. **检测变更**：执行 `git diff` 获取本地未提交的变更（或 `git diff HEAD~1` 获取最近一次提交的变更），识别所有修改的 Java 文件及具体变更行。
2. **分析变更**：逐文件分析 diff，区分以下变更类型：
   - **修改既有逻辑**：原有代码被修改（非新增行）
   - **新增逻辑**：在已有方法中新增代码
   - **删除逻辑**：删除了既有代码
   - **新增方法/类**：全新添加的方法或类（通常不需要灰度）
3. **包裹灰度**：对需要保护的变更，将新逻辑放入 `if (GrayUtils.isGray(...))` 分支，将原逻辑放入 `else` 分支。

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

- **保留旧逻辑**：原逻辑必须完整保留在 `else` 分支中。
- **新逻辑在 if 分支**：所有新增/修改的逻辑放在 `GrayUtils.isGray(...)` 为 true 的分支。
- **原逻辑在 else 分支**：所有原有的被替换逻辑放在 `else` 分支。
- 绝不允许删除旧逻辑，也不允许直接内联替换且不保留回退路径。
- 新逻辑必须受 gray switch 保护。
- gray 关闭时，旧逻辑必须仍然可执行。
- 回滚必须是纯配置、且立即生效。
- **禁止在灰度 if 开关中混用 `&&` 或业务逻辑**。灰度判断必须独立，不得与业务条件组合。

### 核心包裹模式（强制）

所有变更必须按以下模式包裹：

```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.{module}.{feature}", "描述"))) {
    // 新逻辑（从 diff 中检测到的变更内容）
} else {
    // 原逻辑（修改前的原始代码，从 git diff 的 - 行恢复）
}
```

**错误示例（禁止）：**

```java
// ❌ 禁止：新逻辑和旧逻辑位置反了
if (GrayUtils.isGray(...)) {
    // 旧逻辑
} else {
    // 新逻辑
}

// ❌ 禁止：没有 else 分支保留旧逻辑
if (GrayUtils.isGray(...)) {
    // 新逻辑
}
// 旧逻辑直接删除了

// ❌ 禁止：灰度开关与业务条件用 && 组合
if (GrayUtils.isGray(...) && StringUtils.isNotEmpty(code)) {
    // 新逻辑
}
```

**正确示例：**

```java
// ✅ 修改既有逻辑：新逻辑在 if，原逻辑在 else
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-a", "描述"))) {
    // 新逻辑
    processNew(dataList);
} else {
    // 原逻辑
    processOld(dataList);
}

// ✅ 新增逻辑：原逻辑不变，新逻辑在 if 分支
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-b", "描述"))) {
    // 新增的逻辑
    extraCheck(data);
}
// 原逻辑继续正常执行（不需要 else）

// ✅ 有返回值的变更
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-c", "描述"))) {
    // 新逻辑
    return newValue;
} else {
    // 原逻辑
    return oldValue;
}
```

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

// ✅ 正确：新逻辑在 if，原逻辑在 else
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-b", "描述"))) {
    // 新逻辑（可包含任意业务条件判断）
} else {
    // 原逻辑
}
```

### 例外：简单新增逻辑（不需要创建新方法/类）

当新增逻辑足够简单时，可以直接在原方法中使用带 gray switch 的内联 `if`，不需要额外抽取新方法，也不需要创建 `*Old` 方法。

"简单逻辑"定义如下：

1. 完全新增的逻辑由 `if (GrayUtils.isGray(...))` 保护，且 `if` 代码块不超过 10 行。
2. 简单的 `get` / `set` 风格调整。
3. 不超过 5 行的小改动。

示例：

```java
// 新增逻辑，原逻辑不受影响
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
// 修改既有逻辑：新逻辑在 if，原逻辑在 else
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-b", "sample gray switch B"))) {
    // 新逻辑
    processNew(dataList);
} else {
    // 原逻辑
    processOld(dataList);
}
```

```java
// 有返回值变更
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-c", "sample gray switch C"))) {
    // 新逻辑
    return newValue;
} else {
    // 原逻辑
    return oldValue;
}
```

## 执行步骤

### 第一步：检测本地变更

执行以下命令获取变更：

```bash
# 获取未提交的变更
git diff

# 或获取最近一次提交的变更
git diff HEAD~1

# 或获取指定 commit 之后的变更
git diff <commit-id>

# 仅查看变更的文件列表
git diff --name-only
```

### 第二步：分析变更内容

对每个变更的 Java 文件：
1. 读取完整 diff 内容，识别 `+`（新增）和 `-`（删除）行。
2. 对于每个变更区域（hunk），判断：
   - 是否修改了既有逻辑（既有 `-` 行又有 `+` 行）
   - 是否纯新增逻辑（只有 `+` 行）
   - 是否删除逻辑（只有 `-` 行）
3. 读取修改前的完整文件内容（`git show HEAD:文件路径`）获取原始代码。

### 第三步：应用灰度包裹

根据变更类型应用灰度：

**修改既有逻辑**：
- 从 diff 的 `-` 行恢复原逻辑
- 从 diff 的 `+` 行获取新逻辑
- 新逻辑放入 `if (GrayUtils.isGray(...))` 分支
- 原逻辑放入 `else` 分支

**纯新增逻辑**：
- 新逻辑放入 `if (GrayUtils.isGray(...))` 分支
- 原逻辑不受影响，不需要 else

**删除逻辑**：
- 将删除的代码放入 `else` 分支
- `if` 分支为空或仅包含注释说明删除原因

### 第四步：确保依赖与规范

1. 确保灰度依赖存在；如不存在则补上。
2. 按命名规范引入 gray switch key。
3. 确保回滚是纯配置、且能立即生效。
4. 确保灰度 if 条件未与业务逻辑混用。

## 实现模式

模式 1：条件灰度（最常用 — V2 推荐）

```java
if (GrayUtils.isGray(
        GraySwitch.of("gray-switch.module.example.gray-test", "描述")
)) {
    // 新逻辑（从 diff 检测到的变更）
} else {
    // 原逻辑（从 git diff - 行恢复）
}
```

模式 2：方法级灰度（AOP）

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

模式 3：局部灰度（有返回值）

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

模式 4：局部灰度（无返回值）

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

模式 5：XML（MyBatis）灰度

```xml
<choose>
   <when test="@com.yl.sqs.gray.utils.GrayUtils@isGray(
    @com.yl.sqs.gray.common.GraySwitch@of(
      'gray-switch.module.sample.query-order',
      'Sample query order gray'
    ))">
      <!-- 新逻辑 -->
      order by t1.create_time desc
   </when>
   <otherwise>
      <!-- 原逻辑 -->
      order by t1.id desc
   </otherwise>
</choose>
```

## 自检（必做）

在最终输出前，检查以下事项：

- 灰度依赖已存在
- gray switch key 符合命名规范
- **新逻辑在 `if (GrayUtils.isGray(...))` 分支**
- **原逻辑在 `else` 分支**
- 旧逻辑已保留
- 新逻辑已受 gray switch 保护
- 回滚是纯配置且立即生效
- **灰度 if 条件未与业务逻辑混用 `&&` 或 `||`**
- 已通过 git diff 检测所有变更点，无遗漏

如果任一项不满足，拒绝生成代码。

## 最终原则

没有 gray switch，不允许合并。
没有回滚路径，不允许发布。
所有变更必须通过 git diff 检测，不留遗漏。
