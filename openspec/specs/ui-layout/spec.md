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

### Requirement: 美食評論區預設展開
訂餐頁面的美食評論區 SHALL 預設為展開狀態。

#### Scenario: 聊天室初始狀態
- **GIVEN** 使用者開啟訂餐頁
- **WHEN** 頁面載入完成
- **THEN** 美食評論區為展開狀態
- **AND** 使用者可點擊收合聊天室

### Requirement: 今日店家資訊顯示
系統 SHALL 在所有頁面的今日店家區塊顯示完整店家資訊，包含名稱、電話（如有）、備註（如有）。

#### Scenario: 顯示完整店家資訊
- **GIVEN** 今日已設定店家
- **AND** 店家有電話和備註資訊
- **WHEN** 使用者查看今日店家區塊
- **THEN** 顯示店家名稱
- **AND** 顯示店家電話
- **AND** 顯示店家備註

#### Scenario: 顯示部分店家資訊
- **GIVEN** 今日已設定店家
- **AND** 店家沒有電話或備註
- **WHEN** 使用者查看今日店家區塊
- **THEN** 顯示店家名稱
- **AND** 只顯示有值的欄位（電話或備註）
- **AND** 沒有值的欄位不佔空間

### Requirement: 歡迎詞使用偏好稱呼
訂購頁和管理頁的歡迎詞 SHALL 使用使用者的偏好稱呼（preferred_name），稱呼置於句子中間以適應各種稱呼方式。

#### Scenario: 有設定偏好稱呼
- **GIVEN** 使用者已設定 `preferred_name` 為「老闆」
- **WHEN** 使用者進入訂購頁或管理頁
- **THEN** 歡迎詞顯示「哇係呷爸，老闆今天想吃什麼呢？」

#### Scenario: 沒有設定偏好稱呼
- **GIVEN** 使用者沒有設定 `preferred_name`
- **WHEN** 使用者進入訂購頁或管理頁
- **THEN** 歡迎詞顯示「哇係呷爸，我們今天想吃什麼呢？」

### Requirement: 顯示訂單品項備註
系統 SHALL 在所有訂單顯示處呈現品項的備註資訊。

#### Scenario: 看板顯示備註
- **GIVEN** 訂單品項有 `note` 欄位
- **WHEN** 看板頁面顯示訂單
- **THEN** 在品項名稱後顯示備註內容

#### Scenario: 訂餐頁顯示備註
- **GIVEN** 使用者查看自己的訂單
- **WHEN** 訂餐頁面顯示訂單品項
- **THEN** 顯示品項備註（如：不加香菜、大杯去冰）

#### Scenario: 管理頁顯示備註
- **GIVEN** 管理員查看今日訂單
- **WHEN** 管理頁面顯示訂單列表
- **THEN** 每個品項顯示其備註資訊

### Requirement: 菜單顯示品項尺寸變體
系統 SHALL 在菜單顯示中，當品項有尺寸變體（variants）時，顯示各尺寸名稱和對應價格。

#### Scenario: 管理員查看店家菜單（有尺寸變體）
- **GIVEN** 品項有 variants 陣列（如 M、L 杯）
- **WHEN** 管理員在「所有店家」面板展開店家菜單
- **THEN** 顯示各尺寸名稱和價格（如「M $50 / L $60」）

#### Scenario: 使用者在訂餐頁查看菜單（有尺寸變體）
- **GIVEN** 品項有 variants 陣列
- **WHEN** 使用者在訂餐頁查看菜單
- **THEN** 顯示各尺寸選項
- **AND** 點擊特定尺寸時，以該尺寸的價格下單

#### Scenario: 菜單品項無尺寸變體
- **GIVEN** 品項沒有 variants 陣列
- **WHEN** 顯示該品項
- **THEN** 只顯示預設價格（item.price）

### Requirement: 管理員直接編輯店家菜單
管理員 SHALL 能夠直接編輯現有店家的菜單，不需要重新上傳圖片辨識。

#### Scenario: 點擊編輯按鈕
- **GIVEN** 管理員在「所有店家」面板
- **WHEN** 點擊某店家的「編輯」按鈕
- **THEN** 彈出菜單編輯畫面
- **AND** 載入該店家現有的菜單內容

#### Scenario: 編輯並儲存菜單
- **GIVEN** 管理員在菜單編輯畫面
- **WHEN** 修改品項名稱、價格、尺寸等並儲存
- **THEN** 更新該店家的菜單
- **AND** 關閉編輯畫面

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

