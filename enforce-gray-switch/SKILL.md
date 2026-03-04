---
name: enforce-gray-switch
description: "Enforce gray-switch guarding and config-only rollback for production-behavior changes in Java/Spring Boot services. Use when modifying business logic, adding new logic that affects existing flows, changing API semantics/contracts, or handling security/performance/legacy-logic changes."
---

# Enforce Gray Switch

## Goal

Guarantee any production-behavior change is guarded by a gray switch and can be rolled back via config only.

## Required Dependency

Ensure this dependency exists:

```xml
<dependency>
   <groupId>com.yl</groupId>
   <artifactId>yl-jms-sqs-utils</artifactId>
   <version>${yl-jms-sqs-utils.version}</version>
</dependency>
```

## Gray Switch Key Spec

Naming convention (mandatory):

- `gray-switch.module.{module}.{feature}`

Examples:

- `gray-switch.module.example.gray-test`
- `gray-switch.module.example.feature-toggle.enabled`
- `gray-switch.module.example.feature-toggle.condition`

Condition examples:

- `#{#dto.code == 'X001'}`
- `#{['X001','X002'].contains(#dto.code)}`
- `#{#dto.codes.contains('X001')}`

Config rules:

- Apollo config is optional.
- If not configured, the switch defaults to enabled.

## Mandatory Rules (Hard Constraints)

- Preserve old logic.
- When modifying existing logic, copy the original implementation.
- Rename old method with `Old` suffix.
- Mark old method with `@Deprecated`.
- Never delete or inline-replace old logic without fallback.
- New logic must be guarded by gray switch.
- Old logic must be executable when gray is off.
- Rollback must be config-only and instant.

### Exception: Simple New Logic (No need to create new method/class)

When the added logic is simple, you can use inline `if` / `if-else` with gray switch directly in the original method. No need to extract new method or create `*Old` method.

Simple logic is defined as:

1. Fully new logic guarded by `if (GrayUtils.isGray(...))`, and the code inside the `if` block is no more than 10 lines.
2. Simple `get` / `set` style adjustment.
3. Tiny change with no more than 5 lines.

Examples:

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
if (!GrayUtils.isGray(GraySwitch.of("gray-switch.module.sample.feature-b", "sample gray switch B"))
        && !codeSet.contains(dataList.get(0).getCode())) {
    // 旧逻辑
    processOld(dataList);
    return;
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

## Implementation Patterns

Pattern 1: Method-level gray (AOP)

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

Pattern 2: Local gray (with return value)

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

Note:

- `result` may be null. Handle NPE risk in the caller.

Pattern 3: Local gray (without return value)

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

Pattern 4: Conditional gray

```java
if (GrayUtils.isGray(
        GraySwitch.of("gray-switch.module.example.gray-test", "Fallback guard")
)) {
        // New logic
        } else {
        // Old logic
        }
```

Pattern 5: XML (MyBatis) gray

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

## Execution Steps

1. Detect triggers and confirm the skill applies.
2. Ensure dependency exists or add it.
3. Copy the original logic to an `Old` method and mark it `@Deprecated`.
4. Introduce a gray switch key following naming rules.
5. Guard new logic with gray switch and ensure old logic runs when gray is off.
6. Ensure rollback is config-only and instant.
7. Add or update tests for gray on and off.
8. Run relevant checks or state they were not run.

## Self-Check (Mandatory)

Before final output, verify:

- Gray dependency exists
- Gray switch key follows naming rules
- Old logic is preserved and deprecated
- New logic is guarded by gray switch
- Rollback is config-only and instant

If any item fails, reject code generation.

## Final Principle

No gray switch, no merge.
No rollback path, no release.
