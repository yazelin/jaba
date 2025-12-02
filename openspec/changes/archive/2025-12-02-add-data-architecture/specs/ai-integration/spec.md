## ADDED Requirements

### Requirement: Claude CLI 整合
系統 SHALL 透過 subprocess 執行 Claude CLI 與 AI Agent 互動，不使用 API。

#### Scenario: 呼叫 AI Agent
- **WHEN** 使用者發送訊息
- **THEN** 後端執行 `claude -p` 命令並解析 JSON 回應

### Requirement: Session 管理
系統 SHALL 為每個使用者每天維護獨立的 Claude session，儲存於 `users/{username}/sessions/{date}.txt`。

#### Scenario: 新使用者首次對話
- **WHEN** 使用者今日首次發送訊息
- **THEN** 建立新 session 並儲存 session ID

#### Scenario: 繼續對話
- **WHEN** 使用者今日已有 session
- **THEN** 使用 `claude -r [sessionId]` 繼續對話

#### Scenario: 隔天新 session
- **WHEN** 使用者隔天使用系統
- **THEN** 建立新的 session，不延續昨日對話

### Requirement: 前端名稱暫存
系統 SHALL 在前端使用 localStorage 儲存使用者名稱，下次自動填入。

#### Scenario: 記住使用者名稱
- **WHEN** 使用者輸入名稱並開始對話
- **THEN** 將名稱存入 localStorage

#### Scenario: 自動填入名稱
- **WHEN** 使用者再次開啟頁面
- **THEN** 自動填入上次使用的名稱

### Requirement: AI 動作執行
系統 SHALL 根據 AI 回應的 action 執行對應操作並廣播事件。

#### Scenario: 執行建立訂單
- **WHEN** AI 回應 action.type 為 create_order
- **THEN** 建立訂單、更新彙整、廣播 order_created
