# super-admin-ui Specification

## Purpose
TBD - created by archiving change refactor-super-admin-panel. Update Purpose after archive.
## Requirements
### Requirement: 使用者識別
系統 SHALL 使用 LINE User ID 作為使用者唯一識別，profile.json 中記錄 display_name 作為顯示名稱。

#### Scenario: 建立 LINE 使用者
- **WHEN** LINE 使用者首次點餐
- **THEN** 建立 `data/users/{line_user_id}/profile.json`
- **AND** profile 包含 `line_user_id` 和 `display_name` 欄位

#### Scenario: Profile 結構
- **GIVEN** LINE 使用者的 profile.json
- **THEN** 包含以下結構：
  ```json
  {
    "line_user_id": "Uxxxxxxxxxxxxxxxxx",
    "display_name": "王小明",
    "created_at": "建立時間",
    "preferences": {
      "dietary_restrictions": [],
      "allergies": [],
      "drink_preferences": [],
      "notes": ""
    }
  }
  ```

#### Scenario: 讀取使用者名稱
- **GIVEN** 呼叫 `get_user_profile(line_user_id)`
- **WHEN** 使用者存在
- **THEN** 回傳 profile 資料
- **AND** 可從 `display_name` 取得顯示名稱

