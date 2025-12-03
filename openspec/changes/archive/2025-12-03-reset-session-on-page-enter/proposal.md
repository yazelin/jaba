# Proposal: reset-session-on-page-enter

## Summary
使用者進入訂購頁或管理頁時重置 Claude session，避免跨訪問的對話混亂，同時保留同一次訪問內的對話延續能力。

## Motivation
目前系統會為每個使用者每天維護一個 Claude session，跨訪問延續對話。但這造成問題：

1. **跨訪問的對話脈絡已不相關**：使用者重新進入頁面時，先前的對話上下文可能造成呷爸回應混亂
2. **所有必要資訊都已動態傳入 context**：偏好（profile）、訂單（orders）、菜單等都由後端動態加入，不需依賴 session 記憶

## Scope
- 新增 session 重置 API
- 修改前端在進入頁面時呼叫重置 API
- 更新 `ai-integration` spec

## Approach
1. 新增 `POST /api/session/reset` API 端點
2. 前端 `startChat()` 時（訂購頁）先呼叫此 API 清除舊 session
3. 前端管理頁初始化時也呼叫此 API
4. 後端 `call_claude()` 邏輯不變：
   - 無 session ID → 建立新 session
   - 有 session ID → 用 `--resume` 延續（同一次訪問內）

## Out of Scope
- Profile 和訂單儲存機制（維持不變）
- Context 建構邏輯（維持不變）
