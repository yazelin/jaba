# ai-integration Specification

## Purpose
TBD - created by archiving change add-data-architecture. Update Purpose after archive.
## Requirements
### Requirement: Claude CLI 整合
系統 SHALL 透過 subprocess 執行 Claude CLI 與 AI Agent 互動，不使用 API。

#### Scenario: 呼叫 AI Agent
- **WHEN** 使用者發送訊息
- **THEN** 後端執行 `claude -p` 命令並解析 JSON 回應

### Requirement: Session 管理
系統 SHALL 為每個使用者每天維護獨立的 Claude session，儲存於 `users/{username}/sessions/{date}.txt`。

#### Scenario: 新使用者首次對話
- **WHEN** 使用者今日首次發送訊息
- **THEN** 建立新 session 並儲存 session ID

#### Scenario: 繼續對話
- **WHEN** 使用者今日已有 session
- **THEN** 使用 `claude -r [sessionId]` 繼續對話

#### Scenario: 隔天新 session
- **WHEN** 使用者隔天使用系統
- **THEN** 建立新的 session，不延續昨日對話

### Requirement: 前端名稱暫存
系統 SHALL 在前端使用 localStorage 儲存使用者名稱，下次自動填入。

#### Scenario: 記住使用者名稱
- **WHEN** 使用者輸入名稱並開始對話
- **THEN** 將名稱存入 localStorage

#### Scenario: 自動填入名稱
- **WHEN** 使用者再次開啟頁面
- **THEN** 自動填入上次使用的名稱

### Requirement: AI 動作執行
系統 SHALL 根據 AI 回應的 action 執行對應操作並廣播事件。

#### Scenario: 執行建立訂單
- **WHEN** AI 回應 action.type 為 create_order
- **THEN** 建立訂單、更新彙整、廣播 order_created

### Requirement: 對話上下文延續
系統 SHALL 維護使用者的對話上下文，讓 AI 能記住之前的對話內容。

#### Scenario: 首次對話建立 session
- **GIVEN** 使用者今日首次與 AI 對話
- **WHEN** 呼叫 `call_claude()`
- **THEN** 系統生成新的 UUID 作為 session ID
- **AND** 使用 `--session-id <uuid>` 參數建立對話
- **AND** 儲存 session ID 到 `users/{username}/sessions/{date}.txt`

#### Scenario: 後續對話恢復上下文
- **GIVEN** 使用者今日已有 session ID
- **WHEN** 呼叫 `call_claude()`
- **THEN** 使用 `--resume <sessionId>` 參數恢復對話
- **AND** AI 能理解之前對話的上下文

#### Scenario: 確認型回應
- **GIVEN** AI 詢問「要我幫你設定嗎？」
- **WHEN** 使用者回應「好」
- **THEN** AI 理解這是對之前提議的確認
- **AND** 執行之前提議的動作

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

### Requirement: AI 模型設定
系統 SHALL 支援透過設定檔指定不同任務使用的 Claude 模型。

#### Scenario: 讀取 AI 設定
- **GIVEN** 系統啟動或呼叫 AI 功能
- **WHEN** 讀取 `data/system/ai_config.json`
- **THEN** 取得各任務對應的模型設定
- **AND** 若設定檔不存在則使用預設值（sonnet）

#### Scenario: Chat 對話指定模型
- **GIVEN** 使用者發送訊息
- **WHEN** 呼叫 `call_claude()`
- **THEN** 讀取 `chat.model` 設定
- **AND** 使用 `--model` 參數指定模型（如 sonnet、haiku、opus）

#### Scenario: 菜單辨識指定模型
- **GIVEN** 管理員上傳菜單圖片
- **WHEN** 呼叫 `recognize_menu_image()`
- **THEN** 讀取 `menu_recognition.model` 設定
- **AND** 使用 `--model` 參數指定模型

### Requirement: 支援的模型簡稱
系統 SHALL 支援 Claude CLI 的模型簡稱。

#### Scenario: 使用模型簡稱
- **GIVEN** 設定檔中指定模型簡稱
- **WHEN** 建立 CLI 命令
- **THEN** 直接使用簡稱作為 `--model` 參數值
- **AND** 支援 `haiku`、`sonnet`、`opus` 等簡稱

