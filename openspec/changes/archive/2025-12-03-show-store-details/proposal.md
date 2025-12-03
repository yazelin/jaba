# Proposal: show-store-details

## Why
目前看板、訂餐頁、管理頁的「今日店家」區域只顯示店家名稱。雖然店家資料已有電話和備註欄位，且 API 也回傳這些資訊，但前端沒有顯示。

使用者需要知道店家電話（方便聯絡訂餐）和備註（如截止時間、特殊說明）。

## What Changes
在三個頁面的「今日店家」區塊中，以卡片式佈局顯示：
- 店家名稱（必填）
- 電話（選填，有則顯示）
- 備註（選填，有則顯示）

## Scope
- `templates/index.html` - 看板頁
- `templates/order.html` - 訂餐頁
- `templates/manager.html` - 管理頁
- `static/css/style.css` - 店家卡片樣式

## Out of Scope
- 新增欄位（地址、描述等）
- 修改店家資料結構
