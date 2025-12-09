# Tasks: cleanup-legacy-order-system

## Implementation Tasks

- [x] 移除 `data.py` 中個人訂單相關函式
  - `get_user_order`, `get_user_orders`, `save_user_order`, `delete_user_order`
  - `get_daily_summary`, `save_daily_summary`, `update_daily_summary_with_order`
  - `get_payments`, `save_payments`（獨立付款）

- [x] 移除 `data.py` 中 `ensure_user` 建立 `orders/` 和 `sessions/` 資料夾

- [x] 移除 `ai.py` 中個人訂單 action handlers
  - `_create_order`, `_update_order`
  - `_cancel_order`, `_clear_all_orders`, `_clean_history_orders`
  - `_mark_paid`, `_mark_refunded`
  - `_remove_item`, `_update_payments_after_cancel`
  - `_get_recent_store_history`

- [x] 移除 `ai.py` 中 `build_context` 的 `user_orders` 和 `today_summary`

- [x] 移除 `ai.py` 中 `execute_action` 對應的 action type cases

- [x] 更新 `manager_prompt.md` 移除不可用的 actions

- [x] 更新 `order-management` spec 移除個人訂單相關 requirements

- [x] 更新 `data-storage` spec 移除個人訂單資料結構

- [x] 更新 README 移除過時的資料結構說明

## Validation

- [ ] 執行系統確認啟動正常
- [ ] 測試群組點餐流程
- [ ] 測試管理員基本功能
