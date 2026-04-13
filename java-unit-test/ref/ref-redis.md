# Redis Mock 参考

## 依赖声明——必须同时 Mock RedisTemplate 和中间操作对象

```java
@Mock
private RedisTemplate<String, String> redisTemplate;
@Mock
private ValueOperations<String, String> valueOperations;

@Before
public void setUp() {
    // opsForValue() 返回的中间对象必须提前 Mock，否则链式调用 NPE
    when(redisTemplate.opsForValue()).thenReturn(valueOperations);
    userService = new UserService(userMapper, redisTemplate);
}
```

## 必须覆盖两个分支（各自独立测试方法）

### 场景一：缓存命中——不应查 DB

```java
when(valueOperations.get("user:1")).thenReturn("{\"id\":1,\"username\":\"admin\"}");
UserVO result = userService.getUserById(1L);
assertThat(result.getUsername()).isEqualTo("admin");
// 缓存命中时 Mapper 必须未被调用
verify(userMapper, never()).selectById(anyLong());
```

### 场景二：缓存未命中——应查 DB 并回写缓存

```java
when(valueOperations.get("user:1")).thenReturn(null);
when(userMapper.selectById(1L)).thenReturn(mockUser);
UserVO result = userService.getUserById(1L);
assertThat(result.getUsername()).isEqualTo("admin");
// 验证缓存 key、value、TTL 三要素
verify(valueOperations, times(1))
    .set(eq("user:1"), anyString(), eq(30L), eq(TimeUnit.MINUTES));
```

### 缓存删除场景

```java
// 验证更新/删除操作后缓存被清除，防止与 DB 不一致
verify(redisTemplate, times(1)).delete("user:1");
```
