# Proposal: refactor-super-admin-panel

## Summary
將 jaba 管理員後台重構為「超級管理員後台」，從管理個人訂單轉變為管理多個 LINE 群組的訂單。

## Motivation
目前管理員後台設計用於管理個人訂單（透過 Web UI 訂餐），但實際使用情境已轉移到 LINE Bot 群組點餐。需要將後台改造為：
1. 管理多個 LINE 群組的訂單
2. 管理 LINE 使用者資料（使用 LINE User ID 作為識別）
3. 支援代理點餐和訂單編輯功能

## Scope

### In Scope
1. **群組訂單管理**：下拉選單切換群組，查看/編輯該群組的訂單
2. **使用者資料結構調整**：使用 LINE User ID 作為資料夾名稱，profile.json 中記錄 display_name
3. **AI Prompt 調整**：使用 profile 中的 display_name 與使用者溝通
4. **代理點餐功能**：超級管理員可代替群組成員新增/修改/刪除訂單
5. **付款管理**：標記付款狀態、退款處理
6. **群組管理**：查看已啟用的群組列表

### Out of Scope
- 個人訂單管理功能（將逐步廢棄）
- LINE Bot 端的修改（僅 jaba 後端/前端）
- 新增 LINE Bot 整合 API

## Key Changes

### 1. 資料結構調整
- `data/users/{username}/` → `data/users/{line_user_id}/`
- profile.json 新增 `line_user_id`、`display_name` 欄位
- 群組訂單從 session 移到正式訂單結構
- 現有使用者資料可直接清除，無需遷移

### 2. 前端重構
- 新增群組選擇器（下拉選單）
- 訂單列表按群組篩選
- 新增代理點餐介面
- 使用者管理面板

### 3. API 調整
- 新增群組訂單查詢 API
- 新增代理點餐 API
- 調整使用者識別邏輯

### 4. AI Prompt 調整
- 使用 `display_name` 而非 `username`（LINE User ID）與使用者對話

## Dependencies
- 現有群組點餐 Session 機制
- LINE Bot whitelist 資料

## Risks
- 向後兼容：需要處理舊格式資料的讀取（或直接清除）

## Success Criteria
1. 超級管理員可以選擇並管理任一群組的訂單
2. 可以代替任何群組成員進行點餐操作
3. 付款狀態可以正確追蹤和更新
4. AI 使用 display_name 與使用者互動，而非 LINE User ID
