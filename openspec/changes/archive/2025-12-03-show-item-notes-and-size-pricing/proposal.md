# Proposal: show-item-notes-and-size-pricing

## Problem
1. **備註沒有顯示**：訂單品項已儲存 `note` 欄位（如「不加香菜」、「大杯、無糖、去冰」），但前端看板、訂餐頁、管理頁都沒有顯示
2. **尺寸價格未區分**：飲料店的 M/L 杯價格不同（如珍珠奶茶 M杯50/L杯60），但目前菜單只有單一 `price`，AI 無法正確計算價格

## Solution

### Part 1: 顯示品項備註
在所有訂單顯示處加入 `note` 欄位的顯示：
- `index.html` 看板
- `order.html` 訂餐頁
- `manager.html` 管理頁

### Part 2: 支援尺寸變體價格
為菜單品項新增 `variants` 欄位：
```json
{
  "id": "item-2-2",
  "name": "珍珠奶茶",
  "price": 50,
  "variants": [
    {"name": "M", "price": 50},
    {"name": "L", "price": 60}
  ]
}
```

- `price` 仍為預設價格（通常是 M 杯）
- `variants` 為可選欄位，有此欄位時 AI 可指定尺寸
- AI 建立訂單時在 `items[].size` 指定尺寸，後端根據 variants 查找正確價格

## Scope
- 影響 specs: `menu-management`, `order-management`, `ui-layout`
- 前端 3 個 HTML 模板
- 後端 `app/claude.py` 訂單建立邏輯
