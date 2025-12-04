# Design: refactor-cli-providers

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                      app/ai.py                          │
│  (主入口：call_ai, build_context, execute_actions)       │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│               app/providers/__init__.py                 │
│  (get_provider, BaseProvider 抽象類別)                   │
└──────────┬────────────────────────────┬─────────────────┘
           │                            │
           ▼                            ▼
┌─────────────────────┐    ┌──────────────────────────────┐
│ providers/claude.py │    │     providers/gemini.py      │
│   ClaudeProvider    │    │       GeminiProvider         │
└─────────────────────┘    └──────────────────────────────┘
```

## Component Design

### 1. BaseProvider (Abstract Base Class)

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CommandResult:
    cmd: list[str]
    cwd: str
    new_session_id: str | int | None = None

class BaseProvider(ABC):
    """CLI Provider 抽象基底類別"""

    @abstractmethod
    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_info: SessionInfo | None
    ) -> CommandResult:
        """建構對話命令"""
        pass

    @abstractmethod
    def build_menu_command(
        self,
        model: str,
        prompt: str,
        image_path: str
    ) -> CommandResult:
        """建構菜單辨識命令"""
        pass

    @abstractmethod
    def parse_response(self, stdout: str, stderr: str) -> dict:
        """解析 CLI 回應"""
        pass

    @abstractmethod
    def get_session_info_after_call(
        self,
        is_new_session: bool,
        return_code: int
    ) -> SessionInfo | None:
        """呼叫後取得 session 資訊（如 Gemini 需事後追蹤）"""
        pass

    @abstractmethod
    def delete_session(self, session_info: SessionInfo) -> bool:
        """刪除 session"""
        pass
```

### 2. ClaudeProvider

實作 Claude CLI 特定邏輯：
- 使用 `-p` 參數傳遞 prompt
- 使用 `--system-prompt` 傳遞系統提示
- Session 使用 UUID，透過 `--session-id` 和 `--resume` 管理
- 菜單辨識使用 Read 工具

### 3. GeminiProvider

實作 Gemini CLI 特定邏輯：
- 使用位置參數傳遞 prompt
- 系統提示需併入 prompt 開頭
- Session 使用索引，需事後呼叫 `--list-sessions` 追蹤
- 菜單辨識使用 `@檔名` 語法引用圖片
- YOLO 模式使用 `-y` 參數

### 4. Provider Factory

```python
def get_provider(provider_name: str) -> BaseProvider:
    """根據名稱取得 provider 實例"""
    providers = {
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
    }
    provider_class = providers.get(provider_name, ClaudeProvider)
    return provider_class()
```

## Module Responsibilities

### app/ai.py（原 app/claude.py）

保留與 provider 無關的邏輯：
- `get_system_prompt()` - 取得系統提示詞
- `build_context()` - 建立 AI 上下文
- `call_ai()` - 主要入口，呼叫 provider 執行 CLI
- `execute_actions()` / `execute_action()` - 執行 AI 回應的動作
- 所有 `_create_order`, `_cancel_order` 等動作函數

### app/providers/claude.py

Claude CLI 專屬邏輯：
- `_build_claude_command()` → `ClaudeProvider.build_chat_command()`
- `_build_claude_menu_command()` → `ClaudeProvider.build_menu_command()`
- 回應解析（JSON from stdout）

### app/providers/gemini.py

Gemini CLI 專屬邏輯：
- `_build_gemini_command()` → `GeminiProvider.build_chat_command()`
- `_build_gemini_menu_command()` → `GeminiProvider.build_menu_command()`
- `_get_gemini_latest_session_index()` → `GeminiProvider.get_session_info_after_call()`
- `_delete_gemini_session()` → `GeminiProvider.delete_session()`
- 回應解析（需移除 markdown code block）

## Migration Strategy

1. **建立新結構**：建立 `app/providers/` 目錄和檔案
2. **實作 providers**：將 Claude/Gemini 特定程式碼實作為 provider 類別
3. **建立新主模組**：建立 `app/ai.py`，實作使用 provider 的邏輯
4. **刪除舊模組**：刪除 `app/claude.py`
5. **更新 imports**：更新所有 `from app.claude import` 為 `from app.ai import`
6. **驗證功能**：確保所有功能正常運作

## Trade-offs

### 選擇此設計的原因

1. **最小變更原則**：只重構內部結構，對外 API 保持不變
2. **清晰的職責分離**：每個 provider 只關心自己的 CLI 實作
3. **易於擴展**：新增 provider 只需實作 BaseProvider 介面

### 考慮但未採用的方案

1. **Strategy Pattern with Dependency Injection**
   - 過於複雜，不符合專案「保持簡單」的原則

2. **Plugin 架構**
   - 對於只有 2-3 個 provider 的情況過於工程化

## Risks and Mitigations

| 風險 | 影響 | 緩解措施 |
|------|------|----------|
| Import 路徑變更導致錯誤 | 中 | 全面搜尋並更新所有 import |
| 重構後功能異常 | 高 | 保留原有測試，確保通過 |
| 回應解析邏輯遺漏 | 中 | 仔細比對原程式碼 |
