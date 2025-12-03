## MODIFIED Requirements

### Requirement: 呷爸個性設定
系統 SHALL 在 prompts 中定義呷爸為「親切可愛」的形象，語氣活潑自然，讓人感到溫暖有人情味。

#### Scenario: 呷爸對話風格
- **GIVEN** 使用者或管理員與呷爸對話
- **WHEN** 呷爸回應
- **THEN** 使用親切可愛的語氣
- **AND** 說話簡潔自然、不冗長
- **AND** 可以適時使用口語化表達（如「哇係呷爸」）

#### Scenario: 稱呼使用者
- **GIVEN** 呷爸需要稱呼使用者
- **WHEN** 使用者沒有設定稱呼偏好
- **THEN** 直接稱呼使用者名字或「你」
- **AND** 不使用性別代稱（如先生、小姐）

#### Scenario: 使用個人化稱呼
- **GIVEN** 呷爸需要稱呼使用者
- **WHEN** 使用者在 profile 中設定了稱呼偏好
- **THEN** 使用使用者偏好的稱呼

### Requirement: 歡迎訊息流程
系統 SHALL 使用靜態歡迎訊息讓使用者立即看到回應，歡迎詞風格活潑親切。

#### Scenario: 管理員靜態歡迎訊息
- **GIVEN** 管理員成功登入
- **WHEN** 進入管理模式
- **THEN** 立即顯示靜態歡迎訊息
- **AND** 訊息包含操作教學（設定店家、查看訂單等）
- **AND** 訊息包含提示「需要店家建議可以問我」

#### Scenario: 一般使用者靜態歡迎訊息
- **GIVEN** 使用者輸入名字開始訂餐
- **WHEN** 進入訂餐模式
- **THEN** 立即顯示靜態歡迎訊息：「嗨！哇係呷爸，今天想吃什麼呢？」
- **AND** 訊息包含今日店家資訊
- **AND** 訊息包含提示「不知道吃什麼？可以問我建議」

#### Scenario: 使用者主動詢問建議
- **GIVEN** 使用者已進入系統
- **WHEN** 使用者詢問「今天吃什麼好」或類似問題
- **THEN** AI 根據 prompt 中的建議邏輯回應
- **AND** 參考使用者 profile 中的偏好進行個人化推薦

## ADDED Requirements

### Requirement: 使用者偏好記憶
系統 SHALL 支援呷爸在對話中記錄使用者偏好，並在後續對話中參考這些偏好。

#### Scenario: 記錄飲食偏好
- **GIVEN** 使用者告知呷爸飲食限制（如「我不吃辣」）
- **WHEN** 呷爸理解並回應
- **THEN** 執行 `update_user_profile` 動作記錄偏好
- **AND** 下次點餐時可根據偏好推薦

#### Scenario: 記錄稱呼偏好
- **GIVEN** 使用者告知希望被稱呼的方式
- **WHEN** 呷爸理解並回應
- **THEN** 執行 `update_user_profile` 動作記錄稱呼
- **AND** 後續對話使用該稱呼

#### Scenario: 主動詢問偏好
- **GIVEN** 使用者首次與呷爸互動
- **AND** profile 中偏好資料為空
- **WHEN** 呷爸適時詢問（如「你有什麼不吃的嗎？我記下來方便推薦」）
- **AND** 使用者回答
- **THEN** 記錄使用者的回答到 profile

### Requirement: 更新使用者 Profile 動作
系統 SHALL 提供 `update_user_profile` 動作讓 AI 可以更新使用者的偏好設定。

#### Scenario: AI 執行 profile 更新
- **GIVEN** AI 回應包含 `action.type` 為 `update_user_profile`
- **WHEN** 系統執行該動作
- **THEN** 更新 `users/{username}/profile.json` 中的對應欄位
- **AND** 回傳更新成功訊息

#### Scenario: 更新飲食限制
- **GIVEN** AI 回應 `update_user_profile` 動作
- **AND** `action.data` 包含 `dietary_restrictions` 欄位
- **WHEN** 系統執行動作
- **THEN** 更新 profile 的 `preferences.dietary_restrictions` 陣列

#### Scenario: 更新稱呼偏好
- **GIVEN** AI 回應 `update_user_profile` 動作
- **AND** `action.data` 包含 `preferred_name` 欄位
- **WHEN** 系統執行動作
- **THEN** 更新 profile 的 `preferences.preferred_name` 欄位

### Requirement: AI 上下文包含使用者偏好
系統 SHALL 在 `build_context()` 中包含使用者的 profile 偏好資訊，讓 AI 能參考進行個人化回應。

#### Scenario: Context 包含偏好
- **GIVEN** 呼叫 `build_context(username)`
- **WHEN** 該使用者有設定偏好
- **THEN** context 包含 `user_profile` 欄位
- **AND** 包含 `preferred_name`、`dietary_restrictions` 等資訊
