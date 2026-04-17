# Mapper/MyBatis 测试参考（JUnit 5）

MyBatis-Plus Mapper 测试规范和常见场景。

## 1. 基础配置

### 测试类结构

```java
package com.yl.cswot.mapper;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.yl.cswot.model.entity.XxxEntity;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

/**
 * XxxMapper单元测试
 * 测试范围：数据库查询和操作
 */
@ExtendWith(MockitoExtension.class)
public class XxxMapperTest {

    @Mock
    private XxxMapper xxxMapper;

    private XxxEntity testEntity;

    @BeforeEach
    public void setUp() {
        testEntity = new XxxEntity();
        testEntity.setId(1L);
        testEntity.setName("测试");
    }
}
```

## 2. 查询场景

### 2.1 根据 ID 查询

```java
@Test
public void test_selectById_exists_returnEntity() {
    // 模拟查询返回结果
    when(xxxMapper.selectById(1L)).thenReturn(testEntity);

    // 执行查询
    XxxEntity result = xxxMapper.selectById(1L);

    // 验证结果
    assertThat(result).isNotNull();
    assertThat(result.getId()).isEqualTo(1L);
    assertThat(result.getName()).isEqualTo("测试");

    // 验证调用次数
    verify(xxxMapper, times(1)).selectById(1L);
}

@Test
public void test_selectById_notExists_returnNull() {
    // 模拟查询返回 null
    when(xxxMapper.selectById(999L)).thenReturn(null);

    // 执行查询
    XxxEntity result = xxxMapper.selectById(999L);

    // 验证结果
    assertThat(result).isNull();
}
```

### 2.2 条件查询

```java
@Test
public void test_selectList_withCondition_returnList() {
    // 准备测试数据
    List<XxxEntity> expectedList = Arrays.asList(testEntity);

    // 模拟查询返回结果
    when(xxxMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(expectedList);

    // 执行查询
    LambdaQueryWrapper<XxxEntity> wrapper = new LambdaQueryWrapper<>();
    wrapper.eq(XxxEntity::getId, 1L);
    List<XxxEntity> result = xxxMapper.selectList(wrapper);

    // 验证结果
    assertThat(result).isNotNull();
    assertThat(result).hasSize(1);
    assertThat(result.get(0).getId()).isEqualTo(1L);
}

@Test
public void test_selectList_emptyCondition_returnEmpty() {
    // 模拟查询返回空列表
    when(xxxMapper.selectList(any(LambdaQueryWrapper.class))).thenReturn(Collections.emptyList());

    // 执行查询
    List<XxxEntity> result = xxxMapper.selectList(new LambdaQueryWrapper<>());

    // 验证结果
    assertThat(result).isNotNull();
    assertThat(result).isEmpty();
}
```

### 2.3 分页查询

```java
@Test
public void test_selectPage_validParams_returnPage() {
    // 准备分页参数
    Page<XxxEntity> page = new Page<>(1, 10);
    page.setRecords(Arrays.asList(testEntity));
    page.setTotal(1);

    // 模拟查询返回结果
    when(xxxMapper.selectPage(any(Page.class), any(LambdaQueryWrapper.class))).thenReturn(page);

    // 执行查询
    Page<XxxEntity> result = xxxMapper.selectPage(page, new LambdaQueryWrapper<>());

    // 验证结果
    assertThat(result).isNotNull();
    assertThat(result.getRecords()).hasSize(1);
    assertThat(result.getTotal()).isEqualTo(1);
}
```

## 3. 写操作场景

### 3.1 插入数据

```java
@Test
public void test_insert_validParam_returnSuccess() {
    // 模拟插入返回1（成功）
    when(xxxMapper.insert(any(XxxEntity.class))).thenReturn(1);

    // 执行插入
    int result = xxxMapper.insert(testEntity);

    // 验证结果
    assertThat(result).isEqualTo(1);

    // 验证调用参数
    verify(xxxMapper, times(1)).insert(argThat(entity ->
        entity.getId().equals(1L) && entity.getName().equals("测试")
    ));
}

@Test
public void test_insert_invalidParam_returnFailure() {
    // 模拟插入返回0（失败）
    when(xxxMapper.insert(any(XxxEntity.class))).thenReturn(0);

    // 执行插入
    int result = xxxMapper.insert(testEntity);

    // 验证结果
    assertThat(result).isEqualTo(0);
}
```

### 3.2 更新数据

```java
@Test
public void test_updateById_exists_returnSuccess() {
    // 模拟更新返回1（成功）
    when(xxxMapper.updateById(any(XxxEntity.class))).thenReturn(1);

    // 执行更新
    testEntity.setName("更新后的名称");
    int result = xxxMapper.updateById(testEntity);

    // 验证结果
    assertThat(result).isEqualTo(1);

    // 验证调用参数
    verify(xxxMapper, times(1)).updateById(argThat(entity ->
        entity.getId().equals(1L) && entity.getName().equals("更新后的名称")
    ));
}

@Test
public void test_updateById_notExists_returnFailure() {
    // 模拟更新返回0（失败）
    when(xxxMapper.updateById(any(XxxEntity.class))).thenReturn(0);

    // 执行更新
    int result = xxxMapper.updateById(testEntity);

    // 验证结果
    assertThat(result).isEqualTo(0);
}
```

### 3.3 删除数据

```java
@Test
public void test_deleteById_exists_returnSuccess() {
    // 模拟删除返回1（成功）
    when(xxxMapper.deleteById(1L)).thenReturn(1);

    // 执行删除
    int result = xxxMapper.deleteById(1L);

    // 验证结果
    assertThat(result).isEqualTo(1);
}

@Test
public void test_deleteById_notExists_returnFailure() {
    // 模拟删除返回0（失败）
    when(xxxMapper.deleteById(999L)).thenReturn(0);

    // 执行删除
    int result = xxxMapper.deleteById(999L);

    // 验证结果
    assertThat(result).isEqualTo(0);
}
```

## 4. ServiceImpl 测试

### 4.1 继承 ServiceImpl 的测试

```java
@ExtendWith(MockitoExtension.class)
public class XxxServiceImplTest {

    @Mock
    private XxxMapper xxxMapper;

    @InjectMocks
    private XxxServiceImpl xxxService;

    private XxxEntity testEntity;

    @BeforeEach
    public void setUp() {
        // 手动设置 MyBatis-Plus 的 baseMapper
        try {
            java.lang.reflect.Field field = xxxService.getClass().getSuperclass().getDeclaredField("baseMapper");
            field.setAccessible(true);
            field.set(xxxService, xxxMapper);
        } catch (Exception e) {
            throw new RuntimeException("Failed to set baseMapper", e);
        }

        testEntity = new XxxEntity();
        testEntity.setId(1L);
    }

    @Test
    public void test_page_validParams_returnPage() {
        // 准备分页参数
        Page<XxxEntity> mockPage = new Page<>(1, 10);
        mockPage.setRecords(Arrays.asList(testEntity));

        // 模拟查询返回结果
        when(xxxMapper.selectPage(any(Page.class), any(LambdaQueryWrapper.class))).thenReturn(mockPage);

        // 执行查询
        Page<XxxEntity> result = xxxService.page(new Page<>(1, 10));

        // 验证结果
        assertThat(result).isNotNull();
        assertThat(result.getRecords()).hasSize(1);
    }
}
```

## 5. 批量操作

```java
@Test
public void test_insertBatch_someValid_returnCount() {
    // 准备测试数据
    List<XxxEntity> entities = Arrays.asList(
        new XxxEntity(1L, "测试1"),
        new XxxEntity(2L, "测试2")
    );

    // 模拟批量插入返回2
    when(xxxMapper.insertBatchSomeColumn(entities)).thenReturn(2);

    // 执行批量插入
    int result = xxxMapper.insertBatchSomeColumn(entities);

    // 验证结果
    assertThat(result).isEqualTo(2);
}
```

## 6. 聚合查询

```java
@Test
public void test_selectCount_withCondition_returnCount() {
    // 模拟查询返回数量
    when(xxxMapper.selectCount(any(LambdaQueryWrapper.class))).thenReturn(10L);

    // 执行查询
    Long result = xxxMapper.selectCount(new LambdaQueryWrapper<>());

    // 验证结果
    assertThat(result).isEqualTo(10L);
}
```

## 7. 最佳实践

1. **使用 argThat 验证参数**：写操作必须验证参数字段，禁止只用 `any()`
2. **覆盖三种返回值**：存在、不存在（null）、空集合
3. **分页测试**：测试总记录数、当前页记录数
4. **条件查询**：测试不同条件组合
5. **避免真实数据库**：使用 Mock 模拟所有数据库操作
