# data-storage Specification

## Purpose

定義系統的檔案儲存結構和資料格式。

## Requirements

### Requirement: 資料目錄結構
系統 SHALL 使用 `data/` 目錄作為所有資料的根目錄。

#### Scenario: 首次啟動建立目錄
- **WHEN** 系統首次啟動且 `data/` 不存在
- **THEN** 自動建立目錄結構：`system/`、`stores/`、`users/`、`linebot/`

#### Scenario: 使用者資料目錄
- **WHEN** 建立新使用者
- **THEN** 建立 `users/{line_user_id}/` 目錄
- **AND** 建立 `profile.json`
- **AND** 按需建立 `chat_history/` 目錄（有對話時）

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
系統 SHALL 統一使用 `stores[]` 陣列格式儲存今日店家。

#### Scenario: 儲存今日店家
- **GIVEN** 管理員設定今日店家
- **WHEN** 系統儲存至 `system/today.json`
- **THEN** 使用 `stores[]` 陣列儲存

#### Scenario: 讀取今日店家
- **GIVEN** 系統讀取 `system/today.json`
- **WHEN** 處理店家資訊
- **THEN** 直接使用 `stores[]` 陣列

### Requirement: 群組訂單儲存
系統 SHALL 將群組訂單儲存在群組 session 檔案中。

#### Scenario: 儲存群組訂單
- **GIVEN** 使用者在群組中點餐
- **WHEN** 建立訂單
- **THEN** 訂單存在 `linebot/sessions/{group_id}.json` 的 `orders` 陣列中

#### Scenario: 付款追蹤
- **GIVEN** 群組有訂單
- **WHEN** 追蹤付款狀態
- **THEN** 付款記錄存在 `linebot/sessions/{group_id}.json` 的 `payments` 物件中
