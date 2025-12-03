# Tasks: fix-update-order-logic

## Implementation Tasks

### 1. 新增 `remove_item` 動作處理函數
- [x] 在 `app/claude.py` 新增 `_remove_item(username, action_data)` 函數
- [x] 從 `current_orders` 中找到包含該品項的訂單
- [x] 若品項數量 > 移除數量，更新訂單減少數量
- [x] 若品項數量 = 移除數量，從訂單移除該品項
- [x] 若訂單只剩該品項，刪除整筆訂單
- [x] 更新 daily summary 和 payments

### 2. 註冊 `remove_item` 動作
- [x] 在 `execute_action()` 中加入 `remove_item` 的 case
- [x] 呼叫 `_remove_item()` 處理

### 3. 更新 user_prompt.md
- [x] 新增 `remove_item` 動作說明
- [x] 指示呷爸查看 `current_orders` 了解現有訂單
- [x] 說明何時用 `remove_item` vs `create_order`
- [x] 強調：移除品項不是建立新訂單

### 4. 修正 `_update_order` 邏輯（可選）
- [ ] 若要保留 `update_order`，需要求傳入 `order_id`
- [ ] 先刪除舊訂單再建立新訂單
- [ ] 或改為直接修改現有訂單內容

（此項保留為可選，目前使用 `remove_item` + `create_order` 組合可達成目的）

## Verification
- [x] 測試：有 [A, B] 訂單，說「不要 A」→ 變成 [B]
- [x] 測試：有 [A] 訂單，說「不要 A」→ 訂單被刪除
- [x] 測試：有 [A] 訂單，說「加 B」→ 新增訂單 [B] 或合併為 [A, B]
- [x] 測試：有 [A x2] 訂單，說「不要 1 個 A」→ 變成 [A x1]
- [x] 確認 daily summary 正確更新
- [x] 確認 payments 正確更新
