# Tasks: show-item-notes-and-size-pricing

## Part 1: 顯示品項備註

1. [x] **更新 index.html 訂單顯示**
   - 在訂單品項後顯示 note（如有）
   - 格式：`品名 x1 (備註)`

2. [x] **更新 order.html 訂單顯示**
   - 右側面板訂單列表顯示 note
   - 我的訂單區塊顯示 note
   - 新增 `.live-order-note` CSS 樣式

3. [x] **更新 manager.html 訂單顯示**
   - 訂單列表顯示 note

## Part 2: 支援尺寸變體價格

4. [x] **更新 app/claude.py 訂單建立邏輯**
   - `_create_order()` 支援 `size` 欄位
   - 從 `variants` 查找對應價格
   - 無 variants 或未指定 size 時使用預設 price

5. [x] **更新 AI prompt**
   - create_order 動作新增 `size` 欄位
   - 建立訂單注意事項新增 variants 說明
   - 指導 AI 詢問使用者尺寸

6. [x] **驗證功能**
   - 測試 size 價格查找邏輯
   - 測試無 variants 時使用預設價格
