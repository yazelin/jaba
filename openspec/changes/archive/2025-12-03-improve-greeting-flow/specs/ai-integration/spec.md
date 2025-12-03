# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 歡迎訊息流程
系統 SHALL 使用靜態歡迎訊息讓使用者立即看到回應，建議功能改為使用者主動詢問。

#### Scenario: 管理員靜態歡迎訊息
- **GIVEN** 管理員成功登入
- **WHEN** 進入管理模式
- **THEN** 立即顯示靜態歡迎訊息
- **AND** 訊息包含操作教學（設定店家、查看訂單等）
- **AND** 訊息包含提示「需要店家建議可以問我」

#### Scenario: 一般使用者靜態歡迎訊息
- **GIVEN** 使用者輸入名字開始訂餐
- **WHEN** 進入訂餐模式
- **THEN** 立即顯示靜態歡迎訊息
- **AND** 訊息包含今日店家資訊
- **AND** 訊息包含提示「不知道吃什麼？可以問我建議」

#### Scenario: 使用者主動詢問建議
- **GIVEN** 使用者已進入系統
- **WHEN** 使用者詢問「今天吃什麼好」或類似問題
- **THEN** AI 根據 prompt 中的建議邏輯回應
- **AND** 管理員會收到店家建議（根據 recent_store_history）
- **AND** 一般使用者會收到餐點建議或健康提醒
