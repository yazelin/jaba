# Proposal: improve-greeting-flow

## Summary
改善歡迎訊息流程，採用「靜態歡迎 + 主動詢問建議」的設計。

## Why
目前的問題：
1. **管理員**：完全依賴 AI 生成歡迎訊息，需要等待較長時間才能看到任何回應
2. **一般使用者**：歡迎訊息是靜態的，沒有提示可以詢問建議

## What Changes
採用方案 B「使用者主動呼叫」：
1. 管理員和使用者都使用靜態歡迎訊息（立即顯示）
2. 歡迎訊息中提示「可以問我今天吃什麼好」或「需要建議可以問我」
3. AI 的 prompt 已有建議邏輯，使用者問就會回答

優點：
- 簡單直觀，使用者有控制感
- 省資源，按需呼叫 AI
- 符合呷爸「成熟穩重大叔」個性：不會一見面就碎碎念

## Scope
- 修改 `templates/manager.html`：改回靜態歡迎訊息，移除 `getAiGreeting()`
- 修改 `templates/order.html`：在歡迎訊息中加入提示
- 不需修改後端

## Affected Specs
- `ai-integration`：新增歡迎流程需求
