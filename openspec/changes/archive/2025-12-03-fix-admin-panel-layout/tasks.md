# Tasks

## 1. 訂單權限檢查（安全修復，優先處理）
- [x] 1.1 修改 `app/claude.py` 的 `execute_action` 傳入 `is_manager` 參數
- [x] 1.2 修改 `_cancel_order` 檢查權限：非管理員只能取消自己的訂單
- [x] 1.3 修改 `main.py` 的 `/api/chat` 傳遞 `is_manager` 給動作執行
- [x] 1.4 測試驗證權限檢查

## 2. 管理員面板三欄佈局
- [x] 2.1 修改 `templates/manager.html` 結構為三欄（左：店家管理、中：對話、右：資訊面板）
- [x] 2.2 新增 CSS 三欄佈局樣式
- [x] 2.3 調整 RWD 小螢幕為單欄

## 3. 修復店家管理面板滾動問題
- [x] 3.1 調整 `.stores-panel-content` 高度計算（使用 flex:1 + overflow-y:auto）
- [x] 3.2 確保最後一個店家可滾動到可視區域

## 4. 修復菜單上傳新增店家錯誤
- [x] 4.1 修復 `/api/recognize-menu` 中文店名 store_id 產生邏輯（使用 MD5 hash）
- [x] 4.2 改善前端錯誤訊息顯示（檢查 res.ok 狀態）

## 5. 增強菜單上傳入口
- [x] 5.1 將 icon 改為明顯按鈕並加上文字提示「📷 上傳菜單」
