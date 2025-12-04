# ai-integration Spec Delta

## ADDED Requirements

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
