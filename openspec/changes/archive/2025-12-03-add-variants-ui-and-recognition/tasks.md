# Tasks: add-variants-ui-and-recognition

## Part 1: AI 菜單辨識

1. [x] **更新辨識 prompt**
   - 修改 `app/claude.py` 的 `recognize_menu_image()`
   - prompt 新增 variants 格式說明
   - 指導 AI 辨識 M/L、大/中/小、大碗/小碗等尺寸

## Part 2: 管理員 UI

2. [x] **更新 generateItemRow() 函數**
   - 新增 variants 顯示區塊
   - 有 variants 時顯示尺寸列表
   - 無 variants 時顯示「+ 新增尺寸」按鈕

3. [x] **新增 variants 編輯函數**
   - `addVariant(catIdx, itemIdx)`: 新增尺寸
   - `removeVariant(catIdx, itemIdx, varIdx)`: 刪除尺寸
   - 更新 `saveRecognizedMenu()` 收集 variants 資料

4. [x] **新增 CSS 樣式**
   - `.item-variants`: variants 容器
   - `.variant-row`: 尺寸編輯列

## Part 3: AI 對話編輯

5. [x] **新增 update_item_variants 動作**
   - 在 `app/claude.py` 新增 `_update_item_variants()` 函數
   - 支援新增/修改/刪除品項的尺寸價格
   - 在 `execute_action()` 加入處理

6. [x] **更新管理員 prompt**
   - 在 `manager_prompt.md` 新增動作說明
   - 說明如何使用對話編輯尺寸價格

## Part 4: 驗證

7. [x] **驗證功能**
   - 測試 AI 辨識飲料/便當菜單產生 variants
   - 測試手動新增/編輯/刪除 variants
   - 測試 AI 對話編輯 variants
   - 測試儲存後 variants 資料正確
