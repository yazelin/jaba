## ADDED Requirements

### Requirement: 使用者識別
系統 SHALL 使用名字作為使用者唯一識別，輸入名字即可存取對應資料。

#### Scenario: 新使用者首次使用
- **WHEN** 使用者輸入不存在的名字
- **THEN** 自動建立 `data/users/{username}/` 與 profile.json

#### Scenario: 既有使用者登入
- **WHEN** 使用者輸入已存在的名字
- **THEN** 載入該使用者的資料

### Requirement: 使用者資料儲存
系統 SHALL 在 `data/users/{username}/` 儲存 profile.json 與 orders/ 目錄。

#### Scenario: 儲存使用者偏好
- **WHEN** 使用者設定偏好（如不吃辣）
- **THEN** 更新 profile.json 的 preferences 欄位

### Requirement: 管理員使用者管理
系統 SHALL 允許管理員檢視與管理所有使用者清單。

#### Scenario: 列出所有使用者
- **WHEN** 管理員查看使用者列表
- **THEN** 列出 `data/users/` 下所有使用者
