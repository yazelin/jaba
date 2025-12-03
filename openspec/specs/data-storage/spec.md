# data-storage Specification

## Purpose
TBD - created by archiving change add-data-architecture. Update Purpose after archive.
## Requirements
### Requirement: 資料目錄結構
系統 SHALL 使用 `data/` 目錄作為所有資料的根目錄，包含 system/、stores/、users/、orders/ 子目錄。

#### Scenario: 首次啟動建立目錄
- **WHEN** 系統首次啟動且 `data/` 不存在
- **THEN** 自動建立完整的目錄結構

### Requirement: JSON 資料格式
系統 SHALL 使用 JSON 格式儲存所有結構化資料，使用 UTF-8 編碼與 2 空格縮排。

#### Scenario: 寫入資料檔案
- **WHEN** 系統或 AI Agent 寫入任何資料
- **THEN** 輸出格式化的 JSON 檔案

### Requirement: 資料存取模組
系統 SHALL 提供 Python 模組處理 JSON 檔案的讀寫與目錄操作。

#### Scenario: 讀取 JSON 檔案
- **WHEN** 後端需要讀取資料
- **THEN** 解析 JSON 並回傳 Python dict

#### Scenario: 寫入 JSON 檔案
- **WHEN** 後端需要儲存資料
- **THEN** 將 dict 序列化為格式化 JSON 並寫入

### Requirement: 今日店家資料格式
系統 SHALL 統一使用 `stores[]` 陣列格式儲存今日店家，不再維護冗餘的頂層欄位。

#### Scenario: 儲存今日店家
- **GIVEN** 管理員設定今日店家
- **WHEN** 系統儲存至 `system/today.json`
- **THEN** 只使用 `stores[]` 陣列儲存
- **AND** 不設定頂層 `store_id` 和 `store_name`

#### Scenario: 讀取今日店家
- **GIVEN** 系統讀取 `system/today.json`
- **WHEN** 處理店家資訊
- **THEN** 直接使用 `stores[]` 陣列
- **AND** 不需要檢查頂層欄位

### Requirement: 訂單檔案格式
系統 SHALL 統一使用 `{date}-{timestamp}.json` 格式儲存使用者訂單。

#### Scenario: 儲存訂單
- **GIVEN** 使用者建立訂單
- **WHEN** 系統儲存訂單
- **THEN** 使用 `{date}-{timestamp}.json` 格式命名
- **AND** 不使用舊的 `{date}.json` 格式

#### Scenario: 讀取訂單
- **GIVEN** 系統讀取使用者訂單
- **WHEN** 搜尋訂單檔案
- **THEN** 只匹配 `{date}-*.json` 模式
- **AND** 不檢查 `{date}.json` 舊格式

