## MODIFIED Requirements

### Requirement: 彈性訂餐
系統 SHALL 允許使用者每天建立多筆訂單，不限店家數量或同店家訂單數（如午餐+晚餐都訂同一間）。

#### Scenario: 建立訂單
- **WHEN** 使用者透過 AI 確認訂單
- **THEN** 建立 `users/{username}/orders/{date}-{order_id}.json`（order_id 為時間戳或 UUID）
- **AND** 更新 `orders/{date}/summary.json`

#### Scenario: 同一使用者同店家多筆訂單
- **WHEN** 使用者已訂 A 店午餐，再訂 A 店晚餐
- **THEN** 兩筆訂單分別儲存為不同 order_id
- **AND** 彙整中顯示為兩筆獨立訂單

#### Scenario: 同一使用者多店家訂單
- **WHEN** 使用者訂 A 店便當又訂 B 店飲料
- **THEN** 兩筆訂單分別儲存
- **AND** 彙整中按店家分組顯示

## ADDED Requirements

### Requirement: 管理員清除訂單
系統 SHALL 允許管理員透過 AI 清除訂單。

#### Scenario: 清除特定使用者特定訂單
- **WHEN** 管理員說「取消小明的 A 店訂單」
- **THEN** AI 執行 `cancel_order` 動作
- **AND** 刪除對應訂單檔案並更新彙整

#### Scenario: 清除特定使用者所有訂單
- **WHEN** 管理員說「取消小明今天所有訂單」
- **THEN** AI 執行 `cancel_order` 動作，清除該使用者當日所有訂單

#### Scenario: 清除所有今日訂單
- **WHEN** 管理員說「清除所有今日訂單」
- **THEN** AI 執行 `clear_all_orders` 動作
- **AND** 刪除今日所有訂單檔案與彙整

### Requirement: 歷史訂單清理
系統 SHALL 允許管理員清理歷史訂單。

#### Scenario: 清理指定日期前訂單
- **WHEN** 管理員說「清理一週前的訂單」
- **THEN** AI 執行 `clean_history_orders` 動作
- **AND** 刪除指定日期之前的訂單目錄
