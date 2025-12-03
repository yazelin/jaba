# Tasks: improve-greeting-flow

## Implementation Tasks

1. [x] **修改管理員歡迎訊息**
   - 檔案：`templates/manager.html`
   - 移除 `getAiGreeting()` 函數
   - 改為靜態歡迎訊息，包含操作教學
   - 加入提示：「需要店家建議的話，可以問我『今天訂哪家好？』」

2. [x] **修改一般使用者歡迎訊息**
   - 檔案：`templates/order.html`
   - 在現有歡迎訊息中加入提示
   - 提示：「不知道吃什麼？可以問我『今天吃什麼好？』」

3. [x] **驗證修改**
   - 管理員登入後立即看到歡迎訊息（無等待）
   - 一般使用者看到建議提示
   - AI prompt 已有建議邏輯，詢問時會正確回應
