# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 菜單辨識尺寸變體
系統 SHALL 在辨識菜單圖片時，自動提取品項的尺寸變體資訊。

#### Scenario: 辨識多尺寸品項
- **GIVEN** 菜單圖片顯示 M/L、大/中/小、大碗/小碗等尺寸價格
- **WHEN** AI 辨識菜單
- **THEN** 輸出 `variants` 陣列包含各尺寸名稱和價格
- **AND** `price` 欄位填入最小尺寸的價格

#### Scenario: 無尺寸區分
- **GIVEN** 菜單品項只有單一價格
- **WHEN** AI 辨識菜單
- **THEN** 不產生 `variants` 欄位
- **AND** `price` 欄位填入該價格

### Requirement: AI 對話編輯尺寸變體
系統 SHALL 支援管理員透過對話讓 AI 編輯品項的尺寸價格。

#### Scenario: 修改尺寸價格
- **GIVEN** 管理員說「把珍珠奶茶的 L 杯改成 65 元」
- **WHEN** AI 執行 `update_item_variants` 動作
- **THEN** 更新該品項的 L 尺寸價格為 65

#### Scenario: 新增尺寸
- **GIVEN** 管理員說「幫雞腿便當加一個大份選項，100元」
- **WHEN** AI 執行 `update_item_variants` 動作
- **THEN** 在該品項的 variants 中新增大份尺寸
