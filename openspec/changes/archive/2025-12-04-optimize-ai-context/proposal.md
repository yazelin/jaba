# Proposal: optimize-ai-context

## Why

目前 AI 對話的 context 包含大量冗餘資訊，導致：
- 每次呼叫傳送約 8,000-10,000 字元
- Gemini API 回應時間約 25-35 秒
- 大部分資訊（如品項 description、available 狀態）AI 不需要

## What Changes

精簡 `build_context()` 產生的上下文，只保留 AI 回應必要的資訊：

### 菜單精簡（最大節省）
| 欄位 | 現況 | 調整 |
|------|------|------|
| `description` | 完整描述 | 移除 |
| `available` | true/false | 移除（預設都可用） |
| `store_id`, `updated_at` | 包含 | 移除（冗餘） |

精簡後品項格式：`{"id": "xxx", "name": "品名", "price": 95}` 或含 `variants`

### 其他精簡
- `available_stores`: 訂購頁不需要（已有 today_menus）
- `today_store`: 簡化結構，只保留店家名稱列表
- 管理員模式的 `today_summary.orders`: 只保留統計，不傳完整訂單明細

### 預估效果
- 菜單：2,800 → ~800 字元（-70%）
- 整體 context：~4,000 → ~1,500 字元（-60%）
- 預期回應時間：25-35 秒 → 10-15 秒

## Scope

- 修改 `app/ai.py` 的 `build_context()` 函數
- 不影響 AI 回應品質（保留必要欄位）
- 不改變 API 介面

## Out of Scope

- 精簡 system prompt（另案處理）
- 對話歷史的精簡
