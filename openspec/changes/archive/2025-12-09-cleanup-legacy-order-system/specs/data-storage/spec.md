# data-storage Spec Delta

## ADDED Requirements

### Requirement: 群組訂單儲存
系統 SHALL 將群組訂單儲存在群組 session 檔案中。

#### Scenario: 儲存群組訂單
- **GIVEN** 使用者在群組中點餐
- **WHEN** 建立訂單
- **THEN** 訂單存在 `linebot/sessions/{group_id}.json` 的 `orders` 陣列中

#### Scenario: 付款追蹤
- **GIVEN** 群組有訂單
- **WHEN** 追蹤付款狀態
- **THEN** 付款記錄存在 `linebot/sessions/{group_id}.json` 的 `payments` 物件中
