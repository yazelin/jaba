# Design: remove-web-order-page

## 架構變更

### 移除前架構
```
使用者入口
├── Web Order (/order) ─── 輸入名字 ─── /api/chat (個人模式)
│                                          └── data/orders/{date}/
│                                          └── data/users/{username}/
│
└── LINE Bot ─── line_user_id ─── 群組點餐 session
                                      └── data/groups/{group_id}/session.json
                                      └── data/users/{line_user_id}/
```

### 移除後架構
```
使用者入口
└── LINE Bot ─── line_user_id ─── 群組點餐 session
                                      └── data/groups/{group_id}/session.json
                                      └── data/users/{line_user_id}/

管理入口
├── /manager (超級管理員) ─── 管理群組訂單
└── / (看板) ─── 顯示群組訂單、美食評論區
```

## 移除清單

### 前端
- `templates/order.html` - 整個檔案刪除

### 後端路由
- `GET /order` - 移除
- `POST /api/chat` - 移除個人模式（保留群組模式）
- `GET /api/today` - 移除或重構（僅保留看板需要的部分）
- `POST /api/session/reset` - 移除（只有 order.html 使用）
- `GET /api/chat/messages` - 移除（order.html 的美食評論區用，已被群組聊天取代）
- `POST /api/chat/send` - 移除（同上）

### 資料邏輯
- `data/orders/{date}/` - 不再寫入（可保留歷史資料）
- 個人訂單相關函數 - 標記為 deprecated 或移除

### AI Prompt
- `user_prompt.md` - 移除（個人對話模式）

## 保留項目

### 使用者偏好（透過 LINE 對話）
使用者可透過 LINE 對話設定偏好，AI 會解析並存入 profile：
- 「我不吃辣」→ dietary_restrictions
- 「我對海鮮過敏」→ allergies
- 「叫我小明就好」→ preferred_name

### 群組點餐
- LINE 群組訂餐流程不變
- 群組 session 儲存訂單
- 超級管理員管理群組訂單

### 看板頁面
- `/` - 顯示群組訂單、美食評論區、QRCode

## 風險評估

### 低風險
- Web Order 使用率極低，移除影響小
- 現有 LINE 使用者不受影響

### 注意事項
- 舊的 `data/orders/` 資料可保留作為歷史紀錄
- 舊的 `data/users/{username}/` 非 LINE User ID 格式資料可歸檔

## 未來擴充（擱置）
- LINE LIFF 偏好設定頁面（需建立 LINE Login channel）
- 使用者歷史訂單查詢
- 個人付款狀態查詢
