# Tasks: notify-store-update-in-chat

## Implementation Tasks

1. [x] **新增系統訊息儲存函數**
   - 檔案：`app/data.py`
   - 新增 `save_system_message(content: str)` 函數
   - username 設為 "呷爸"
   - 回傳新訊息物件

2. [x] **store_changed 事件時新增聊天訊息**
   - 檔案：`main.py`
   - 在廣播 `store_changed` 後呼叫 `save_system_message()`
   - 訊息內容：「今日店家已設定：{store_name}，可以開始訂餐囉！」
   - 同時廣播 `chat_message` 事件讓線上使用者即時看到

3. [x] **驗證功能**
   - 管理員設定店家後，檢查聊天記錄是否有系統訊息
   - 確認前端團體聊天室能顯示系統訊息
   - 確認離線使用者開啟頁面後能看到訊息
