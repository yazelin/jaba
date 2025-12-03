# Tasks: show-store-details

## Implementation Tasks

1. [x] **新增店家卡片 CSS 樣式**
   - 檔案：`static/css/style.css`
   - 新增 `.store-phone` 樣式
   - 電話前加「電話：」前綴（側邊面板）或 📞 圖示（看板頁）

2. [x] **更新訂餐頁店家顯示**
   - 檔案：`templates/order.html`
   - 修改 `updateStoreInfoPanel()` 函數
   - 顯示店家名稱、電話（如有）、備註（如有）

3. [x] **更新管理頁店家顯示**
   - 檔案：`templates/manager.html`
   - 修改 `updateStoreInfoPanel()` 函數
   - 顯示店家名稱、電話（如有）、備註（如有）

4. [x] **更新看板頁店家顯示**
   - 檔案：`templates/index.html`
   - 修改 `updateBoard()` 函數
   - 顯示店家名稱、電話（如有）、備註（如有）

5. [x] **驗證功能**
   - 使用有電話和備註的店家測試顯示
   - 使用無電話無備註的店家測試顯示
   - 確認多店家情況下每個店家都正確顯示
