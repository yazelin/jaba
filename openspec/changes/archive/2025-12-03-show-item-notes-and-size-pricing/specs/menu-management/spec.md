# menu-management Spec Delta

## ADDED Requirements

### Requirement: 品項尺寸變體
系統 SHALL 支援菜單品項的尺寸變體，每個變體可有不同價格。

#### Scenario: 定義尺寸變體
- **GIVEN** 飲料店菜單品項有多種尺寸
- **WHEN** 定義菜單品項
- **THEN** 可選擇性設定 `variants` 陣列
- **AND** 每個 variant 包含 `name`（尺寸名稱）和 `price`

#### Scenario: 無變體品項
- **GIVEN** 便當店菜單品項無尺寸區分
- **WHEN** 定義菜單品項
- **THEN** 只設定 `price` 欄位，不需 `variants`

#### Scenario: AI 讀取變體資訊
- **GIVEN** AI 需要介紹飲料品項
- **WHEN** 品項有 `variants` 欄位
- **THEN** AI 可列出各尺寸的價格供使用者選擇
