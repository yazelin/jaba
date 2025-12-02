# Tasks

## 1. 群組聊天功能（新功能）
- [x] 1.1 建立聊天資料結構
  - [x] 新增 `data/chat/` 目錄
  - [x] 聊天記錄格式：`data/chat/{date}.json`
  - [x] 訊息結構：`{ messages: [{ id, username, content, timestamp }] }`
- [x] 1.2 在 `app/data.py` 新增聊天相關函數
  - [x] `get_chat_messages(date)` 取得當日聊天記錄
  - [x] `save_chat_message(username, content)` 儲存新訊息
- [x] 1.3 在 `main.py` 新增聊天 API
  - [x] `GET /api/chat/messages` 取得當日訊息
  - [x] `POST /api/chat/send` 發送訊息
- [x] 1.4 新增 Socket.IO 聊天事件
  - [x] `chat_message` 事件：廣播新訊息給所有連線者
- [x] 1.5 前端聊天室 UI
  - [x] 在訂餐頁新增聊天室視窗（獨立於 AI 對話）
  - [x] 在管理頁新增聊天室視窗
  - [x] 在看板頁新增聊天訊息顯示（唯讀模式）
  - [x] 載入當日歷史訊息
  - [x] 監聽 `chat_message` 事件即時更新
  - [x] 新訊息自動捲動到底部
- [x] 1.6 聊天室樣式設計（暖色系）

## 2. 瀏覽器推播通知（新功能）
- [x] 2.1 在各頁面請求瀏覽器通知權限（Notification API）
- [x] 2.2 新增通知發送函數 `sendBrowserNotification(title, body)`
- [x] 2.3 聊天訊息通知
  - [x] 收到 chat_message 事件且非本人發送時，發送通知
- [x] 2.4 訂單事件通知
  - [x] 新訂單：「{username} 訂了便當！」
  - [x] 訂單取消：「{username} 取消了訂單」
  - [x] 全部清除：「管理員已清除所有訂單」
- [x] 2.5 店家變更通知：「今日店家已更新：{store_name}」
- [x] 2.6 點擊通知時開啟或聚焦頁面

## 3. 多訂單支援（架構變更）
- [x] 3.1 修改 `app/data.py` 訂單檔案結構
  - [x] `get_user_order` 改為 `get_user_orders`，回傳該使用者當日所有訂單
  - [x] `save_user_order` 檔名改為 `{date}-{timestamp}.json`（支援同店家多筆）
  - [x] 新增 `delete_user_order(username, order_id)` 刪除特定訂單
- [x] 3.2 修改 `data/system/today.json` 結構支援多店家
  - [x] 從單一物件改為 `{ stores: [...] }` 陣列
  - [x] 保留向後相容的 `store_id` 和 `store_name` 欄位
- [x] 3.3 修改 `app/data.py` 支援多店家
  - [x] 新增 `add_today_store()` 函數
  - [x] 新增 `remove_today_store()` 函數
  - [x] `set_today_store()` 改為清除其他店家並設定單一店家
- [x] 3.4 修改 `update_daily_summary_with_order` 邏輯
  - [x] 以 `order_id` 為唯一識別
  - [x] 同一使用者多筆訂單分開記錄
- [x] 3.5 更新 `app/claude.py` 建立訂單邏輯支援多訂單

## 4. 專案重命名（jiaba → jaba）
- [x] 4.1 修改 `pyproject.toml` 專案名稱為 `jaba`
- [x] 4.2 將 `data/system/prompts/jiaba.json` 重命名為 `jaba.json`
- [x] 4.3 修改 `app/data.py` 的 `get_jiaba_prompt` 為 `get_jaba_prompt`
- [x] 4.4 修改 `app/claude.py` 呼叫 `get_jaba_prompt`
- [x] 4.5 修改 `main.py` 註解與 FastAPI title
- [x] 4.6 修改 `app/__init__.py` 註解
- [x] 4.7 修改 `static/css/style.css` 註解
- [x] 4.8 修改 `templates/order.html` localStorage key 為 `jaba_username`
- [x] 4.9 更新 `openspec/project.md` 專案名稱說明

## 5. 視覺設計改版
- [x] 5.1 形象照已放置於 `static/images/jaba-bg.jpg`
- [x] 5.2 圓形 logo 已放置於 `static/images/jaba.png`
- [x] 5.3 設定 `jaba.png` 為網站 favicon（各頁面 `<link rel="icon">`）
- [x] 5.4 在各頁面標題旁加入 logo 圖示
- [x] 5.5 在 AI 對話中，呷爸訊息旁顯示 logo 作為頭像
- [x] 5.6 瀏覽器通知使用 logo 作為 icon
- [x] 5.7 全面修改 `static/css/style.css` 配色為暖色系
  - [x] 主色調改為 `#8B6914`、`#A67B5B`
  - [x] 背景改為形象照 + 半透明遮罩
  - [x] 按鈕、標題、強調色改為暖色系
- [x] 5.8 調整各頁面背景樣式

## 6. 品牌與 UI 更新
- [x] 6.1 將 `templates/index.html` 中前端顯示改為「呷爸」
- [x] 6.2 將 `templates/order.html` 中前端顯示改為「呷爸」
- [x] 6.3 將 `templates/manager.html` 中前端顯示改為「呷爸」
- [x] 6.4 修改看板頁日期格式，將「二」改為「星期二」
- [x] 6.5 更新 `data/system/prompts/jaba.json` 中的顯示名稱為「呷爸」

## 7. 訂單管理修復與增強
- [x] 7.1 在管理員 system prompt 加入 `cancel_order` 動作（修復 bug）
- [x] 7.2 新增 `clear_all_orders` 動作，清除今日所有訂單
- [x] 7.3 實作 `_clear_all_orders` 函數於 `app/claude.py`
- [x] 7.4 新增 `clean_history_orders` 動作，清除指定日期前的歷史訂單
- [x] 7.5 實作 `_clean_history_orders` 函數於 `app/claude.py`
- [x] 7.6 在 `app/data.py` 新增 `delete_daily_orders` 和 `clean_old_orders` 函數（邏輯已整合於 `app/claude.py` 的 `_clear_all_orders` 和 `_clean_history_orders` 中）

## 8. AI 對話增強
- [x] 8.1 修改 system prompt，指示 AI 在使用者無訂單時明確回覆「你今天還沒有訂餐喔」
- [x] 8.2 更新 AI 上下文建構邏輯，加入店家 note 欄位
- [x] 8.3 新增菜單圖片辨識 API (`/api/recognize-menu`)
- [x] 8.4 實作 `recognize_menu_image` 函數，呼叫 Claude Vision 解析圖片

## 9. 店家資料增強
- [x] 9.1 在 `data/stores/{store-id}/info.json` 結構中新增 `note` 欄位
- [x] 9.2 更新 `app/claude.py` 中的 `_create_store` 和 `_update_store` 支援 note 欄位
- [x] 9.3 更新範例店家 `sample-store/info.json` 加入 note 範例

## 10. 訂餐頁增強
- [x] 10.1 在 `templates/order.html` 對話框旁邊新增今日菜單面板
  - [x] 顯示今日所有店家名稱（支援多店家）
  - [x] 顯示各店家 note/說明
  - [x] 顯示菜單分類與品項（含價格）
- [x] 10.2 新增即時訂單側邊面板
  - [x] 載入並顯示今日所有訂單（呼叫 `/api/today`）
  - [x] 按店家分組顯示（多店家時）
  - [x] 顯示品項統計與總金額
- [x] 10.3 新增團隊聊天室視窗
- [x] 10.4 監聯 Socket.IO 事件即時更新訂單面板與聊天室
- [x] 10.5 修改歡迎訊息，呷爸主動介紹今日店家與菜單重點

## 11. 管理頁增強
- [x] 11.1 新增訂單總覽面板（獨立區塊）
  - [x] 顯示所有人訂單列表（按店家分組）
  - [x] 顯示總金額
  - [x] 顯示付款狀態（已付/未付）
- [x] 11.2 新增店家管理面板
  - [x] 列出所有店家（可展開/收合）
  - [x] 每個店家顯示完整菜單品項清單
  - [x] 顯示店家 note/說明
  - [x] 支援透過 AI 對話編輯
- [x] 11.3 新增菜單圖片上傳功能
  - [x] 新增圖片上傳按鈕（📷 按鈕於店家管理面板）
  - [x] 上傳後呼叫 AI 辨識並建立菜單
  - [x] 顯示辨識結果供編輯確認
- [x] 11.4 新增團隊聊天室視窗
- [x] 11.5 監聯 Socket.IO 事件即時更新面板與聊天室

## 12. 看板頁增強
- [x] 12.1 在看板頁顯示店家 note/說明
- [x] 12.2 支援顯示多店家訂單（按店家分組）
- [x] 12.3 新增聊天訊息顯示區（唯讀模式，顯示最近 10 則訊息）
- [x] 12.4 看板頁改為左右兩欄排版（左：店家+聊天，右：訂單+統計+按鈕）

## 13. 後端 API 增強
- [x] 13.1 新增 `/api/recognize-menu` API，接收圖片並回傳辨識結果
- [x] 13.2 更新 `/api/today` 回傳多店家資訊與店家 note 欄位
- [x] 13.3 更新 `/api/stores` 回傳店家 note 欄位
- [x] 13.4 新增 `/api/chat/messages` 取得聊天記錄
- [x] 13.5 新增 `/api/chat/send` 發送聊天訊息
- [x] 13.6 新增 `/api/stores/all` 取得所有店家與菜單（管理員用）

## 14. 測試與驗證
- [x] 14.1 測試專案重命名：jiaba → jaba 是否完整
- [x] 14.2 測試瀏覽器通知功能
  - [x] 權限請求
  - [x] 聊天訊息通知
  - [x] 訂單事件通知
- [x] 14.3 測試群組聊天功能
  - [x] 發送訊息
  - [x] 即時接收其他人訊息
  - [x] 新加入者看到歷史訊息
- [x] 14.4 測試多訂單功能：同一使用者同店家多筆訂單
- [x] 14.5 測試視覺設計：背景圖片、暖色系配色是否正確
- [x] 14.6 測試品牌名稱更新是否完整（顯示為「呷爸」）
- [x] 14.7 測試管理員清除訂單功能（單一使用者特定訂單）
- [x] 14.8 測試管理員清除所有今日訂單功能
- [x] 14.9 測試歷史訂單清理功能
- [x] 14.10 測試無訂單時 AI 回覆是否正確
- [x] 14.11 測試訂餐頁菜單顯示與即時訂單面板
- [x] 14.12 測試管理頁訂單總覽與店家管理功能
- [x] 14.13 測試菜單圖片辨識功能

