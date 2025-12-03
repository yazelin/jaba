# ai-integration Spec Delta

## ADDED Requirements

### Requirement: AI 訂單操作指引
系統 SHALL 在 prompt 中指示呷爸根據使用者意圖選擇正確的訂單動作。

#### Scenario: 呷爸查看現有訂單
- **GIVEN** 使用者要求修改訂單
- **WHEN** 呷爸處理請求
- **THEN** 先查看 context 中的 `current_orders`
- **AND** 了解使用者目前有哪些訂單和品項

#### Scenario: 呷爸移除品項
- **GIVEN** 使用者說「不要 X」或「取消 X」
- **AND** `current_orders` 中有品項 X
- **WHEN** 呷爸執行動作
- **THEN** 使用 `remove_item` 動作
- **AND** 不使用 `create_order`

#### Scenario: 呷爸新增品項
- **GIVEN** 使用者說「加一個 X」或「我要 X」
- **AND** `current_orders` 中沒有品項 X（或使用者明確要新增）
- **WHEN** 呷爸執行動作
- **THEN** 使用 `create_order` 動作

### Requirement: remove_item 動作格式
系統 SHALL 支援 `remove_item` 動作讓 AI 從現有訂單移除品項。

#### Scenario: AI 執行 remove_item
- **GIVEN** AI 回應包含 `action.type` 為 `remove_item`
- **AND** `action.data` 包含 `item_name` 和可選的 `quantity`
- **WHEN** 系統執行該動作
- **THEN** 從使用者訂單中移除指定品項
- **AND** 回傳更新後的訂單狀態
