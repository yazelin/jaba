# admin-ui Spec Delta

## ADDED Requirements

### Requirement: 菜單品項尺寸編輯
系統 SHALL 支援管理員在菜單編輯介面編輯品項的尺寸變體。

#### Scenario: 顯示現有尺寸
- **GIVEN** 品項有 `variants` 欄位
- **WHEN** 顯示菜單編輯介面
- **THEN** 列出所有尺寸名稱和價格

#### Scenario: 新增尺寸
- **GIVEN** 管理員點選「新增尺寸」
- **WHEN** 輸入尺寸名稱和價格
- **THEN** 新增一筆尺寸變體

#### Scenario: 刪除尺寸
- **GIVEN** 品項有多個尺寸
- **WHEN** 管理員點選刪除某尺寸
- **THEN** 該尺寸從 variants 中移除

#### Scenario: 儲存尺寸
- **GIVEN** 管理員編輯完 variants
- **WHEN** 儲存菜單
- **THEN** variants 資料正確寫入 menu.json
