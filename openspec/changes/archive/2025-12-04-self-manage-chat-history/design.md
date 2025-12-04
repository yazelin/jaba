# Design: self-manage-chat-history

## 概述

移除 CLI session 依賴，改為在每次 AI 呼叫時自行組合完整的對話上下文：

```
[系統上下文] + [使用者偏好] + [對話歷史] + [當前訊息]
```

## 資料結構

### 對話歷史暫存

**位置**: `data/users/{username}/chat_history/{date}-{mode}.json`
- `mode`: `order` 或 `manager`

**格式**:
```json
{
  "date": "2025-12-04",
  "mode": "order",
  "messages": [
    {
      "role": "user",
      "content": "我要點雞腿飯",
      "timestamp": "2025-12-04T10:30:00"
    },
    {
      "role": "assistant",
      "content": "好的，已幫您點一份雞腿飯...",
      "timestamp": "2025-12-04T10:30:05"
    }
  ],
  "created_at": "2025-12-04T10:30:00"
}
```

### 訊息精簡

為避免歷史過長，每條訊息只保留必要資訊：
- **user**: 原始訊息內容
- **assistant**: 只保留 `message` 欄位，不保留 `actions`（actions 已執行）

## 程式變更

### 1. app/data.py - 新增對話歷史管理

```python
def get_chat_history(username: str, is_manager: bool = False) -> list[dict]:
    """取得使用者當日對話歷史"""
    ...

def append_chat_history(
    username: str,
    role: str,
    content: str,
    is_manager: bool = False
) -> None:
    """新增一條對話記錄"""
    ...

def clear_chat_history(username: str, is_manager: bool = False) -> bool:
    """清除使用者當日對話歷史"""
    ...
```

### 2. app/ai.py - 修改 call_ai()

```python
def call_ai(username: str, message: str, is_manager: bool = False) -> dict:
    # 1. 取得對話歷史
    history = data.get_chat_history(username, is_manager)

    # 2. 建立上下文（已有）
    context = build_context(username, is_manager)

    # 3. 組合完整 prompt
    full_message = f"""[系統上下文]
{json.dumps(context, ensure_ascii=False, indent=2)}

[對話歷史]
{format_history(history)}

[當前訊息]
{message}

請以 JSON 格式回應...
"""

    # 4. 呼叫 AI（不使用 session）
    cmd_result = provider.build_chat_command(
        model, full_message, system_prompt,
        session_info=None  # 永遠不傳 session
    )

    # 5. 儲存對話
    data.append_chat_history(username, "user", message, is_manager)

    response = ...

    # 6. 儲存 AI 回應
    data.append_chat_history(username, "assistant", response.get("message", ""), is_manager)

    return response
```

### 3. app/providers/*.py - 簡化 session 處理

移除 `build_chat_command()` 中 session 相關邏輯：
- `session_info` 參數可選（向後相容）
- 不再使用 `--resume`, `--session-id`

移除 `get_session_info_after_call()`、`delete_session()` 的實作。

### 4. main.py - 頁面進入時清空歷史

在 `/order` 和 `/manager` 頁面進入 endpoint 中：

```python
@app.get("/order")
async def order_page(username: str = ...):
    # 清空該使用者的訂購對話歷史
    data.clear_chat_history(username, is_manager=False)
    ...

@app.get("/manager")
async def manager_page(username: str = ...):
    # 清空該使用者的管理員對話歷史
    data.clear_chat_history(username, is_manager=True)
    ...
```

## 對話歷史格式化

```python
def format_history(history: list[dict]) -> str:
    """格式化對話歷史為 prompt 可讀格式"""
    if not history:
        return "(無先前對話)"

    lines = []
    for msg in history:
        role = "使用者" if msg["role"] == "user" else "助手"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)
```

## 歷史長度控制

為避免 prompt 過長，限制：
- 最多保留最近 20 條訊息（10 輪對話）
- 或總字數不超過 5000 字

```python
def get_chat_history(username: str, is_manager: bool = False, max_messages: int = 20) -> list[dict]:
    history = _load_full_history(username, is_manager)
    return history[-max_messages:]  # 只取最近的訊息
```

## 移除的程式碼

1. **SessionInfo.session_id / session_index** - 不再需要
2. **data.py**: `get_session_info()`, `save_session_info()`, `clear_session_info()` - 可保留向後相容但不再使用
3. **providers/gemini.py**: `_find_gemini_chats_dir()`, `_get_session_id_from_file()` - 移除
4. **providers/claude.py**: session 相關邏輯 - 簡化
5. **ai.py**: `_reset_session()` action - 改為 `_clear_chat_history()`

## 優點

1. **效能提升**：每次呼叫都是新對話，沒有 session 恢復開銷
2. **可控性**：自行管理歷史長度，避免無限增長
3. **簡化**：移除對外部 CLI session 的依賴
4. **彈性**：可隨時調整歷史格式和長度

## 考量

1. **Token 使用**：每次呼叫都帶完整上下文，token 使用量較高
   - 但比起 CLI session 的隱藏 overhead，更加可控
2. **向後相容**：保留 session 相關函數（deprecated）
