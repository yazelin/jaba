# order-management Spec Delta

## ADDED Requirements

### Requirement: 付款狀態獨立按鈕
管理員頁面 SHALL 提供獨立按鈕讓管理員直接更新付款狀態，無需透過 AI 對話。

#### Scenario: 顯示確認付款按鈕（未付款）
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount=0`
- **WHEN** 管理員查看付款面板
- **THEN** 顯示「確認付款」按鈕

#### Scenario: 顯示確認付款按鈕（待補款）
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount > 0`（部分已付）
- **WHEN** 管理員查看付款面板
- **THEN** 顯示「確認付款」按鈕

#### Scenario: 點擊確認付款按鈕
- **WHEN** 管理員點擊「確認付款」按鈕
- **THEN** 呼叫 `/api/mark-paid` API
- **AND** 設定 `paid` 為 true
- **AND** 設定 `paid_amount` 為當前 `amount`
- **AND** 清除 `note`
- **AND** 廣播 `payment_updated` 事件
- **AND** 即時更新付款面板顯示

#### Scenario: 已付款不顯示確認付款按鈕
- **GIVEN** 付款記錄 `paid=true` 且無待補備註
- **WHEN** 管理員查看付款面板
- **THEN** 不顯示「確認付款」按鈕

#### Scenario: 顯示確認退款按鈕
- **GIVEN** 付款記錄有「待退」備註
- **WHEN** 管理員查看付款面板
- **THEN** 顯示「確認退款」按鈕
