# ai-integration Spec Delta

## MODIFIED Requirements

### Requirement: AI 動作執行
系統 SHALL 統一使用 `actions` 陣列格式處理 AI 回應的動作。

#### Scenario: AI 回應動作
- **GIVEN** AI 回應訊息
- **WHEN** 回應包含需要執行的動作
- **THEN** 使用 `actions` 陣列格式
- **AND** 不使用單一 `action` 欄位

#### Scenario: 執行動作
- **GIVEN** 收到 AI 回應
- **WHEN** 處理動作
- **THEN** 只從 `actions` 陣列讀取動作
- **AND** 不檢查 `action` 單一欄位
