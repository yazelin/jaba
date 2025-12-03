# Tasks: remove-legacy-compat

## Implementation Tasks

### 店家格式清理

1. [x] **清理 app/data.py 店家相關**
   - 移除 `get_today_info()` 中的舊格式轉換邏輯
   - 移除 `add_today_store()` 中的向後相容欄位設定
   - 移除 `remove_today_store()` 中的向後相容欄位更新

2. [x] **清理 main.py 店家相關**
   - 移除 `/api/today` 中的 `store` 向後相容欄位

3. [x] **清理前端店家分支**
   - `templates/index.html`：移除 `else if (todayInfo.store_name)` 分支
   - `templates/order.html`：簡化 `updateStoreInfoPanel()` 移除 today 參數
   - `templates/manager.html`：簡化 `updateStoreInfoPanel()` 移除 today 參數

### 訂單格式清理

4. [x] **清理 app/data.py 訂單相關**
   - 簡化 `get_user_order()` 使用 `get_user_orders()`
   - 移除 `get_user_orders()` 中的舊格式讀取
   - 簡化 `update_daily_summary_with_order()` 移除 username 識別邏輯

5. [x] **清理 app/claude.py 訂單相關**
   - 移除單店家菜單向後相容
   - 移除 `current_order` 向後相容
   - 移除 `_cancel_order()` 中的舊格式處理
   - 修正 `_create_order()` 使用 `today_stores[0]` 作為預設店家

### AI Action 格式清理

6. [x] **清理 app/claude.py prompt**
   - 修改 prompt 只告訴 AI 使用 `actions` 陣列格式
   - 移除 `build_context()` 中的單訂單向後相容

7. [x] **清理 main.py action 處理**
   - 移除 `action = response.get("action")`
   - 移除 `elif action:` 向後相容分支
   - 簡化 return 語句只包含 `actions` 和 `action_results`

### 其他清理

8. [x] **清理前端訂單顯示分支**
   - `templates/order.html`：更新歡迎訊息使用 `todayStores` 而非 `todayInfo.store_name`
   - `templates/order.html`：更新 action 處理使用 `action_results` 陣列
   - `templates/manager.html`：移除 `action_result` 向後相容轉換
   - `templates/manager.html`：修正使用 `result.store_name` 而非 `result.today?.store_name`

9. [x] **清理 static/css/style.css**
   - 移除「舊版兩欄（保留向後相容）」的未使用 CSS 規則

10. [x] **驗證功能**
    - 搜尋確認無「向後相容」、「舊格式」、「舊邏輯」等文字殘留
