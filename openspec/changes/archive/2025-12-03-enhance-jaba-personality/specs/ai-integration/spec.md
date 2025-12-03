# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 呷爸個性設定
系統 SHALL 在 prompts 中定義呷爸為「成熟穩重的大叔」形象，語氣溫和有條理，給人信賴感。

#### Scenario: 呷爸對話風格
- **GIVEN** 使用者或管理員與呷爸對話
- **WHEN** 呷爸回應
- **THEN** 使用成熟穩重的語氣
- **AND** 說話有條理、不過度熱情
- **AND** 給人可靠的大叔形象

### Requirement: 健康飲食提醒與卡路里估算
系統 SHALL 在 `user_prompt` 中加入健康飲食提醒邏輯，當使用者點餐時適時推薦較健康的選項，並估算餐點卡路里。

#### Scenario: 使用者點餐時的健康提醒
- **GIVEN** 使用者正在點餐
- **WHEN** 呷爸協助點餐
- **THEN** 可適時推薦較健康的餐點選項
- **AND** 提醒均衡飲食
- **AND** 以友善建議方式呈現，不強制

#### Scenario: 點餐時估算卡路里
- **GIVEN** 使用者選擇餐點
- **WHEN** 呷爸確認訂單
- **THEN** 估算每道餐點的大約卡路里
- **AND** 在 action.data.items 中包含 calories 欄位
- **AND** 計算並顯示總卡路里估算值
- **AND** 同時顯示總金額和總卡路里

### Requirement: 訂單儲存卡路里資訊
系統 SHALL 在建立訂單時儲存每個品項的估算卡路里，並計算總卡路里。

#### Scenario: 儲存卡路里至訂單
- **GIVEN** AI 回傳 create_order 動作
- **AND** items 中包含 calories 欄位
- **WHEN** 系統執行 `_create_order()`
- **THEN** 儲存每個品項的 calories 值
- **AND** 計算並儲存 total_calories

### Requirement: 前端顯示卡路里
系統 SHALL 在訂單顯示區域呈現各餐點的卡路里和總卡路里。

#### Scenario: 我的訂單顯示卡路里
- **GIVEN** 使用者已有訂單
- **WHEN** 查看「我的訂單」區域
- **THEN** 顯示各餐點的估算卡路里
- **AND** 顯示總卡路里

### Requirement: 管理員店家建議
系統 SHALL 在管理員模式下，當今日尚未設定店家時，根據歷史訂餐記錄提供店家選擇建議。

#### Scenario: 今日未設定店家時提供建議
- **GIVEN** 管理員進入管理模式
- **AND** 今日尚未設定任何店家
- **WHEN** 管理員與呷爸對話
- **THEN** 呷爸可主動或被動提供店家建議
- **AND** 建議基於過去幾天的訂餐記錄（避免連續訂同一家）

#### Scenario: 今日已設定店家時不主動建議
- **GIVEN** 管理員進入管理模式
- **AND** 今日已設定店家
- **WHEN** 管理員與呷爸對話
- **THEN** 呷爸不主動建議更換店家
- **AND** 專注於其他管理任務

### Requirement: 管理員 Context 包含歷史店家資訊
系統 SHALL 在 `build_context()` 中為管理員提供過去 N 天的店家訂餐記錄，供 AI 分析並給出建議。

#### Scenario: 提供歷史店家資訊
- **GIVEN** 呼叫 `build_context(username, is_manager=True)`
- **WHEN** 建立管理員上下文
- **THEN** context 包含 `recent_store_history` 欄位
- **AND** 記錄過去 7 天每日訂購的店家
