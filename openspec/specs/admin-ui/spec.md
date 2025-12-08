# admin-ui Specification

## Purpose
TBD - created by archiving change fix-admin-panel-layout. Update Purpose after archive.
## Requirements
### Requirement: 管理員面板三欄佈局
管理員頁面 SHALL 採用三欄佈局：左側為店家管理、中間為對話框、右側為資訊面板（今日店家、今日訂單、付款狀態）。

#### Scenario: 桌面版顯示
- **WHEN** 在寬度足夠的螢幕檢視管理員頁面
- **THEN** 顯示三欄佈局：左側店家管理、中間對話、右側資訊面板

#### Scenario: 行動版顯示
- **WHEN** 在小螢幕檢視管理員頁面
- **THEN** 改為單欄垂直排列

### Requirement: 店家管理面板完整滾動
店家管理面板 SHALL 確保所有店家都能透過滾動查看，包含最後一個店家。

#### Scenario: 多店家滾動
- **WHEN** 店家數量超過面板可視高度
- **THEN** 可滾動查看所有店家，最後一個店家能完整顯示

### Requirement: 菜單上傳入口明顯化
菜單上傳功能 SHALL 提供明顯的入口，讓管理員容易發現並使用。

#### Scenario: 顯示上傳按鈕
- **WHEN** 管理員檢視店家管理面板
- **THEN** 顯示明顯的「上傳菜單」按鈕（含文字提示）

### Requirement: 新增店家菜單上傳
系統 SHALL 支援在上傳菜單時同時新增店家，正確處理中文店名。

#### Scenario: 中文店名新增店家
- **WHEN** 選擇「新增店家」並輸入中文店名後上傳菜單
- **THEN** 成功建立店家並儲存菜單

#### Scenario: 上傳錯誤處理
- **WHEN** 菜單上傳發生錯誤
- **THEN** 顯示具體錯誤訊息而非 HTML 解析錯誤

### Requirement: 菜單品項尺寸編輯
系統 SHALL 支援管理員在菜單編輯介面編輯品項的尺寸變體。

#### Scenario: 顯示現有尺寸
- **GIVEN** 品項有 `variants` 欄位
- **WHEN** 顯示菜單編輯介面
- **THEN** 列出所有尺寸名稱和價格

#### Scenario: 新增尺寸
- **GIVEN** 管理員點選「新增尺寸」
- **WHEN** 輸入尺寸名稱和價格
- **THEN** 新增一筆尺寸變體

#### Scenario: 刪除尺寸
- **GIVEN** 品項有多個尺寸
- **WHEN** 管理員點選刪除某尺寸
- **THEN** 該尺寸從 variants 中移除

#### Scenario: 儲存尺寸
- **GIVEN** 管理員編輯完 variants
- **WHEN** 儲存菜單
- **THEN** variants 資料正確寫入 menu.json

### Requirement: 店家啟用狀態切換按鈕
管理員頁面 SHALL 提供可點擊的按鈕讓管理員直接切換店家啟用狀態，無需透過 AI 對話。

#### Scenario: 顯示啟用狀態按鈕
- **GIVEN** 店家 `active=true`
- **WHEN** 管理員查看店家管理面板
- **THEN** 顯示綠色「啟用」按鈕

#### Scenario: 顯示停用狀態按鈕
- **GIVEN** 店家 `active=false`
- **WHEN** 管理員查看店家管理面板
- **THEN** 顯示灰色「停用」按鈕

#### Scenario: 點擊停用店家
- **GIVEN** 店家目前為啟用狀態
- **WHEN** 管理員點擊「啟用」按鈕
- **THEN** 呼叫 `/api/store/{store_id}/toggle` API
- **AND** 設定店家 `active` 為 false
- **AND** 按鈕變為灰色「停用」

#### Scenario: 點擊啟用店家
- **GIVEN** 店家目前為停用狀態
- **WHEN** 管理員點擊「停用」按鈕
- **THEN** 呼叫 `/api/store/{store_id}/toggle` API
- **AND** 設定店家 `active` 為 true
- **AND** 按鈕變為綠色「啟用」

### Requirement: 菜單差異預覽介面
管理員頁面 SHALL 在菜單辨識完成後顯示差異預覽介面，讓使用者檢視並選擇要套用的變更。

#### Scenario: 顯示新增品項
- **GIVEN** 辨識結果有新增品項
- **WHEN** 顯示差異預覽
- **THEN** 以綠色標記顯示新增品項
- **AND** 預設勾選新增品項

#### Scenario: 顯示修改品項
- **GIVEN** 辨識結果有修改品項
- **WHEN** 顯示差異預覽
- **THEN** 以黃色標記顯示修改品項
- **AND** 顯示變更前後的差異（如價格 $40 → $45）
- **AND** 預設勾選修改品項

#### Scenario: 顯示可刪除品項
- **GIVEN** 現有菜單有品項但辨識結果沒有
- **WHEN** 顯示差異預覽
- **THEN** 以紅色標記顯示可刪除品項
- **AND** 顯示「新菜單中未出現」提示
- **AND** 預設不勾選（避免誤刪）

#### Scenario: 套用選取項目
- **WHEN** 使用者點擊「套用選取項目」按鈕
- **THEN** 只更新勾選的品項
- **AND** 未勾選的品項維持原狀

### Requirement: 特價品項編輯介面
管理員頁面 SHALL 提供特價品項的促銷設定介面。

#### Scenario: 選擇促銷類型
- **GIVEN** 編輯菜單品項
- **WHEN** 點選「設定促銷」
- **THEN** 顯示促銷類型下拉選單
- **AND** 選項包含：無、買一送一、第二杯折扣、限時特價

#### Scenario: 設定買一送一
- **GIVEN** 選擇促銷類型為「買一送一」
- **WHEN** 確認設定
- **THEN** 顯示「買一送一」標籤
- **AND** 顯示計價說明「2杯收1杯價」

#### Scenario: 設定第二杯折扣
- **GIVEN** 選擇促銷類型為「第二杯折扣」
- **WHEN** 輸入第二杯價格（如 10 元）
- **THEN** 顯示「第二杯10元」標籤
- **AND** 顯示計價說明「第2杯$10」

#### Scenario: 設定限時特價
- **GIVEN** 選擇促銷類型為「限時特價」
- **WHEN** 輸入原價與特價
- **THEN** 顯示「限時特價」標籤
- **AND** 顯示原價劃掉與特價

### Requirement: 特價品項顯示
管理員頁面 SHALL 在菜單列表中清楚標示特價品項。

#### Scenario: 顯示促銷標籤
- **GIVEN** 品項有 `promo` 設定
- **WHEN** 顯示菜單列表
- **THEN** 品項旁顯示彩色促銷標籤（如「買一送一」）

#### Scenario: 顯示計價預覽
- **GIVEN** 品項有促銷設定
- **WHEN** 滑鼠懸停在品項上
- **THEN** 顯示計價說明 tooltip

