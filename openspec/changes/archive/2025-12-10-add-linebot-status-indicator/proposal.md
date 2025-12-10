# Change: 新增 LINE Bot 運行狀態指示器

## Why
Render 免費帳號在閒置時會進入休眠狀態，導致冷啟動時間較長。透過在看板頁（`/`）和管理員頁（`/manager`）定期觸發 LINE Bot 端點，可以：
1. 提早觸發冷啟動，縮短使用者實際使用時的等待時間
2. 讓管理員和使用者明確知道 LINE Bot 是否正常運行
3. 保持 LINE Bot 活躍，避免閒置休眠

## What Changes
- 在看板頁（`index.html`）和管理員頁（`manager.html`）新增 LINE Bot 狀態指示器
- 頁面載入時背景 fetch `https://jaba-line-bot.onrender.com`
- 每 1 分鐘重新檢查一次狀態（keep-alive 效果）
- 根據回應內容（預期包含 `Jaba LINE Bot is running!`）判斷運行狀態
- 顯示狀態：載入中 → 運行中 / 無法連線

## UI 位置設計
- **看板頁**：狀態指示器放在「加入呷爸好友」QRCode 區塊附近，與 QRCode 資訊整合顯示
- **管理員頁**：在左側「店家管理」panel 的上方新增獨立的「LINE Bot 狀態」panel

## Impact
- Affected specs: `specs/ui-layout/spec.md`
- Affected code: `templates/index.html`, `templates/manager.html`, `static/css/style.css`
