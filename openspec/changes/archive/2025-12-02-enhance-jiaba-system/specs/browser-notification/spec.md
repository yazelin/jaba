## ADDED Requirements

### Requirement: 通知權限請求
系統 SHALL 在使用者首次進入頁面時請求瀏覽器通知權限。

#### Scenario: 請求通知權限
- **WHEN** 使用者首次進入任一頁面
- **THEN** 顯示請求通知權限的提示
- **AND** 使用者可選擇允許或拒絕

#### Scenario: 記住權限狀態
- **WHEN** 使用者已授權或拒絕通知
- **THEN** 不再重複請求（由瀏覽器管理）

### Requirement: 聊天訊息通知
系統 SHALL 在收到新聊天訊息時發送瀏覽器通知。

#### Scenario: 發送聊天通知
- **WHEN** 收到 chat_message 事件且訊息非本人發送
- **THEN** 發送瀏覽器通知，標題為發送者名稱，內容為訊息內容

#### Scenario: 點擊通知開啟頁面
- **WHEN** 使用者點擊聊天通知
- **THEN** 開啟或聚焦到訂餐頁面

### Requirement: 訂單事件通知
系統 SHALL 在訂單相關事件發生時發送瀏覽器通知。

#### Scenario: 新訂單通知
- **WHEN** 收到 order_created 事件
- **THEN** 發送通知「{username} 訂了便當！」

#### Scenario: 訂單取消通知
- **WHEN** 收到 order_cancelled 事件
- **THEN** 發送通知「{username} 取消了訂單」

#### Scenario: 全部清除通知
- **WHEN** 收到 orders_cleared 事件
- **THEN** 發送通知「管理員已清除所有訂單」

### Requirement: 店家變更通知
系統 SHALL 在今日店家變更時發送瀏覽器通知。

#### Scenario: 店家變更通知
- **WHEN** 收到 store_changed 事件
- **THEN** 發送通知「今日店家已更新：{store_name}」
