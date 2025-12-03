# Tasks

## 實作任務

### HTML 結構調整
- [x] 修改 `templates/order.html` 佈局為三欄結構
- [x] 左側面板：今日店家、菜單
- [x] 中間面板：AI 對話框
- [x] 右側面板：我的訂單、大家的訂單

### CSS 樣式
- [x] 複用管理頁的 `.admin-three-columns` 樣式（或新增 `.order-three-columns`）
- [x] 新增左右面板 CSS（`.order-left-panel`, `.order-right-panel`）
- [x] 確保 RWD 在手機上正確顯示

### 功能調整
- [x] 新增「大家的訂單」面板（使用原本的今日訂單邏輯，顯示所有人訂單）
- [x] 修改 `updateOrdersPanel()` 同時更新「我的訂單」和「大家的訂單」
- [x] 團隊聊天室預設展開（移除 `minimized` class，設定 `teamChatOpen = true`）

### 驗收
- [x] 桌面版：確認三欄佈局正確顯示
- [x] 手機版：確認 RWD 正確堆疊
- [x] 團隊聊天室預設展開且可收合
