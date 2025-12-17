# Change: 品項統計不含備註

## Why

目前群組點餐摘要中的「品項統計」會將備註（note）視為不同品項，導致相同餐點因備註不同而分開統計。例如：

- 珍奶 x1
- 珍奶（微糖微冰）x2

這讓管理員難以快速統計要訂多少數量。備註資訊已經記錄在每個人的訂單明細中，品項統計只需要顯示總數即可。

## What Changes

- 修改品項統計邏輯，只以品項名稱（name）作為統計 key，不含備註
- 統計結果會將所有相同名稱的品項合計，例如：`珍奶 x3`
- 每個人訂單明細中的備註資訊保持不變（可看到「珍奶（微糖微冰）」等）

## Impact

- Affected specs: `order-management`
- Affected code: `main.py` - `generate_session_summary()` 函數
