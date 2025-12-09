# data-storage Spec Delta

## REMOVED Requirements

### Requirement: 訂單檔案格式
移除：個人訂單檔案 `users/{username}/orders/{date}-{timestamp}.json` 不再使用。

## MODIFIED Requirements

### Requirement: 資料目錄結構
系統 SHALL 使用 `data/` 目錄作為所有資料的根目錄。

#### Scenario: 首次啟動建立目錄
- **WHEN** 系統首次啟動且 `data/` 不存在
- **THEN** 自動建立目錄結構：`system/`、`stores/`、`users/`、`linebot/`
- **AND** 不再建立 `orders/` 目錄（已棄用）
- **AND** 使用者目錄不再自動建立 `orders/` 和 `sessions/` 子目錄

#### Scenario: 使用者資料目錄
- **WHEN** 建立新使用者
- **THEN** 只建立 `users/{line_user_id}/` 目錄
- **AND** 建立 `profile.json`
- **AND** 按需建立 `chat_history/` 目錄（有對話時）
