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
系統 SHALL 在管理員進入對話頁面時重置 session，並在同一次訪問內維持對話延續。LINE Bot 群組模式使用群組 session 而非個人 session。

#### Scenario: 進入訂購頁重置 session（移除）
原因：訂餐頁已移除。

#### Scenario: 重新進入頁面（修改）
- **GIVEN** 管理員重新整理頁面或重新進入
- **WHEN** 再次執行管理頁初始化
- **THEN** 重置 session，開始全新對話
- **AND** 呷爸不會混淆先前訪問的對話內容

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
系統 SHALL 使用靜態歡迎訊息讓管理員立即看到回應，歡迎詞風格活潑親切。LINE 使用者歡迎訊息由 LINE Bot 處理。

#### Scenario: 一般使用者靜態歡迎訊息（移除）
原因：訂餐頁已移除，LINE 使用者歡迎訊息由 LINE Bot 回覆處理。

#### Scenario: 使用者主動詢問建議（修改）
- **GIVEN** LINE 群組使用者已加入點餐
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

### Requirement: CLI Provider 模組化架構

系統 SHALL 將 AI CLI 整合程式碼組織為模組化的 provider 架構。

#### Scenario: Provider 目錄結構
- **GIVEN** AI CLI 整合模組
- **WHEN** 組織程式碼結構
- **THEN** 建立 `app/providers/` 目錄
- **AND** 包含 `__init__.py`（基底類別與工廠）
- **AND** 包含 `claude.py`（Claude CLI 實作）
- **AND** 包含 `gemini.py`（Gemini CLI 實作）

#### Scenario: 主入口模組命名
- **GIVEN** AI 整合主模組
- **WHEN** 命名模組檔案
- **THEN** 使用 `app/ai.py` 作為主入口
- **AND** 包含 `call_ai()`、`build_context()`、`execute_actions()` 等公用函數

### Requirement: Provider 抽象介面

系統 SHALL 定義統一的 Provider 抽象介面，讓不同 CLI 工具實作共同的方法。

#### Scenario: BaseProvider 介面
- **GIVEN** 新增 CLI provider 需求
- **WHEN** 實作 provider 類別
- **THEN** 需繼承 `BaseProvider` 抽象類別
- **AND** 實作 `build_chat_command()` 方法
- **AND** 實作 `build_menu_command()` 方法
- **AND** 實作 `parse_response()` 方法
- **AND** 實作 `get_session_info_after_call()` 方法
- **AND** 實作 `delete_session()` 方法

#### Scenario: Provider 工廠
- **GIVEN** 需要取得 provider 實例
- **WHEN** 呼叫 `get_provider(provider_name)`
- **THEN** 根據名稱回傳對應的 provider 實例
- **AND** 若名稱無效則回傳預設的 ClaudeProvider

### Requirement: Claude Provider 實作

系統 SHALL 將 Claude CLI 特定邏輯封裝在 ClaudeProvider 類別中。

#### Scenario: Claude 對話命令建構
- **GIVEN** provider 為 `claude`
- **WHEN** 呼叫 `ClaudeProvider.build_chat_command()`
- **THEN** 回傳包含正確 Claude CLI 參數的命令
- **AND** 使用 `-p` 傳遞 prompt
- **AND** 使用 `--system-prompt` 傳遞系統提示
- **AND** 使用 `--model` 指定模型

#### Scenario: Claude 菜單辨識命令建構
- **GIVEN** provider 為 `claude`
- **WHEN** 呼叫 `ClaudeProvider.build_menu_command()`
- **THEN** 回傳包含 Read 工具權限的命令
- **AND** 在 prompt 中指示使用 Read 工具讀取圖片

### Requirement: Gemini Provider 實作

系統 SHALL 將 Gemini CLI 特定邏輯封裝在 GeminiProvider 類別中。

#### Scenario: Gemini 對話命令建構
- **GIVEN** provider 為 `gemini`
- **WHEN** 呼叫 `GeminiProvider.build_chat_command()`
- **THEN** 回傳包含正確 Gemini CLI 參數的命令
- **AND** 將系統提示併入 prompt 開頭
- **AND** 使用 `-m` 指定模型

#### Scenario: Gemini 菜單辨識命令建構
- **GIVEN** provider 為 `gemini`
- **WHEN** 呼叫 `GeminiProvider.build_menu_command()`
- **THEN** 使用 `@檔名` 語法引用圖片
- **AND** 使用 `-y` 參數啟用 YOLO 模式

#### Scenario: Gemini Session 追蹤
- **GIVEN** provider 為 `gemini`
- **AND** 執行完首次對話
- **WHEN** 呼叫 `GeminiProvider.get_session_info_after_call()`
- **THEN** 透過 `--list-sessions` 取得最新 session 索引
- **AND** 回傳包含索引的 SessionInfo

### Requirement: Gemini CLI 命令建構優化
系統 SHALL 為 Gemini CLI 建構正確的命令參數，使用指定模型並支援 session 恢復。

#### Scenario: Gemini 對話命令
- **GIVEN** provider 為 `gemini`
- **WHEN** 建構對話命令
- **THEN** 使用 `-m` 指定模型（由 ai_config 載入，預設 `gemini-2.5-flash-lite`）
- **AND** 使用位置參數傳遞 prompt
- **AND** 將系統提示併入 prompt 開頭
- **AND** 若有現有 session UUID，使用 `--resume <uuid>` 恢復對話

### Requirement: Gemini 回應解析
系統 SHALL 正確解析 Gemini CLI 的回應，並在格式解析失敗時顯示 AI 的實際回應。

#### Scenario: 解析 AI 回應
- **GIVEN** Gemini CLI 回傳 stdout
- **WHEN** 解析回應
- **THEN** 清理可能的 markdown code block 包裝
- **AND** 嘗試從回應中提取我們的 JSON 格式

#### Scenario: AI 回應非 JSON 格式
- **GIVEN** AI 回應文字不是有效的 JSON
- **WHEN** 解析回應
- **THEN** 直接將 AI 回應文字作為 `message` 回傳
- **AND** `actions` 為空陣列
- **AND** 不視為錯誤（AI 可能只是聊天回應）

#### Scenario: 解析失敗時提供診斷資訊
- **GIVEN** 回應無法解析
- **WHEN** 發生 JSON 解析錯誤
- **THEN** 回傳 `error: "parse_error"`
- **AND** 回傳 `raw_response` 包含原始輸出（截取前 500 字元）
- **AND** `message` 欄位包含 AI 的實際回應（截取前 300 字元）

### Requirement: Gemini Session 自管理
系統 SHALL 透過讀取 Gemini CLI 的 session 檔案來管理 session，取代 `--list-sessions` 呼叫。

#### Scenario: 首次對話建立 Session
- **GIVEN** 使用者沒有現有的 Gemini session UUID
- **WHEN** 執行 Gemini 對話
- **THEN** 不帶 `--resume` 參數執行
- **AND** 對話完成後從 `~/.gemini/tmp/*/chats/` 目錄找新建的 session 檔案
- **AND** 讀取檔案內的 `sessionId` 欄位取得完整 UUID
- **AND** 儲存 UUID 到我們的 session 管理

#### Scenario: 恢復現有 Session
- **GIVEN** 使用者有儲存的 Gemini session UUID
- **WHEN** 執行 Gemini 對話
- **THEN** 使用 `--resume <uuid>` 參數恢復 session
- **AND** Gemini 會記得之前的對話內容

### Requirement: 前端顯示 AI 實際回應
系統 SHALL 在前端顯示 AI 的實際回應，即使格式不符預期也能讓使用者看到內容。

#### Scenario: 顯示超時錯誤
- **GIVEN** AI 回應包含 `error: "timeout"`
- **WHEN** 前端處理回應
- **THEN** 顯示「回應超時，請再試一次」

#### Scenario: 顯示格式解析失敗的回應
- **GIVEN** AI 回應包含 `error: "parse_error"`
- **WHEN** 前端處理回應
- **THEN** 顯示 `message` 欄位的內容（AI 的實際回應）
- **AND** 不顯示技術性錯誤訊息給一般使用者

#### Scenario: 正常顯示 AI 回應
- **GIVEN** AI 回應無 `error` 欄位
- **WHEN** 前端處理回應
- **THEN** 顯示 `message` 欄位的內容

### Requirement: 非同步 AI CLI 執行

系統 SHALL 使用非同步方式執行 AI CLI 命令，避免阻塞其他請求。

#### Scenario: 非同步執行 AI 對話
- **GIVEN** 使用者發送對話訊息
- **WHEN** 後端呼叫 AI CLI
- **THEN** 使用 `asyncio.create_subprocess_exec()` 非同步執行
- **AND** 其他使用者的請求不受影響

#### Scenario: 非同步執行菜單辨識
- **GIVEN** 管理員上傳菜單圖片
- **WHEN** 後端呼叫 AI 辨識
- **THEN** 使用 `asyncio.create_subprocess_exec()` 非同步執行
- **AND** 其他使用者可正常載入頁面和聊天

#### Scenario: 處理超時
- **GIVEN** AI CLI 執行中
- **WHEN** 超過設定的 timeout 時間
- **THEN** 使用 `asyncio.wait_for()` 取消任務
- **AND** 回傳超時錯誤訊息

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

