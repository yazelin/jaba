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

