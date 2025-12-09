# user-management Specification

## Purpose
TBD - created by archiving change add-data-architecture. Update Purpose after archive.
## Requirements
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

### Requirement: 管理員使用者管理
系統 SHALL 允許管理員檢視與管理所有使用者清單。

#### Scenario: 列出所有使用者
- **WHEN** 管理員查看使用者列表
- **THEN** 列出 `data/users/` 下所有使用者

