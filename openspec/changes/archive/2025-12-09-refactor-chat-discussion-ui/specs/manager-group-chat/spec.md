# Spec: manager-group-chat

管理員介面的群組討論區功能。

## ADDED Requirements

### Requirement: 群組討論區標題
系統 SHALL 動態顯示選定群組名稱作為討論區標題。

#### Scenario: 選擇群組後標題更新
- Given 管理員已登入管理介面
- When 從下拉選單選擇「午餐群」
- Then 討論區標題顯示「💬 午餐群 群組討論」

#### Scenario: 未選擇群組
- Given 管理員已登入管理介面
- When 尚未選擇任何群組
- Then 討論區標題顯示「💬 請選擇群組」

### Requirement: 顯示群組對話記錄
系統 SHALL 在討論區內容顯示選定群組與 jaba 的 LINE 對話記錄。

#### Scenario: 載入群組對話
- Given 管理員選擇了「午餐群」
- And 該群組今日有 5 筆對話記錄
- When 載入完成
- Then 討論區顯示該 5 筆對話
- And 每筆顯示「使用者名稱: 內容」格式
- And 呷爸的回覆有特殊樣式區分

#### Scenario: 群組無對話
- Given 管理員選擇了「午餐群」
- And 該群組今日無對話記錄
- When 載入完成
- Then 顯示「尚無對話記錄」

### Requirement: 切換群組更新對話
系統 SHALL 在切換群組下拉選單時，同步更新討論區內容。

#### Scenario: 切換群組
- Given 管理員正在查看「午餐群」的對話
- When 切換到「下午茶群」
- Then 討論區清空並載入「下午茶群」的對話
- And 標題更新為「💬 下午茶群 群組討論」

### Requirement: 即時更新對話
系統 SHALL 在 LINE Bot 有新對話時，即時更新討論區。

#### Scenario: 收到新對話
- Given 管理員正在查看「午餐群」的討論區
- When 「午餐群」有人傳送新訊息給 jaba
- Then 新訊息即時出現在討論區底部
- And 自動滾動到最新訊息

#### Scenario: 其他群組對話不影響
- Given 管理員正在查看「午餐群」的討論區
- When 「下午茶群」有新對話
- Then 「午餐群」討論區不更新

### Requirement: 唯讀模式
系統 SHALL 將討論區設為唯讀模式，不提供發送功能。

#### Scenario: 無輸入框
- Given 管理員已登入管理介面
- When 查看群組討論區
- Then 不顯示訊息輸入框
- And 不顯示發送按鈕

### Requirement: 增加顯示高度
系統 SHALL 增加討論區 UI 高度，以顯示更多對話訊息。

#### Scenario: 高度增加
- Given 管理員查看群組討論區
- When 對話記錄超過原顯示範圍
- Then 可顯示至少 15 筆訊息
- And 超出部分可滾動查看
