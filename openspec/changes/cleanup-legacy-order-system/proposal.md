# Proposal: cleanup-legacy-order-system

## Why

系統目前有兩套訂單管理機制：

1. **群組訂單系統**（使用中）：訂單和付款都存在 `linebot/sessions/{group_id}.json`
2. **個人訂單系統**（死代碼）：設計給 `users/{username}/orders/` 和 `orders/{date}/summary.json`

個人訂單系統從未被實際使用，因為：
- `create_order` action 存在於程式碼中，但沒有任何 prompt 指示 AI 使用它
- 管理員功能（`cancel_order`、`mark_paid`、`clear_all_orders` 等）依賴這些資料，但資料從未建立
- 群組點餐結單時只產生文字摘要，不存到 `daily_summary`

這些死代碼增加了維護負擔和混淆。

## What Changes

### 移除的程式碼

**app/data.py:**
- `get_user_order()` / `get_user_orders()`
- `save_user_order()` / `delete_user_order()`
- `get_daily_summary()` / `save_daily_summary()`
- `update_daily_summary_with_order()`
- `get_payments()` / `save_payments()`（獨立付款系統）
- `ensure_user()` 中建立 `orders/` 和 `sessions/` 資料夾的程式碼

**app/ai.py:**
- `_create_order()` / `_update_order()`
- `_cancel_order()`（個人訂單版本）
- `_clear_all_orders()`
- `_mark_paid()` / `_mark_refunded()`（獨立付款版本）
- `_clean_history_orders()`
- `_remove_item()`
- `_update_payments_after_cancel()`
- `build_context()` 中的 `user_orders` 和 `today_summary`
- action handler 中對應的 case

**manager_prompt.md:**
- 移除不再可用的 actions：`cancel_order`、`clear_all_orders`、`clean_history_orders`、`mark_paid`、`mark_refunded`、`query_payments`、`query_all_orders`

### 保留的功能

- 群組訂單 API（`group_create_order` 等）
- 群組 session 中的付款追蹤
- 超級管理員 API（`/api/super-admin/*`）

## Impact Analysis

### 影響範圍
- `app/data.py`：移除約 100 行死代碼
- `app/ai.py`：移除約 400 行死代碼
- `manager_prompt.md`：簡化可執行動作列表
- `order-management` spec：大幅簡化，移除個人訂單相關 requirements

### 向下相容
- 不影響現有群組點餐功能
- 管理員原本就無法使用這些功能（因為資料不存在）

## Success Criteria

1. 所有死代碼已移除
2. 群組點餐功能正常運作
3. 管理員 prompt 只列出可用的 actions
4. 系統啟動和測試通過
