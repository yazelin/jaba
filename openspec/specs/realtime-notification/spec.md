# realtime-notification Specification

## Purpose
TBD - created by archiving change add-data-architecture. Update Purpose after archive.
## Requirements
### Requirement: Socket.IO 即時連線
系統 SHALL 使用 Socket.IO 建立即時連線，所有使用者與管理員共享訂餐動態。

#### Scenario: 使用者連線
- **WHEN** 使用者開啟訂餐頁面
- **THEN** 自動建立 Socket.IO 連線

### Requirement: 訂單事件廣播
系統 SHALL 在訂單建立、修改、取消時廣播事件給所有連線者。

#### Scenario: 新訂單通知
- **WHEN** 有人完成訂餐
- **THEN** 廣播 order_created 事件，含 username、store_name、items、total

#### Scenario: 訂單修改通知
- **WHEN** 有人修改訂單
- **THEN** 廣播 order_updated 事件

#### Scenario: 訂單取消通知
- **WHEN** 有人取消訂單
- **THEN** 廣播 order_cancelled 事件

### Requirement: 團體訂餐看板
系統 SHALL 提供即時更新的團體訂餐看板，顯示當日所有人的訂單。

#### Scenario: 查看團體訂單
- **WHEN** 使用者查看看板
- **THEN** 顯示今日所有訂單、品項統計、總金額

#### Scenario: 即時更新看板
- **WHEN** 收到訂單事件
- **THEN** 前端自動更新看板內容

