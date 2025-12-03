# data-storage Spec Delta

## ADDED Requirements

### Requirement: 今日店家資料格式
系統 SHALL 統一使用 `stores[]` 陣列格式儲存今日店家，不再維護冗餘的頂層欄位。

#### Scenario: 儲存今日店家
- **GIVEN** 管理員設定今日店家
- **WHEN** 系統儲存至 `system/today.json`
- **THEN** 只使用 `stores[]` 陣列儲存
- **AND** 不設定頂層 `store_id` 和 `store_name`

#### Scenario: 讀取今日店家
- **GIVEN** 系統讀取 `system/today.json`
- **WHEN** 處理店家資訊
- **THEN** 直接使用 `stores[]` 陣列
- **AND** 不需要檢查頂層欄位

### Requirement: 訂單檔案格式
系統 SHALL 統一使用 `{date}-{timestamp}.json` 格式儲存使用者訂單。

#### Scenario: 儲存訂單
- **GIVEN** 使用者建立訂單
- **WHEN** 系統儲存訂單
- **THEN** 使用 `{date}-{timestamp}.json` 格式命名
- **AND** 不使用舊的 `{date}.json` 格式

#### Scenario: 讀取訂單
- **GIVEN** 系統讀取使用者訂單
- **WHEN** 搜尋訂單檔案
- **THEN** 只匹配 `{date}-*.json` 模式
- **AND** 不檢查 `{date}.json` 舊格式
