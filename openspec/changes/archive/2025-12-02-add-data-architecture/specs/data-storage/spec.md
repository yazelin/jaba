## ADDED Requirements

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
