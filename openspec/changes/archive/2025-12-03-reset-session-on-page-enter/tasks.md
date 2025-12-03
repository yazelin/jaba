# Tasks: reset-session-on-page-enter

## Implementation Tasks

### 1. 新增 session 重置 API
- [x] 在 `main.py` 新增 `POST /api/session/reset` 端點
- [x] 接受 `username` 和 `is_manager` 參數
- [x] 呼叫 `data.clear_session_id()` 清除 session

### 2. 修改訂購頁 startChat 流程
- [x] 在 `templates/order.html` 的 `startChat()` 函數中
- [x] 在顯示歡迎訊息前呼叫 `/api/session/reset`
- [x] 確保重置完成後再開始對話

### 3. 修改管理頁初始化流程
- [x] 在 `templates/manager.html` 的 `verifyPassword()` 成功後
- [x] 呼叫 `/api/session/reset`（is_manager=true）
- [x] 確保重置完成後再開始對話

## Verification
- [x] 訂購頁：重新整理後，呷爸不會延續舊對話上下文
- [x] 訂購頁：同一次訪問內，「好」等確認回應能正常運作
- [x] 管理頁：重新整理後，呷爸不會延續舊對話上下文
- [x] 確認 profile 偏好仍正常載入 context
- [x] 確認訂單資訊仍正常載入 context
