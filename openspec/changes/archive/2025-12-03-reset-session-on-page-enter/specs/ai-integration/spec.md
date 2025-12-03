# ai-integration Spec Delta

## MODIFIED Requirements

### Requirement: Session 管理
系統 SHALL 在使用者每次進入對話頁面時重置 session，並在同一次訪問內維持對話延續。

#### Scenario: 進入訂購頁重置 session
- **GIVEN** 使用者輸入名字點擊「開始訂餐」
- **WHEN** 前端執行 `startChat()`
- **THEN** 先呼叫 `/api/session/reset` 清除舊 session
- **AND** 後續對話會建立新的 session

#### Scenario: 進入管理頁重置 session
- **GIVEN** 管理員進入管理頁面
- **WHEN** 頁面初始化
- **THEN** 呼叫 `/api/session/reset`（is_manager=true）清除舊 session
- **AND** 後續對話會建立新的 session

#### Scenario: 同一次訪問內延續對話
- **GIVEN** 使用者已開始對話且尚未離開頁面
- **WHEN** 使用者繼續發送訊息
- **THEN** 使用 `--resume` 延續同一個 session
- **AND** AI 能理解對話上下文（如確認型回應「好」、「對」）

#### Scenario: 重新進入頁面
- **GIVEN** 使用者重新整理頁面或重新進入
- **WHEN** 再次執行 `startChat()` 或管理頁初始化
- **THEN** 重置 session，開始全新對話
- **AND** 呷爸不會混淆先前訪問的對話內容

## REMOVED Scenarios

### ~~Scenario: 繼續對話（跨訪問）~~
- ~~**WHEN** 使用者今日已有 session~~
- ~~**THEN** 使用 `claude -r [sessionId]` 繼續對話~~

（移除跨訪問延續，改為每次進入頁面重置）

### ~~Scenario: 隔天新 session~~
- ~~**WHEN** 使用者隔天使用系統~~
- ~~**THEN** 建立新的 session，不延續昨日對話~~

（不再需要，因為每次進入頁面都會重置）
