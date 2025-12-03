# Design: support-multi-cli-provider

## CLI 參數對照

| 功能 | Claude CLI | Gemini CLI |
|------|------------|------------|
| 非互動查詢 | `-p <prompt>` | 位置參數 `<prompt>` |
| 繼續對話 | `--resume <uuid>` | `--resume <index>` 或 `--resume latest` |
| 建立 session | `--session-id <uuid>` | 自動建立，無法指定 ID |
| 查詢 sessions | 無 | `--list-sessions` |
| 刪除 session | 無 | `--delete-session <index>` |
| 指定模型 | `--model <name>` | `-m <name>` |
| 輸出格式 | `--output-format json` | `-o json` |
| 系統提示 | `--system-prompt <text>` | 無，需併入 prompt |
| 跳過確認 | `--dangerously-skip-permissions` | `-y` 或 `--yolo` |
| 指定工具 | `--tools <t>` | `--allowed-tools <t>` |

## Session 管理差異

| 特性 | Claude CLI | Gemini CLI |
|------|------------|------------|
| ID 類型 | 自訂 UUID | 系統分配索引（0, 1, 2...） |
| 首次對話 | `--session-id <uuid>` | 直接執行，自動建立 |
| 後續對話 | `--resume <uuid>` | `--resume <index>` |
| 多使用者 | UUID 天然隔離 | 需追蹤索引對照 |

## 設定檔格式

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

## Session 抽象層設計

為了統一處理兩種 CLI 的 session 管理差異，建立抽象的 session 追蹤機制：

### 統一 Session 儲存格式

```
users/{username}/sessions/{date}.json
```

```json
{
  "provider": "claude",
  "session_id": "uuid-xxx",      // Claude: UUID
  "session_index": null,          // Gemini: 索引編號
  "is_manager": false,
  "created_at": "2025-12-03T10:00:00"
}
```

### Provider 介面

```python
class SessionInfo:
    provider: str
    session_id: str | None      # Claude 用
    session_index: int | None   # Gemini 用

def get_session(username: str, provider: str, is_manager: bool) -> SessionInfo | None
def save_session(username: str, provider: str, session_info: SessionInfo, is_manager: bool)
def clear_session(username: str, provider: str, is_manager: bool)
```

### Claude Session 流程

1. 首次對話：生成 UUID，用 `--session-id <uuid>` 建立
2. 後續對話：用 `--resume <uuid>` 接續
3. 重置：刪除 session 檔案

### Gemini Session 流程

1. 首次對話：不加 --resume，執行後解析輸出或用 `--list-sessions` 取得新 session 索引
2. 後續對話：用 `--resume <index>` 接續
3. 重置：用 `--delete-session <index>` 刪除（或不刪，讓它自然累積）

### 開發策略

1. **Phase 1**：先用 Claude 測試抽象層
   - 重構現有 session 儲存格式
   - 實作 Claude provider 的命令建構
   - 確認功能正常

2. **Phase 2**：加入 Gemini 支援
   - 實作 Gemini provider 的命令建構
   - 實作 session 索引追蹤
   - 處理 system prompt 併入 prompt 的邏輯

## 實作架構

採用簡單方案（不拆檔案），在現有 `claude.py` 中新增 provider 切換邏輯：

```python
def _build_claude_command(model, prompt, system_prompt, session_info) -> list[str]:
    cmd = ["claude", "-p", "--model", model, "--system-prompt", system_prompt]
    if session_info and session_info.session_id:
        cmd.extend(["--resume", session_info.session_id])
    else:
        new_id = str(uuid.uuid4())
        cmd.extend(["--session-id", new_id])
    cmd.append(prompt)
    return cmd, new_id

def _build_gemini_command(model, prompt, system_prompt, session_info) -> list[str]:
    # 將 system prompt 併入 prompt 開頭
    full_prompt = f"{system_prompt}\n\n{prompt}"
    cmd = ["gemini", "-m", model, "-o", "json"]
    if session_info and session_info.session_index is not None:
        cmd.extend(["--resume", str(session_info.session_index)])
    cmd.append(full_prompt)
    return cmd, None  # Gemini 需要事後取得 session index
```
