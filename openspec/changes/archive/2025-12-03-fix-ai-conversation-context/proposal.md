# fix-ai-conversation-context

## Summary
修復 AI 對話上下文問題，讓 Claude 能記住之前的對話內容。

## Problem
目前與呷爸對話時，AI 不記得之前說過什麼。例如：
- 使用者說「好」來確認之前的提議
- 但 AI 卻回應了完全無關的歡迎訊息

**根本原因：**
程式碼嘗試從 Claude CLI 的 stderr 解析 session ID：
```python
session_match = re.search(r'session[:\s]+([a-f0-9-]+)', result.stderr, re.I)
```
但 Claude CLI 不會以這種格式輸出 session ID，所以 session 從未被保存。

## Solution
根據 Claude CLI 文檔，正確的用法是：

1. **首次對話**：使用 `uuid.uuid4()` 生成 session ID，用 `--session-id <uuid>` 建立對話
2. **後續對話**：使用 `--resume <sessionId>` 恢復對話

修改 `call_claude()` 函數：
```python
import uuid

session_id = data.get_session_id(username)

if session_id:
    # 後續對話：恢復 session
    cmd = ["claude", "-p", "--resume", session_id]
else:
    # 首次對話：建立新 session
    new_session_id = str(uuid.uuid4())
    data.save_session_id(username, new_session_id)
    cmd = ["claude", "-p", "--session-id", new_session_id, "--append-system-prompt", system_prompt]

cmd.append(full_message)
```

## Scope
- **範圍內**：`app/claude.py` 的 `call_claude()` 函數
- **範圍外**：其他功能不受影響

## Dependencies
無
