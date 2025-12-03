# Proposal: add-claude-model-config

## Summary
新增 Claude 模型設定功能，讓不同任務可以使用不同的模型（haiku/sonnet/opus）。

## Why
目前系統使用 Claude CLI 時沒有指定模型，預設會使用較貴的模型。需求：
1. **Chat 對話**：可選擇 haiku（快速便宜）或 sonnet（平衡）
2. **菜單辨識**：可選擇 sonnet 或 opus（複雜視覺任務）
3. **成本控制**：不同任務使用適合的模型，降低 API 成本

## What Changes

### 1. 新增設定檔
建立 `data/system/ai_config.json`：
```json
{
  "chat": {
    "model": "sonnet"
  },
  "menu_recognition": {
    "model": "sonnet"
  }
}
```

### 2. 修改 Claude CLI 呼叫
在 `app/claude.py` 中：
- `call_claude()`：讀取 `chat.model` 設定，加入 `--model` 參數
- `recognize_menu_image()`：讀取 `menu_recognition.model` 設定，加入 `--model` 參數

### 3. Claude CLI 模型參數
```bash
# 使用 haiku
claude -p --model claude-haiku-4-20250514 "..."

# 使用 sonnet（預設）
claude -p --model claude-sonnet-4-20250514 "..."

# 使用 opus
claude -p --model claude-opus-4-20250514 "..."
```

## Scope
- 新增 `data/system/ai_config.json` 設定檔
- 修改 `app/claude.py`：
  - 新增 `get_ai_config()` 函數
  - 修改 `call_claude()` 加入 `--model` 參數
  - 修改 `recognize_menu_image()` 加入 `--model` 參數
- 不需修改前端

## Affected Specs
- `ai-integration`：新增模型設定需求
