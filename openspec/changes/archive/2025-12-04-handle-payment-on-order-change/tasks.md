# Tasks

## 後端邏輯 - 付款狀態智慧更新
- [x] 修改 `data.py` 的 `update_daily_summary_with_order()` 函數，實作智慧付款狀態更新
  - 金額增加 → paid=false, note="已付 $X，待補 $Y"
  - 金額減少 → paid=true, note="待退 $Z"
  - 保留 paid_amount 用於計算差額
- [x] 修改 `claude.py` 的 `_mark_paid()` 函數，設定 `paid_amount = amount` 並清除 `note`

## 後端邏輯 - 訂單取消處理
- [x] 修改 `claude.py` 的 `_update_payments_after_cancel()` 函數
  - 如果 paid_amount > 0，設定 note="待退 $X"
  - 保留 paid_amount，不移除記錄

## 後端邏輯 - 清除所有訂單
- [x] 修改 `claude.py` 的 `_clear_all_orders()` 函數
  - 保留 paid_amount > 0 的付款記錄
  - 設定這些記錄的 amount=0, note="待退 $X"
  - 只移除 paid_amount=0 的記錄

## 後端邏輯 - 標記已退款
- [x] 新增 `_mark_refunded()` 函數
  - 檢查 amount=0 且 paid_amount > 0
  - 移除該付款記錄
- [x] 在 `execute_action()` 加入 `mark_refunded` action 處理
- [x] 更新 AI prompt，加入「標記已退款」指令說明

## 總額計算
- [x] 修改 `data.py` 中 `total_collected` 的計算邏輯，改為 `sum(paid_amount)`
- [x] 修改 `data.py` 中 `total_pending` 的計算邏輯，改為 `sum(amount) - total_collected`
- [x] 確保所有新建付款記錄的 `paid_amount` 初始值為 `0`

## 前端顯示
- [x] 修改 `manager.html` 的 `updatePaymentsPanel()` 函數
  - 根據狀態顯示不同樣式和文字
  - 待退款記錄顯示「確認退款」按鈕
- [x] 新增 CSS 樣式
  - `.payment-status.partial`（橘色）- 部分已付/待補
  - `.payment-status.refund`（藍色）- 待退款
- [x] 實作「確認退款」按鈕的 API 呼叫
- [x] 新增 `/api/refund` API 端點
