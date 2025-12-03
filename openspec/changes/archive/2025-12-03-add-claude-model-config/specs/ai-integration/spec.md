# ai-integration Spec Delta

## ADDED Requirements

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
