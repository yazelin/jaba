## 1. 基礎架構

- [x] 1.1 建立 `data/` 目錄結構
- [x] 1.2 建立 `data/system/config.json`
- [x] 1.3 建立 `data/system/today.json`
- [x] 1.4 建立 `data/system/prompts/jiaba.json`
- [x] 1.5 實作啟動時自動建立目錄

## 2. 資料存取模組

- [x] 2.1 實作 JSON 讀取/寫入函數
- [x] 2.2 實作目錄列表函數

## 3. 便當店資料

- [x] 3.1 建立範例店家 `data/stores/sample-store/`
- [x] 3.2 實作店家 CRUD 操作
- [x] 3.3 實作菜單讀取/更新

## 4. 使用者資料

- [x] 4.1 實作使用者資料夾自動建立
- [x] 4.2 實作 session 管理（查詢/儲存 session ID）

## 5. 訂單管理

- [x] 5.1 實作訂單建立
- [x] 5.2 實作每日彙整更新
- [x] 5.3 實作付款記錄管理

## 6. Claude CLI 整合

- [x] 6.1 實作 claude CLI 呼叫（新 session / resume）
- [x] 6.2 實作 AI 回應解析
- [x] 6.3 實作訂餐動作執行器
- [x] 6.4 實作管理動作執行器

## 7. Socket.IO 即時通知

- [x] 7.1 安裝 python-socketio
- [x] 7.2 設定 FastAPI + Socket.IO 整合
- [x] 7.3 實作訂單事件廣播

## 8. 前端 - 今日看板（首頁）

- [x] 8.1 建立看板 HTML/CSS 大畫面版型
- [x] 8.2 顯示今日店家、訂單列表、品項統計、總金額
- [x] 8.3 實作「我要訂便當」「管理員」按鈕
- [x] 8.4 實作 Socket.IO 即時更新

## 9. 前端 - 訂餐頁

- [x] 9.1 建立名稱輸入（localStorage 暫存）
- [x] 9.2 建立 AI 對話介面
- [x] 9.3 實作訊息發送/接收

## 10. 前端 - 管理頁

- [x] 10.1 建立密碼驗證
- [x] 10.2 建立 AI 對話管理介面
- [x] 10.3 實作圖片上傳功能
