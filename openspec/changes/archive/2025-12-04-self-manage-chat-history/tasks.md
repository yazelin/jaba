# Tasks: self-manage-chat-history

## 對話歷史管理
- [x] 在 `app/data.py` 新增 `get_ai_chat_history()`
- [x] 在 `app/data.py` 新增 `append_ai_chat_history()`
- [x] 在 `app/data.py` 新增 `clear_ai_chat_history()`
- [x] 實作歷史長度限制（最多 20 條訊息）

## AI 呼叫修改
- [x] 修改 `app/ai.py` 的 `call_ai()` 組合對話歷史
- [x] 新增 `_format_chat_history()` 格式化函數
- [x] 儲存使用者訊息到歷史
- [x] 儲存 AI 回應到歷史

## Provider 簡化
- [x] 簡化 `app/providers/gemini.py` - 移除 session 相關邏輯
- [x] 簡化 `app/providers/claude.py` - 移除 session 相關邏輯
- [x] 更新 `app/providers/__init__.py` - 簡化 BaseProvider 介面

## 頁面進入清空
- [x] 修改 `main.py` 的 `/api/session/reset` endpoint 清空對話歷史
- [x] order.html 已有呼叫（無需修改）
- [x] manager.html 已有呼叫（無需修改）

## reset_session 動作更新
- [x] 將 `_reset_session()` 改為清空對話歷史（不再刪除 CLI session）

## 測試驗證
- [x] 測試對話功能（訊息記憶）
- [x] 測試頁面重新進入（歷史清空）
- [x] 測試長對話（歷史長度限制）
- [x] 測試 Claude 和 Gemini provider
