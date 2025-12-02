## ADDED Requirements

### Requirement: 彈性訂餐
系統 SHALL 允許使用者隨時建立訂單，無固定週期限制。

#### Scenario: 建立訂單
- **WHEN** 使用者透過 AI 確認訂單
- **THEN** 建立 `users/{username}/orders/{date}.json`
- **AND** 更新 `orders/{date}/summary.json`

### Requirement: 訂單永久保留
系統 SHALL 永久保留所有訂單紀錄。

#### Scenario: 查詢歷史訂單
- **WHEN** 使用者查詢過去訂單
- **THEN** AI 讀取對應日期的訂單檔案

### Requirement: 每日訂單彙整
系統 SHALL 在 `orders/{date}/summary.json` 維護當日所有訂單彙整。

#### Scenario: 查看當日彙整
- **WHEN** 查看某日訂單
- **THEN** 顯示所有人的訂單與品項統計

### Requirement: 付款記錄
系統 SHALL 在 `orders/{date}/payments.json` 記錄付款狀態。

#### Scenario: 標記已付款
- **WHEN** 管理員標記某人已付款
- **THEN** 更新 paid 為 true 並記錄時間

#### Scenario: 查看未付款
- **WHEN** 管理員查看未付款清單
- **THEN** 列出 paid 為 false 的紀錄
