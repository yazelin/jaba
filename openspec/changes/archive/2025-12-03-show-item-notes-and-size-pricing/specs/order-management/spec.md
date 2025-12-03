# order-management Spec Delta

## ADDED Requirements

### Requirement: 訂單品項尺寸
系統 SHALL 支援訂單品項指定尺寸，並根據尺寸計算正確價格。

#### Scenario: 指定尺寸建立訂單
- **GIVEN** 使用者點選有變體的飲料品項
- **WHEN** AI 建立訂單
- **THEN** 訂單品項包含 `size` 欄位
- **AND** 系統從 `variants` 查找對應價格

#### Scenario: 未指定尺寸
- **GIVEN** 使用者點選有變體的品項但未指定尺寸
- **WHEN** AI 建立訂單
- **THEN** 使用品項的預設 `price`
