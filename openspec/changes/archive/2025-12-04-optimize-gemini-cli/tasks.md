# Tasks: optimize-gemini-cli

## Gemini Provider 優化
- [x] 修改 `build_chat_command()` 支援預設模型（若未指定則用 `gemini-2.5-flash-lite`）
- [x] 實作 `find_gemini_chats_dir()` 找到 Gemini session 目錄
- [x] 實作 `get_session_id_from_file()` 從新建 session 檔案取得 UUID
- [x] 修改 `build_chat_command()` 支援 `--resume <uuid>`

## Session 管理優化
- [x] 移除 `get_session_info_after_call()` 中的 `--list-sessions` 呼叫
- [x] 改為讀取 session 檔案取得 UUID（在命令執行後）
- [x] 更新 `ai.py` 中 Gemini 相關的 session 處理
- [x] 確保 session UUID 正確儲存到我們的 session 管理

## 錯誤處理改進
- [x] 更新 `parse_response()` 在解析失敗時回傳 AI 實際回應
- [x] 回傳 `raw_response` 供診斷

## 前端錯誤顯示
- [x] `order.html`：顯示更詳細的錯誤訊息
- [x] `manager.html`：顯示更詳細的錯誤訊息
- [x] 區分 timeout、parse_error、其他錯誤

## 測試驗證
- [x] 測試 Gemini 對話功能（回應速度、格式正確性）
- [x] 測試 Gemini session 恢復功能（對話記憶）
- [x] 測試 Claude 對話功能（確保不受影響）
- [x] 測試菜單辨識功能（Gemini）
- [x] 測試錯誤情境（超時、格式錯誤）
