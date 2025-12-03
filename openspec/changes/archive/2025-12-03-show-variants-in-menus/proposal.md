# Proposal: show-variants-in-menus

## Why
目前菜單顯示只顯示品項的預設價格（`item.price`），沒有顯示品項的尺寸變體（`variants`）。

問題：
1. 管理員頁面「所有店家」面板 - 展開店家菜單時只顯示預設價格，管理員無法確認價格是否正確
2. 訂餐頁菜單面板 - 只能點擊品項的預設價格，無法選擇尺寸
3. 管理員無法直接編輯現有菜單（目前只能透過重新拍照辨識）

## What Changes

### 1. 顯示尺寸與價格
- 管理員頁面 `updateStoresPanel()` - 當品項有 variants 時，顯示各尺寸名稱和價格
- 訂餐頁 `updateMenuPanel()` - 當品項有 variants 時，顯示各尺寸，讓使用者可以點擊特定尺寸來點餐

### 2. 加入編輯功能
- 在管理員頁面的店家列表中，每個店家的「啟用/停用」標籤旁加一個「編輯」按鈕
- 點擊「編輯」彈出菜單編輯畫面（重用菜單辨識完成後的編輯畫面）
- 管理員可以直接編輯品項名稱、價格、尺寸等

## Scope
- `templates/manager.html` - 修改 `updateStoresPanel()` 函數、加入編輯按鈕和編輯功能
- `templates/order.html` - 修改 `updateMenuPanel()` 函數

## Out of Scope
- 修改菜單資料結構
- 修改菜單辨識邏輯
