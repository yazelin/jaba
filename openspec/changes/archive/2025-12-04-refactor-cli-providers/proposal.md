# Proposal: refactor-cli-providers

## Summary

重構 AI CLI 整合模組，將目前混在 `app/claude.py` 中的 Claude CLI 和 Gemini CLI 程式碼分離成獨立的 provider 模組，以提高程式碼的可維護性和擴展性。

## Why

目前 `app/claude.py` 檔案存在以下問題：

1. **命名不準確**：檔案名為 `claude.py`，但實際上同時包含 Claude 和 Gemini 兩種 CLI 的實作
2. **職責混雜**：命令建構、session 管理、回應解析等功能都混在同一個檔案中
3. **擴展困難**：若要新增其他 CLI provider（如未來的其他 AI 服務），需要繼續在同一檔案中增加程式碼
4. **難以維護**：不同 provider 的邏輯穿插在各函數中，增加理解和維護的難度

## What Changes

採用 Provider 抽象模式，將程式碼重構為：

```
app/
├── ai.py              # 主要入口，包含 call_ai(), execute_actions() 等公用函數
├── providers/
│   ├── __init__.py    # Provider 工廠和基底類別
│   ├── claude.py      # Claude CLI provider 實作
│   └── gemini.py      # Gemini CLI provider 實作
```

### 設計要點

1. **Provider 基底類別**：定義統一的介面（build_command, parse_response, manage_session）
2. **工廠模式**：根據 ai_config.json 中的 provider 設定動態選擇實作
3. **共用邏輯保留**：build_context、execute_actions 等與 provider 無關的邏輯保留在主模組

## Impact

- **變更範圍**：刪除 `app/claude.py`，建立新的 `app/ai.py` 和 `app/providers/` 模組
- **Breaking Change**：所有 `from app.claude import` 需改為 `from app.ai import`
- **測試影響**：需要更新相關測試的 import 路徑

## Out of Scope

- 不新增任何 AI 功能
- 不修改 ai_config.json 的格式
- 不修改前端或 API 端點
