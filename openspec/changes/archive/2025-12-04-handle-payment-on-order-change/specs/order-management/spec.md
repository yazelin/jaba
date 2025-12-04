# order-management Spec Delta

## MODIFIED Requirements

### Requirement: 付款記錄
系統 SHALL 在 `orders/{date}/payments.json` 記錄付款狀態，並在訂單金額變動時智慧更新付款狀態。

#### Scenario: 標記已付款
- **WHEN** 管理員標記某人已付款
- **THEN** 更新 `paid` 為 true
- **AND** 設定 `paid_amount` 為當前 `amount`
- **AND** 記錄 `paid_at` 時間
- **AND** 清除 `note`

#### Scenario: 查看未付款
- **WHEN** 管理員查看未付款清單
- **THEN** 列出 `paid` 為 false 的紀錄

#### Scenario: 已付款後訂單金額增加
- **GIVEN** 使用者已標記付款，`paid_amount` 為 100
- **WHEN** 修改訂單導致 `amount` 變為 150
- **THEN** 設定 `paid` 為 false
- **AND** 保留 `paid_amount` 為 100
- **AND** 設定 `note` 為「已付 $100，待補 $50」

#### Scenario: 已付款後訂單金額減少
- **GIVEN** 使用者已標記付款，`paid_amount` 為 100
- **WHEN** 修改訂單導致 `amount` 變為 70
- **THEN** 維持 `paid` 為 true
- **AND** 保留 `paid_amount` 為 100
- **AND** 設定 `note` 為「待退 $30」

#### Scenario: 已付款後訂單金額不變
- **GIVEN** 使用者已標記付款
- **WHEN** 修改訂單但 `amount` 不變
- **THEN** 維持原有付款狀態

#### Scenario: 訂單取消且已付款
- **GIVEN** 使用者已標記付款，`paid_amount` 為 100
- **WHEN** 訂單被取消
- **THEN** 設定 `amount` 為 0
- **AND** 設定 `note` 為「待退 $100」

#### Scenario: 取消後重新訂餐
- **GIVEN** 使用者已付款 100 後取消訂單，`paid_amount` 為 100
- **WHEN** 使用者重新訂餐 80 元
- **THEN** 設定 `amount` 為 80
- **AND** 保留 `paid_amount` 為 100
- **AND** 設定 `note` 為「待退 $20」

#### Scenario: 清除所有訂單（有待退款）
- **GIVEN** 有使用者已付款，`paid_amount` > 0
- **WHEN** 管理員清除所有訂單
- **THEN** 清除訂單記錄
- **AND** 保留有 `paid_amount` > 0 的付款記錄
- **AND** 設定這些記錄的 `amount` 為 0
- **AND** 設定 `note` 為「待退 $X」

#### Scenario: 清除所有訂單（無待退款）
- **GIVEN** 使用者 `paid_amount` = 0（從未付款）
- **WHEN** 管理員清除所有訂單
- **THEN** 清除訂單記錄
- **AND** 移除該使用者的付款記錄

#### Scenario: 標記已退款（無剩餘訂單）
- **GIVEN** 付款記錄 `amount` 為 0 且 `paid_amount` > 0
- **WHEN** 管理員標記已退款
- **THEN** 移除該付款記錄
- **AND** 重新計算 `total_collected` 和 `total_pending`

#### Scenario: 標記已退款（有剩餘訂單）
- **GIVEN** 付款記錄 `amount` > 0 且 `paid_amount` > `amount`（有待退款）
- **WHEN** 管理員標記已退款
- **THEN** 設定 `paid_amount` 為 `amount`（多付的已退還）
- **AND** 設定 `paid` 為 true
- **AND** 清除 `note`
- **AND** 該記錄變成「已付清」狀態

## ADDED Requirements

### Requirement: 付款狀態前端顯示
管理員頁面 SHALL 根據付款狀態顯示不同樣式和資訊。

#### Scenario: 顯示未付款狀態
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount=0`
- **WHEN** 管理員查看付款面板
- **THEN** 顯示灰色「未付」標籤

#### Scenario: 顯示已付款狀態
- **GIVEN** 付款記錄 `paid=true` 且無待退備註
- **WHEN** 管理員查看付款面板
- **THEN** 顯示綠色「已付」標籤

#### Scenario: 顯示部分已付狀態
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount > 0`
- **WHEN** 管理員查看付款面板
- **THEN** 顯示橘色「待補 $X」標籤
- **AND** 滑鼠懸停顯示備註內容

#### Scenario: 顯示待退款狀態
- **GIVEN** 付款記錄 `paid=true` 且 `note` 包含「待退」
- **WHEN** 管理員查看付款面板
- **THEN** 顯示藍色「待退 $X」標籤
