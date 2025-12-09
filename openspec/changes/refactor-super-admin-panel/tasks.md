# Tasks: refactor-super-admin-panel

## Phase 1: 資料結構調整

- [x] 1.1 更新 `data.py` 中的使用者相關函數
  - 支援 `line_user_id` 作為資料夾名稱
  - `get_user_profile()` 回傳 `display_name`
  - `create_user()` 接受 `line_user_id` 和 `display_name`
  - **驗證**：單元測試建立/讀取使用者資料

- [x] 1.2 擴充群組 session 結構
  - 在 session 中加入 `payments` 欄位
  - 訂單記錄加入 `line_user_id` 和 `display_name`
  - **驗證**：現有群組點餐流程正常運作

- [x] 1.3 清除舊使用者資料
  - 刪除 `data/users/` 下的舊資料
  - **驗證**：資料目錄結構正確

## Phase 2: API 實作

- [x] 2.1 新增群組列表 API
  - `GET /api/super-admin/groups`
  - 回傳所有已啟用群組及訂單統計
  - **驗證**：API 回傳正確群組列表

- [x] 2.2 新增群組訂單 API
  - `GET /api/super-admin/groups/{group_id}/orders`
  - `POST /api/super-admin/groups/{group_id}/orders` (代理點餐)
  - `PUT /api/super-admin/groups/{group_id}/orders/{user_id}`
  - `DELETE /api/super-admin/groups/{group_id}/orders/{user_id}`
  - **驗證**：CRUD 操作正常

- [x] 2.3 新增付款管理 API
  - `POST /api/super-admin/groups/{group_id}/payments/{user_id}/mark-paid`
  - `POST /api/super-admin/groups/{group_id}/payments/{user_id}/refund`
  - **驗證**：付款狀態正確更新

- [x] 2.4 調整現有 chat API
  - 支援超級管理員模式
  - 傳入 `group_id` 和 `target_user_id` 進行代理操作
  - **驗證**：代理點餐流程正常

## Phase 3: 前端重構

- [x] 3.1 新增群組選擇器
  - 下拉選單顯示已啟用群組
  - 切換時載入該群組訂單
  - **驗證**：切換群組後顯示正確訂單

- [x] 3.2 重構訂單列表
  - 按使用者分組顯示（使用 display_name）
  - 顯示品項、金額、備註
  - **驗證**：訂單資訊完整顯示

- [x] 3.3 新增訂單操作按鈕
  - 編輯按鈕：開啟編輯對話框
  - 刪除按鈕：確認後刪除
  - **驗證**：編輯/刪除功能正常

- [x] 3.4 新增代理點餐介面
  - 選擇使用者
  - 選擇餐點（從今日菜單）
  - 設定數量和備註
  - **驗證**：代理點餐成功建立訂單

- [x] 3.5 重構付款狀態面板
  - 按群組篩選顯示
  - 付款/退款按鈕
  - **驗證**：付款操作正常

## Phase 4: AI Prompt 調整

- [x] 4.1 調整 `build_context()` 函數
  - 使用 `display_name` 作為 `username` 傳給 AI
  - 保留 `line_user_id` 作為內部識別
  - **驗證**：AI 使用正確名稱對話

- [x] 4.2 調整 `group_ordering_prompt.md`
  - 說明 username 即為使用者顯示名稱
  - 確保 action 中使用正確欄位
  - **驗證**：群組點餐對話正常

- [x] 4.3 調整 `user_prompt.md`
  - 同樣使用 display_name 邏輯
  - **驗證**：個人對話正常

## Phase 5: 整合測試

- [x] 5.1 端對端測試
  - LINE Bot 群組點餐 → 超級管理員查看
  - 超級管理員代理點餐 → 訂單正確建立
  - 付款標記 → 狀態正確更新
  - **驗證**：完整流程正常運作

- [ ] 5.2 清理與文件更新
  - 移除廢棄的個人訂單相關程式碼
  - 更新 README 說明
  - **驗證**：文件與實作一致
  - **備註**: 後續再清理
