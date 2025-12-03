# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 多 CLI Provider 支援
系統 SHALL 支援在設定檔中為每個 AI 功能指定使用的 CLI 工具（provider）。

#### Scenario: 設定 provider
- **GIVEN** `ai_config.json` 中某功能設定 `provider` 欄位
- **WHEN** 呼叫該 AI 功能
- **THEN** 使用對應的 CLI 工具（claude 或 gemini）
- **AND** 若未指定 provider，預設使用 `claude`

#### Scenario: 不同功能使用不同 provider
- **GIVEN** chat 設定 `provider: "claude"`
- **AND** menu_recognition 設定 `provider: "gemini"`
- **WHEN** 使用者發送對話訊息
- **THEN** 執行 `claude` CLI
- **AND** 當管理員上傳菜單圖片時執行 `gemini` CLI

### Requirement: Claude CLI 命令建構
系統 SHALL 為 Claude CLI 建構正確的命令參數。

#### Scenario: Claude 對話命令
- **GIVEN** provider 為 `claude`
- **WHEN** 建構對話命令
- **THEN** 使用 `-p` 參數傳遞 prompt
- **AND** 使用 `--system-prompt` 傳遞系統提示
- **AND** 使用 `--model` 指定模型
- **AND** 首次對話使用 `--session-id`，後續使用 `--resume`

### Requirement: Gemini CLI 命令建構
系統 SHALL 為 Gemini CLI 建構正確的命令參數。

#### Scenario: Gemini 對話命令
- **GIVEN** provider 為 `gemini`
- **WHEN** 建構對話命令
- **THEN** 使用位置參數傳遞 prompt
- **AND** 將系統提示併入 prompt 開頭
- **AND** 使用 `-m` 或 `--model` 指定模型
- **AND** 使用 `-o json` 指定 JSON 輸出格式

### Requirement: Gemini Session 索引追蹤
系統 SHALL 為 Gemini CLI 維護每個使用者的 session 索引對照。

#### Scenario: Gemini 首次對話
- **GIVEN** provider 為 `gemini`
- **AND** 使用者今日無 session 記錄
- **WHEN** 建構對話命令
- **THEN** 不加 `--resume` 參數
- **AND** 執行後追蹤新建的 session 索引

#### Scenario: Gemini 後續對話
- **GIVEN** provider 為 `gemini`
- **AND** 使用者今日有 session 索引記錄
- **WHEN** 建構對話命令
- **THEN** 使用 `--resume <index>` 接續對話

### Requirement: Gemini 自動確認模式
系統 SHALL 在使用 Gemini CLI 執行需要工具的任務時啟用自動確認。

#### Scenario: 菜單辨識自動確認
- **GIVEN** provider 為 `gemini`
- **AND** 執行菜單辨識
- **WHEN** 建構命令
- **THEN** 使用 `-y` 或 `--yolo` 參數自動確認

### Requirement: 統一 Session 儲存格式
系統 SHALL 使用 JSON 格式儲存 session 資訊，支援不同 provider 的 session 追蹤需求。

#### Scenario: Session 檔案格式
- **GIVEN** 使用者開始對話
- **WHEN** 儲存 session 資訊
- **THEN** 寫入 `users/{username}/sessions/{date}.json`
- **AND** 包含 `provider`、`session_id`（Claude）、`session_index`（Gemini）等欄位

#### Scenario: 讀取 Session
- **GIVEN** 使用者繼續對話
- **WHEN** 讀取 session 資訊
- **THEN** 根據 provider 類型取得對應的 session 識別資訊

## MODIFIED Requirements

### Requirement: AI 模型設定
系統 SHALL 支援透過設定檔指定不同任務使用的 CLI provider 和模型。

#### Scenario: 讀取 AI 設定
- **GIVEN** 系統啟動或呼叫 AI 功能
- **WHEN** 讀取 `data/system/ai_config.json`
- **THEN** 取得各任務對應的 provider 和模型設定
- **AND** 若 provider 未指定則預設為 `claude`
- **AND** 若 model 未指定則使用各 provider 的預設模型

#### Scenario: 設定檔格式
- **GIVEN** `ai_config.json` 內容
- **WHEN** 解析設定
- **THEN** 支援以下格式：
```json
{
  "chat": {
    "provider": "claude",
    "model": "haiku"
  },
  "menu_recognition": {
    "provider": "gemini",
    "model": "gemini-2.5-pro"
  }
}
```
