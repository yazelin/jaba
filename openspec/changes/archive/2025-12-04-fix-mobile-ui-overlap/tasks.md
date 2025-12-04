# Tasks: fix-mobile-ui-overlap

## 返回按鈕重新設計
- [x] 將返回按鈕整合進 chat-header，成為標準 nav bar 佈局
- [x] header 使用 flex 佈局：左側返回按鈕、中間標題、右側 spacer
- [x] 返回按鈕使用半透明白色背景，與 header 風格一致
- [x] 密碼頁保留獨立的返回按鈕樣式 (.back-link-standalone)

## 手機版底部留白
- [x] 訂餐頁 (order.html)：為 `.order-right-panel` 在手機版增加 `padding-bottom: 80px`
- [x] 管理員頁 (manager.html)：為 `.admin-right-panel` 在手機版增加 `padding-bottom: 80px`

## 手機版 RWD 調整
- [x] header padding 和字體大小縮小以適應手機螢幕
- [x] 返回按鈕字體和 padding 縮小
- [x] spacer 寬度調整以維持標題置中

## 驗證
- [x] 手機版訂餐頁：「共 x 筆」行在美食評論區展開時仍可見
- [x] 手機版管理員頁：收款面板下緣在美食評論區展開時仍可見
- [x] 返回按鈕在各頁面清楚可辨識且不遮擋標題
