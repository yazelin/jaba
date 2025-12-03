# admin-ui Spec Delta

## ADDED Requirements

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
