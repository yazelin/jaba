## MODIFIED Requirements

### Requirement: 使用者訂單儲存
系統 SHALL 在 `users/{username}/orders/` 儲存使用者訂單，檔案格式為 `{date}-{order_id}.json`，支援同一天多筆訂單。

#### Scenario: 儲存新訂單
- **WHEN** 使用者建立訂單
- **THEN** 儲存為 `{date}-{timestamp}.json`（timestamp 為建立時間）

#### Scenario: 取得使用者當日訂單
- **WHEN** 查詢使用者今日訂單
- **THEN** 回傳該使用者當日所有訂單列表

### Requirement: 今日店家設定
系統 SHALL 在 `data/system/today.json` 儲存今日店家資訊，支援多店家同時營業。

#### Scenario: 今日店家結構
- **WHEN** 設定今日店家
- **THEN** 儲存為 `{ date, stores: [{ store_id, store_name, set_by, set_at }] }`

#### Scenario: 新增今日店家
- **WHEN** 管理員新增一個今日店家
- **THEN** 將店家加入 stores 陣列

## ADDED Requirements

### Requirement: 聊天記錄儲存
系統 SHALL 在 `data/chat/{date}.json` 儲存每日團隊聊天記錄。

#### Scenario: 聊天記錄結構
- **WHEN** 儲存聊天訊息
- **THEN** 格式為 `{ date, messages: [{ id, username, content, timestamp }] }`

#### Scenario: 新增聊天訊息
- **WHEN** 使用者發送訊息
- **THEN** 將訊息加入當日 messages 陣列

#### Scenario: 取得當日聊天記錄
- **WHEN** 使用者開啟頁面
- **THEN** 回傳當日所有聊天訊息
