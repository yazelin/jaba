# Tasks: support-multi-cli-provider

## Phase 1: 抽象層建立（先用 Claude 測試）

### Session 儲存重構
- [x] 將 session 儲存格式從 `.txt` 改為 `.json`
- [x] 新增 `SessionInfo` 資料結構（provider, session_id, session_index）
- [x] 修改 `data.py` 的 `get_session_id()` → `get_session_info()`
- [x] 修改 `data.py` 的 `save_session_id()` → `save_session_info()`
- [x] 修改 `data.py` 的 `clear_session_id()` → `clear_session_info()`

### Provider 抽象
- [x] 更新 `ai_config.json` 格式，新增 provider 欄位
- [x] 新增 `_build_claude_command()` 函式封裝 Claude CLI 命令建構
- [x] 修改 `call_claude()` 使用新的 session 與命令建構函式
- [x] 修改 `recognize_menu_image()` 使用新的命令建構函式

### 驗證
- [x] 測試 Claude provider 對話功能（首次、後續、重置）
- [x] 測試 Claude provider 菜單辨識功能
- [x] 確認 session 檔案格式正確

## Phase 2: Gemini 支援

### Gemini 命令建構
- [x] 新增 `_build_gemini_command()` 函式
- [x] 處理 system prompt 併入 prompt 開頭
- [x] 不使用 `-o json`（讓模型直接回應 prompt 要求的 JSON 格式）
- [x] 統一解析邏輯：移除 markdown code block 後解析 JSON

### Gemini Session 管理
- [x] 實作 Gemini session 索引追蹤（解析 `--list-sessions`，注意輸出在 stderr）
- [x] 實作 Gemini 後續對話的 `--resume <index>` 邏輯
- [x] 實作 Gemini session 重置邏輯（含 `--delete-session`）

### 驗證
- [x] 測試 Gemini provider 對話功能（注意：Gemini CLI 的 session 記憶有限）
- [x] 測試 Gemini provider 菜單辨識功能（使用 @檔名 語法）
- [x] 測試混合使用（chat 用 Claude、menu_recognition 用 Gemini）
- [x] 測試多使用者同時使用 Gemini 的 session 隔離
