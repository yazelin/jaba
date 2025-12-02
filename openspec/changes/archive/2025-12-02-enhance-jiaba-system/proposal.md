# Change: 呷爸系統功能增強與品牌更新

## Why
目前系統存在以下使用體驗問題：
1. 使用者無訂單時，AI 未明確回應「今天還沒有訂」
2. 訂餐頁無法看到即時訂單動態和今日菜單
3. 管理頁缺乏訂單總覽、付款狀態面板
4. 管理頁缺乏店家分頁管理介面和菜單上傳功能
5. **管理員無法清除訂單**（管理員 prompt 缺少 cancel_order 動作）
6. 前端品牌名稱「jiaba」應改為中文「呷爸」
7. 看板日期格式不完整（「二」應為「星期二」）
8. 店家缺乏備註/說明欄位的顯示
9. 訂餐頁對話開始時未主動提供店家與菜單資訊
10. **視覺設計需要改版**：現有紫色漸層不符合品牌形象
11. **每人每天只能訂一單**：無法同時訂午餐和飲料（不同店家）
12. **缺乏團隊溝通管道**：無法討論今天要吃什麼

## What Changes

### 群組聊天功能（新功能）
- **ADDED**: 獨立於 AI 對話的「團隊聊天室」視窗
- **ADDED**: 所有訂購人和管理員都可以在聊天室打字
- **ADDED**: 即時訊息同步（透過 Socket.IO）
- **ADDED**: 聊天記錄保留一天（存於 `data/chat/{date}.json`）
- **ADDED**: 新加入者可看到當日所有歷史訊息
- **ADDED**: 有新訊息時自動更新畫面

### 瀏覽器推播通知（新功能）
- **ADDED**: 請求瀏覽器通知權限（Notification API）
- **ADDED**: 新聊天訊息時發送瀏覽器通知（即使頁面未開啟）
- **ADDED**: 新訂單建立時發送瀏覽器通知
- **ADDED**: 訂單取消/清除時發送瀏覽器通知
- **ADDED**: 今日店家變更時發送瀏覽器通知

### 多訂單支援（架構變更）
- **MODIFIED**: 訂單檔案結構從 `{date}.json` 改為 `{date}-{order_id}.json`（order_id 為時間戳）
- **MODIFIED**: 每人每天可建立多筆訂單，不限店家或同店家數量（如午餐+晚餐都訂同一間）
- **MODIFIED**: 彙整邏輯支援同一使用者多筆訂單（按店家分組顯示）
- **MODIFIED**: 今日可設定多個店家（不只一個）

### 視覺設計改版
- **MODIFIED**: 使用呷爸形象照 (`jaba-bg.jpg`) 作為各頁背景
- **ADDED**: 使用呷爸圓形 logo (`jaba.png`) 作為：
  - 網站 favicon
  - 頁面標題旁的 logo
  - 瀏覽器通知的 icon
  - AI 對話中呷爸訊息的頭像
- **MODIFIED**: 配色從紫色漸層改為暖色系（棕色、米色、奶茶色）
- 建議配色方案：
  - 主色調：#8B6914（溫暖棕色）、#A67B5B（奶茶色）
  - 背景色：#FAF3E0（米白色）、#FFF8DC（奶油色）
  - 強調色：#5D4037（深棕色）、#D4A574（淺奶茶）
  - 文字色：#4E342E（深咖啡）

### 專案重命名（jiaba → jaba）
- **MODIFIED**: 專案英文名稱從 `jiaba` 改為 `jaba`
- **MODIFIED**: `pyproject.toml` 專案名稱改為 `jaba`
- **MODIFIED**: `data/system/prompts/jiaba.json` 改為 `jaba.json`
- **MODIFIED**: `app/data.py` 的 `get_jiaba_prompt` 改為 `get_jaba_prompt`
- **MODIFIED**: localStorage key 從 `jiaba_username` 改為 `jaba_username`
- **MODIFIED**: 程式碼註解與 FastAPI title 中的 jiaba 改為 jaba

### 品牌與 UI 調整
- 所有前端顯示的「jaba」改為中文「呷爸」
- 看板日期格式從「2025/12/2 二」改為「2025/12/2 星期二」

### AI 對話增強
- **MODIFIED**: 當使用者無訂單時，AI 應回覆「你今天還沒有訂餐喔」
- **ADDED**: 店家備註/說明 (note) 欄位，在對話中可提及
- **MODIFIED**: 訂餐頁歡迎訊息改為主動提供今日店家、說明、菜單資訊

### 訂餐頁增強
- **ADDED**: 在訂餐頁新增即時訂單動態面板，顯示所有人的訂單（同看板頁）
- **ADDED**: 在對話框旁邊顯示今日店家菜單（不需等使用者問）
- **ADDED**: 團隊聊天室視窗（獨立於 AI 對話）
- **MODIFIED**: 呷爸開場白主動介紹今日店家與菜單

### 管理頁增強
- **ADDED**: 訂單總覽面板（所有人訂單、品項、金額、總價、付款狀態）
- **ADDED**: 店家分頁管理介面（每個店家一個分頁，顯示品項與說明）
- **ADDED**: 菜單圖片上傳功能（AI 辨識圖片並自動建立菜單）
- **ADDED**: 團隊聊天室視窗
- 今日資訊與店家資料預載到畫面，AI 對話用於修改操作

### 訂單管理增強（修復 bug）
- **MODIFIED**: 管理員 system prompt 加入 `cancel_order` 動作（修復無法清除訂單的問題）
- **ADDED**: 管理員可清除特定使用者的訂單（需指定店家）
- **ADDED**: 管理員可清除所有今日訂單 (`clear_all_orders`)
- **ADDED**: 歷史訂單清理功能（刪除指定日期之前的訂單）

### 店家資料增強
- **ADDED**: 店家 note 欄位（備註/說明），可在看板頁與訂餐頁顯示
- **ADDED**: 店家提示欄位（如最後點餐時間注意事項）

## Impact
- Affected specs: `ai-integration`, `menu-management`, `realtime-notification`, `order-management`, `data-storage`
- New specs: `team-chat`, `browser-notification`
- Affected code:
  - `static/css/style.css` (全面改版配色與背景、聊天室樣式)
  - `static/images/` (新增形象照)
  - `templates/index.html` (品牌名稱、日期格式、店家 note、背景、多店家顯示、聊天室)
  - `templates/order.html` (品牌名稱、即時訂單面板、菜單顯示、歡迎訊息、背景、聊天室)
  - `templates/manager.html` (品牌名稱、訂單面板、店家管理、背景、聊天室)
  - `app/claude.py` (管理員 prompt、cancel_order、clear_all_orders、多訂單邏輯)
  - `app/data.py` (訂單檔案結構、多店家今日設定、清除訂單函數、聊天記錄存取)
  - `main.py` (菜單圖片上傳 API、聊天 API、Socket.IO 聊天事件)
  - `data/system/today.json` (改為支援多店家陣列)
  - `data/chat/` (新增聊天記錄目錄)
