# realtime-notification Spec Delta

## ADDED Requirements

### Requirement: 店家設定聊天通知
系統 SHALL 在管理員設定今日店家時，自動在團體聊天室新增系統訊息。

#### Scenario: 設定店家時新增聊天訊息
- **GIVEN** 管理員透過 AI 設定今日店家
- **WHEN** 系統廣播 `store_changed` 事件
- **THEN** 在團體聊天室新增一則系統訊息
- **AND** 訊息內容包含店家名稱和可開始訂餐提示
- **AND** 訊息以 "呷爸" 為發送者

#### Scenario: 離線使用者查看聊天記錄
- **GIVEN** 使用者當時不在線上
- **WHEN** 使用者稍後開啟訂餐頁面
- **THEN** 在團體聊天記錄中看到店家設定的系統訊息
- **AND** 得知今日可訂購的店家
