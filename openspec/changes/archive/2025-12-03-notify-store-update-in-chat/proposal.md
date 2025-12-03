# Proposal: notify-store-update-in-chat

## Summary
當管理員更新今日店家時，除了現有的 Socket.IO 即時通知外，系統自動在團體聊天室新增一則系統訊息，讓沒看到通知的使用者也能從聊天記錄得知今天可以開始訂餐。

## Motivation
目前管理員設定店家後，系統會透過 Socket.IO 廣播 `store_changed` 事件通知所有連線中的使用者。但如果使用者當時不在線上，後來才開啟系統時看不到任何訊息提示今天的店家已經設定好了。

透過在團體聊天室新增系統訊息，可以讓：
1. 離線使用者回來後從聊天記錄知道今日店家
2. 提供明確的「現在可以開始訂餐了」提示
3. 保留店家設定的歷史記錄

## Scope
- 修改 `main.py` 中的 `store_changed` 事件處理
- 新增系統訊息儲存邏輯
- 前端團體聊天室顯示系統訊息

## Out of Scope
- 店家移除時的通知（若需要可另開提案）
- 推送通知（Push Notification）

## Dependencies
無
