# Tasks

## 後端 - 新增 API 端點
- [x] 在 `main.py` 新增 `/api/store/{store_id}/toggle` POST 端點
  - 讀取店家資訊
  - 切換 `active` 狀態
  - 儲存並回傳結果

## 前端 - 店家管理面板
- [x] 修改 `manager.html` 的 `updateStoresPanel()` 函數
  - 將狀態標籤改為可點擊按鈕
  - 加入 `onclick` 事件呼叫 `toggleStoreActive(storeId)`
- [x] 新增 `toggleStoreActive(storeId)` JavaScript 函數
  - 呼叫 `/api/store/{store_id}/toggle` API
  - 成功後重新載入店家列表

## CSS 樣式
- [x] 新增 `.store-status-btn` 樣式為可點擊按鈕外觀
  - 加入 hover 效果
  - 加入 cursor: pointer
