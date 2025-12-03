# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 對話上下文延續
系統 SHALL 維護使用者的對話上下文，讓 AI 能記住之前的對話內容。

#### Scenario: 首次對話建立 session
- **GIVEN** 使用者今日首次與 AI 對話
- **WHEN** 呼叫 `call_claude()`
- **THEN** 系統生成新的 UUID 作為 session ID
- **AND** 使用 `--session-id <uuid>` 參數建立對話
- **AND** 儲存 session ID 到 `users/{username}/sessions/{date}.txt`

#### Scenario: 後續對話恢復上下文
- **GIVEN** 使用者今日已有 session ID
- **WHEN** 呼叫 `call_claude()`
- **THEN** 使用 `--resume <sessionId>` 參數恢復對話
- **AND** AI 能理解之前對話的上下文

#### Scenario: 確認型回應
- **GIVEN** AI 詢問「要我幫你設定嗎？」
- **WHEN** 使用者回應「好」
- **THEN** AI 理解這是對之前提議的確認
- **AND** 執行之前提議的動作
