## ADDED Requirements

### Requirement: 團隊聊天室
系統 SHALL 提供獨立於 AI 對話的團隊聊天室，讓所有訂購人和管理員可以即時溝通。

#### Scenario: 發送聊天訊息
- **WHEN** 使用者在聊天室輸入訊息並送出
- **THEN** 訊息儲存至 `data/chat/{date}.json`
- **AND** 透過 Socket.IO 廣播 `chat_message` 事件給所有連線者

#### Scenario: 即時接收訊息
- **WHEN** 其他使用者發送訊息
- **THEN** 本地聊天室自動更新顯示新訊息
- **AND** 新訊息自動捲動到底部

#### Scenario: 載入歷史訊息
- **WHEN** 使用者開啟頁面
- **THEN** 自動載入當日所有歷史聊天訊息

### Requirement: 聊天記錄保留
系統 SHALL 保留每日聊天記錄於 `data/chat/{date}.json`。

#### Scenario: 聊天記錄結構
- **WHEN** 儲存聊天訊息
- **THEN** 訊息包含 id、username、content、timestamp 欄位

#### Scenario: 隔日清除
- **WHEN** 日期變更
- **THEN** 新的一天使用新的聊天記錄檔案

### Requirement: 聊天室 UI
系統 SHALL 在訂餐頁、管理頁、看板頁提供聊天室視窗。

#### Scenario: 聊天室顯示
- **WHEN** 使用者開啟任一頁面
- **THEN** 可看到團隊聊天室視窗
- **AND** 聊天室與 AI 對話區域分開

#### Scenario: 看板頁聊天室可摺疊
- **WHEN** 在看板頁
- **THEN** 聊天室可摺疊以節省空間
