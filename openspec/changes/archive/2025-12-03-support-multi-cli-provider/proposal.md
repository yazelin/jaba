# Proposal: support-multi-cli-provider

## Why

目前系統只支援 Claude CLI，但團隊希望能彈性切換使用 Gemini CLI 或其他 AI CLI 工具。不同功能（對話、菜單辨識）可能適合用不同的 provider，例如：
- 對話功能用成本較低的 provider
- 菜單辨識用視覺能力較強的 provider

## What Changes

1. 擴展 `ai_config.json` 格式，每個功能可設定 `provider`（claude/gemini）和 `model`
2. 抽象化 CLI 呼叫邏輯，根據 provider 選擇對應的命令與參數
3. 處理兩者參數差異（如 `--resume` vs `-r`、`-p` vs 位置參數）

## Scope

- ai-integration spec

## Design Considerations

參見 design.md
