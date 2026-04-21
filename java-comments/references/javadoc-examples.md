# JavaDoc 与方法体注释示例

## 示例 1：多参数方法

```java
/**
 * 作用：创建工单并触发后续派发流程。
 * 说明：请求号必须全局唯一，用于幂等去重。
 *
 * 参数示例（JSON）：
 * <pre>{@code
 * {
 *   "requestNo": "REQ-20260319-001",
 *   "tenantId": 1001,
 *   "payload": {
 *     "workOrderType": "INSTALL",
 *     "priority": "HIGH"
 *   }
 * }
 * }</pre>
 *
 * @param requestNo 请求唯一号，用于幂等控制
 * @param tenantId 租户标识
 * @param payload 创建工单时的业务载荷
 * @return 新建工单 ID
 * @throws BizException 当请求号重复或参数不合法时抛出
 */
public Long createWorkOrder(String requestNo, Long tenantId, CreateWorkOrderPayload payload) {
    // 先校验请求参数，避免无效数据进入领域层。
    validator.checkCreatePayload(payload);

    // 基于请求号做幂等校验，防止重复重试导致多次创建。
    idempotentService.assertNotProcessed(requestNo);

    // 持久化工单主数据，并返回主键供后续派发链路使用。
    return workOrderRepository.insert(requestNo, tenantId, payload);
}
```

## 示例 2：无参方法

```java
/**
 * 作用：扫描超时未完成的工单并触发后续处理。
 *
 * 参数示例（JSON）：
 * <pre>{@code
 * {}
 * }</pre>
 *
 * @return 本次扫描命中的工单数量
 */
public int scanTimeoutWorkOrders() {
    // 只扫描处理中状态，避免误处理已完结或已关闭工单。
    return timeoutScanner.scanProcessingOrders();
}
```

## 示例 3：带状态校验与外部调用的方法

```java
/**
 * 作用：审核通过后推送工单到下游施工系统。
 * 说明：只有待派发状态的工单允许继续流转。
 *
 * @param workOrderId 工单 ID
 * @param operator 当前操作人
 * @throws BizException 当工单状态非法或下游调用失败时抛出
 */
public void dispatchWorkOrder(Long workOrderId, String operator) {
    // 派发前先校验状态，避免已派发数据重复进入下游系统。
    WorkOrder workOrder = workOrderRepository.findById(workOrderId);
    validateDispatchable(workOrder);

    // 记录操作轨迹，便于后续审计和问题排查。
    operationLogService.recordDispatch(workOrderId, operator);

    // 调用下游施工系统前更新本地状态，确保失败时可做补偿处理。
    workOrderRepository.markDispatching(workOrderId, operator);
    constructionClient.dispatch(workOrder);
}
```
