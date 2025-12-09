# Tasks: remove-web-order-page

## Phase 1: 前端移除

- [x] 1.1 刪除 `templates/order.html`
  - **驗證**：訪問 `/order` 回傳 404

## Phase 2: 後端路由移除

- [x] 2.1 移除 `/order` 路由
  - 刪除 `main.py` 中的 `GET /order` handler
  - **驗證**：路由不存在

- [x] 2.2 移除個人聊天相關 API
  - 移除 `GET /api/chat/messages`（order.html 美食評論區）
  - 移除 `POST /api/chat/send`（order.html 美食評論區）
  - 保留 `POST /api/session/reset`（manager.html 仍需使用）
  - **驗證**：API 不存在

- [x] 2.3 調整 `/api/chat` 路由
  - 移除個人模式（`is_manager=false` 且非群組）
  - 保留群組點餐模式和管理員模式
  - **驗證**：群組點餐仍正常運作

- [x] 2.4 調整 `/api/today` 路由
  - 移除 `username` 參數處理
  - 僅保留看板需要的功能
  - **驗證**：看板頁面正常顯示

## Phase 3: 資料邏輯清理

- [x] 3.1 移除個人訂單相關函數
  - 移除 `data.py` 中的 `get_chat_messages`、`save_chat_message`、`save_system_message`
  - 移除 `main.py` 中店家變更時的系統訊息發送
  - **驗證**：無 import 錯誤

- [x] 3.2 移除個人對話 AI prompt
  - 刪除 `user_prompt.md`
  - 更新 `ai.py` 移除個人模式分支
  - **驗證**：群組點餐 AI 正常運作

## Phase 4: Socket.IO 事件清理

- [x] 4.1 檢視不再使用的事件
  - 保留 `order_created`、`order_cancelled` 等事件（管理員模式仍可能觸發）
  - 移除 `chat_message` 事件發送（僅舊 order.html 團隊聊天使用）
  - **驗證**：看板、管理員頁面正常

## Phase 5: 整合測試

- [x] 5.1 驗證現有功能正常
  - Python 語法驗證通過
  - **驗證**：端對端測試通過

- [x] 5.2 首頁導航調整
  - 確認首頁（看板）不再連結到 /order
  - **驗證**：無死連結
