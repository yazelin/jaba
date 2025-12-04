# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 精簡 AI Context

系統 SHALL 在建立 AI 上下文時只包含必要資訊，減少 token 使用量以加快回應速度。

#### Scenario: 精簡菜單資訊
- **GIVEN** 建立 AI 上下文
- **WHEN** 包含今日菜單
- **THEN** 只保留品項的 `id`、`name`、`price`、`variants`
- **AND** 移除 `description`、`available`、`store_id`、`updated_at`

#### Scenario: 使用者模式精簡
- **GIVEN** 呼叫 `build_context(username, is_manager=False)`
- **WHEN** 建立使用者上下文
- **THEN** 不包含 `available_stores`（訂購頁已有 today_menus）
- **AND** `today_store` 只包含店家名稱列表

#### Scenario: 管理員模式精簡
- **GIVEN** 呼叫 `build_context(username, is_manager=True)`
- **WHEN** 建立管理員上下文
- **THEN** 保留 `available_stores`（管理員需要設定店家）
- **AND** `today_summary` 只包含統計數據，不含完整訂單明細
