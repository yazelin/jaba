# user-management Specification

## Purpose
TBD - created by archiving change add-data-architecture. Update Purpose after archive.
## Requirements
### Requirement: 使用者識別
系統 SHALL 使用名字作為使用者唯一識別，輸入名字即可存取對應資料。

#### Scenario: 新使用者首次使用
- **WHEN** 使用者輸入不存在的名字
- **THEN** 自動建立 `data/users/{username}/` 與 profile.json

#### Scenario: 既有使用者登入
- **WHEN** 使用者輸入已存在的名字
- **THEN** 載入該使用者的資料

### Requirement: 使用者資料儲存
系統 SHALL 在 `data/users/{username}/` 儲存 profile.json 與 orders/ 目錄，profile.json 支援擴充的個人化欄位。

#### Scenario: 儲存使用者偏好
- **WHEN** 使用者設定偏好（如不吃辣、稱呼方式）
- **THEN** 更新 profile.json 的 preferences 欄位

#### Scenario: Profile 結構
- **GIVEN** 使用者的 profile.json
- **THEN** 包含以下結構：
  ```json
  {
    "username": "使用者名稱",
    "created_at": "建立時間",
    "preferences": {
      "preferred_name": "希望被稱呼的名字",
      "dietary_restrictions": ["不吃辣", "素食"],
      "allergies": ["海鮮過敏"],
      "notes": "其他備註"
    }
  }
  ```

#### Scenario: 讀取使用者偏好
- **GIVEN** 呼叫 `get_user_profile(username)`
- **WHEN** 使用者存在
- **THEN** 回傳完整的 profile 資料

#### Scenario: 更新使用者偏好
- **GIVEN** 呼叫 `update_user_profile(username, updates)`
- **WHEN** 傳入要更新的欄位
- **THEN** 合併更新 profile.json 中的 preferences
- **AND** 保留未更新的欄位

### Requirement: 管理員使用者管理
系統 SHALL 允許管理員檢視與管理所有使用者清單。

#### Scenario: 列出所有使用者
- **WHEN** 管理員查看使用者列表
- **THEN** 列出 `data/users/` 下所有使用者

