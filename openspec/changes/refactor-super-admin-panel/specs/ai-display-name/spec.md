# ai-display-name Specification

## Purpose
確保 AI 在與使用者對話時使用 display_name（LINE 顯示名稱）而非 LINE User ID。

## MODIFIED Requirements

### Requirement: AI 對話使用 display_name（修改自 ai-integration）
AI 對話系統 SHALL 使用使用者的 display_name 作為對話中的稱呼，而非 LINE User ID。

#### Scenario: 建立對話上下文
- **GIVEN** 使用者 profile 包含 `line_user_id` 和 `display_name`
- **WHEN** 呼叫 `build_context()` 建立 AI 上下文
- **THEN** `username` 欄位使用 `display_name` 值
- **AND** 內部識別使用 `line_user_id`

#### Scenario: AI 回應使用顯示名稱
- **GIVEN** 使用者 display_name 為「王小明」
- **WHEN** AI 回應訊息
- **THEN** 使用「王小明」稱呼使用者
- **AND** 不使用 LINE User ID (Uxxxxxxxxx)

#### Scenario: 群組對話歷史格式
- **GIVEN** 群組點餐對話歷史
- **WHEN** 格式化對話歷史給 AI
- **THEN** 使用 display_name 顯示每個訊息的發送者
- **AND** 格式如：「王小明: 我要雞腿便當」

#### Scenario: 訂單確認訊息
- **GIVEN** 使用者 display_name 為「王小明」
- **WHEN** AI 建立訂單並回應
- **THEN** 回應訊息使用「王小明」
- **AND** 如：「好喔，王小明點了雞腿便當 $85～」

### Requirement: 群組訂單上下文
AI 群組點餐模式 SHALL 在 session_orders 中包含 display_name。

#### Scenario: session_orders 格式
- **GIVEN** 群組點餐模式
- **WHEN** 建立 AI 上下文
- **THEN** session_orders 包含 display_name：
  ```json
  [
    {
      "display_name": "王小明",
      "items": [{"name": "雞腿便當", "price": 85, "quantity": 1}],
      "total": 85
    }
  ]
  ```

#### Scenario: 跟單處理使用 display_name
- **GIVEN** 對話歷史中「王小明」點了雞腿便當
- **WHEN** 「李大華」說「+1」
- **THEN** AI 回應使用 display_name
- **AND** 如：「收到！李大華也要雞腿便當 $85～」

### Requirement: Action 執行使用 line_user_id
AI 執行動作（action）時 SHALL 使用 line_user_id 作為內部識別，由系統自動處理。

#### Scenario: 建立訂單動作
- **GIVEN** AI 執行 `group_create_order` 動作
- **WHEN** 系統處理動作
- **THEN** 使用當前使用者的 `line_user_id` 儲存訂單
- **AND** 訂單記錄同時包含 `line_user_id` 和 `display_name`

#### Scenario: 更新偏好動作
- **GIVEN** AI 執行 `update_user_profile` 動作
- **WHEN** 系統處理動作
- **THEN** 使用 `line_user_id` 找到對應的 profile
- **AND** 更新偏好設定
