# Tasks

## 實作任務

- [x] 在 `call_claude()` 開頭 import uuid
- [x] 修改 session 邏輯：首次對話時生成 UUID 並立即儲存
- [x] 首次對話使用 `--session-id <uuid>` 和 `--append-system-prompt` 參數
- [x] 後續對話使用 `--resume <sessionId>` 參數（不需要再傳 system prompt）
- [x] 移除從 stderr 解析 session ID 的舊邏輯
- [x] 測試：確認對話上下文正確延續（回應「好」時 AI 能理解是確認）
