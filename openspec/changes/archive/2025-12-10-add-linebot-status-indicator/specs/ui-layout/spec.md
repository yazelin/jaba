## ADDED Requirements

### Requirement: LINE Bot 狀態指示器

系統 SHALL 在看板頁（`/`）和管理員頁（`/manager`）顯示 LINE Bot 運行狀態指示器，並定期檢查狀態以維持 LINE Bot 活躍。

#### Scenario: 頁面載入時檢查 LINE Bot 狀態
- **WHEN** 使用者進入看板頁或管理員頁
- **THEN** 系統自動背景 fetch `https://jaba-line-bot.onrender.com`
- **AND** 狀態指示器顯示「檢查中...」

#### Scenario: 定期重新檢查狀態
- **WHEN** 頁面持續開啟
- **THEN** 系統每 1 分鐘自動重新 fetch LINE Bot URL
- **AND** 更新狀態指示器顯示

#### Scenario: LINE Bot 正常運行
- **WHEN** fetch 回應成功且內容包含 `Jaba LINE Bot is running!`
- **THEN** 狀態指示器顯示「LINE Bot 運行中」並顯示綠色圖示

#### Scenario: LINE Bot 無法連線
- **WHEN** fetch 失敗或回應內容不包含預期字串
- **THEN** 狀態指示器顯示「LINE Bot 離線」並顯示灰色或紅色圖示

### Requirement: 看板頁 LINE Bot 狀態位置

系統 SHALL 在看板頁的「加入呷爸好友」QRCode 區塊附近顯示 LINE Bot 狀態。

#### Scenario: 看板頁狀態顯示位置
- **WHEN** 使用者查看看板頁
- **THEN** LINE Bot 狀態指示器顯示於 QRCode 區塊內，與好友資訊整合呈現

### Requirement: 管理員頁 LINE Bot 狀態面板

系統 SHALL 在管理員頁左側面板區域新增獨立的「LINE Bot 狀態」panel。

#### Scenario: 管理員頁狀態面板位置
- **WHEN** 管理員登入管理頁面
- **THEN** 「LINE Bot 狀態」panel 顯示於「店家管理」panel 的上方
- **AND** panel 獨立顯示當前 LINE Bot 運行狀態
