# Design: optimize-gemini-cli

## 問題分析

### 1. 回應速度問題

經分析，可能的原因：

| 因素 | Claude CLI | Gemini CLI | 影響 |
|------|------------|------------|------|
| CLI 啟動時間 | 較快 | 較慢（Node.js runtime） | 中 |
| Session 追蹤 | 無額外呼叫 | 需呼叫 `--list-sessions` | 高 |
| 模型回應時間 | 依模型 | 依模型 | 依情況 |
| 輸出處理 | 直接 stdout | stdout + stderr 混合 | 低 |

**Session 追蹤是主要開銷**：每次新 session 後，需額外執行 `gemini --list-sessions` 取得索引，這增加約 2-5 秒。

### 2. 輸出格式問題

Gemini 模型不保證遵循我們 prompt 要求的 JSON 格式，可能回傳：
- 正確的 JSON：`{"message": "...", "actions": [...]}`
- markdown code block：` ```json {...} ``` `
- 純文字：`好的，我幫你點了雞腿飯`

**結論**：這是模型行為問題，無法完全解決。現有的 markdown 清理邏輯已能處理，保持現狀即可。

### 3. Session 自管理方案

經過調查，發現 Gemini CLI session 有以下特性：

**Session 儲存機制**：
- 位置：`~/.gemini/tmp/<project_hash>/chats/`
- 檔名格式：`session-YYYY-MM-DDTHH-MM-<uuid前8碼>.json`
- 內容結構：`{ sessionId, projectHash, messages: [...] }`
- `--resume <uuid>` 可直接用完整 UUID 恢復（不需要索引）

**關鍵發現**：
```bash
# 檔名包含 UUID 前 8 碼
session-2025-12-03T15-29-585ea11e.json

# 檔案內含完整 sessionId
{
  "sessionId": "585ea11e-b3cb-4b34-a5be-0ddcb0598263",
  "projectHash": "224b7019c0b2eeed...",
  "messages": [...]
}
```

**新方案：Session 自管理**
1. 首次對話：執行 Gemini，不帶 `--resume`
2. 取得 Session：監控 chats 目錄找新檔案，讀取 `sessionId`
3. 儲存 Session：在我們的 session 管理中記錄 UUID
4. 後續對話：使用 `--resume <full-uuid>` 直接恢復

**優點**：
- 省去 `--list-sessions` 開銷（每次省 2-5 秒）
- 保留完整對話記憶
- 不需要解析索引

## 實作方案

### 1. Gemini Provider 修改

```python
GEMINI_CHATS_BASE = Path.home() / ".gemini" / "tmp"

def find_gemini_chats_dir(self) -> Optional[Path]:
    """找到 Gemini CLI 使用的 chats 目錄（基於最近使用時間）"""
    chats_dirs = list(GEMINI_CHATS_BASE.glob("*/chats"))
    if not chats_dirs:
        return None
    # 返回最近修改的目錄
    return max(chats_dirs, key=lambda p: p.stat().st_mtime)

def get_session_id_from_file(self, chats_dir: Path, after_time: float) -> Optional[str]:
    """從新建的 session 檔案取得 sessionId"""
    for f in chats_dir.glob("session-*.json"):
        if f.stat().st_mtime > after_time:
            try:
                data = json.loads(f.read_text())
                return data.get("sessionId")
            except:
                pass
    return None

def build_chat_command(self, model: str, ...) -> CommandResult:
    # 模型由 ai_config 傳入，若未指定則用預設值
    actual_model = model or "gemini-2.5-flash-lite"
    cmd = ["gemini", "-m", actual_model]

    # 如果有儲存的 session UUID，使用 --resume
    if session_uuid:
        cmd.extend(["--resume", session_uuid])

    cmd.append(full_prompt)
    return CommandResult(cmd=cmd, cwd=..., is_new_session=not session_uuid)
```

### 2. 回應解析（保持現有邏輯，改進錯誤處理）

```python
def parse_response(self, stdout, stderr, return_code) -> dict:
    response_text = stdout.strip()

    if not response_text:
        return {"message": stderr or "AI 沒有回應", "actions": [], "error": "no_response"}

    try:
        # 清理 markdown code block（現有邏輯）
        clean_text = re.sub(r'^```(?:json)?\s*', '', response_text)
        clean_text = re.sub(r'\s*```$', '', clean_text).strip()

        # 嘗試提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', clean_text)
        if json_match:
            return json.loads(json_match.group())
        else:
            # AI 沒有回傳 JSON，直接用回應作為 message
            return {"message": response_text, "actions": []}

    except json.JSONDecodeError as e:
        # 【改進】回傳原始回應以便診斷
        return {
            "message": response_text[:300],  # 顯示 AI 的實際回應
            "actions": [],
            "error": "parse_error",
            "raw_response": response_text[:500]
        }
```

### 3. 前端錯誤顯示改進

```javascript
if (data.error) {
    if (data.error === 'timeout') {
        addMessage('assistant', '抱歉，回應超時了，請再試一次。');
    } else if (data.error === 'parse_error') {
        // 顯示 AI 實際回應（可能格式不對但內容有意義）
        addMessage('assistant', data.message || '回應格式錯誤');
    } else {
        addMessage('assistant', data.message || '發生錯誤');
    }
} else {
    addMessage('assistant', data.message || '...');
}
```

## 效能預估

| 項目 | 修改前 | 修改後 |
|------|--------|--------|
| Session 追蹤開銷 | 2-5 秒（`--list-sessions`） | ~0 秒（讀取本地檔案） |
| 對話記憶 | 有（但開銷大） | 有（無額外開銷） |
| 預設模型 | 無（必須指定） | `gemini-2.5-flash-lite`（若未設定） |
| 錯誤診斷 | 困難 | 容易（有原始回應） |
| 格式解析失敗處理 | 顯示空白 | 顯示實際回應內容 |

## 相容性考量

- Claude Provider 不受影響
- Gemini session 繼續使用，但改由我們自行管理 UUID（不透過 `--list-sessions`）
- API 回應格式維持相容，新增 `raw_response` 欄位供診斷
