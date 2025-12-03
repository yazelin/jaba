# ui-layout Spec Delta

## ADDED Requirements

### Requirement: 顯示訂單品項備註
系統 SHALL 在所有訂單顯示處呈現品項的備註資訊。

#### Scenario: 看板顯示備註
- **GIVEN** 訂單品項有 `note` 欄位
- **WHEN** 看板頁面顯示訂單
- **THEN** 在品項名稱後顯示備註內容

#### Scenario: 訂餐頁顯示備註
- **GIVEN** 使用者查看自己的訂單
- **WHEN** 訂餐頁面顯示訂單品項
- **THEN** 顯示品項備註（如：不加香菜、大杯去冰）

#### Scenario: 管理頁顯示備註
- **GIVEN** 管理員查看今日訂單
- **WHEN** 管理頁面顯示訂單列表
- **THEN** 每個品項顯示其備註資訊
