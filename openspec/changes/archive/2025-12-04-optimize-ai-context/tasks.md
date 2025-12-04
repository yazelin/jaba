# Tasks: optimize-ai-context

## Implementation Tasks

1. [x] 新增 `_slim_menu()` 輔助函數
   - 移除品項的 `description`、`available` 欄位
   - 移除菜單的 `store_id`、`updated_at` 欄位
   - 保留 `id`、`name`、`price`、`variants`

2. [x] 修改 `build_context()` 使用者模式
   - 使用 `_slim_menu()` 精簡菜單
   - 移除 `available_stores`（訂購頁不需要）
   - 簡化 `today_store` 為店家名稱列表

3. [x] 修改 `build_context()` 管理員模式
   - 使用 `_slim_menu()` 精簡菜單
   - 保留 `available_stores`（管理員需要設定店家）
   - 精簡 `today_summary`，只保留統計數據

4. [x] 測試驗證
   - 使用者模式: 3,446 → 1,659 字元（-52%）
   - 管理員模式: 3,916 → 2,337 字元（-40%）
   - 完整 prompt: 10,610 → 6,761 字元（-36%）
