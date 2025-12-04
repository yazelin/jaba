# ai-integration Spec Delta

## REMOVED Requirements

### Requirement: 精簡 AI Context

> 此要求已移除。系統改為提供完整的 AI 上下文資訊。

**移除原因**：
1. 管理員需要完整訂單明細來進行管理，僅有統計數據不足
2. 使用者需要菜單描述資訊，呷爸才能根據菜品特色提供個人化建議
3. Context 大小實際影響有限，過度精簡會犧牲 AI 服務品質

---

## ADDED Requirements

### Requirement: 完整 AI Context

系統 SHALL 在建立 AI 上下文時提供完整資訊，讓呷爸能提供高品質的個人化服務。

#### Scenario: 完整菜單資訊
- **GIVEN** 建立 AI 上下文
- **WHEN** 包含今日菜單
- **THEN** 保留品項的完整欄位（`id`、`name`、`price`、`description`、`variants` 等）
- **AND** 讓呷爸能根據菜品描述提供建議

#### Scenario: 使用者模式完整資訊
- **GIVEN** 呼叫 `build_context(username, is_manager=False)`
- **WHEN** 建立使用者上下文
- **THEN** 包含今日店家的完整菜單資訊
- **AND** 包含使用者偏好和現有訂單

#### Scenario: 管理員模式完整資訊
- **GIVEN** 呼叫 `build_context(username, is_manager=True)`
- **WHEN** 建立管理員上下文
- **THEN** 包含 `available_stores` 完整店家列表
- **AND** `today_summary` 包含完整訂單明細（各使用者的品項、數量、備註等）
- **AND** 包含付款狀態和歷史店家記錄
