# ui-layout Spec Delta

## ADDED Requirements

### Requirement: 今日店家資訊顯示
系統 SHALL 在所有頁面的今日店家區塊顯示完整店家資訊，包含名稱、電話（如有）、備註（如有）。

#### Scenario: 顯示完整店家資訊
- **GIVEN** 今日已設定店家
- **AND** 店家有電話和備註資訊
- **WHEN** 使用者查看今日店家區塊
- **THEN** 顯示店家名稱
- **AND** 顯示店家電話
- **AND** 顯示店家備註

#### Scenario: 顯示部分店家資訊
- **GIVEN** 今日已設定店家
- **AND** 店家沒有電話或備註
- **WHEN** 使用者查看今日店家區塊
- **THEN** 顯示店家名稱
- **AND** 只顯示有值的欄位（電話或備註）
- **AND** 沒有值的欄位不佔空間
