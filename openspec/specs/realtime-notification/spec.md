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

### Requirement: 店家設定聊天通知
系統 SHALL 在管理員設定今日店家時，自動在團體聊天室新增系統訊息。

#### Scenario: 設定店家時新增聊天訊息
- **GIVEN** 管理員透過 AI 設定今日店家
- **WHEN** 系統廣播 `store_changed` 事件
- **THEN** 在團體聊天室新增一則系統訊息
- **AND** 訊息內容包含店家名稱和可開始訂餐提示
- **AND** 訊息以 "呷爸" 為發送者

#### Scenario: 離線使用者查看聊天記錄
- **GIVEN** 使用者當時不在線上
- **WHEN** 使用者稍後開啟訂餐頁面
- **THEN** 在團體聊天記錄中看到店家設定的系統訊息
- **AND** 得知今日可訂購的店家

