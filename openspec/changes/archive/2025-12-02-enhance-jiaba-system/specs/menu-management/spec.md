## MODIFIED Requirements

### Requirement: 店家資訊儲存
系統 SHALL 在 info.json 儲存店家 id、name、phone、address、active、note（備註說明）等欄位。

#### Scenario: 停用店家
- **WHEN** 管理員停用某店家
- **THEN** 將 active 設為 false，訂餐時不顯示

#### Scenario: 顯示店家備註
- **WHEN** 查看店家資訊
- **THEN** 顯示 note 欄位內容（如最後點餐時間、特別說明）

### Requirement: 多店家支援
系統 SHALL 支援多家便當店，每家店在 `data/stores/{store-id}/` 有獨立目錄。今日可設定多個店家同時營業。

#### Scenario: 列出可用店家
- **WHEN** 查詢可用店家
- **THEN** 回傳所有 active 為 true 的店家

#### Scenario: 設定多個今日店家
- **WHEN** 管理員設定今日店家
- **THEN** 可新增多個店家到今日營業列表

## ADDED Requirements

### Requirement: 店家備註欄位
系統 SHALL 支援店家 note 欄位，用於顯示特別說明（如最後點餐時間、外送費說明等）。

#### Scenario: 編輯店家備註
- **WHEN** 管理員透過 AI 編輯店家備註
- **THEN** 更新 info.json 中的 note 欄位

#### Scenario: 前端顯示備註
- **WHEN** 在看板頁、訂餐頁顯示店家資訊
- **THEN** 一併顯示 note 備註內容
