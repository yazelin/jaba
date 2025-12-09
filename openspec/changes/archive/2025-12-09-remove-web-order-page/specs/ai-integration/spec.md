# ai-integration Specification Delta

## Purpose
移除 Web Order 頁面相關的 AI 整合規格。

## REMOVED Requirements

### Requirement: 前端名稱暫存
移除：Web Order 頁面已不再使用，LINE 模式透過 LINE User ID 識別使用者。

#### Scenario: 記住使用者名稱（移除）
原因：訂餐頁已移除，使用者身份由 LINE User ID 識別。

#### Scenario: 自動填入名稱（移除）
原因：訂餐頁已移除。

## MODIFIED Requirements

### Requirement: Session 管理
系統 SHALL 在管理員進入對話頁面時重置 session，並在同一次訪問內維持對話延續。LINE Bot 群組模式使用群組 session 而非個人 session。

#### Scenario: 進入訂購頁重置 session（移除）
原因：訂餐頁已移除。

#### Scenario: 重新進入頁面（修改）
- **GIVEN** 管理員重新整理頁面或重新進入
- **WHEN** 再次執行管理頁初始化
- **THEN** 重置 session，開始全新對話
- **AND** 呷爸不會混淆先前訪問的對話內容

### Requirement: 歡迎訊息流程
系統 SHALL 使用靜態歡迎訊息讓管理員立即看到回應，歡迎詞風格活潑親切。LINE 使用者歡迎訊息由 LINE Bot 處理。

#### Scenario: 一般使用者靜態歡迎訊息（移除）
原因：訂餐頁已移除，LINE 使用者歡迎訊息由 LINE Bot 回覆處理。

#### Scenario: 使用者主動詢問建議（修改）
- **GIVEN** LINE 群組使用者已加入點餐
- **WHEN** 使用者詢問「今天吃什麼好」或類似問題
- **THEN** AI 根據 prompt 中的建議邏輯回應
- **AND** 參考使用者 profile 中的偏好進行個人化推薦
