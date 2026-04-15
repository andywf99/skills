# MyBatis Mapper Mock 参考

## 依赖声明

```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserMapper userMapper;
    @InjectMocks
    private UserService userService;
}
```

## 查询场景——必须覆盖三个分支（各自独立测试方法）

**记录存在**：
```java
when(userMapper.selectById(1L)).thenReturn(mockUser);
```

**记录不存在（null）**：
```java
when(userMapper.selectById(99L)).thenReturn(null);
```

**结果为空集合**：
```java
when(userMapper.selectList(any())).thenReturn(Collections.emptyList());
```

## 写操作——必须覆盖两个分支

**成功（影响行数=1）**：
```java
when(userMapper.updateById(any())).thenReturn(1);
```

**失败（影响行数=0，记录不存在）**：
```java
when(userMapper.updateById(any())).thenReturn(0);
```

## verify 必须验证到入参字段级别

```java
// 禁止——只验证调用次数，参数错误也通过
verify(userMapper, times(1)).insert(any());

// 必须——验证关键字段值正确
verify(userMapper, times(1)).insert(argThat(user ->
    "admin".equals(user.getUsername()) && Integer.valueOf(1).equals(user.getStatus())));
```
