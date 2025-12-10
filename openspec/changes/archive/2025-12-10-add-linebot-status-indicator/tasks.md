## 1. Implementation

- [x] 1.1 在 `index.html` QRCode 區塊內新增 LINE Bot 狀態指示器
- [x] 1.2 在 `index.html` 新增 `checkLineBotStatus()` 函數與 60 秒定期檢查
- [x] 1.3 在 `manager.html` 店家管理 panel 上方新增獨立的「LINE Bot 狀態」panel
- [x] 1.4 在 `manager.html` 新增相同的狀態檢查邏輯與定期刷新
- [x] 1.5 新增對應的 CSS 樣式（狀態指示器：載入中/運行中/離線）

## 2. Testing

- [ ] 2.1 測試看板頁載入時 QRCode 區塊內狀態指示器正常顯示
- [ ] 2.2 測試管理員頁登入後獨立 panel 狀態指示器正常顯示
- [ ] 2.3 測試 LINE Bot 離線時顯示正確狀態
- [ ] 2.4 測試定期刷新功能（等待 1 分鐘觀察狀態更新）
