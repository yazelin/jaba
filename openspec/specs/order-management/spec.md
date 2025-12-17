# order-management Specification

## Purpose

定義群組訂單的管理功能。訂單透過群組點餐功能建立，儲存在群組 session 中。
## Requirements
### Requirement: 訂單品項尺寸
系統 SHALL 支援訂單品項指定尺寸，並根據尺寸計算正確價格。

#### Scenario: 指定尺寸建立訂單
- **GIVEN** 使用者點選有變體的飲料品項
- **WHEN** 建立群組訂單
- **THEN** 訂單品項包含 `size` 欄位
- **AND** 系統從 `variants` 查找對應價格

#### Scenario: 未指定尺寸
- **GIVEN** 使用者點選有變體的品項但未指定尺寸
- **WHEN** 建立群組訂單
- **THEN** 使用品項的預設 `price`

### Requirement: 特價品項訂單計價
系統 SHALL 根據菜單品項的 `promo` 設定，正確計算訂單金額。

#### Scenario: 買一送一計價
- **GIVEN** 品項設定為買一送一，單價 $50
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $50（買一送一，2杯收1杯價）

#### Scenario: 買一送一奇數杯計價
- **GIVEN** 品項設定為買一送一，單價 $50
- **WHEN** 使用者訂購 3 杯
- **THEN** 訂單金額為 $100（第1-2杯買一送一$50 + 第3杯原價$50）

#### Scenario: 第二杯固定價計價
- **GIVEN** 品項設定為第二杯 $10，單價 $50
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $60（$50 + $10）

#### Scenario: 無促銷正常計價
- **GIVEN** 品項無 `promo` 設定，單價 $50
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $100（$50 × 2）

### Requirement: 訂單品項促銷資訊記錄
系統 SHALL 在訂單品項中記錄促銷資訊，以便查詢和核對。

#### Scenario: 記錄促銷類型
- **GIVEN** 使用者訂購有促銷的品項
- **WHEN** 建立訂單
- **THEN** 訂單品項包含 `promo_type` 欄位
- **AND** 包含 `promo_label` 顯示文字

### Requirement: 群組點餐摘要品項統計
系統 SHALL 在群組點餐結束時產生品項統計，以品項名稱為統計單位，不含備註。

#### Scenario: 相同品項不同備註合計統計
- **GIVEN** 群組點餐結束
- **AND** 訂單包含：
  - 珍奶 x1（無備註）
  - 珍奶（微糖微冰）x2
- **WHEN** 產生摘要的品項統計
- **THEN** 品項統計顯示：`珍奶 x3`
- **AND** 不區分備註內容

#### Scenario: 個人訂單明細保留備註
- **GIVEN** 群組點餐結束
- **AND** 王小明訂了「珍奶（微糖微冰）」
- **WHEN** 產生摘要
- **THEN** 個人訂單明細顯示：`珍奶（微糖微冰）$55`
- **AND** 備註資訊完整保留

