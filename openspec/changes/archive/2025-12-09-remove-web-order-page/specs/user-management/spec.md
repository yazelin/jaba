# user-management Specification Delta

## Purpose
調整使用者管理規格，移除 Web Order 頁面的名字輸入識別方式。

## MODIFIED Requirements

### Requirement: 使用者識別
系統 SHALL 使用 LINE User ID 作為使用者唯一識別。Web 輸入名字識別方式已移除。

#### Scenario: 新使用者首次使用（修改）
- **WHEN** LINE 使用者首次在群組中點餐
- **THEN** 自動建立 `data/users/{line_user_id}/profile.json`
- **AND** profile 包含 `line_user_id` 和 `display_name`

#### Scenario: 既有使用者識別（修改）
- **WHEN** LINE 使用者再次點餐
- **THEN** 透過 `line_user_id` 載入該使用者的資料

### Requirement: 使用者資料儲存
系統 SHALL 在 `data/users/{line_user_id}/` 儲存 profile.json，profile.json 支援擴充的個人化欄位。

#### Scenario: Profile 結構（修改）
- **GIVEN** LINE 使用者的 profile.json
- **THEN** 包含以下結構：
  ```json
  {
    "line_user_id": "Uxxxxxxxxxxxxxxxxx",
    "display_name": "王小明",
    "created_at": "建立時間",
    "preferences": {
      "dietary_restrictions": ["不吃辣"],
      "allergies": ["海鮮過敏"],
      "drink_preferences": [],
      "notes": "其他備註"
    }
  }
  ```
