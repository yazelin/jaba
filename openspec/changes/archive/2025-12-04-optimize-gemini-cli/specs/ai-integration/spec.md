## ADDED Requirements

### Requirement: Gemini CLI 命令建構優化
系統 SHALL 為 Gemini CLI 建構正確的命令參數，使用指定模型並支援 session 恢復。

#### Scenario: Gemini 對話命令
- **GIVEN** provider 為 `gemini`
- **WHEN** 建構對話命令
- **THEN** 使用 `-m` 指定模型（由 ai_config 載入，預設 `gemini-2.5-flash-lite`）
- **AND** 使用位置參數傳遞 prompt
- **AND** 將系統提示併入 prompt 開頭
- **AND** 若有現有 session UUID，使用 `--resume <uuid>` 恢復對話

### Requirement: Gemini 回應解析
系統 SHALL 正確解析 Gemini CLI 的回應，並在格式解析失敗時顯示 AI 的實際回應。

#### Scenario: 解析 AI 回應
- **GIVEN** Gemini CLI 回傳 stdout
- **WHEN** 解析回應
- **THEN** 清理可能的 markdown code block 包裝
- **AND** 嘗試從回應中提取我們的 JSON 格式

#### Scenario: AI 回應非 JSON 格式
- **GIVEN** AI 回應文字不是有效的 JSON
- **WHEN** 解析回應
- **THEN** 直接將 AI 回應文字作為 `message` 回傳
- **AND** `actions` 為空陣列
- **AND** 不視為錯誤（AI 可能只是聊天回應）

#### Scenario: 解析失敗時提供診斷資訊
- **GIVEN** 回應無法解析
- **WHEN** 發生 JSON 解析錯誤
- **THEN** 回傳 `error: "parse_error"`
- **AND** 回傳 `raw_response` 包含原始輸出（截取前 500 字元）
- **AND** `message` 欄位包含 AI 的實際回應（截取前 300 字元）

### Requirement: Gemini Session 自管理
系統 SHALL 透過讀取 Gemini CLI 的 session 檔案來管理 session，取代 `--list-sessions` 呼叫。

#### Scenario: 首次對話建立 Session
- **GIVEN** 使用者沒有現有的 Gemini session UUID
- **WHEN** 執行 Gemini 對話
- **THEN** 不帶 `--resume` 參數執行
- **AND** 對話完成後從 `~/.gemini/tmp/*/chats/` 目錄找新建的 session 檔案
- **AND** 讀取檔案內的 `sessionId` 欄位取得完整 UUID
- **AND** 儲存 UUID 到我們的 session 管理

#### Scenario: 恢復現有 Session
- **GIVEN** 使用者有儲存的 Gemini session UUID
- **WHEN** 執行 Gemini 對話
- **THEN** 使用 `--resume <uuid>` 參數恢復 session
- **AND** Gemini 會記得之前的對話內容

### Requirement: 前端顯示 AI 實際回應
系統 SHALL 在前端顯示 AI 的實際回應，即使格式不符預期也能讓使用者看到內容。

#### Scenario: 顯示超時錯誤
- **GIVEN** AI 回應包含 `error: "timeout"`
- **WHEN** 前端處理回應
- **THEN** 顯示「回應超時，請再試一次」

#### Scenario: 顯示格式解析失敗的回應
- **GIVEN** AI 回應包含 `error: "parse_error"`
- **WHEN** 前端處理回應
- **THEN** 顯示 `message` 欄位的內容（AI 的實際回應）
- **AND** 不顯示技術性錯誤訊息給一般使用者

#### Scenario: 正常顯示 AI 回應
- **GIVEN** AI 回應無 `error` 欄位
- **WHEN** 前端處理回應
- **THEN** 顯示 `message` 欄位的內容
