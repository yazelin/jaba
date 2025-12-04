# Proposal: optimize-gemini-cli

## Why

使用 Gemini CLI 時發現幾個問題影響使用體驗：

1. **回應速度慢**
   - 前端感覺回應非常慢，有時甚至超時
   - **主因**：每次新 session 後需額外呼叫 `--list-sessions` 取得索引（約 2-5 秒）
   - 次因：Gemini CLI 啟動時間本身較長

2. **輸出格式不穩定**
   - Gemini 模型不保證遵循我們 prompt 要求的 JSON 格式
   - 可能回傳 markdown code block、純文字、或不完整的 JSON
   - 這是模型行為問題，無法完全解決

3. **錯誤訊息不明確**
   - JSON 解析失敗時，前端只顯示「AI 沒有回應」
   - 使用者看不到 AI 實際回應內容，無法診斷問題

## What Changes

1. **Session 自管理（取代 `--list-sessions`）**
   - Gemini session 檔案儲存在 `~/.gemini/tmp/<project_hash>/chats/`
   - 檔名格式：`session-YYYY-MM-DDTHH-MM-<uuid前8碼>.json`
   - 檔案內含完整 `sessionId` 欄位，可直接用 `--resume <uuid>` 恢復
   - **新方案**：監控 chats 目錄取得新建的 session UUID，省去 `--list-sessions` 開銷
   - 這樣既保留對話記憶，又不需要額外 2-5 秒的索引查詢

2. **Gemini 預設模型**
   - 模型由 `ai_config.json` 載入
   - 若未指定模型，chat 預設使用 `gemini-2.5-flash-lite`（較快）

3. **改進錯誤處理與回饋**
   - 當 JSON 解析失敗時，直接顯示 AI 的原始回應
   - 區分「AI 沒回應」vs「回應格式錯誤」vs「執行錯誤」

4. **前端顯示實際回應**
   - 即使格式解析失敗，也顯示 AI 的回應內容
   - 讓使用者至少能看到 AI 說了什麼

## Scope

- ai-integration spec
