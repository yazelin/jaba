# Tasks: refactor-chat-discussion-ui

## Phase 1: 後端 API 與資料層

### 1.1 新增群組對話 API
- [x] 新增 `GET /api/super-admin/groups/{group_id}/chat` 端點
- [x] 回傳該群組的對話記錄和群組名稱
- **驗證**: curl 測試 API 回傳正確格式

### 1.2 修改對話儲存邏輯
- [x] 在 `append_group_chat_history()` 後，同時儲存到聚合檔案
- [x] 新增 `append_to_board_chat()` 函數
- [x] 聚合檔案包含 group_name 欄位
- **驗證**: 群組對話後，檢查 daily_chat_messages.json 有正確資料

### 1.3 Socket.IO 事件
- [x] 在群組對話後廣播 `group_chat_updated` 事件
- [x] 在群組對話後廣播 `board_chat_message` 事件
- **驗證**: 使用瀏覽器 DevTools 確認收到事件

## Phase 2: 管理員介面重構

### 2.1 移除發送功能
- [x] 移除 `team-chat-input` 區塊
- [x] 移除 `sendTeamChatMessage()` 函數
- [x] 移除 `handleTeamChatKeyPress()` 函數
- **驗證**: UI 不再顯示輸入框

### 2.2 標題動態更新
- [x] 標題改為動態：`{群組名稱} 群組討論`
- [x] 未選擇群組時顯示「請選擇群組」
- **驗證**: 切換群組時標題跟著變

### 2.3 載入群組對話
- [x] 新增 `loadGroupChat(groupId)` 函數
- [x] 切換群組時呼叫 `loadGroupChat()`
- [x] 清空並重新渲染對話內容
- **驗證**: 切換群組後顯示正確對話

### 2.4 即時更新
- [x] 監聽 `group_chat_updated` 事件
- [x] 只更新當前選中群組的對話
- **驗證**: LINE Bot 對話後，管理員介面自動更新

### 2.5 增加 UI 高度
- [x] 調整 `.team-chat-messages` 的 max-height
- [x] 確保可顯示更多訊息
- **驗證**: 目視確認高度增加

## Phase 3: 看板頁面修改

### 3.1 修改資料來源
- [x] 新增 `/api/board/chat` 端點
- **驗證**: API 回傳所有群組對話

### 3.2 修改顯示格式
- [x] 訊息顯示格式：`[群組名稱] 使用者: 內容`
- [x] 區分呷爸回覆和使用者訊息
- **驗證**: 看板顯示格式正確

### 3.3 即時更新
- [x] 監聽 `board_chat_message` 事件
- [x] 新訊息自動加入並滾動到底部
- **驗證**: LINE Bot 對話後，看板即時更新

### 3.4 移除「我要訂便當」按鈕，改為 QRCode
- [x] 移除原「我要訂便當」按鈕
- [x] 新增 LINE 好友 QRCode 圖片
- [x] 加入「掃碼加入呷爸好友」文字說明
- **驗證**: 看板顯示 QRCode 而非按鈕

## Phase 4: 清理與測試

### 4.1 移除廢棄程式碼
- [ ] 移除原 team chat 發送相關的後端程式碼（如不再需要）
- [ ] 清理未使用的函數
- **驗證**: 程式碼無錯誤
- **備註**: 保留供 order.html 使用，後續再清理

### 4.2 端對端測試
- [x] LINE 群組點餐 → 管理員看到對話
- [x] LINE 群組點餐 → 看板看到對話
- [x] 切換群組 → 對話正確切換
- [x] 隔天 → 對話清除
- **驗證**: 所有流程正常

## Dependencies

```
Phase 1 ──► Phase 2
         └─► Phase 3
              └──► Phase 4
```

Phase 2 和 Phase 3 可並行進行，都依賴 Phase 1 完成。
