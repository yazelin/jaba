# jaba (呷爸) - 精簡專案規格

## 專案定義

**呷爸**是一個 AI 驅動的團隊午餐訂餐系統，使用者透過自然語言對話完成訂餐。

---

## 技術棧

| 層級 | 技術 |
|------|------|
| 後端 | Python 3.12 + FastAPI + Socket.IO |
| 前端 | 純 HTML/CSS/JavaScript |
| 資料 | JSON 檔案（無資料庫） |
| AI | Claude CLI / Gemini CLI |
| 套件 | uv |

---

## 核心架構

```
jaba/
├── main.py                 # FastAPI 入口 + Socket.IO
├── app/
│   ├── ai.py               # AI 整合（call_ai, build_context, execute_actions）
│   ├── data.py             # 資料 CRUD
│   └── providers/          # CLI Provider 抽象
│       ├── __init__.py     # BaseProvider + 工廠
│       ├── claude.py
│       └── gemini.py
├── data/
│   ├── system/             # config.json, today.json, ai_config.json, prompts/
│   ├── stores/{id}/        # info.json, menu.json
│   ├── users/{name}/       # profile.json, orders/, chat_history/
│   ├── orders/{date}/      # summary.json, payments.json
│   └── chat/               # {date}.json
├── templates/              # index.html, order.html, manager.html
└── static/                 # css/, images/
```

---

## 資料結構

### 店家菜單 (`stores/{id}/menu.json`)
```json
{
  "store_id": "coco",
  "categories": [{
    "name": "飲品",
    "items": [{
      "id": "item-1",
      "name": "珍珠奶茶",
      "price": 50,
      "variants": [{"name": "M", "price": 50}, {"name": "L", "price": 60}],
      "promo": {"type": "buy_one_get_one", "label": "買一送一"}
    }]
  }]
}
```

**促銷類型**: `buy_one_get_one` | `second_discount` | `time_limited`

### 訂單 (`users/{name}/orders/{id}.json`)
```json
{
  "order_id": "2025-12-08-123456",
  "username": "小明",
  "store_id": "coco",
  "items": [{
    "name": "珍珠奶茶", "price": 50, "size": "L",
    "quantity": 2, "calories": 400,
    "promo_type": "buy_one_get_one", "discount": 50
  }],
  "total": 50,
  "total_calories": 800
}
```

### 付款 (`orders/{date}/payments.json`)
```json
{
  "records": [{
    "username": "小明",
    "amount": 50,
    "paid": false,
    "paid_amount": 0,
    "note": null
  }]
}
```

### 使用者偏好 (`users/{name}/profile.json`)
```json
{
  "username": "小明",
  "preferences": {
    "preferred_name": "阿明",
    "dietary_restrictions": ["不吃辣"],
    "allergies": []
  }
}
```

---

## API 端點

### 頁面
| 路徑 | 說明 |
|------|------|
| `/` | 今日看板 |
| `/order` | 訂餐頁（三欄：菜單/對話/訂單） |
| `/manager` | 管理頁（三欄：店家/對話/狀態） |

### 核心 API
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/api/today` | 今日店家與訂單 |
| GET | `/api/stores` | 啟用店家列表 |
| GET | `/api/menu/{id}` | 店家菜單 |
| POST | `/api/chat` | AI 對話 `{username, message, is_manager}` |
| POST | `/api/recognize-menu` | AI 菜單辨識 `{store_id, image_base64}` |
| POST | `/api/save-menu` | 儲存菜單（支援差異模式） |
| POST | `/api/mark-paid` | 標記付款 |

### Socket.IO 事件
`order_created` | `order_updated` | `order_cancelled` | `store_changed` | `payment_updated` | `chat_message`

---

## AI 整合

### 訊息組合（四層架構）
```
Layer 4: 當前訊息（使用者輸入）
Layer 3: 對話歷史（最近 20 條）
Layer 2: 動態上下文（JSON：店家、菜單、偏好、訂單）
Layer 1: 系統提示詞（user_prompt.md / manager_prompt.md）
         ↓
    AI 回應: {"message": "...", "actions": [...]}
```

### AI 動作類型
| 動作 | 說明 |
|------|------|
| `create_order` | 建立訂單 |
| `remove_item` | 移除品項 |
| `cancel_order` | 取消訂單 |
| `set_today_store` | 設定今日店家 |
| `add_today_store` | 新增今日店家 |
| `mark_paid` | 標記付款 |
| `update_user_profile` | 更新使用者偏好 |

### 呷爸個性
- 親切可愛、簡潔自然
- 使用「我們」營造參與感
- 稱呼優先用 `preferred_name`
- 估算卡路里、適時健康建議

---

## 業務邏輯

### 促銷計價
| 類型 | 規則 |
|------|------|
| 買一送一 | 2杯收1杯價（3杯=2杯價） |
| 第二杯折扣 | 第2,4,6杯享折扣價 |
| 限時特價 | 直接使用特價 |

### 付款狀態
| 情境 | paid | note |
|------|------|------|
| 未付款 | false | - |
| 已付款 | true | - |
| 金額增加 | false | "待補 $X" |
| 金額減少 | true | "待退 $X" |

### 權限
- 一般用戶：只能取消自己訂單
- 管理員：可取消任何訂單

---

## Provider 模組

```python
class BaseProvider(ABC):
    def build_chat_command(model, prompt, system_prompt) -> CommandResult
    def build_menu_command(model, prompt, image_path) -> CommandResult
    def parse_response(stdout, stderr, return_code) -> dict
```

- **ClaudeProvider**: `claude -p <prompt> --model <model> --system-prompt <prompt>`
- **GeminiProvider**: `gemini -m <model> <prompt>` (系統提示併入 prompt)

---

## 設定檔

### ai_config.json
```json
{
  "chat": {"provider": "claude", "model": "haiku"},
  "menu_recognition": {"provider": "claude", "model": "sonnet"}
}
```

### config.json
```json
{
  "admin_password": "9898",
  "server_port": 8098
}
```

---

## 啟動

```bash
uv sync
uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8098
```

---

## 關鍵功能摘要

1. **AI 對話訂餐** - 自然語言 → actions 陣列 → 自動執行
2. **菜單辨識** - 圖片上傳 → AI Vision → 差異預覽（綠/黃/紅）→ 選擇性套用
3. **即時同步** - Socket.IO 廣播所有訂單/付款變更
4. **促銷計價** - 自動套用買一送一、第二杯折扣
5. **付款追蹤** - 智慧狀態更新（待補/待退）
6. **偏好記錄** - AI 自動記住稱呼與飲食限制
