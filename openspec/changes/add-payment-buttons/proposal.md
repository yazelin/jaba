# Change: 新增獨立付款/退款按鈕

## Why
目前管理員只能透過呷爸 AI 對話來標記付款狀態，而「確認退款」已有獨立按鈕。為了操作一致性和效率，「確認付款」也應該要有獨立按鈕，讓管理員能快速直接更新付款狀態。

## What Changes
- 在付款面板中，未付款/待補狀態的記錄顯示「確認付款」按鈕
- 新增 `/api/mark-paid` API 端點，直接呼叫 `_mark_paid()` 函數
- 確認付款按鈕點擊後即時更新付款狀態

## Impact
- Affected specs: order-management
- Affected code: `main.py`, `templates/manager.html`
