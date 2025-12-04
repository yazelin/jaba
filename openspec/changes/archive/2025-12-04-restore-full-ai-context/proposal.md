# Proposal: restore-full-ai-context

## Summary
移除「精簡 AI Context」的限制，讓 AI 上下文保持完整資訊，使呷爸能提供更好的服務。

## Motivation
目前的「精簡 AI Context」設計有以下問題：

1. **管理員需要完整訂單資訊**：管理員需要知道每筆訂單的詳細內容（誰點了什麼、數量、備註等），而非僅有統計數據。精簡版無法滿足管理需求。

2. **使用者需要菜單詳細資訊**：呷爸在建議餐點時，需要知道每道菜的描述（如口味、食材、特色），才能根據使用者偏好提供個人化推薦。目前移除 `description` 欄位會導致呷爸無法給出有品質的建議。

3. **效能考量過度優化**：實際 context 大小約幾千 token，屬於正常範圍。Gemini 回應慢是模型本身特性，非 context 過長造成。過度精簡反而犧牲了 AI 的服務品質。

## Changes
移除「精簡 AI Context」規格要求，改為提供完整上下文：

- **菜單資訊**：保留 `description`、`available` 等完整欄位
- **管理員 today_summary**：包含完整訂單明細，不只是統計數據
- **使用者模式**：可視需要包含 `available_stores` 供 AI 參考

## Impact
- **ai-integration**: 移除「精簡 AI Context」相關要求

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Context 變大可能增加 token 成本 | 菜單和訂單資料本身不大，成本影響有限 |
| 回應時間可能略增 | 實際增量很小，AI 品質提升帶來更大價值 |
