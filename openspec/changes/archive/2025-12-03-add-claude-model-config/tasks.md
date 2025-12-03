# Tasks: add-claude-model-config

## Implementation Tasks

1. [x] **建立 AI 設定檔**
   - 檔案：`data/system/ai_config.json`
   - 包含 `chat.model` 和 `menu_recognition.model` 設定
   - 預設都使用 `sonnet`

2. [x] **新增設定讀取函數**
   - 檔案：`app/data.py`
   - 新增 `get_ai_config()` 函數
   - 提供預設值處理

3. [x] **修改 call_claude() 支援模型設定**
   - 檔案：`app/claude.py`
   - 讀取 `chat.model` 設定
   - 在 CLI 命令加入 `--model` 參數
   - Claude CLI 支援直接使用 sonnet/opus/haiku 簡稱

4. [x] **修改 recognize_menu_image() 支援模型設定**
   - 檔案：`app/claude.py`
   - 讀取 `menu_recognition.model` 設定
   - 在 CLI 命令加入 `--model` 參數

5. [x] **驗證修改**
   - 程式碼結構驗證完成
   - 設定檔格式正確
   - 使用 Claude CLI 原生支援的模型簡稱
