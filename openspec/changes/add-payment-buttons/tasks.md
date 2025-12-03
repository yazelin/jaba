# Tasks

## 後端 - 新增 API 端點
- [x] 在 `main.py` 新增 `/api/mark-paid` POST 端點
  - 接收 `username` 參數
  - 呼叫 `claude._mark_paid()` 函數
  - 廣播 `payment_updated` 事件
  - 回傳執行結果

## 前端 - 付款面板按鈕
- [x] 修改 `manager.html` 的 `updatePaymentsPanel()` 函數
  - 未付款（`paid=false` 且 `paid_amount=0`）顯示「確認付款」按鈕
  - 待補款（`paid=false` 且 `paid_amount > 0`）顯示「確認付款」按鈕
  - 已付款不顯示「確認付款」按鈕
- [x] 新增 `confirmPaid(username)` JavaScript 函數
  - 呼叫 `/api/mark-paid` API
  - 成功後重新載入付款資料

## CSS 樣式
- [x] 新增 `.btn-paid` 樣式（綠色按鈕）
