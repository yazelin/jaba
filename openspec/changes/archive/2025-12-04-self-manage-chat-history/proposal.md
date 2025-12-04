# Proposal: self-manage-chat-history

## Status
draft

## Summary
移除對 Gemini/Claude CLI 內建 session 管理的依賴，改為自行管理對話歷史。每次 AI 呼叫時載入：(1) 系統上下文、(2) 使用者偏好、(3) 對話歷史，省去 CLI session 恢復的開銷和大型 session 檔案造成的 timeout 問題。

## Motivation

### 問題
1. **Session 檔案過大**：Gemini CLI session 檔案會持續累積，單一 session 可達 500KB+，恢復時造成 timeout
2. **CLI 開銷**：每次 `--resume` 都需要載入完整 session 歷史，隨著對話增長越來越慢
3. **依賴外部管理**：依賴 Gemini/Claude CLI 的 session 機制，難以控制和優化

### 解決方案
自行管理對話歷史：
- 對話歷史依使用者暫存，只保留必要的訊息
- 每次呼叫 AI 時，組合 context + history 到 prompt 中
- 不再使用 CLI 的 `--resume` / `--session-id`，每次都開新對話

### 已有的資料
1. **系統上下文** - `build_context()` 已經提供：店家、菜單、訂單、付款等
2. **使用者偏好** - `profile.json` 已經儲存：飲食限制、過敏等
3. **對話歷史** - **新增**：依使用者暫存當日對話

## Scope

### 包含
- 新增對話歷史暫存機制（per user, per day）
- 修改 `call_ai()` 組合對話歷史到 prompt
- 移除 CLI session 相關邏輯（`--resume`, `--session-id`）
- 前端頁面進入時清空歷史

### 不包含
- 前端 UI 變更
- prompt 內容調整
- 其他 AI 功能（菜單辨識等）

## Design
詳見 [design.md](design.md)

## Tasks
詳見 [tasks.md](tasks.md)
