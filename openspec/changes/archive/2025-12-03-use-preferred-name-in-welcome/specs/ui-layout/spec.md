# ui-layout Spec Delta

## ADDED Requirements

### Requirement: 歡迎詞使用偏好稱呼
訂購頁和管理頁的歡迎詞 SHALL 使用使用者的偏好稱呼（preferred_name），稱呼置於句子中間以適應各種稱呼方式。

#### Scenario: 有設定偏好稱呼
- **GIVEN** 使用者已設定 `preferred_name` 為「老闆」
- **WHEN** 使用者進入訂購頁或管理頁
- **THEN** 歡迎詞顯示「哇係呷爸，老闆今天想吃什麼呢？」

#### Scenario: 沒有設定偏好稱呼
- **GIVEN** 使用者沒有設定 `preferred_name`
- **WHEN** 使用者進入訂購頁或管理頁
- **THEN** 歡迎詞顯示「哇係呷爸，我們今天想吃什麼呢？」
