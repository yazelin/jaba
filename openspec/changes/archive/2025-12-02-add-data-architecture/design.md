## Context
jiaba 是內部午餐訂便當系統，所有操作都由 AI Agent 協助處理。資料格式必須方便 AI 讀取、解析與修改。

## Goals / Non-Goals
**Goals:**
- 所有資料使用 JSON 格式，AI 可準確解析與生成
- 結構固定、欄位明確，減少 AI 出錯機率
- 支援選擇性圖片（圖片路徑存在 JSON 中）

**Non-Goals:**
- 不追求人類手動編輯的便利性（透過 AI 操作即可）
- 不使用 Markdown 或 YAML（AI 處理較易出錯）

## Decisions

### 目錄結構

```
data/
├── system/
│   ├── config.json            # 全域設定
│   └── prompts/
│       └── jiaba.json         # AI 系統提示詞與角色設定
│
├── stores/                     # 便當店
│   └── {store-id}/
│       ├── info.json          # 店家資訊
│       ├── menu.json          # 菜單（結構化）
│       └── images/            # 菜品圖片（選擇性）
│
├── users/                      # 使用者
│   └── {username}/
│       ├── profile.json       # 使用者資料
│       ├── orders/
│       │   └── {date}.json    # 每日訂單
│       └── sessions/
│           └── {date}.txt     # 當日 Claude session ID
│
└── orders/                     # 每日彙整（管理用）
    └── {date}/
        ├── summary.json       # 訂單彙整
        └── payments.json      # 付款記錄
```

### 檔案格式（全部 JSON）

**system/config.json:**
```json
{
  "admin_password": "9898",
  "today_store": "happy-bento",
  "order_deadline": "10:30",
  "server_port": 8098
}
```

**system/today.json:**（每日訂餐狀態）
```json
{
  "date": "2025-01-15",
  "store_id": "happy-bento",
  "store_name": "幸福便當",
  "status": "open",
  "set_by": "管理員",
  "set_at": "2025-01-15T08:00:00"
}
```

**system/prompts/jiaba.json:**
```json
{
  "name": "jiaba",
  "role": "午餐訂便當助手",
  "system_prompt": "你是 jiaba，一個友善的午餐訂便當助手...",
  "greeting": "嗨！我是 jiaba，今天想吃什麼呢？",
  "capabilities": ["查看菜單", "建立訂單", "查詢訂單歷史"]
}
```

**stores/{store-id}/info.json:**
```json
{
  "id": "happy-bento",
  "name": "幸福便當",
  "phone": "02-1234-5678",
  "address": "台北市中正區...",
  "active": true,
  "created_at": "2025-01-15T00:00:00"
}
```

**stores/{store-id}/menu.json:**
```json
{
  "store_id": "happy-bento",
  "updated_at": "2025-01-15T10:00:00",
  "categories": [
    {
      "name": "便當類",
      "items": [
        {
          "id": "chicken-leg",
          "name": "雞腿便當",
          "price": 85,
          "description": "酥脆雞腿配三樣配菜",
          "image": "images/chicken-leg.jpg",
          "available": true
        },
        {
          "id": "pork-chop",
          "name": "排骨便當",
          "price": 80,
          "description": "香酥排骨配三樣配菜",
          "image": null,
          "available": true
        }
      ]
    },
    {
      "name": "湯品",
      "items": [
        {
          "id": "miso-soup",
          "name": "味噌湯",
          "price": 20,
          "description": null,
          "image": null,
          "available": true
        }
      ]
    }
  ]
}
```

**users/{username}/profile.json:**
```json
{
  "username": "小明",
  "created_at": "2025-01-15T10:00:00",
  "preferences": {
    "default_store": "happy-bento",
    "notes": "不吃辣"
  }
}
```

**users/{username}/orders/{date}.json:**
```json
{
  "date": "2025-01-15",
  "username": "小明",
  "store_id": "happy-bento",
  "store_name": "幸福便當",
  "items": [
    {
      "id": "chicken-leg",
      "name": "雞腿便當",
      "price": 85,
      "quantity": 1,
      "note": "飯少一點"
    }
  ],
  "total": 85,
  "status": "confirmed",
  "created_at": "2025-01-15T09:30:00"
}
```

**orders/{date}/summary.json:**
```json
{
  "date": "2025-01-15",
  "store_id": "happy-bento",
  "store_name": "幸福便當",
  "orders": [
    {
      "username": "小明",
      "items": [{"name": "雞腿便當", "quantity": 1, "price": 85}],
      "total": 85
    },
    {
      "username": "小華",
      "items": [{"name": "排骨便當", "quantity": 2, "price": 160}],
      "total": 160
    }
  ],
  "item_summary": [
    {"name": "雞腿便當", "quantity": 1},
    {"name": "排骨便當", "quantity": 2}
  ],
  "grand_total": 245,
  "updated_at": "2025-01-15T10:30:00"
}
```

**orders/{date}/payments.json:**
```json
{
  "date": "2025-01-15",
  "records": [
    {
      "username": "小明",
      "amount": 85,
      "paid": true,
      "paid_at": "2025-01-15T12:00:00",
      "note": null
    },
    {
      "username": "小華",
      "amount": 160,
      "paid": false,
      "paid_at": null,
      "note": "說明天給"
    }
  ],
  "total_collected": 85,
  "total_pending": 160
}
```

### 路由設計

| 路徑 | 說明 |
|------|------|
| `/` | 今日看板（首頁） |
| `/order` | AI 對話訂餐頁 |
| `/manager` | AI 對話管理頁 |

### 頁面設計

**首頁 `/` - 今日看板**

大畫面清楚顯示：
- 今日店家名稱（大標題）
- 訂單列表：每個人訂了什麼、數量、金額
- 品項統計：雞腿便當 x3、排骨便當 x2...
- 總金額（醒目顯示）
- 按鈕：「我要訂便當」→ `/order`
- 按鈕：「管理員」→ `/manager`

即時更新：透過 Socket.IO 自動刷新

**訂餐頁 `/order` - AI 對話訂餐**

- 輸入名稱（localStorage 自動填入）
- 與 jiaba AI 對話點餐
- 可查看菜單、詢問推薦、下訂單
- 訂單完成後自動更新首頁看板

**管理頁 `/manager` - AI 對話管理**

- 簡單密碼驗證進入
- 與 jiaba AI 對話進行管理操作：
  - 上傳/編輯菜單（圖片、品項、價格）
  - 設定今日店家
  - 新增/編輯店家資訊（名稱、電話、說明）
  - 查看/管理訂單
  - 標記付款狀態
  - 管理使用者

### AI Agent 整合方式（Claude CLI）

使用 Claude CLI 而非 API，透過 subprocess 執行命令，CLI 已登入不需管理 API key。

**Session 管理規則：**
- 每個使用者 + 每天 = 一個獨立 session
- Session ID 格式：`{username}-{date}`（如：`小明-2025-01-15`）
- 同一天內使用 `claude -r [sessionId]` 繼續對話
- 隔天或換名稱 = 建立新 session
- Session ID 儲存在 `data/users/{username}/sessions/{date}.txt`

**前端名稱暫存：**
- 使用者輸入名稱後存入 localStorage
- 下次開啟自動填入，不需重複輸入
- 使用者可手動切換名稱（視為不同使用者）

**執行方式：**
```python
import subprocess
from pathlib import Path
from datetime import date

def get_or_create_session(username: str) -> str:
    """取得或建立今日 session"""
    today = date.today().isoformat()
    session_file = Path(f"data/users/{username}/sessions/{today}.txt")

    if session_file.exists():
        return session_file.read_text().strip()

    # 新 session，先呼叫一次建立
    return None

def call_jiaba(username: str, user_message: str, context: dict) -> dict:
    """呼叫 jiaba AI Agent"""
    session_id = get_or_create_session(username)
    system_prompt = load_system_prompt()

    cmd = ["claude", "-p", "--output-format", "json"]

    if session_id:
        # 繼續既有 session
        cmd.extend(["--resume", session_id])
    else:
        # 新 session，附加系統提示詞
        cmd.extend(["--system-prompt", system_prompt])

    # 注入上下文到訊息中
    context_str = json.dumps(context, ensure_ascii=False, indent=2)
    full_message = f"[上下文]\n{context_str}\n\n[使用者訊息]\n{user_message}"

    cmd.append(full_message)

    result = subprocess.run(cmd, capture_output=True, text=True)

    # 儲存 session ID（從輸出解析或用 --session-id 指定）
    save_session_id(username, result)

    return json.loads(result.stdout)
```

**AI 回應格式（JSON）：**
```json
{
  "message": "好的，幫你點了雞腿便當！",
  "action": {
    "type": "create_order",
    "data": {
      "store_id": "happy-bento",
      "items": [{"id": "chicken-leg", "quantity": 1}]
    }
  }
}
```

**後端處理流程：**
1. 前端發送使用者名稱與訊息
2. 後端查詢該使用者今日是否有 session
3. 有 → resume，無 → 建立新 session
4. 組合上下文呼叫 Claude CLI
5. 解析 AI 回應，執行對應動作
6. 透過 Socket.IO 廣播事件
7. 回傳 AI 訊息給前端

**AI 可請求的動作：**

訂餐相關：
- `create_order` - 建立訂單
- `update_order` - 修改訂單
- `cancel_order` - 取消訂單
- `query_menu` - 查詢菜單
- `query_history` - 查詢歷史訂單

管理相關：
- `set_today_store` - 設定今日店家
- `create_store` - 新增店家
- `update_store` - 更新店家資訊
- `update_menu` - 更新菜單內容
- `upload_image` - 上傳菜品圖片
- `mark_paid` - 標記已付款
- `query_payments` - 查詢付款狀態
- `query_all_orders` - 查詢所有訂單

### 即時通知設計（Socket.IO）

使用 python-socketio 實現即時通知，所有連線的使用者都能收到訂餐動態。

**事件類型：**

| 事件名稱 | 觸發時機 | 資料內容 |
|----------|----------|----------|
| `order_created` | 新訂單建立 | `{username, store_name, items, total}` |
| `order_updated` | 訂單修改 | `{username, store_name, items, total, action}` |
| `order_cancelled` | 訂單取消 | `{username, store_name}` |

**前端接收範例：**
```javascript
socket.on('order_created', (data) => {
  // 顯示通知：「小明 訂了 幸福便當 $85」
  showNotification(`${data.username} 訂了 ${data.store_name} $${data.total}`);
});
```

**後端發送（AI Tool）：**
```python
# AI 完成訂單後呼叫
broadcast_event('order_created', {
  'username': '小明',
  'store_name': '幸福便當',
  'items': [{'name': '雞腿便當', 'quantity': 1}],
  'total': 85
})
```

**連線架構：**
```
使用者 A (訂餐頁) ──┐
使用者 B (訂餐頁) ──┼── Socket.IO Server ── 廣播事件
管理員   (後台)   ──┘
```

### 團體訂餐看板

所有使用者都能看到當日團體訂單的即時狀態：

**看板顯示內容：**
- 今日選擇的店家
- 每個人的訂單項目與金額
- 品項統計（如：雞腿便當 x3、排骨便當 x2）
- 總金額

**資料來源：** `data/orders/{date}/summary.json`

**即時更新：** 當有人訂餐/修改/取消時，透過 Socket.IO 推送更新，前端自動刷新看板

## Risks / Trade-offs

| 風險 | 緩解措施 |
|------|----------|
| JSON 格式錯誤 | AI 寫入前驗證 JSON 格式 |
| 同時寫入衝突 | 內部工具使用者少，風險低 |

## Open Questions
- AI 系統提示詞要多細緻？
- 是否需要訂單狀態流程（如：pending → confirmed → completed）？
