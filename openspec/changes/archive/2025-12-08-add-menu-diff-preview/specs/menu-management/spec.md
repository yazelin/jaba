## ADDED Requirements

### Requirement: 特價品項促銷欄位
系統 SHALL 在菜單品項結構中支援 `promo` 欄位，用於定義促銷類型與計價規則。

#### Scenario: 定義買一送一促銷
- **GIVEN** 菜單品項需要設定買一送一優惠
- **WHEN** 設定 `promo.type` 為 `buy_one_get_one`
- **THEN** 品項包含 `promo.label` 顯示文字
- **AND** 訂購時每兩杯計算一杯價格

#### Scenario: 定義第二杯折扣促銷
- **GIVEN** 菜單品項需要設定第二杯折扣
- **WHEN** 設定 `promo.type` 為 `second_discount`
- **THEN** 品項包含 `promo.second_price`（固定價格）或 `promo.second_ratio`（折數）
- **AND** 訂購時第 2, 4, 6... 杯享折扣價

#### Scenario: 定義限時特價促銷
- **GIVEN** 菜單品項需要設定限時特價
- **WHEN** 設定 `promo.type` 為 `time_limited`
- **THEN** 品項包含 `promo.original_price` 和 `promo.promo_price`
- **AND** 訂購時使用 `promo_price` 計算

#### Scenario: 無促銷品項
- **GIVEN** 菜單品項無促銷
- **WHEN** 品項沒有 `promo` 欄位或 `promo` 為 null
- **THEN** 使用原始 `price` 計算

### Requirement: 特價優惠分類
系統 SHALL 支援「特價優惠」分類，用於歸類所有促銷品項。

#### Scenario: AI 辨識特價品項
- **GIVEN** 菜單圖片包含特價促銷文字（如「買一送一」、「第二杯10元」）
- **WHEN** AI 辨識菜單
- **THEN** 將該品項歸類至「特價優惠」分類
- **AND** 自動設定對應的 `promo` 欄位

#### Scenario: 顯示特價標籤
- **GIVEN** 品項有 `promo` 欄位
- **WHEN** 顯示菜單
- **THEN** 品項名稱旁顯示 `promo.label` 標籤

### Requirement: 菜單差異比對
系統 SHALL 在辨識菜單後，比對現有菜單與辨識結果的差異。

#### Scenario: 識別新增品項
- **GIVEN** 辨識結果包含現有菜單沒有的品項
- **WHEN** 執行差異比對
- **THEN** 將該品項標記為 `added`

#### Scenario: 識別修改品項
- **GIVEN** 辨識結果與現有菜單有相同名稱但內容不同的品項
- **WHEN** 執行差異比對
- **THEN** 將該品項標記為 `modified`
- **AND** 顯示變更前後的差異（價格、促銷等）

#### Scenario: 識別可刪除品項
- **GIVEN** 現有菜單有品項但辨識結果中沒有
- **WHEN** 執行差異比對
- **THEN** 將該品項標記為 `removed`
- **AND** 提示使用者「此品項可能已停售」

#### Scenario: 識別未變更品項
- **GIVEN** 辨識結果與現有菜單有完全相同的品項
- **WHEN** 執行差異比對
- **THEN** 將該品項標記為 `unchanged`

### Requirement: 選擇性菜單更新
系統 SHALL 允許使用者選擇要套用的菜單變更。

#### Scenario: 勾選新增品項
- **GIVEN** 差異預覽顯示新增品項
- **WHEN** 使用者勾選該品項並儲存
- **THEN** 將該品項加入菜單

#### Scenario: 勾選修改品項
- **GIVEN** 差異預覽顯示修改品項
- **WHEN** 使用者勾選該品項並儲存
- **THEN** 更新該品項的內容

#### Scenario: 勾選刪除品項
- **GIVEN** 差異預覽顯示可刪除品項
- **WHEN** 使用者勾選「標記刪除」並儲存
- **THEN** 從菜單中移除該品項

#### Scenario: 不勾選則保留原狀
- **GIVEN** 差異預覽顯示變更品項
- **WHEN** 使用者未勾選該品項並儲存
- **THEN** 該品項維持原狀不變
