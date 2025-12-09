# Spec: board-all-groups-chat

看板頁面的美食評論區功能，顯示所有群組對話。

## ADDED Requirements

### Requirement: 顯示所有群組對話
系統 SHALL 在美食評論區顯示所有群組與 jaba 的對話。

#### Scenario: 載入所有群組對話
- Given 今日有 2 個群組各有對話
- When 訪客開啟看板頁面
- Then 美食評論區顯示所有群組的對話
- And 每筆訊息標示來源群組名稱

#### Scenario: 訊息顯示格式
- Given 「午餐群」的「林亞澤」說了「我要雞腿便當」
- When 訊息顯示在美食評論區
- Then 顯示格式為「[午餐群] 林亞澤: 我要雞腿便當」

#### Scenario: 呷爸回覆顯示
- Given 呷爸在「午餐群」回覆了「好喔，點了雞腿便當」
- When 訊息顯示在美食評論區
- Then 顯示格式為「[午餐群] 呷爸: 好喔，點了雞腿便當」
- And 呷爸訊息有特殊樣式區分

### Requirement: 即時更新
系統 SHALL 在任何群組有新對話時，即時更新美食評論區。

#### Scenario: 收到新對話
- Given 訪客正在查看看板頁面
- When 「午餐群」有人傳送新訊息給 jaba
- Then 新訊息即時出現在美食評論區
- And 自動滾動到最新訊息

### Requirement: 隔天清除
系統 SHALL 在隔天自動清除美食評論區的對話記錄。

#### Scenario: 日期變更後清除
- Given 今日美食評論區有 10 筆對話
- When 隔天重新載入頁面
- Then 美食評論區顯示空狀態
- And 顯示「尚無聊天訊息」

### Requirement: LINE 好友 QRCode
系統 SHALL 在看板頁面顯示呷爸 LINE 好友 QRCode。

#### Scenario: 顯示 QRCode
- Given 訪客開啟看板頁面
- When 查看美食評論區下方
- Then 顯示加入呷爸好友的 LINE QRCode
- And 顯示「掃碼加入呷爸好友」文字說明

### Requirement: 唯讀模式
系統 SHALL 將美食評論區設為唯讀模式，不提供發送功能。

#### Scenario: 無輸入功能
- Given 訪客查看看板頁面的美食評論區
- When 試圖發送訊息
- Then 不提供任何輸入介面
- And 只能查看對話內容
