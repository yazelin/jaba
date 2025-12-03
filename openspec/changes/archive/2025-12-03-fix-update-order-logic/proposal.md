# Proposal: fix-update-order-logic

## Summary
修正訂單修改邏輯，當使用者要移除品項時，應從現有訂單中移除而非建立新訂單。

## Problem
目前 `_update_order` 只是呼叫 `_create_order`，導致：

**用戶訂單 [排骨便當, 味噌湯]，說「不要排骨便當」：**
- 預期：訂單變成 [味噌湯]
- 實際：原訂單 [排骨便當, 味噌湯] 保留 + 新訂單 [味噌湯]
- 結果：2 份味噌湯 + 1 份排骨便當 ❌

## Scope
- 修正 `_update_order` 後端邏輯
- 新增 `remove_item` 動作處理品項移除
- 更新 prompt 指示呷爸正確使用動作

## Approach

### 動作分類
1. **新增品項**（不在現有訂單中）→ `create_order` 建立新訂單
2. **移除品項**（從現有訂單中移除）→ `remove_item` 新動作
3. **修改整筆訂單**（整體替換）→ `update_order` 需指定 `order_id`

### 新增 `remove_item` 動作
```json
{
  "type": "remove_item",
  "data": {
    "item_name": "排骨便當",
    "quantity": 1
  }
}
```
- 從使用者現有訂單中找到該品項並移除
- 如果訂單只剩該品項，刪除整筆訂單
- 如果訂單還有其他品項，更新訂單內容

### Prompt 更新
指示呷爸：
1. 查看 `current_orders` 了解使用者現有訂單
2. 移除品項時使用 `remove_item` 而非 `create_order`
3. 新增品項時才用 `create_order`

## Out of Scope
- 訂單合併功能（多筆訂單合併為一筆）
- 跨店家品項調整
