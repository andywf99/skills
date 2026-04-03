---
name: clean-rabbitmq
description: 该技能用于清理项目中指定的 Spring Cloud Stream RabbitMQ Input/Output 相关代码，移除灰度切换逻辑，保留纯 RocketMQ 实现。适用于从 RabbitMQ 完全迁移到 RocketMQ 后，需要清理旧代码的场景。
---

# 使用说明

当用户提到以下关键词时，**必须**加载并执行此技能：
- "清理RabbitMQ"
- "清理Input/Output"
- "移除Spring Cloud Stream"
- "RabbitMQ迁移清理"
- 提供Input/Output名称列表要求清理

---

## 前置条件

执行本技能前，请确保：
1. 项目已完成从 RabbitMQ 到 RocketMQ 的迁移
2. 所有消费者方法都已添加 `@RocketMQDynamicListener` 注解
3. 所有生产者方法都已使用 `RocketMQDynamicPublisher` 发送消息
4. 灰度验证已完成，确认 RocketMQ 功能正常

如果尚未完成迁移，请先执行 `rabbit-to-rocketmq` 技能。

---

## 清理工作流程

### 第一步：接收并解析用户指定的 Input/Output 列表

用户会提供需要清理的 Input/Output 名称列表，格式如下：

```
lmdm-data-change-input
session-create-close-evaluation-result-output
session-create-close-evaluation-result-input
...
```

将用户提供的名称分类为：
- **Input 名称列表**（通常以 `-input` 结尾）：对应消费者方法
- **Output 名称列表**（通常以 `-output` 结尾）：对应生产者方法

---

### 第二步：分析项目结构

#### 2.1 查找相关文件

1. **查找生产者类**
   ```
   Glob: **/MessageProducer.java 或 **/*Producer.java
   ```

2. **查找消费者类**
   ```
   Glob: **/MessageReceiver.java 或 **/*Receiver.java 或 **/*Consumer.java
   ```

3. **查找接口定义**
   ```
   Glob: **/InputInterface.java
   Glob: **/OutputInterface.java
   Glob: **/*InputInterface.java
   Glob: **/*OutputInterface.java
   ```

4. **读取所有相关文件内容**，记录当前状态

---

### 第三步：清理 MessageProducer 类

对于每个用户指定的 **Output 名称**：

#### 3.1 定位方法

1. 在 OutputInterface 中查找该 Output 名称对应的常量
2. 在 MessageProducer 中查找使用该 Output 的方法（通过 `RocketMQGrayUtils.gray()` 或 `outputInterface.xxxOutput().send()` 调用）

#### 3.2 判断是否需要清理

检查方法内的代码：

**情况A：方法内有 RocketMQ 灰度切换代码** → **需要清理**
```java
// 示例：需要清理的代码
Boolean result = RocketMQGrayUtils.gray(topic,
    () -> rocketMQDynamicPublisher.syncSend(topic, data),
    () -> outputInterface.xxxOutput().send(message));
```

**情况B：方法内只有纯 RocketMQ 代码** → **跳过清理**
```java
// 示例：已经清理完成的代码
SendResult sendResult = rocketMQDynamicPublisher.syncSend(topic, data);
Boolean result = sendResult.getSendStatus() == SendStatus.SEND_OK;
```

**情况C：方法内没有 RocketMQ 相关代码** → **跳过清理，记录到报告**

#### 3.3 执行清理

对于需要清理的方法，按以下步骤操作：

1. **移除 MessageBuilder 构建**
   ```java
   // 删除
   Message message = MessageBuilder.withPayload(data).build();
   ```

2. **移除灰度切换逻辑**
   ```java
   // 删除
   Boolean result = RocketMQGrayUtils.gray(topic,
       () -> rocketMQDynamicPublisher.syncSend(topic, data),
       () -> outputInterface.xxxOutput().send(message));
   ```

3. **改为纯 RocketMQ 发送**
   ```java
   // 新增
   SendResult sendResult = rocketMQDynamicPublisher.syncSend(topic, data);
   Boolean result = sendResult.getSendStatus() == SendStatus.SEND_OK;
   ```

4. **保留日志打印**
   ```java
   log.info("发送消息到队列data={},result={}", JSON.toJSONString(data), result);
   ```

#### 3.4 清理类级别代码

**检查时机**：当所有 Output 方法都已清理完成

**执行操作**：
1. 移除 `@EnableBinding` 注解
   ```java
   // 删除
   @EnableBinding(value = {OutputInterface.class})
   ```

2. 移除 OutputInterface 字段
   ```java
   // 删除
   private final OutputInterface outputInterface;
   ```

3. 移除构造函数
   ```java
   // 删除
   public MessageProducer(OutputInterface outputInterface) {
       this.outputInterface = outputInterface;
   }
   ```

4. 清理未使用的 import
   ```java
   // 删除
   import org.springframework.cloud.stream.annotation.EnableBinding;
   import org.springframework.messaging.Message;
   import org.springframework.messaging.support.MessageBuilder;
   import com.yl.css.online.utils.RocketMQGrayUtils;

   // 新增（如果还没有）
   import org.apache.rocketmq.client.producer.SendResult;
   import org.apache.rocketmq.client.producer.SendStatus;
   ```

---

### 第四步：清理 MessageReceiver 类

对于每个用户指定的 **Input 名称**：

#### 4.1 定位方法

1. 在 InputInterface 中查找该 Input 名称对应的常量
2. 在 MessageReceiver 中查找使用 `@StreamListener` 注解的方法

#### 4.2 判断是否需要清理

检查方法上的注解：

**情况A：方法同时有 @RocketMQDynamicListener 和 @StreamListener** → **需要清理**
```java
@RocketMQDynamicListener("topic-name")
@StreamListener(InputInterface.XXX_INPUT)
public void processXxx(@Payload String body) { ... }
```

**情况B：方法只有 @RocketMQDynamicListener** → **跳过清理**
```java
@RocketMQDynamicListener("topic-name")
public void processXxx(@Payload String body) { ... }
```

**情况C：方法只有 @StreamListener，没有 @RocketMQDynamicListener** → **跳过清理，记录到报告**

#### 4.3 执行清理

对于需要清理的方法：

1. **移除 @StreamListener 注解**
   ```java
   // 删除
   @StreamListener(InputInterface.XXX_INPUT)
   ```

2. **保留 @RocketMQDynamicListener 注解**
   ```java
   // 保留
   @RocketMQDynamicListener("topic-name")
   ```

3. **检查并修复日志格式**

   **错误格式**：
   ```java
   log.error("消费消息异常：{}, 异常信息: {}", body, e);
   ```

   **正确格式**：
   ```java
   log.error("消费消息异常：{}", body, e);
   ```

   **错误级别**：
   ```java
   log.info("消费消息异常", e);  // 应该用 error
   ```

   **正确级别**：
   ```java
   log.error("消费消息异常", e);
   ```

#### 4.4 清理类级别代码

**检查时机**：当所有 Input 方法都已清理完成

**执行操作**：
1. 移除 `@EnableBinding` 注解
   ```java
   // 删除
   @EnableBinding(InputInterface.class)
   ```

2. 清理未使用的 import
   ```java
   // 删除
   import org.springframework.cloud.stream.annotation.EnableBinding;
   import org.springframework.cloud.stream.annotation.StreamListener;
   ```

---

### 第五步：清理 InputInterface 和 OutputInterface

**重要原则**：
- ✅ 如果接口内容为空（所有常量都已清理），**删除整个接口类**
- ✅ 如果接口内容不为空（还有其他常量），**保留接口类**
- ✅ 删除接口后，需要清理所有引用该接口的地方

#### 5.1 检查接口是否为空

**对于 InputInterface**：
1. 读取 InputInterface.java 文件
2. 检查是否还有未清理的常量定义
3. 如果所有用户指定的 Input 常量都已清理，且没有其他常量，则接口为空

**对于 OutputInterface**：
1. 读取 OutputInterface.java 文件
2. 检查是否还有未清理的常量定义
3. 如果所有用户指定的 Output 常量都已清理，且没有其他常量，则接口为空

#### 5.2 删除空接口

如果接口为空：

1. **删除接口文件**
   ```bash
   git rm src/main/java/com/yl/css/online/stream/InputInterface.java
   git rm src/main/java/com/yl/css/online/stream/OutputInterface.java
   ```

2. **清理所有引用**

   搜索所有引用该接口的地方：
   ```bash
   rg "InputInterface" --type java
   rg "OutputInterface" --type java
   ```

   常见引用位置：
   - `@EnableBinding(InputInterface.class)` - 已在第四步清理
   - `import com.yl.css.online.stream.InputInterface;` - 需要删除
   - `import com.yl.css.online.stream.OutputInterface;` - 需要删除

3. **验证没有编译错误**

#### 5.3 保留非空接口

如果接口不为空：

1. **保留接口文件**
2. **可选：注释掉已清理的常量**
   ```java
   // 已清理: String LMDM_DATA_CHANGE_INPUT = "lmdm-data-change-input";
   ```
3. **在报告中说明保留了哪些常量**

---

### 第六步：清理 RocketMQGrayUtils 工具类

**重要原则**：如果项目中不再有任何地方调用 `RocketMQGrayUtils`，则应删除该工具类。

#### 6.1 检查 RocketMQGrayUtils 是否被使用

1. **搜索 RocketMQGrayUtils 的调用**
   ```bash
   rg "RocketMQGrayUtils" --type java
   ```

2. **分析搜索结果**
   - 如果搜索结果只包含 `RocketMQGrayUtils.java` 文件本身（类定义），说明该类已无调用
   - 如果搜索结果为空，说明该类可能已被删除
   - 如果搜索结果包含其他文件的调用，说明该类仍在使用，不能删除

#### 6.2 删除未被使用的 RocketMQGrayUtils

**前提条件**：
- ✅ 所有用户指定的 Output 方法都已清理完成
- ✅ 项目中不再有任何 `RocketMQGrayUtils.gray()` 调用
- ✅ 确认该类不是公共库的一部分（如 `com.yl.css.online.utils.RocketMQGrayUtils` 是项目内部工具类）

**执行操作**：

1. **记录并删除文件**
   ```bash
   # 先调用 MCP specBeforeEditFile 记录
   # 然后删除文件
   git rm src/main/java/com/yl/css/online/utils/RocketMQGrayUtils.java
   # 最后调用 MCP specAfterEditFile 记录
   ```

2. **清理所有引用**
   ```bash
   rg "import.*RocketMQGrayUtils" --type java
   ```
   如果有残留的 import 语句，需要清理。

#### 6.3 保留仍在使用的 RocketMQGrayUtils

如果项目中仍有其他地方使用 `RocketMQGrayUtils`：
- **保留该文件**
- **在报告中说明保留原因**：列出仍在使用的位置

---

### 第七步：MCP 记录

**重要**：在修改每个文件前后，必须调用 MCP 工具记录。

#### 6.1 修改前记录

```
mcp__spec-metrics-mcp__specBeforeEditFile
- absoluteFilePath: 文件绝对路径
- appName: 项目名称（从 pom.xml 或 git 仓库获取）
- sessionId: claude-YYYYMMDD-clean-rabbitmq
- teamId: sqs
- userId: git config user.name 的结果
- gitBranch: git rev-parse --abbrev-ref HEAD 的结果
```

#### 6.2 修改后记录

```
mcp__spec-metrics-mcp__specAfterEditFile
- absoluteFilePath: 文件绝对路径
- appName: 项目名称
- sessionId: claude-YYYYMMDD-clean-rabbitmq
- teamId: sqs
- userId: git config user.name 的结果
- gitBranch: git rev-parse --abbrev-ref HEAD 的结果
```

**注意事项**：
- 必须单文件单闭环执行，禁止先批量 before 再集中修改
- sessionId 必须在同一任务内保持稳定一致
- 每次修改都要记录，包括删除文件

---

### 第八步：生成清理报告

清理完成后，向用户报告：

## 清理结果

### ✅ 已成功清理的 Input/Output

**Output 列表** (MessageProducer):
- `xxx-output` - 对应方法 `sendXxx()`
- ...

**Input 列表** (MessageReceiver):
- `xxx-input` - 对应方法 `processXxx()`
- ...

### ⚠️ 未清理的 Input/Output (需要手动确认)

以下 Input/Output 对应的方法中没有 RocketMQ 相关代码或已经清理完成，请手动确认：

**Output 列表**:
- `xxx-output` - 原因: 方法内未使用 RocketMQ 发送逻辑 / 已经是纯 RocketMQ 实现

**Input 列表**:
- `xxx-input` - 原因: 方法未使用 @RocketMQDynamicListener 注解 / 已经是纯 RocketMQ 实现

### 🗑️ 已删除的接口

- `InputInterface.java` - 原因: 所有常量已清理，接口为空
- `OutputInterface.java` - 原因: 所有常量已清理，接口为空

### 📦 保留的接口

- `XxxInputInterface.java` - 原因: 接口内还有其他未清理的常量
  - 保留的常量: `XXX_INPUT`, `YYY_INPUT`

### 🧹 RocketMQGrayUtils 工具类

**已删除**:
- `RocketMQGrayUtils.java` - 原因: 项目中已无任何调用

**保留**:
- `RocketMQGrayUtils.java` - 原因: 以下位置仍在使用
  - `com.xxx.Service.method()` - 仍在使用灰度切换

### 📝 清理统计

- **总计**: X 个 Input/Output
- **已清理**: Y 个
- **未清理**: Z 个（需要手动确认）
- **已删除接口**: N 个
- **保留接口**: M 个

### 🔍 修改的文件

1. **MessageProducer.java**
   - 清理了 X 个发送方法
   - 移除了 @EnableBinding 注解
   - 移除了 OutputInterface 字段和构造函数
   - 清理了未使用的 import

2. **MessageReceiver.java**
   - 清理了 Y 个消费方法
   - 移除了 @StreamListener 注解
   - 移除了 @EnableBinding 注解
   - 修复了日志格式错误
   - 清理了未使用的 import

3. **已删除的文件**:
   - `InputInterface.java`
   - `OutputInterface.java`
   - `RocketMQGrayUtils.java` (如果无调用)

---

## 代码转换对照表

### 生产者转换模板

**转换前（灰度切换）**:
```java
public void sendXxx(XxxDTO data) {
    String topic = "sqs-xxx-topic";
    Message message = MessageBuilder.withPayload(data).build();

    Boolean result = RocketMQGrayUtils.gray(topic,
        () -> rocketMQDynamicPublisher.syncSend(topic, data),
        () -> outputInterface.xxxOutput().send(message));

    log.info("发送消息data={},result={}", JSON.toJSONString(data), result);
}
```

**转换后（纯 RocketMQ）**:
```java
public void sendXxx(XxxDTO data) {
    String topic = "sqs-xxx-topic";
    SendResult sendResult = rocketMQDynamicPublisher.syncSend(topic, data);
    Boolean result = sendResult.getSendStatus() == SendStatus.SEND_OK;
    log.info("发送消息data={},result={}", JSON.toJSONString(data), result);
}
```

### 消费者转换模板

**转换前（双监听）**:
```java
@RocketMQDynamicListener("sqs-xxx-topic")
@StreamListener(InputInterface.XXX_INPUT)
public void processXxx(@Payload String body) {
    log.info("消费消息：{}", body);
    try {
        // 业务逻辑
    } catch (Exception e) {
        log.error("消费消息异常：{}, 异常信息: {}", body, e);
    }
}
```

**转换后（纯 RocketMQ）**:
```java
@RocketMQDynamicListener("sqs-xxx-topic")
public void processXxx(@Payload String body) {
    log.info("消费消息：{}", body);
    try {
        // 业务逻辑
    } catch (Exception e) {
        log.error("消费消息异常：{}", body, e);
    }
}
```

---

## 注意事项

### 1. 判断是否需要清理的标准

**不要盲目清理**，必须先检查方法内是否有 RocketMQ 相关代码：

```java
// 需要清理的标志
RocketMQGrayUtils.gray(...)  // 有灰度切换
outputInterface.xxxOutput().send(...)  // 有 RabbitMQ 发送
@StreamListener  // 有 StreamListener 注解

// 不需要清理的标志
rocketMQDynamicPublisher.syncSend(...)  // 只有 RocketMQ 发送
@RocketMQDynamicListener  // 只有 RocketMQ 监听
```

### 2. 接口删除的条件

**必须同时满足以下条件才能删除接口**：
- ✅ 用户指定的所有常量都已清理
- ✅ 接口内没有其他未清理的常量
- ✅ 所有引用该接口的地方都已清理

**不能删除接口的情况**：
- ❌ 接口内还有其他未清理的常量
- ❌ 其他类还在使用该接口（即使常量已清理）

### 3. 日志格式规范

**正确格式**：
```java
log.error("消息异常：{}", body, e);  // 异常对象在最后，不需要占位符
log.info("处理消息：{}", body);  // 正常日志
```

**错误格式**：
```java
log.error("消息异常：{}, 异常信息: {}", body, e);  // 多余的占位符
log.info("消息异常", e);  // 错误的日志级别
```

### 4. MCP 记录要求

- **必须单文件单闭环**：一个文件的 beforeEditFile → 修改 → afterEditFile 完成后，才能处理下一个文件
- **sessionId 必须稳定**：整个清理任务使用同一个 sessionId
- **包括删除文件**：删除文件也需要记录 beforeEditFile 和 afterEditFile

### 5. RocketMQGrayUtils 删除条件

**必须同时满足以下条件才能删除 RocketMQGrayUtils**：
- ✅ 所有指定的 Output 方法都已清理完成
- ✅ 项目中不再有任何 `RocketMQGrayUtils.gray()` 调用
- ✅ 该类是项目内部工具类，不是公共库

**不能删除的情况**：
- ❌ 项目中还有其他地方使用该工具类
- ❌ 该类来自公共库（如 common 包）

### 6. 编译验证

清理完成后，建议执行编译验证：

```bash
mvn clean compile
```

确保没有编译错误，特别是：
- 没有找不到类的错误
- 没有未使用的 import 警告
- 没有方法签名不匹配的错误

---

## 常见问题

### 问题1：如何判断方法是否已经清理完成？

**答案**：检查方法内是否还有以下代码：
- `RocketMQGrayUtils.gray()`
- `outputInterface.xxxOutput().send()`
- `@StreamListener` 注解

如果都没有，说明已经清理完成，可以跳过。

### 问题2：接口内还有其他常量，怎么办？

**答案**：保留接口文件，不要删除。在报告中说明保留了哪些常量，让用户确认是否需要继续清理。

### 问题3：删除接口后编译报错怎么办？

**答案**：检查是否还有地方引用了该接口：
- 搜索 `import ...InputInterface`
- 搜索 `import ...OutputInterface`
- 搜索 `@EnableBinding(...Interface.class)`

清理所有引用后，编译错误应该消失。

### 问题4：用户提供的 Input/Output 名称在代码中找不到？

**答案**：在报告中列出未找到的名称，让用户确认：
- 名称是否正确
- 是否已经被清理
- 是否在其他模块中

### 问题5：RocketMQGrayUtils 什么时候需要删除？

**答案**：当满足以下所有条件时，应删除 RocketMQGrayUtils：
- 所有指定的 Output 方法都已清理完成（不再有灰度切换代码）
- 搜索 `rg "RocketMQGrayUtils" --type java` 结果只包含类定义文件本身
- 该类是项目内部工具类，不是公共库的一部分

如果项目中还有其他地方使用该类，则保留并在报告中说明。

---

## 检查清单

完成清理后，请确认以下事项：

- [ ] 所有指定的 Output 方法都已清理（或确认不需要清理）
- [ ] 所有指定的 Input 方法都已清理（或确认不需要清理）
- [ ] MessageProducer 类的 @EnableBinding 注解已移除（如果所有方法已清理）
- [ ] MessageReceiver 类的 @StreamListener 注解已移除
- [ ] MessageReceiver 类的 @EnableBinding 注解已移除（如果所有方法已清理）
- [ ] 未使用的 import 已清理
- [ ] 日志格式错误已修复
- [ ] 空接口已删除
- [ ] 接口引用已清理
- [ ] RocketMQGrayUtils 工具类已检查（无调用时删除，有调用时保留）
- [ ] MCP 记录已完成
- [ ] 编译验证通过
- [ ] 清理报告已生成

---

## 示例

### 清理需求示例

用户提供以下列表：
```
lmdm-data-change-input
session-create-close-evaluation-result-output
session-create-close-evaluation-result-input
im-chat-bot-knowledge-result-output
im-chat-bot-knowledge-result-input
```

### 执行步骤

1. **分类**：
   - Input: lmdm-data-change-input, session-create-close-evaluation-result-input, im-chat-bot-knowledge-result-input
   - Output: session-create-close-evaluation-result-output, im-chat-bot-knowledge-result-output

2. **查找文件**：
   - MessageProducer.java
   - MessageReceiver.java
   - InputInterface.java
   - OutputInterface.java

3. **清理 MessageProducer**：
   - sendSessionEventMessage() - 清理灰度切换，改为纯 RocketMQ
   - sendChatBotKnowledgeBaseId() - 清理灰度切换，改为纯 RocketMQ
   - 移除 @EnableBinding(OutputInterface.class)
   - 移除 outputInterface 字段和构造函数

4. **清理 MessageReceiver**：
   - lmdmDataChangeInput() - 移除 @StreamListener
   - processSessionMessage() - 移除 @StreamListener
   - chatBotKnowledge() - 移除 @StreamListener
   - 修复日志格式错误
   - 移除 @EnableBinding(InputInterface.class)

5. **清理接口**：
   - 检查 InputInterface - 所有常量已清理 → 删除文件
   - 检查 OutputInterface - 所有常量已清理 → 删除文件

6. **清理 RocketMQGrayUtils**：
   - 搜索 RocketMQGrayUtils 调用 → 无调用
   - 删除 RocketMQGrayUtils.java 文件

7. **生成报告**：
   - 已清理: 5 个
   - 未清理: 0 个
   - 已删除接口: 2 个
   - 已删除工具类: 1 个

### 最终代码示例

**MessageProducer.java**:
```java
@Component
@Slf4j
public class MessageProducer {

    @Resource
    private RocketMQDynamicPublisher rocketMQDynamicPublisher;

    public void sendSessionEventMessage(SessionMessageVO sessionMessageVO) {
        String topic = "sqs-online-create-close-evaluation-result";
        SendResult sendResult = rocketMQDynamicPublisher.syncSend(topic, sessionMessageVO);
        Boolean result = sendResult.getSendStatus() == SendStatus.SEND_OK;
        log.info("sendSessionWorkOrderMessage,data={},result={}", JSON.toJSONString(sessionMessageVO), result);
    }

    public void sendChatBotKnowledgeBaseId(Long knowledgeBaseId) {
        String topic = "sqs-online-chat-bot-knowledge";
        SendResult sendResult = rocketMQDynamicPublisher.syncSend(topic, knowledgeBaseId);
        Boolean result = sendResult.getSendStatus() == SendStatus.SEND_OK;
        log.info("预发布知识库id推送到队列 knowledgeBaseId={},result={}", knowledgeBaseId, result);
    }
}
```

**MessageReceiver.java**:
```java
@Component
@Slf4j
public class MessageReceiver {

    @Autowired
    private UserService userService;

    @Autowired
    private KnowledgeBaseService knowledgeBaseService;

    @RocketMQDynamicListener("lmdm-data-change-sys-staff")
    public void lmdmDataChangeInput(@Payload String body) {
        log.info("基础数据变更通知-消费消息：{}", body);
        SysStaffDTO sysStaffDTO = JsonUtils.toObject(body, SysStaffDTO.class);
        userService.staffChangeConsumer(sysStaffDTO);
    }

    @RocketMQDynamicListener("sqs-online-create-close-evaluation-result")
    public void processSessionMessage(@Payload String body) {
        log.info("processSessionMessage消费消息：{}", body);
        try {
            SessionMessageVO sessionMessage = JSON.parseObject(body, SessionMessageVO.class);
            sessionMessageService.processSessionMessage(sessionMessage);
        } catch (Exception e) {
            log.error("processSessionMessage消费消息异常：{}", body, e);
        }
    }

    @RocketMQDynamicListener("sqs-online-chat-bot-knowledge")
    public void chatBotKnowledge(@Payload String body) {
        log.info("预发布知识库ID body={}", body);
        knowledgeBaseService.knowledgeDataPushChatBotService();
    }
}
```
