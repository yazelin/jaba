# Proposal: use-preferred-name-in-welcome

## Why
目前訂購頁和管理頁的歡迎詞是固定的「嗨！哇係呷爸，我們今天想吃什麼呢？」，沒有使用使用者的偏好稱呼（preferred_name）。

## What Changes
1. 修改 `/api/today` API，加上 `username` 參數，回傳該使用者的 `preferred_name`
2. 前端在知道 username 後重新呼叫 API 取得 `preferred_name`
3. 歡迎詞改為：
   - 有設定：`哇係呷爸，{preferred_name}今天想吃什麼呢？`
   - 沒設定：`哇係呷爸，我們今天想吃什麼呢？`

## Scope
- `main.py` - 修改 `/api/today` 端點
- `templates/order.html` - 修改歡迎詞邏輯
- `templates/manager.html` - 同上

## Out of Scope
- 新增欄位
- 修改 profile 結構
- AI 產生歡迎詞
