# ui-layout Specification

## Purpose
TBD - created by archiving change redesign-order-page-layout. Update Purpose after archive.
## Requirements
### Requirement: 訂餐頁三欄佈局
訂餐頁面 SHALL 採用三欄式佈局，與管理頁面風格一致。

#### Scenario: 桌面版三欄顯示
- **GIVEN** 使用者在桌面瀏覽器開啟訂餐頁
- **WHEN** 頁面載入完成
- **THEN** 左側顯示「今日店家」和「菜單」面板
- **AND** 中間顯示 AI 對話框
- **AND** 右側顯示「我的訂單」和「大家的訂單」面板

#### Scenario: 手機版堆疊顯示
- **GIVEN** 使用者在手機瀏覽器開啟訂餐頁
- **WHEN** 螢幕寬度小於 768px
- **THEN** 面板垂直堆疊，對話框優先顯示

### Requirement: 雙訂單面板
訂餐頁面 SHALL 同時顯示「我的訂單」和「大家的訂單」兩個面板。

#### Scenario: 我的訂單
- **GIVEN** 使用者在訂餐頁
- **WHEN** 訂單更新
- **THEN** 「我的訂單」只顯示當前使用者的訂單

#### Scenario: 大家的訂單
- **GIVEN** 使用者在訂餐頁
- **WHEN** 訂單更新
- **THEN** 「大家的訂單」顯示所有人的訂單彙總（原今日訂單邏輯）
- **AND** 顯示訂單總數和總金額

### Requirement: 團隊聊天室預設展開
訂餐頁面的團隊聊天室 SHALL 預設為展開狀態。

#### Scenario: 聊天室初始狀態
- **GIVEN** 使用者開啟訂餐頁
- **WHEN** 頁面載入完成
- **THEN** 團隊聊天室為展開狀態
- **AND** 使用者可點擊收合聊天室

