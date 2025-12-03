# order-management Spec Delta

## ADDED Requirements

### Requirement: 訂單品項移除
系統 SHALL 支援從現有訂單中移除特定品項，而非建立新訂單。

#### Scenario: 移除訂單中的一個品項
- **GIVEN** 使用者有訂單包含 [排骨便當, 味噌湯]
- **WHEN** 使用者說「不要排骨便當」
- **AND** AI 執行 `remove_item` 動作
- **THEN** 從訂單中移除排骨便當
- **AND** 訂單變成只有 [味噌湯]
- **AND** 更新 daily summary
- **AND** 更新 payments 記錄

#### Scenario: 移除訂單中的唯一品項
- **GIVEN** 使用者有訂單只包含 [味噌湯]
- **WHEN** 使用者說「不要湯了」
- **AND** AI 執行 `remove_item` 動作
- **THEN** 刪除整筆訂單
- **AND** 更新 daily summary
- **AND** 更新 payments 記錄

#### Scenario: 減少品項數量
- **GIVEN** 使用者有訂單包含 [雞腿便當 x2]
- **WHEN** 使用者說「少一個雞腿便當」
- **AND** AI 執行 `remove_item` 動作 (quantity: 1)
- **THEN** 訂單變成 [雞腿便當 x1]
- **AND** 重新計算訂單總額

#### Scenario: 跨訂單移除品項
- **GIVEN** 使用者有多筆訂單，其中一筆包含目標品項
- **WHEN** AI 執行 `remove_item` 動作
- **THEN** 從包含該品項的訂單中移除
- **AND** 不影響其他訂單

### Requirement: 訂單修改邏輯
系統 SHALL 根據操作類型選擇正確的處理方式。

#### Scenario: 新增不在現有訂單中的品項
- **GIVEN** 使用者現有訂單不包含品項 X
- **WHEN** 使用者說「加一個 X」
- **THEN** AI 執行 `create_order` 建立新訂單
- **AND** 新訂單包含品項 X

#### Scenario: 移除現有訂單中的品項
- **GIVEN** 使用者現有訂單包含品項 X
- **WHEN** 使用者說「不要 X」
- **THEN** AI 執行 `remove_item` 動作
- **AND** 不執行 `create_order`
- **AND** 不會產生重複品項
