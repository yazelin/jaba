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
系統 SHALL 在使用者每次進入對話頁面時重置 session，並在同一次訪問內維持對話延續。

#### Scenario: 進入訂購頁重置 session
- **GIVEN** 使用者輸入名字點擊「開始訂餐」
- **WHEN** 前端執行 `startChat()`
- **THEN** 先呼叫 `/api/session/reset` 清除舊 session
- **AND** 後續對話會建立新的 session

#### Scenario: 進入管理頁重置 session
- **GIVEN** 管理員進入管理頁面
- **WHEN** 頁面初始化
- **THEN** 呼叫 `/api/session/reset`（is_manager=true）清除舊 session
- **AND** 後續對話會建立新的 session

#### Scenario: 同一次訪問內延續對話
- **GIVEN** 使用者已開始對話且尚未離開頁面
- **WHEN** 使用者繼續發送訊息
- **THEN** 使用 `--resume` 延續同一個 session
- **AND** AI 能理解對話上下文（如確認型回應「好」、「對」）

#### Scenario: 重新進入頁面
- **GIVEN** 使用者重新整理頁面或重新進入
- **WHEN** 再次執行 `startChat()` 或管理頁初始化
- **THEN** 重置 session，開始全新對話
- **AND** 呷爸不會混淆先前訪問的對話內容

### Requirement: 前端名稱暫存
系統 SHALL 在前端使用 localStorage 儲存使用者名稱，下次自動填入。

#### Scenario: 記住使用者名稱
- **WHEN** 使用者輸入名稱並開始對話
- **THEN** 將名稱存入 localStorage

#### Scenario: 自動填入名稱
- **WHEN** 使用者再次開啟頁面
- **THEN** 自動填入上次使用的名稱

### Requirement: AI 動作執行
系統 SHALL 統一使用 `actions` 陣列格式處理 AI 回應的動作。

#### Scenario: AI 回應動作
- **GIVEN** AI 回應訊息
- **WHEN** 回應包含需要執行的動作
- **THEN** 使用 `actions` 陣列格式
- **AND** 不使用單一 `action` 欄位

#### Scenario: 執行動作
- **GIVEN** 收到 AI 回應
- **WHEN** 處理動作
- **THEN** 只從 `actions` 陣列讀取動作
- **AND** 不檢查 `action` 單一欄位

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

### Requirement: 呷爸個性設定
系統 SHALL 在 prompts 中定義呷爸為「親切可愛」的形象，語氣活潑自然，讓人感到溫暖有人情味，並使用「我們」營造一起決定的參與感。

#### Scenario: 呷爸對話風格
- **GIVEN** 使用者或管理員與呷爸對話
- **WHEN** 呷爸回應
- **THEN** 使用親切可愛的語氣
- **AND** 說話簡潔自然、不冗長
- **AND** 可以適時使用口語化表達（如「哇係呷爸」）
- **AND** 盡量使用「我們」代替「你」，營造一起決定的感覺

#### Scenario: 稱呼使用者
- **GIVEN** 呷爸需要稱呼使用者
- **WHEN** 使用者沒有設定稱呼偏好
- **THEN** 盡量使用「我們」而非「你」
- **AND** 不使用性別代稱（如先生、小姐）

#### Scenario: 使用個人化稱呼
- **GIVEN** 呷爸需要稱呼使用者
- **WHEN** 使用者在 profile 中設定了稱呼偏好
- **THEN** 使用使用者偏好的稱呼

#### Scenario: 提供建議時的語氣
- **GIVEN** 呷爸要根據歷史記錄提供建議
- **WHEN** 回應使用者
- **THEN** 不說「根據最近的訂餐記錄」等機械化用語
- **AND** 直接說「昨天訂過 xxx，今天要不要試 ooo」
- **AND** 只有當使用者主動詢問歷史時才詳細說明

#### Scenario: 管理員對話風格
- **GIVEN** 管理員與呷爸對話
- **WHEN** 討論今日店家
- **THEN** 使用「我們今天要訂哪家店呢？」等參與感用語

#### Scenario: 訂購者對話風格
- **GIVEN** 訂購者與呷爸對話
- **WHEN** 討論要吃什麼
- **THEN** 使用「我們今天想吃什麼呢？」等參與感用語

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
系統 SHALL 支援透過設定檔指定不同任務使用的 CLI provider 和模型。

#### Scenario: 讀取 AI 設定
- **GIVEN** 系統啟動或呼叫 AI 功能
- **WHEN** 讀取 `data/system/ai_config.json`
- **THEN** 取得各任務對應的 provider 和模型設定
- **AND** 若 provider 未指定則預設為 `claude`
- **AND** 若 model 未指定則使用各 provider 的預設模型

#### Scenario: 設定檔格式
- **GIVEN** `ai_config.json` 內容
- **WHEN** 解析設定
- **THEN** 支援以下格式：
```json
{
  "chat": {
    "provider": "claude",
    "model": "haiku"
  },
  "menu_recognition": {
    "provider": "gemini",
    "model": "gemini-2.5-pro"
  }
}
```

### Requirement: 支援的模型簡稱
系統 SHALL 支援 Claude CLI 的模型簡稱。

#### Scenario: 使用模型簡稱
- **GIVEN** 設定檔中指定模型簡稱
- **WHEN** 建立 CLI 命令
- **THEN** 直接使用簡稱作為 `--model` 參數值
- **AND** 支援 `haiku`、`sonnet`、`opus` 等簡稱

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

### Requirement: 菜單辨識尺寸變體
系統 SHALL 在辨識菜單圖片時，自動提取品項的尺寸變體資訊。

#### Scenario: 辨識多尺寸品項
- **GIVEN** 菜單圖片顯示 M/L、大/中/小、大碗/小碗等尺寸價格
- **WHEN** AI 辨識菜單
- **THEN** 輸出 `variants` 陣列包含各尺寸名稱和價格
- **AND** `price` 欄位填入最小尺寸的價格

#### Scenario: 無尺寸區分
- **GIVEN** 菜單品項只有單一價格
- **WHEN** AI 辨識菜單
- **THEN** 不產生 `variants` 欄位
- **AND** `price` 欄位填入該價格

### Requirement: AI 對話編輯尺寸變體
系統 SHALL 支援管理員透過對話讓 AI 編輯品項的尺寸價格。

#### Scenario: 修改尺寸價格
- **GIVEN** 管理員說「把珍珠奶茶的 L 杯改成 65 元」
- **WHEN** AI 執行 `update_item_variants` 動作
- **THEN** 更新該品項的 L 尺寸價格為 65

#### Scenario: 新增尺寸
- **GIVEN** 管理員說「幫雞腿便當加一個大份選項，100元」
- **WHEN** AI 執行 `update_item_variants` 動作
- **THEN** 在該品項的 variants 中新增大份尺寸

### Requirement: AI 訂單操作指引
系統 SHALL 在 prompt 中指示呷爸根據使用者意圖選擇正確的訂單動作。

#### Scenario: 呷爸查看現有訂單
- **GIVEN** 使用者要求修改訂單
- **WHEN** 呷爸處理請求
- **THEN** 先查看 context 中的 `current_orders`
- **AND** 了解使用者目前有哪些訂單和品項

#### Scenario: 呷爸移除品項
- **GIVEN** 使用者說「不要 X」或「取消 X」
- **AND** `current_orders` 中有品項 X
- **WHEN** 呷爸執行動作
- **THEN** 使用 `remove_item` 動作
- **AND** 不使用 `create_order`

#### Scenario: 呷爸新增品項
- **GIVEN** 使用者說「加一個 X」或「我要 X」
- **AND** `current_orders` 中沒有品項 X（或使用者明確要新增）
- **WHEN** 呷爸執行動作
- **THEN** 使用 `create_order` 動作

### Requirement: remove_item 動作格式
系統 SHALL 支援 `remove_item` 動作讓 AI 從現有訂單移除品項。

#### Scenario: AI 執行 remove_item
- **GIVEN** AI 回應包含 `action.type` 為 `remove_item`
- **AND** `action.data` 包含 `item_name` 和可選的 `quantity`
- **WHEN** 系統執行該動作
- **THEN** 從使用者訂單中移除指定品項
- **AND** 回傳更新後的訂單狀態

### Requirement: 多 CLI Provider 支援
系統 SHALL 支援在設定檔中為每個 AI 功能指定使用的 CLI 工具（provider）。

#### Scenario: 設定 provider
- **GIVEN** `ai_config.json` 中某功能設定 `provider` 欄位
- **WHEN** 呼叫該 AI 功能
- **THEN** 使用對應的 CLI 工具（claude 或 gemini）
- **AND** 若未指定 provider，預設使用 `claude`

#### Scenario: 不同功能使用不同 provider
- **GIVEN** chat 設定 `provider: "claude"`
- **AND** menu_recognition 設定 `provider: "gemini"`
- **WHEN** 使用者發送對話訊息
- **THEN** 執行 `claude` CLI
- **AND** 當管理員上傳菜單圖片時執行 `gemini` CLI

### Requirement: Claude CLI 命令建構
系統 SHALL 為 Claude CLI 建構正確的命令參數。

#### Scenario: Claude 對話命令
- **GIVEN** provider 為 `claude`
- **WHEN** 建構對話命令
- **THEN** 使用 `-p` 參數傳遞 prompt
- **AND** 使用 `--system-prompt` 傳遞系統提示
- **AND** 使用 `--model` 指定模型
- **AND** 首次對話使用 `--session-id`，後續使用 `--resume`

### Requirement: Gemini CLI 命令建構
系統 SHALL 為 Gemini CLI 建構正確的命令參數。

#### Scenario: Gemini 對話命令
- **GIVEN** provider 為 `gemini`
- **WHEN** 建構對話命令
- **THEN** 使用位置參數傳遞 prompt
- **AND** 將系統提示併入 prompt 開頭
- **AND** 使用 `-m` 或 `--model` 指定模型
- **AND** 使用 `-o json` 指定 JSON 輸出格式

### Requirement: Gemini Session 索引追蹤
系統 SHALL 為 Gemini CLI 維護每個使用者的 session 索引對照。

#### Scenario: Gemini 首次對話
- **GIVEN** provider 為 `gemini`
- **AND** 使用者今日無 session 記錄
- **WHEN** 建構對話命令
- **THEN** 不加 `--resume` 參數
- **AND** 執行後追蹤新建的 session 索引

#### Scenario: Gemini 後續對話
- **GIVEN** provider 為 `gemini`
- **AND** 使用者今日有 session 索引記錄
- **WHEN** 建構對話命令
- **THEN** 使用 `--resume <index>` 接續對話

### Requirement: Gemini 自動確認模式
系統 SHALL 在使用 Gemini CLI 執行需要工具的任務時啟用自動確認。

#### Scenario: 菜單辨識自動確認
- **GIVEN** provider 為 `gemini`
- **AND** 執行菜單辨識
- **WHEN** 建構命令
- **THEN** 使用 `-y` 或 `--yolo` 參數自動確認

### Requirement: 統一 Session 儲存格式
系統 SHALL 使用 JSON 格式儲存 session 資訊，支援不同 provider 的 session 追蹤需求。

#### Scenario: Session 檔案格式
- **GIVEN** 使用者開始對話
- **WHEN** 儲存 session 資訊
- **THEN** 寫入 `users/{username}/sessions/{date}.json`
- **AND** 包含 `provider`、`session_id`（Claude）、`session_index`（Gemini）等欄位

#### Scenario: 讀取 Session
- **GIVEN** 使用者繼續對話
- **WHEN** 讀取 session 資訊
- **THEN** 根據 provider 類型取得對應的 session 識別資訊

