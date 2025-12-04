# AI Chat Capability Changes

## ADDED Requirements

### Requirement: REQ-CHAT-HISTORY - Self-managed chat history
系統 SHALL 自行管理對話歷史，而非依賴 CLI 的 session 機制。

- 對話歷史 MUST 依使用者儲存，檔案位於 `data/users/{username}/chat_history/`
- 每次 AI 呼叫時 SHALL 將歷史組合到 prompt 中
- 歷史長度 MUST 限制最多 20 條訊息
- 頁面進入時（/order, /manager）MUST 自動清空歷史

#### Scenario: 多輪對話記憶
Given 使用者已經說過「我要雞腿飯」
When 使用者說「再加一杯紅茶」
Then AI 能理解是要在雞腿飯訂單上加紅茶

#### Scenario: 頁面重新進入
Given 使用者已經有對話歷史
When 使用者重新進入訂購頁面
Then 對話歷史被清空，AI 不記得先前對話

#### Scenario: 長對話限制
Given 使用者已有 25 條對話訊息
When 系統取得對話歷史
Then 只返回最近 20 條訊息

## MODIFIED Requirements

### Requirement: REQ-AI-CALL - AI 呼叫流程
AI 呼叫流程 SHALL 不再使用 CLI session 機制。

- 每次呼叫 MUST 都是新對話，不使用 `--resume` 或 `--session-id`
- Prompt MUST 包含：系統上下文 + 對話歷史 + 當前訊息
- 呼叫前後 SHALL 分別儲存使用者訊息和 AI 回應

#### Scenario: 首次對話
Given 使用者沒有對話歷史
When 使用者發送訊息
Then AI 被呼叫時不帶任何 session 參數
And 使用者訊息和 AI 回應被儲存到歷史

#### Scenario: 後續對話
Given 使用者有 3 輪對話歷史
When 使用者發送新訊息
Then Prompt 包含先前 6 條訊息（3 輪 x 2）
And 新的訊息和回應被追加到歷史

## REMOVED Requirements

- REQ-CLI-SESSION: CLI Session 管理 - 移除對 CLI 內建 session 機制的依賴
  - 不再使用 Gemini 的 `--resume <uuid>`
  - 不再使用 Claude 的 `--resume` / `--session-id`
  - 移除 session 檔案追蹤邏輯
