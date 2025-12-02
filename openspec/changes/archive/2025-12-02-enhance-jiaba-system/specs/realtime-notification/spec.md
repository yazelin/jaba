## MODIFIED Requirements

### Requirement: 訂單事件廣播
系統 SHALL 在訂單建立、修改、取消、全部清除時廣播事件給所有連線者。

#### Scenario: 新訂單通知
- **WHEN** 有人完成訂餐
- **THEN** 廣播 order_created 事件，含 username、store_name、items、total

#### Scenario: 訂單修改通知
- **WHEN** 有人修改訂單
- **THEN** 廣播 order_updated 事件

#### Scenario: 訂單取消通知
- **WHEN** 有人取消訂單
- **THEN** 廣播 order_cancelled 事件

#### Scenario: 全部訂單清除通知
- **WHEN** 管理員清除所有訂單
- **THEN** 廣播 orders_cleared 事件

## ADDED Requirements

### Requirement: 聊天訊息即時同步
系統 SHALL 透過 Socket.IO 即時同步團隊聊天訊息。

#### Scenario: 廣播聊天訊息
- **WHEN** 使用者發送聊天訊息
- **THEN** 廣播 chat_message 事件給所有連線者
- **AND** 事件包含 username、content、timestamp

#### Scenario: 接收聊天訊息
- **WHEN** 收到 chat_message 事件
- **THEN** 前端即時更新聊天室顯示新訊息
