# Change: 新增店家啟用/停用獨立按鈕

## Why
目前管理員頁面的店家狀態（啟用/停用）只是顯示標籤，要切換狀態必須透過呷爸 AI 對話。為了操作效率，應該讓管理員可以直接點擊切換店家啟用狀態。

## What Changes
- 將店家狀態標籤改為可點擊的按鈕
- 新增 `/api/store/{store_id}/toggle` API 端點，切換店家的 `active` 狀態
- 點擊後即時更新店家列表顯示

## Impact
- Affected specs: admin-ui
- Affected code: `main.py`, `templates/manager.html`, `app/data.py`
