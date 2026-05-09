---
name: gray-switch-clean
description: 清理 Java/Spring Boot 项目中已全量开启的灰度开关旧逻辑，删除旧代码分支、@Gray 注解、GrayUtils.isGray 调用等，保留新逻辑。执行前必须先梳理灰度开关清单并让用户确认灰度已开启，再执行清理。适用于灰度验证完成、需要下线旧代码的场景。
---

# 灰度旧代码清理

## 适用场景

当灰度功能已在生产环境全量开启，需要清理旧逻辑代码时使用此技能。

触发关键词：
- "清理灰度代码"
- "删除灰度旧逻辑"
- "灰度开关下线"
- "灰度代码清理"
- "移除GrayUtils"
- "移除@Gray注解"
- 提供类名/方法名/开关key要求清理灰度

---

## 前置条件

执行本技能前，请确保：
1. 灰度功能已在生产环境全量开启并稳定运行
2. 不需要回滚到旧逻辑（灰度开关已无意义）
3. 用户已确认可以清理

**如果灰度尚未全量开启，请先使用 `release-gray-switch` 技能添加灰度保护，而不是清理。**

---

## 核心原则

**先梳理，后清理，确认后再动手。**

1. 必须先完整梳理出所有涉及的灰度开关，输出清单让用户确认
2. 用户确认灰度已开启且可清理后，才能执行代码删除
3. 只删除用户指定范围内的灰度旧逻辑，不越界清理
4. 清理后必须编译验证

---

## 执行流程

### 第一步：接收清理目标

用户会提供以下信息之一：
- 类名（如 `VipCustomerSectorWarningDetailServiceImpl`）
- 方法名（如 `getPageQueryBuilder`）
- 灰度开关 key（如 `gray-switch.vipCustomer.esSwitch`）
- 或组合形式

将用户的目标记录下来，作为后续梳理的范围边界。

---

### 第二步：扫描并梳理灰度开关清单（核心步骤）

在用户指定的范围内，全面扫描所有灰度相关代码，输出完整清单。

#### 2.1 扫描目标文件

根据用户提供的类名，定位到源文件：

```
Glob: **/impl/{ClassName}.java
Glob: **/{ClassName}.java
```

读取文件全文，逐行扫描以下内容：

#### 2.2 识别灰度模式

**模式 1：@Gray 注解（AOP 方式）**

```java
@Gray(
    value = "gray-switch.module.xxx.feature",
    beanName = "xxxBeanName"
)
public Result methodName(DTO dto) {
    // 新逻辑
}

@Deprecated
public Result methodNameOld(DTO dto) {
    // 旧逻辑
}
```

识别要素：
- `@Gray` 注解及属性（value、beanName）
- 新方法名
- 对应的 `Old` 后缀旧方法
- 旧方法上的 `@Deprecated` 注解

**模式 2：GrayUtils.isGray 内联判断**

```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
    // 新逻辑
} else {
    // 旧逻辑
}
```

或反向判断：

```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
    // 旧逻辑
} else {
    // 新逻辑
}
```

识别要素：
- `GrayUtils.isGray` 调用
- `GraySwitch.of` 中的 key 和描述
- `if` 分支中的新逻辑
- `else` 分支中的旧逻辑

**模式 3：GrayUtils.execute 函数式调用**

```java
Result result = GrayUtils.execute(
    GraySwitch.of("gray-switch.module.xxx.feature", "描述"),
    dto,
    e -> { /* 新逻辑 */ return processNew(e); },
    e -> { /* 旧逻辑 */ return processOld(e); }
);
```

或无返回值形式：

```java
GrayUtils.execute(
    GraySwitch.of("gray-switch.module.xxx.feature", "描述"),
    () -> { /* 新逻辑 */ },
    () -> { /* 旧逻辑 */ }
);
```

识别要素：
- `GrayUtils.execute` 调用
- `GraySwitch.of` 中的 key 和描述
- 第一个 lambda/函数（新逻辑）
- 第二个 lambda/函数（旧逻辑）

**模式 4：独立旧方法（被新方法内部条件调用）**

```java
public void methodName(DTO dto) {
    if (GrayUtils.isGray(...)) {
        // 新逻辑
    } else {
        methodNameOld(dto);
    }
}

@Deprecated
private void methodNameOld(DTO dto) {
    // 旧逻辑
}
```

识别要素：
- 新方法中的灰度判断
- 独立的 `Old` 后缀旧方法

**模式 5：XML（MyBatis）灰度**

```xml
<choose>
   <when test="@com.yl.sqs.gray.utils.GrayUtils@isGray(
    @com.yl.sqs.gray.common.GraySwitch@of(
      'gray-switch.module.xxx.feature',
      '描述'
    ))">
      <!-- 新逻辑 SQL -->
   </when>
   <otherwise>
      <!-- 旧逻辑 SQL -->
   </otherwise>
</choose>
```

识别要素：
- XML 文件中的 `GrayUtils.isGray` OGNL 表达式
- `<when>` 中的新 SQL
- `<otherwise>` 中的旧 SQL

#### 2.3 输出灰度开关清单

将扫描结果整理为以下格式，**必须输出给用户确认**：

```
## 灰度开关梳理清单

### 类：{ClassName}

| 序号 | 灰度开关 Key | 描述 | 灰度模式 | 新逻辑位置 | 旧逻辑位置 | 当前状态 |
|------|-------------|------|---------|-----------|-----------|---------|
| 1 | gray-switch.module.xxx.feature-a | 功能A描述 | @Gray注解 | methodName() | methodNameOld() | 需确认 |
| 2 | gray-switch.module.xxx.feature-b | 功能B描述 | isGray内联 | if分支(行120) | else分支(行125) | 需确认 |
| 3 | gray-switch.module.xxx.feature-c | 功能C描述 | execute函数式 | lambda1 | lambda2 | 需确认 |
| ... | ... | ... | ... | ... | ... | ... |

### 涉及的旧方法/旧代码块

- `methodNameOld()` — 被 `@Gray` 注解替代的旧方法，标记 `@Deprecated`
- `methodNameOld2()` — 被 `isGray` 条件调用的旧方法
- 行125-130的 else 分支 — `isGray` 判断的旧逻辑代码块

### 涉及的 import 清理

- `com.yl.sqs.gray.annotation.Gray`
- `com.yl.sqs.gray.utils.GrayUtils`
- `com.yl.sqs.gray.common.GraySwitch`
- 其他仅被旧逻辑使用的 import

### 需要确认的事项

⚠️ **在执行清理前，请确认以下灰度开关已在生产环境全量开启：**

1. [ ] `gray-switch.module.xxx.feature-a` — 功能A描述
2. [ ] `gray-switch.module.xxx.feature-b` — 功能B描述
3. [ ] `gray-switch.module.xxx.feature-c` — 功能C描述
...

确认方式：检查 Apollo 配置中心，确认上述开关值已设置为 `true` 或已删除（默认开启）。
```

**⚠️ 此步骤必须输出给用户，等待用户确认后才能继续。**

---

### 第三步：等待用户确认灰度已开启

输出清单后，**暂停执行**，向用户确认：

> 请确认以上灰度开关已在生产环境全量开启，确认后我将开始清理旧代码。

用户确认后才进入第四步。如果用户反馈某个开关尚未开启，则在清理时跳过该开关相关的代码。

---

### 第四步：执行灰度旧代码清理

用户确认后，按以下规则逐个清理。

#### 4.1 @Gray 注解模式清理

**清理前**：
```java
@Gray(
    value = "gray-switch.module.xxx.feature",
    beanName = "xxxBeanName"
)
public Result methodName(DTO dto) {
    // 新逻辑
}

@Deprecated
public Result methodNameOld(DTO dto) {
    // 旧逻辑
}
```

**清理后**：
```java
public Result methodName(DTO dto) {
    // 新逻辑（原样保留）
}
```

操作：
1. 删除 `@Gray` 注解及其 import
2. 删除 `methodNameOld()` 方法整体
3. 保留新逻辑方法

#### 4.2 GrayUtils.isGray 内联模式清理

**情况 A：if-else 双分支**

清理前：
```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
    // 新逻辑
} else {
    // 旧逻辑
}
```

清理后：
```java
// 新逻辑（直接内联到原位置，去掉 if 包裹）
```

操作：
1. 将 `if` 分支内的新逻辑提取出来，替换整个 `if-else` 块
2. 如果 `if` 块只有一行，直接替换为该行
3. 如果 `if` 块有多行，将内容原样保留但移除 `if` 包裹

**情况 B：反向判断（!isGray）**

清理前：
```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
    // 旧逻辑
} else {
    // 新逻辑
}
```

或：

```java
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
    // 旧逻辑
}
// 新逻辑（在 if 块之后）
```

清理后：
```java
// 新逻辑（保留 else 分支或 if 块之后的代码）
```

操作：
1. 删除 `if` 块中的旧逻辑
2. 将 `else` 分支中的新逻辑提取出来
3. 如果没有 else，保留 if 块之后的代码

**情况 C：仅 if 块（无 else）**

清理前：
```java
if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
    // 新逻辑（如设置字段、调用方法等）
}
```

清理后：
```java
// 新逻辑（去掉 if 包裹，直接内联）
```

操作：
1. 将 `if` 块内的新逻辑提取出来
2. 替换整个 `if` 块

#### 4.3 GrayUtils.execute 函数式模式清理

**有返回值**：

清理前：
```java
Result result = GrayUtils.execute(
    GraySwitch.of("gray-switch.module.xxx.feature", "描述"),
    dto,
    e -> { return processNew(e); },
    e -> { return processOld(e); }
);
```

清理后：
```java
Result result = processNew(dto);
```

操作：
1. 用第一个 lambda（新逻辑）替换整个 `GrayUtils.execute` 调用
2. 如果 lambda 是简单的方法引用，直接调用该方法

**无返回值**：

清理前：
```java
GrayUtils.execute(
    GraySwitch.of("gray-switch.module.xxx.feature", "描述"),
    () -> { /* 新逻辑 */ },
    () -> { /* 旧逻辑 */ }
);
```

清理后：
```java
// 新逻辑（直接内联第一个 lambda 的内容）
```

#### 4.4 独立旧方法清理

当灰度判断中调用了独立的 `Old` 后缀方法：

清理前：
```java
public void methodName(DTO dto) {
    if (GrayUtils.isGray(GraySwitch.of("gray-switch.module.xxx.feature", "描述"))) {
        // 新逻辑
    } else {
        methodNameOld(dto);
    }
}

@Deprecated
private void methodNameOld(DTO dto) {
    // 旧逻辑
}
```

清理后：
```java
public void methodName(DTO dto) {
    // 新逻辑（直接内联）
}
```

操作：
1. 按 4.2 规则清理内联灰度判断
2. 删除 `methodNameOld()` 方法整体
3. 删除 `@Deprecated` 注解

#### 4.5 XML 灰度清理

清理前：
```xml
<choose>
   <when test="@com.yl.sqs.gray.utils.GrayUtils@isGray(
    @com.yl.sqs.gray.common.GraySwitch@of(
      'gray-switch.module.xxx.feature',
      '描述'
    ))">
      <!-- 新逻辑 SQL -->
   </when>
   <otherwise>
      <!-- 旧逻辑 SQL -->
   </otherwise>
</choose>
```

清理后：
```xml
<!-- 新逻辑 SQL（直接保留 when 分支的 SQL，去掉 choose/when/otherwise 包裹） -->
```

#### 4.6 import 清理

清理完代码逻辑后，检查并删除以下不再使用的 import：

```java
import com.yl.sqs.gray.annotation.Gray;
import com.yl.sqs.gray.utils.GrayUtils;
import com.yl.sqs.gray.common.GraySwitch;
```

**注意**：
- 只删除确实不再使用的 import
- 如果类中还有其他方法使用 `GrayUtils`，保留对应 import
- 逐个检查，不要误删仍在使用的 import

#### 4.7 字段清理

如果旧逻辑依赖了新逻辑不需要的字段（如 `ESSqsSearchHolder` 等旧实现类的注入），检查：

1. 搜索该字段在类中的所有引用
2. 如果仅被旧逻辑使用，删除字段声明
3. 如果还被新逻辑使用，保留

#### 4.8 单测文件同步清理

同步清理测试文件中的灰度相关代码：

1. 删除 `@PrepareForTest({GrayUtils.class})` 注解（PowerMock）
2. 删除 `PowerMockito.mockStatic(GrayUtils.class)` 调用
3. 删除 `PowerMockito.when(GrayUtils.isGray(...))` 调用
4. 删除旧逻辑路径的测试用例（如 `test_methodName_grayDisabled`）
5. 如果删除 PowerMock 相关代码后不再需要 PowerMockRunner，考虑切换为 MockitoJUnitRunner
6. 删除仅被旧逻辑测试使用的 mock 字段（如 `ESSqsSearchHolder`）
7. 保留并更新新逻辑路径的测试用例

---

### 第五步：编译验证

清理完成后，执行编译验证：

```bash
mvn clean compile -pl . -q
```

确保没有编译错误。如果编译失败，检查：
- 是否误删了仍在使用的 import
- 是否遗漏了某个灰度引用
- 方法签名是否匹配

---

### 第六步：运行测试

运行相关单元测试：

```bash
mvn test -Dtest={ClassName}Test -pl .
```

如果测试失败：
1. 检查测试文件中是否还有灰度相关的 mock 代码
2. 检查新逻辑路径的测试是否覆盖清理后的代码
3. 修复或更新测试

---

### 第七步：输出清理报告

清理完成后，向用户输出报告：

```
## 灰度旧代码清理报告

### 清理范围

- 类：{ClassName}
- 文件路径：{filePath}

### 已清理的灰度开关

| 序号 | 灰度开关 Key | 描述 | 清理模式 | 清理内容 |
|------|-------------|------|---------|---------|
| 1 | gray-switch.module.xxx.feature-a | 功能A | @Gray注解 | 删除注解+旧方法 |
| 2 | gray-switch.module.xxx.feature-b | 功能B | isGray内联 | 保留新逻辑，删除旧分支 |
| ... | ... | ... | ... | ... |

### 已删除的旧方法

- `methodNameOld()` — 被 `@Gray` 注解替代
- `methodNameOld2()` — 被内联条件调用

### 已清理的 import

- `com.yl.sqs.gray.annotation.Gray`
- `com.yl.sqs.gray.utils.GrayUtils`
- `com.yl.sqs.gray.common.GraySwitch`
- `{其他仅旧逻辑使用的import}`

### 已清理的字段

- `oldField` — 仅被旧逻辑使用

### 单测文件变更

- 删除了 `@PrepareForTest({GrayUtils.class})`
- 删除了 `PowerMockito.mockStatic(GrayUtils.class)` 调用
- 删除了旧逻辑测试用例：`test_methodName_grayDisabled`
- 保留了新逻辑测试用例：`test_methodName_新场景`

### 验证结果

- 编译：✅ 通过
- 单测：✅ {N}个测试全部通过 / ❌ {M}个失败（附原因）

### 灰度开关自检清单

⚠️ 清理前请确认以下灰度开关已在 Apollo 中全量开启：

1. [ ] `gray-switch.module.xxx.feature-a` — 功能A描述
2. [ ] `gray-switch.module.xxx.feature-b` — 功能B描述
...

> 如果任何开关尚未开启，相关旧逻辑已被删除，请尽快在 Apollo 中开启或确认已开启。

### 涉及文件

- `src/main/java/.../{ClassName}.java` — 主代码清理
- `src/test/java/.../{ClassName}Test.java` — 单测同步清理
```

---

## 注意事项

### 1. 先梳理后清理

**这是本技能的核心原则**：
- ✅ 先完整梳理灰度开关清单
- ✅ 让用户确认灰度已开启
- ✅ 确认后才执行清理
- ❌ 绝对禁止不经确认直接删除代码

### 2. 只清理用户指定范围

- ✅ 只清理用户指定类/方法/开关范围内的灰度代码
- ❌ 不越界清理其他类或其他模块的灰度代码
- ❌ 不删除仍被新逻辑使用的字段或 import

### 3. 保留新逻辑

- ✅ 新逻辑代码原样保留
- ✅ 清理后代码行为与灰度开启时完全一致
- ❌ 不修改新逻辑的任何业务代码

### 4. 编译和测试验证

- ✅ 清理后必须编译通过
- ✅ 清理后必须运行单测
- ❌ 不提交未通过编译或测试的代码

### 5. 特殊情况处理

**情况 A：灰度判断嵌套在其他业务逻辑中**

```java
if (condition1 && GrayUtils.isGray(GraySwitch.of("key", "desc"))) {
    // 新逻辑
} else {
    // 旧逻辑
}
```

清理时，将 `GrayUtils.isGray(...)` 部分移除，保留 `condition1`：

```java
if (condition1) {
    // 新逻辑
}
```

**情况 B：灰度判断控制 return**

```java
if (GrayUtils.isGray(GraySwitch.of("key", "desc"))) {
    return newValue;
}
return oldValue;
```

清理后：

```java
return newValue;
```

**情况 C：多处引用同一个旧方法**

如果 `methodNameOld()` 被多处调用（不仅限于灰度分支），不能直接删除：
1. 先将所有调用点迁移到新逻辑
2. 确认无引用后再删除旧方法
3. 如果无法确认，保留旧方法并在报告中标注

### 6. XML 文件灰度清理注意

- MyBatis XML 中的灰度判断使用 OGNL 表达式
- 清理时保留 `<when>` 分支的 SQL，去掉 `<choose>/<when>/<otherwise>` 包裹
- 注意 XML 格式和缩进

---

## 检查清单

完成清理后，请确认以下事项：

**梳理阶段**：
- [ ] 已扫描用户指定范围内的所有灰度代码
- [ ] 已输出完整的灰度开关清单
- [ ] 已等待用户确认灰度已开启

**清理阶段**：
- [ ] @Gray 注解已删除
- [ ] GrayUtils.isGray / GrayUtils.execute 调用已删除
- [ ] 旧方法（*Old 后缀）已删除
- [ ] 旧逻辑分支已删除，新逻辑已内联
- [ ] 仅旧逻辑使用的字段已删除
- [ ] 仅旧逻辑使用的 import 已删除

**单测阶段**：
- [ ] 测试文件中灰度相关 mock 代码已清理
- [ ] 旧逻辑测试用例已删除
- [ ] 新逻辑测试用例保留并更新
- [ ] PowerMock 相关注解和调用已清理（如适用）

**验证阶段**：
- [ ] 编译通过
- [ ] 单测通过
- [ ] 清理报告已输出
- [ ] 灰度开关自检清单已输出

---

## 与 release-gray-switch 的关系

`release-gray-switch` 是灰度代码**添加**技能，本技能 `gray-switch-clean` 是灰度代码**清理**技能。

**生命周期**：
1. 需求开发 → 使用 `release-gray-switch` 添加灰度保护
2. 灰度验证 → 确认功能正常
3. 全量开启 → 使用 `gray-switch-clean` 清理旧代码

**本技能是 `release-gray-switch` 的逆操作**，当灰度功能已稳定全量开启后，使用本技能将代码恢复为干净的、无灰度分支的状态。
