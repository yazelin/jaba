# show-user-own-orders

## Summary
修改訂餐頁面的「今日訂單」面板，只顯示當前使用者自己的訂單，而非所有人的訂單。

## Motivation
目前訂餐頁面（order.html）的「今日訂單」面板會顯示所有人的訂單彙整。這對一般使用者來說不夠直覺：
- 使用者只關心自己點了什麼
- 顯示全部訂單可能造成資訊過載
- 使用者無法快速確認自己的訂單狀態

**注意**：管理頁面（manager.html）和看板首頁（index.html）應該維持顯示所有訂單，讓管理員能綜覽全局。

## Scope
- **範圍內**：訂餐頁 order.html 的訂單面板過濾邏輯
- **範圍外**：管理頁、首頁維持現有行為

## Affected Specs
- order-management (修改使用者視角的訂單顯示要求)

## Dependencies
無
