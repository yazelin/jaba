# Tasks: refactor-cli-providers

## Implementation Order

### Phase 1: 建立 Provider 基礎架構

- [x] **Task 1.1**: 建立 `app/providers/` 目錄
- [x] **Task 1.2**: 建立 `app/providers/__init__.py`，包含：
  - `CommandResult` dataclass
  - `BaseProvider` 抽象基底類別（定義介面）
  - `get_provider()` 工廠函數
- [x] **Task 1.3**: 驗證目錄結構正確

### Phase 2: 實作 Claude Provider

- [x] **Task 2.1**: 建立 `app/providers/claude.py`
- [x] **Task 2.2**: 實作 `ClaudeProvider` 類別：
  - `build_chat_command()` - 從原 `_build_claude_command()` 移植
  - `build_menu_command()` - 從原 `_build_claude_menu_command()` 移植
  - `parse_response()` - 解析 JSON 回應
  - `get_session_info_after_call()` - 回傳首次對話的 session_id
  - `delete_session()` - Claude 無此需求，回傳 True

### Phase 3: 實作 Gemini Provider

- [x] **Task 3.1**: 建立 `app/providers/gemini.py`
- [x] **Task 3.2**: 實作 `GeminiProvider` 類別：
  - `build_chat_command()` - 從原 `_build_gemini_command()` 移植
  - `build_menu_command()` - 從原 `_build_gemini_menu_command()` 移植
  - `parse_response()` - 解析回應（移除 markdown code block）
  - `get_session_info_after_call()` - 從原 `_get_gemini_latest_session_index()` 移植
  - `delete_session()` - 從原 `_delete_gemini_session()` 移植

### Phase 4: 建立新主模組

- [x] **Task 4.1**: 建立 `app/ai.py`，從 `app/claude.py` 移植共用邏輯：
  - `get_system_prompt()`
  - `build_context()`
  - `execute_actions()` / `execute_action()`
  - 所有 `_create_order`, `_cancel_order` 等動作函數
- [x] **Task 4.2**: 實作新的 `call_ai()` 函數：
  - 使用 `get_provider()` 取得 provider
  - 呼叫 provider 方法建構命令和解析回應
- [x] **Task 4.3**: 實作新的 `recognize_menu_image()` 函數：
  - 使用 provider 建構菜單辨識命令
- [x] **Task 4.4**: 更新 `_reset_session()` 函數：
  - 使用 provider 刪除 session
- [x] **Task 4.5**: 刪除 `app/claude.py`

### Phase 5: 更新所有 Import

- [x] **Task 5.1**: 更新 `main.py` 的 import
  - `from app import claude` → `from app import ai`
- [x] **Task 5.2**: 更新所有 `claude.` 呼叫為 `ai.`

### Phase 6: 驗證與測試

- [x] **Task 6.1**: 驗證 Python 語法正確
- [x] **Task 6.2**: 驗證所有模組可正確 import
- [x] **Task 6.3**: 驗證 provider 工廠函數正常
- [x] **Task 6.4**: 驗證檔案結構符合設計

## Dependencies

```
Phase 1 ──► Phase 2 ──┐
                      ├──► Phase 4 ──► Phase 5 ──► Phase 6
Phase 1 ──► Phase 3 ──┘
```

- Phase 2 和 Phase 3 可並行執行
- Phase 4 需等待 Phase 2 和 Phase 3 完成
- Phase 5 需等待 Phase 4 完成
- Phase 6 需等待 Phase 5 完成

## Verification Criteria

- [x] 所有模組語法正確
- [x] Claude provider 可正確載入
- [x] Gemini provider 可正確載入
- [x] Provider 工廠函數正常運作
- [x] `app/claude.py` 已刪除
- [x] 所有 import 已更新為 `from app import ai`
