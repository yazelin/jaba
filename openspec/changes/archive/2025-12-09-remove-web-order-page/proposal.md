# Proposal: remove-web-order-page

## Why

現有系統同時支援兩種訂餐方式：
1. **Web Order 頁面** (`/order`)：使用者輸入名字後透過 AI 聊天點餐
2. **LINE Bot 群組點餐**：透過 LINE 群組與呷爸互動點餐

導入 LINE Bot 後，實際使用情況顯示：
- **所有點餐都在 LINE 群組進行**，Web Order 頁面幾乎無人使用
- 兩套使用者系統造成混淆（username vs line_user_id）
- 兩套訂單儲存架構（`orders/{date}/` vs 群組 session）增加維護成本
- 管理員已轉為使用超級管理員頁面管理群組訂單

## What Changes

### 移除項目
- `/order` 路由和 `order.html` 頁面
- 個人訂餐相關 API（`/api/today` 個人模式、`/api/chat` 個人模式）
- 個人訂單儲存邏輯（`data/orders/{date}/`）
- 舊的使用者名稱識別系統（保留 LINE User ID 識別）

### 保留項目
- LINE 群組點餐完整功能
- 超級管理員後台（`/manager`）
- 看板頁面（`/`，顯示群組訂單和美食評論區）
- 使用者偏好設定（透過 LINE 對話設定，如「我不吃辣」）

### 調整項目
- 使用者偏好儲存改為純 LINE User ID 架構
- 清理不再使用的 API 和資料邏輯
