# jaba (呷爸) - 完整專案規格

> 本文件旨在提供完整的專案規格，讓 AI 能夠根據此規格重建完整的 jaba 專案。

---

## 1. 專案概述

### 1.1 專案資訊
- **專案名稱**: jaba（呷爸）
- **類型**: AI 驅動的午餐訂便當系統
- **目標使用者**: 團隊內部成員
- **授權**: MIT License

### 1.2 核心概念
呷爸是一個專為團隊設計的午餐訂餐系統，透過 AI 對話介面讓訂餐變得簡單直覺。使用者只需用自然語言告訴呷爸想吃什麼，系統就會自動處理訂單。

### 1.3 主要功能

**使用者功能**:
- AI 對話訂餐（自然語言下單）
- 快速點餐（點擊菜單直接加入）
- 多店家選擇
- 訂單修改（新增、移除品項）
- 特價優惠自動套用（買一送一、第二杯折扣、限時特價）
- 卡路里估算
- 個人偏好記錄

**管理員功能**:
- 店家管理（新增、編輯、啟用/停用）
- 菜單辨識（上傳圖片 AI 自動辨識）
- 差異預覽與選擇性套用
- 今日店家設定（單一或多家）
- 訂單總覽與品項統計
- 付款追蹤與退款處理

**系統功能**:
- Socket.IO 即時同步
- 瀏覽器通知
- 團體聊天室
- Session 管理

---

## 2. 技術架構

### 2.1 技術棧

| 組件 | 技術 |
|------|------|
| 後端框架 | Python 3.12 + FastAPI + Socket.IO (ASGI) |
| 前端 | 純 HTML/CSS/JavaScript（無框架） |
| 資料存儲 | JSON 檔案系統（無資料庫） |
| AI 整合 | Claude CLI / Gemini CLI（Provider 模組化架構） |
| 套件管理 | uv |
| 即時通訊 | python-socketio |

### 2.2 架構分層

```
┌─────────────────────────────────────────────────┐
│         前端層 (Frontend)                        │
│  HTML/CSS/JS 三頁面 + Socket.IO 實時同步        │
├─────────────────────────────────────────────────┤
│         API 層 (Routing & Events)               │
│  FastAPI 路由 + Socket.IO 廣播事件              │
├─────────────────────────────────────────────────┤
│      應用邏輯層 (Business Logic)                │
│  ├─ AI 整合 (app/ai.py)                        │
│  └─ 資料操作 (app/data.py)                     │
├─────────────────────────────────────────────────┤
│      提供者層 (Provider Abstraction)            │
│  ├─ Claude CLI Provider                        │
│  └─ Gemini CLI Provider                        │
├─────────────────────────────────────────────────┤
│      資料層 (Data Layer)                        │
│  JSON 檔案系統 - data/                          │
└─────────────────────────────────────────────────┘
```

### 2.3 設計原則
- 簡單直接的單體架構
- FastAPI 路由直接處理業務邏輯
- 檔案儲存使用結構化的目錄組織
- 保持最少的抽象層，優先可讀性
- Python 程式碼遵循 PEP 8 規範
- 使用 type hints 進行型別標註
- 變數和函數使用 snake_case，類別使用 PascalCase

---

## 3. 目錄結構

```
jaba/
├── main.py                     # FastAPI 應用程式入口
├── pyproject.toml              # Python 專案設定與依賴
├── uv.lock                     # 依賴鎖定檔
├── app/
│   ├── __init__.py
│   ├── ai.py                   # AI 整合主入口（1,400 行）
│   ├── data.py                 # 資料存取模組（660 行）
│   └── providers/              # CLI Provider 模組
│       ├── __init__.py         # BaseProvider 抽象類別與工廠
│       ├── claude.py           # Claude CLI 實作
│       └── gemini.py           # Gemini CLI 實作
├── data/
│   ├── system/                 # 系統設定
│   │   ├── config.json         # 伺服器設定
│   │   ├── today.json          # 今日店家資訊
│   │   ├── ai_config.json      # AI 模型設定
│   │   └── prompts/            # AI 提示詞
│   │       ├── user_prompt.md
│   │       ├── manager_prompt.md
│   │       └── menu_recognition_prompt.md
│   ├── stores/                 # 店家資料
│   │   └── {store_id}/
│   │       ├── info.json       # 店家資訊
│   │       ├── menu.json       # 菜單
│   │       └── images/         # 菜品圖片
│   ├── users/                  # 使用者資料
│   │   └── {username}/
│   │       ├── profile.json    # 使用者偏好
│   │       ├── orders/         # 個人訂單
│   │       │   └── {date}-{timestamp}.json
│   │       ├── chat_history/   # 對話歷史
│   │       │   └── {date}-{mode}.json
│   │       └── sessions/       # 會話資訊
│   ├── orders/                 # 每日訂單彙整
│   │   └── {date}/
│   │       ├── summary.json    # 訂單摘要
│   │       └── payments.json   # 付款記錄
│   └── chat/                   # 團體聊天記錄
│       └── {date}.json
├── templates/                  # HTML 頁面
│   ├── index.html              # 看板頁
│   ├── order.html              # 訂餐頁
│   └── manager.html            # 管理頁
├── static/                     # 靜態資源
│   ├── css/
│   │   └── style.css
│   └── images/
│       └── jaba.png            # 呷爸頭像
├── docs/                       # 文件
├── docs-ai/                    # AI 知識庫
│   ├── claude-cli.md
│   ├── gemini-cli.md
│   └── menu-recognition-design.md
└── openspec/                   # OpenSpec 規格
    ├── AGENTS.md
    ├── project.md
    ├── specs/
    └── changes/
```

---

## 4. 資料模型定義

### 4.1 系統設定

#### config.json
```json
{
  "admin_password": "9898",
  "server_port": 8098
}
```

#### today.json
```json
{
  "date": "2025-12-08",
  "stores": [
    {
      "store_id": "coco",
      "store_name": "CoCo都可茶飲",
      "status": "open",
      "set_by": "管理員",
      "set_at": "2025-12-08T11:43:13.624177"
    }
  ]
}
```

#### ai_config.json
```json
{
  "chat": {
    "provider": "claude",
    "model": "haiku"
  },
  "menu_recognition": {
    "provider": "claude",
    "model": "sonnet"
  }
}
```

### 4.2 店家資料

#### stores/{store_id}/info.json
```json
{
  "id": "coco",
  "name": "CoCo都可茶飲",
  "phone": "02 3456789",
  "address": "",
  "description": "",
  "note": "",
  "active": true,
  "created_at": "2025-12-03T11:31:11.864060"
}
```

#### stores/{store_id}/menu.json
```json
{
  "store_id": "coco",
  "updated_at": "2025-12-08T13:08:09.157922",
  "categories": [
    {
      "name": "無咖啡因",
      "items": [
        {
          "id": "item-0-0",
          "name": "日安六條大麥",
          "price": 35,
          "description": "限量優惠",
          "available": true,
          "variants": [
            {"name": "M", "price": 35},
            {"name": "L", "price": 40}
          ],
          "promo": {
            "type": "second_discount",
            "label": "第二杯0元",
            "second_price": 0
          }
        }
      ]
    }
  ]
}
```

**促銷類型 (promo.type)**:
- `buy_one_get_one`: 買一送一
- `second_discount`: 第二杯折扣
  - `second_price`: 固定價格
  - `second_ratio`: 折數（如 0.5 為半價）
- `time_limited`: 限時特價
  - `original_price`: 原價
  - `promo_price`: 特價

### 4.3 使用者資料

#### users/{username}/profile.json
```json
{
  "username": "亞澤",
  "created_at": "2025-12-03T...",
  "preferences": {
    "preferred_name": "阿澤",
    "dietary_restrictions": ["不吃辣"],
    "allergies": ["海鮮"],
    "notes": ""
  }
}
```

#### users/{username}/orders/{order_id}.json
```json
{
  "order_id": "2025-12-08-1153052965",
  "date": "2025-12-08",
  "username": "亞澤",
  "store_id": "coco",
  "store_name": "CoCo都可茶飲",
  "items": [
    {
      "id": "item-2",
      "name": "小湯圓奶茶",
      "price": 50,
      "quantity": 2,
      "size": "L",
      "note": "無糖去冰",
      "calories": 180,
      "subtotal": 50,
      "promo_type": "second_discount",
      "promo_label": "第二杯0元",
      "discount": 50
    }
  ],
  "total": 50,
  "total_calories": 360,
  "status": "confirmed",
  "created_at": "2025-12-08T11:53:05.296960"
}
```

#### users/{username}/chat_history/{date}-{mode}.json
```json
{
  "date": "2025-12-08",
  "mode": "order",
  "messages": [
    {
      "role": "user",
      "content": "我要點雞腿便當",
      "timestamp": "2025-12-08T11:43:05.296960"
    },
    {
      "role": "assistant",
      "content": "好的，已幫你點了雞腿便當...",
      "timestamp": "2025-12-08T11:43:10.296960"
    }
  ],
  "created_at": "2025-12-08T11:43:05.296960"
}
```

### 4.4 訂單與付款

#### orders/{date}/summary.json
```json
{
  "date": "2025-12-08",
  "store_id": "coco",
  "store_name": "CoCo都可茶飲",
  "orders": [
    {
      "order_id": "...",
      "username": "亞澤",
      "items": [...],
      "total": 50
    }
  ],
  "item_summary": [
    {"name": "小湯圓奶茶", "quantity": 2}
  ],
  "grand_total": 50,
  "updated_at": "2025-12-08T11:53:05.296960"
}
```

#### orders/{date}/payments.json
```json
{
  "date": "2025-12-08",
  "records": [
    {
      "username": "亞澤",
      "amount": 50,
      "paid": false,
      "paid_amount": 0,
      "paid_at": null,
      "note": null
    }
  ],
  "total_collected": 0,
  "total_pending": 50
}
```

### 4.5 聊天記錄

#### chat/{date}.json
```json
{
  "date": "2025-12-08",
  "messages": [
    {
      "id": "msg-123",
      "username": "小明",
      "content": "今天的便當好吃",
      "timestamp": "2025-12-08T12:30:00"
    }
  ]
}
```

---

## 5. API 端點規格

### 5.1 頁面路由

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 今日看板首頁 |
| GET | `/order` | 訂餐頁面 |
| GET | `/manager` | 管理頁面 |

### 5.2 公開 API

**查詢類**:
| 方法 | 路徑 | 說明 | 回應 |
|------|------|------|------|
| GET | `/api/today` | 取得今日店家與訂單資訊 | `{date, stores[], orders[], grand_total}` |
| GET | `/api/stores` | 取得啟用的店家列表 | `[{id, name, phone}]` |
| GET | `/api/menu/{store_id}` | 取得店家菜單 | `{store_id, categories[]}` |
| GET | `/api/payments` | 取得今日付款狀態 | `{records[], total_collected, total_pending}` |
| GET | `/api/chat/messages` | 取得今日聊天記錄 | `{messages[]}` |

**操作類**:
| 方法 | 路徑 | 說明 | 請求參數 |
|------|------|------|------|
| POST | `/api/chat` | 與 AI 對話 | `{username, message, is_manager}` |
| POST | `/api/chat/send` | 發送聊天訊息 | `{username, message}` |
| POST | `/api/session/reset` | 重置對話歷史 | `{username, is_manager}` |

### 5.3 管理 API

| 方法 | 路徑 | 說明 | 請求參數 |
|------|------|------|------|
| POST | `/api/verify-admin` | 驗證管理員密碼 | `{password}` |
| GET | `/api/stores/all` | 取得所有店家與菜單 | - |
| POST | `/api/recognize-menu` | AI 辨識菜單圖片 | `{store_id, image_base64}` |
| POST | `/api/save-menu` | 儲存菜單 | `{store_id, menu, diff_mode?, apply_items?, remove_items?}` |
| POST | `/api/mark-paid` | 標記已付款 | `{username}` |
| POST | `/api/refund` | 標記已退款 | `{username}` |
| POST | `/api/store/{store_id}/toggle` | 切換店家啟用狀態 | - |
| POST | `/api/upload-image/{store_id}` | 上傳菜品圖片 | `FormData` |

### 5.4 Socket.IO 事件

| 事件名稱 | 方向 | 說明 | 資料格式 |
|---------|------|------|---------|
| `connect` | 雙向 | 客戶端連接 | - |
| `disconnect` | 雙向 | 客戶端斷線 | - |
| `order_created` | Server→Client | 新訂單建立 | `{username, store_name, items[], total}` |
| `order_updated` | Server→Client | 訂單更新 | `{username, items[], total}` |
| `order_cancelled` | Server→Client | 訂單取消 | `{username, order_id}` |
| `orders_cleared` | Server→Client | 訂單清除 | `{date}` |
| `store_changed` | Server→Client | 今日店家變更 | `{stores[]}` |
| `payment_updated` | Server→Client | 付款狀態更新 | `{username, paid, amount}` |
| `chat_message` | Server→Client | 新聊天訊息 | `{username, content, timestamp}` |

---

## 6. 核心模組規格

### 6.1 AI 整合模組 (`app/ai.py`)

#### 主要函數

```python
def get_system_prompt(is_manager: bool = False) -> str:
    """
    載入系統提示詞
    - is_manager=False: 載入 user_prompt.md
    - is_manager=True: 載入 manager_prompt.md
    """

def build_context(username: str, is_manager: bool = False) -> dict:
    """
    建立動態 AI 上下文

    共用欄位:
    - today: 日期字串
    - today_stores: 今日店家陣列
    - username: 使用者名稱
    - preferred_name: 偏好稱呼
    - menus: 今日店家的完整菜單

    使用者模式額外欄位:
    - user_profile: 使用者偏好
    - current_orders: 現有訂單

    管理員模式額外欄位:
    - available_stores: 所有啟用店家
    - today_summary: 今日訂單彙整
    - payments: 付款記錄
    - recent_store_history: 近 7 天店家紀錄
    """

async def call_ai(username: str, message: str, is_manager: bool = False) -> dict:
    """
    呼叫 AI CLI 並處理回應

    流程:
    1. 載入系統提示詞
    2. 建立動態上下文
    3. 取得對話歷史（最多 20 條）
    4. 組合完整訊息
    5. 呼叫 Provider 執行 CLI
    6. 解析 JSON 回應
    7. 執行 actions
    8. 儲存對話歷史

    回傳: {message, actions[], error?}
    """

async def recognize_menu_image(store_id: str, image_base64: str) -> dict:
    """
    使用 AI Vision 辨識菜單圖片

    流程:
    1. 將 base64 寫入暫存 JPG
    2. 呼叫 AI 辨識
    3. 與現有菜單比對差異

    回傳: {recognized_menu, diff, existing_menu}
    """

def compare_menus(existing: dict, recognized: dict) -> dict:
    """
    比對菜單差異

    回傳: {
        added: [],      # 新增品項（綠色）
        modified: [],   # 修改品項（黃色）
        removed: [],    # 可刪除品項（紅色）
        unchanged: []   # 未變更品項
    }
    """

async def execute_actions(actions: list, username: str, is_manager: bool) -> list:
    """
    執行 AI 回傳的動作陣列
    """

def calculate_promo_price(item: dict, quantity: int) -> tuple[int, int]:
    """
    計算促銷價格

    回傳: (實際金額, 折扣金額)

    計價邏輯:
    - buy_one_get_one: 2杯$50 = $50, 3杯 = $100
    - second_discount: 第2,4,6杯享折扣
    - time_limited: 使用 promo_price
    """
```

#### AI 動作類型

| 動作類型 | 參數 | 說明 |
|---------|------|------|
| `create_order` | `{store_id, items[]}` | 建立新訂單 |
| `update_order` | `{order_id, items[]}` | 更新訂單 |
| `cancel_order` | `{order_id}` 或 `{username}` | 取消訂單 |
| `remove_item` | `{item_name, quantity?}` | 從訂單移除品項 |
| `set_today_store` | `{store_id, store_name}` | 設定今日店家（單一） |
| `add_today_store` | `{store_id, store_name}` | 新增今日店家（多店家） |
| `create_store` | `{id, name, phone?}` | 建立新店家 |
| `update_store` | `{store_id, fields}` | 編輯店家資訊 |
| `update_menu` | `{store_id, categories}` | 更新菜單 |
| `mark_paid` | `{username}` | 標記已付款 |
| `mark_refunded` | `{username}` | 確認已退款 |
| `clear_all_orders` | `{date?}` | 清除所有訂單 |
| `update_user_profile` | `{preferred_name?, dietary_restrictions?, allergies?}` | 更新使用者偏好 |

#### AI 訊息組合架構

```
┌─────────────────────────────────────────────────┐
│  Layer 4 (Top): 當前訊息 (Current Message)      │
│     └─ 使用者輸入的文字                         │
├─────────────────────────────────────────────────┤
│  Layer 3: 對話歷史 (Chat History)               │
│     └─ 最近 20 條對話記錄                       │
├─────────────────────────────────────────────────┤
│  Layer 2: 動態上下文 (Dynamic Context)          │
│     └─ JSON: 今日店家、菜單、偏好、訂單         │
├─────────────────────────────────────────────────┤
│  Layer 1 (Base): 系統提示詞 (System Prompt)     │
│     └─ user_prompt.md 或 manager_prompt.md      │
└─────────────────────────────────────────────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │    AI Response      │
          │  {message, actions[]}│
          └─────────────────────┘
```

### 6.2 資料存取模組 (`app/data.py`)

#### 系統設定

```python
def get_config() -> dict:
    """取得系統配置"""

def get_today_info() -> dict:
    """取得今日店家與訂單資訊"""

def set_today_store(store_id: str, store_name: str, set_by: str) -> None:
    """設定單一今日店家（清除其他）"""

def add_today_store(store_id: str, store_name: str, set_by: str) -> None:
    """新增今日店家（多店家模式）"""

def get_ai_config() -> dict:
    """取得 AI 模型配置"""

def get_jaba_prompt(prompt_type: str) -> str:
    """載入系統提示詞 (user/manager/menu_recognition)"""
```

#### 店家管理

```python
def get_stores() -> list:
    """取得所有店家"""

def get_active_stores() -> list:
    """取得啟用的店家列表"""

def get_store(store_id: str) -> dict:
    """取得單一店家資訊"""

def save_store(store_id: str, info: dict) -> None:
    """儲存店家資訊"""

def toggle_store_active(store_id: str) -> bool:
    """切換店家啟用狀態，回傳新狀態"""

def get_menu(store_id: str) -> dict:
    """取得菜單"""

def save_menu(store_id: str, menu: dict) -> None:
    """儲存菜單"""
```

#### 使用者管理

```python
def ensure_user(username: str) -> None:
    """確保使用者目錄與 profile 存在"""

def get_user_profile(username: str) -> dict:
    """取得使用者偏好"""

def update_user_profile(username: str, updates: dict) -> None:
    """更新使用者偏好（合併更新）"""
```

#### 訂單管理

```python
def save_user_order(username: str, order: dict) -> str:
    """儲存使用者訂單，回傳 order_id"""

def get_user_orders(username: str, date: str = None) -> list:
    """取得使用者訂單"""

def delete_user_order(username: str, order_id: str) -> bool:
    """刪除訂單"""

def update_daily_summary_with_order(date: str, order: dict) -> None:
    """更新每日訂單彙整"""

def get_daily_summary(date: str) -> dict:
    """取得每日訂單摘要"""

def get_payments(date: str = None) -> dict:
    """取得付款記錄"""

def save_payments(date: str, payments: dict) -> None:
    """儲存付款記錄"""

def update_payment_status(username: str, amount: int, paid: bool, paid_amount: int, note: str = None) -> None:
    """更新付款狀態"""
```

#### 對話歷史管理

```python
def get_ai_chat_history(username: str, is_manager: bool, limit: int = 20) -> list:
    """取得對話歷史（最多 limit 條）"""

def append_ai_chat_history(username: str, is_manager: bool, role: str, content: str) -> None:
    """新增對話記錄"""

def clear_ai_chat_history(username: str, is_manager: bool) -> None:
    """清除對話歷史"""
```

#### 聊天功能

```python
def save_chat_message(username: str, content: str) -> dict:
    """儲存聊天訊息，回傳訊息物件"""

def get_chat_messages(date: str = None) -> list:
    """取得聊天記錄"""
```

### 6.3 Provider 模組 (`app/providers/`)

#### BaseProvider 抽象介面

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CommandResult:
    command: list[str]
    env: dict = None

class BaseProvider(ABC):
    @abstractmethod
    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_id: str = None
    ) -> CommandResult:
        """建構對話命令"""

    @abstractmethod
    def build_menu_command(
        self,
        model: str,
        prompt: str,
        image_path: str
    ) -> CommandResult:
        """建構菜單辨識命令"""

    @abstractmethod
    def parse_response(
        self,
        stdout: str,
        stderr: str,
        return_code: int
    ) -> dict:
        """解析 CLI 回應"""

    @abstractmethod
    async def get_session_info_after_call(self, stdout: str) -> dict:
        """取得 session 資訊（供後續對話使用）"""

    @abstractmethod
    async def delete_session(self, session_id: str) -> None:
        """刪除 session"""

def get_provider(provider_name: str) -> BaseProvider:
    """Provider 工廠函數"""
```

#### ClaudeProvider 實作

```python
class ClaudeProvider(BaseProvider):
    def build_chat_command(self, model, prompt, system_prompt, session_id=None):
        cmd = ["claude", "-p", prompt, "--model", model]
        if system_prompt:
            cmd.extend(["--system-prompt", system_prompt])
        # 不使用 --resume，歷史由應用管理
        return CommandResult(command=cmd)

    def build_menu_command(self, model, prompt, image_path):
        # 在 prompt 中指示使用 Read 工具讀取圖片
        full_prompt = f"請使用 Read 工具讀取圖片 {image_path}，然後{prompt}"
        cmd = ["claude", "-p", full_prompt, "--model", model,
               "--allowedTools", "Read"]
        return CommandResult(command=cmd)

    def parse_response(self, stdout, stderr, return_code):
        # 清理 markdown code block，解析 JSON
        ...
```

#### GeminiProvider 實作

```python
class GeminiProvider(BaseProvider):
    def build_chat_command(self, model, prompt, system_prompt, session_id=None):
        # 將系統提示併入 prompt 開頭
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        cmd = ["gemini", "-m", model, full_prompt]
        if session_id:
            cmd.extend(["--resume", session_id])
        return CommandResult(command=cmd)

    def build_menu_command(self, model, prompt, image_path):
        cmd = ["gemini", "-m", model, "-y", f"@{image_path}", prompt]
        return CommandResult(command=cmd)
```

---

## 7. 前端頁面規格

### 7.1 今日看板 (`/` - index.html)

**功能**:
- 顯示今日店家資訊（名稱、電話、備註）
- 訂單列表（所有使用者）
- 品項統計（各品項數量）
- 付款狀態追蹤

**Socket.IO 監聽**:
- `order_created`, `order_updated`, `order_cancelled`
- `store_changed`, `payment_updated`

### 7.2 訂餐頁 (`/order` - order.html)

**佈局**: 三欄式
- 左側：今日店家、菜單面板
- 中間：AI 對話區
- 右側：我的訂單、大家的訂單、美食評論區

**功能**:
- 名稱輸入（localStorage 自動填入）
- AI 對話訂餐
- 快速點餐（點擊菜單）
- 訂單顯示（品項、備註、卡路里、金額）
- 美食評論區（預設展開）
- 瀏覽器通知

**響應式**:
- 桌面：三欄並列
- 手機（< 768px）：垂直堆疊，對話框優先

### 7.3 管理頁 (`/manager` - manager.html)

**佈局**: 三欄式
- 左側：店家管理面板
- 中間：AI 對話區
- 右側：今日店家、訂單總覽、付款狀態

**功能**:
- 管理員登入驗證
- 店家列表（啟用/停用切換按鈕）
- 菜單上傳與 AI 辨識
- 差異預覽介面（綠色新增、黃色修改、紅色刪除）
- 菜單編輯（品項、價格、尺寸變體、促銷設定）
- 訂單總覽
- 付款追蹤（確認付款、確認退款按鈕）
- AI 對話管理

---

## 8. 功能需求規格

### 8.1 AI 整合需求

**Claude CLI 整合**:
- 透過 subprocess 執行 `claude -p` 命令
- 使用 `--system-prompt` 傳遞系統提示
- 使用 `--model` 指定模型（haiku/sonnet/opus）
- 非同步執行，不阻塞其他請求

**Session 管理**:
- 每次進入頁面時重置 session
- 對話歷史由應用自行管理（最多 20 條）
- 不依賴 CLI 的 `--resume` 機制

**AI 動作執行**:
- 統一使用 `actions[]` 陣列格式
- 支援多動作同時執行
- 動作執行後廣播 Socket.IO 事件

**呷爸個性設定**:
- 親切可愛的語氣
- 說話簡潔自然、不冗長
- 使用「我們」營造參與感
- 稱呼使用 preferred_name（若有設定）

### 8.2 訂單管理需求

**彈性訂餐**:
- 允許隨時建立訂單，無固定週期
- 訂單永久保留

**訂單操作**:
- 建立訂單：`create_order` 動作
- 移除品項：`remove_item` 動作
- 取消訂單：`cancel_order` 動作
- 一般用戶只能取消自己的訂單

**付款狀態邏輯**:
- 標記已付款：`paid=true`, `paid_amount=amount`, 清除 note
- 金額增加：`paid=false`, 保留 paid_amount, note="待補 $X"
- 金額減少：維持 `paid=true`, note="待退 $X"
- 訂單取消：`amount=0`, note="待退 $X"
- 標記退款：移除記錄或調整 paid_amount

**促銷計價**:
- 買一送一：2杯收1杯價
- 第二杯折扣：第2,4,6杯享折扣
- 限時特價：直接使用特價

### 8.3 菜單管理需求

**多店家支援**:
- 每家店獨立目錄 `data/stores/{store_id}/`
- 支援啟用/停用狀態

**菜單結構**:
- 分類 (categories) → 品項 (items)
- 品項支援尺寸變體 (variants)
- 品項支援促銷設定 (promo)

**菜單辨識**:
- 上傳圖片 AI 自動辨識
- 自動提取尺寸變體
- 自動識別促銷標示
- 差異比對：新增/修改/刪除/未變更
- 選擇性套用變更

### 8.4 使用者管理需求

**使用者識別**:
- 以名字作為唯一識別
- 自動建立新使用者目錄與 profile

**偏好記錄**:
- preferred_name: 希望被稱呼的名字
- dietary_restrictions: 飲食限制
- allergies: 過敏原
- 透過 AI 對話自動記錄

### 8.5 即時通知需求

**Socket.IO 連線**:
- 使用者開啟頁面自動建立連線
- 所有連線者共享訂餐動態

**事件廣播**:
- 訂單建立/修改/取消
- 店家設定變更
- 付款狀態更新
- 聊天訊息

**店家設定通知**:
- 設定店家時自動在聊天室新增系統訊息

---

## 9. 業務邏輯規則

### 9.1 促銷計價邏輯

```python
def calculate_promo_price(item: dict, quantity: int) -> tuple[int, int]:
    """
    回傳 (實際金額, 折扣金額)
    """
    base_price = item.get("price", 0)
    promo = item.get("promo")

    if not promo:
        return base_price * quantity, 0

    promo_type = promo.get("type")

    if promo_type == "buy_one_get_one":
        # 買一送一：每2杯收1杯價
        pairs = quantity // 2
        singles = quantity % 2
        actual = pairs * base_price + singles * base_price
        discount = pairs * base_price
        return actual, discount

    elif promo_type == "second_discount":
        # 第二杯折扣
        second_price = promo.get("second_price", 0)
        pairs = quantity // 2
        singles = quantity % 2
        actual = pairs * (base_price + second_price) + singles * base_price
        discount = pairs * (base_price - second_price)
        return actual, discount

    elif promo_type == "time_limited":
        # 限時特價
        promo_price = promo.get("promo_price", base_price)
        original = promo.get("original_price", base_price)
        actual = promo_price * quantity
        discount = (original - promo_price) * quantity
        return actual, discount

    return base_price * quantity, 0
```

### 9.2 付款狀態更新規則

| 情境 | paid | paid_amount | note |
|------|------|-------------|------|
| 未付款 | false | 0 | null |
| 已付款 | true | amount | null |
| 金額增加（待補） | false | 原paid_amount | "已付 $X，待補 $Y" |
| 金額減少（待退） | true | 原paid_amount | "待退 $X" |
| 訂單取消（待退） | true | 原paid_amount | "待退 $X" |
| 確認退款（無訂單） | 移除記錄 | - | - |
| 確認退款（有訂單） | true | amount | null |

### 9.3 訂單取消權限

| 角色 | 取消自己訂單 | 取消他人訂單 |
|------|-------------|-------------|
| 一般用戶 | 允許 | 拒絕 |
| 管理員 | 允許 | 允許 |

---

## 10. 系統提示詞規格

### 10.1 使用者模式 (`user_prompt.md`)

**角色定位**: 呷爸是一個親切可愛的午餐訂餐助手

**語氣風格**:
- 親切可愛、活潑自然
- 說話簡潔，不冗長
- 使用「我們」代替「你」
- 可使用口語化表達（如「哇係呷爸」）

**稱呼規則**:
- 優先使用 preferred_name
- 沒有設定時使用「我們」
- 不使用性別代稱

**健康提醒**:
- 適時推薦較健康選項
- 估算每道餐點卡路里
- 友善建議，不強制

**可執行動作**:
- create_order, remove_item, cancel_order
- update_user_profile

**回應格式**:
```json
{
  "message": "回應訊息",
  "actions": [
    {"type": "create_order", "data": {...}}
  ]
}
```

### 10.2 管理員模式 (`manager_prompt.md`)

**角色定位**: 店家與訂單管理助手

**功能**:
- 設定今日店家
- 查看訂單統計
- 標記付款狀態
- 店家與菜單管理
- 歷史店家建議（避免連續訂同一家）

**可執行動作**:
- set_today_store, add_today_store
- create_store, update_store, update_menu
- mark_paid, mark_refunded
- clear_all_orders

### 10.3 菜單辨識 (`menu_recognition_prompt.md`)

**輸入**: 菜單圖片

**輸出格式**:
```json
{
  "categories": [
    {
      "name": "分類名稱",
      "items": [
        {
          "name": "品項名稱",
          "price": 50,
          "description": "描述",
          "variants": [
            {"name": "M", "price": 50},
            {"name": "L", "price": 60}
          ],
          "promo": {
            "type": "buy_one_get_one",
            "label": "買一送一"
          }
        }
      ]
    }
  ]
}
```

---

## 11. 依賴套件

### 11.1 pyproject.toml

```toml
[project]
name = "jaba"
version = "0.1.0"
description = "AI 午餐訂便當系統"
requires-python = ">=3.12"
dependencies = [
    "anthropic>=0.75.0",
    "fastapi>=0.123.4",
    "python-multipart>=0.0.20",
    "python-socketio>=5.15.0",
    "uvicorn[standard]>=0.38.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### 11.2 外部工具需求

| 工具 | 用途 | 必要性 |
|------|------|--------|
| Claude CLI | AI 對話與菜單辨識 | 必要（可選 Gemini） |
| Gemini CLI | 替代 AI Provider | 選用 |
| uv | Python 套件管理 | 建議 |

### 11.3 環境變數

```bash
# Claude CLI 需要
export ANTHROPIC_API_KEY="your-api-key"

# 或 Gemini CLI 需要
export GOOGLE_API_KEY="your-api-key"
```

---

## 12. 啟動與執行

### 12.1 安裝

```bash
# 安裝依賴
uv sync

# 或使用 pip
pip install -r requirements.txt
```

### 12.2 啟動伺服器

```bash
# 使用 uv
uv run uvicorn main:socket_app --reload --host 0.0.0.0 --port 8098

# 或直接使用 uvicorn
uvicorn main:socket_app --reload --host 0.0.0.0 --port 8098
```

### 12.3 預設設定

- **伺服器埠口**: 8098
- **管理員密碼**: 9898
- **AI Chat 模型**: claude haiku
- **AI 菜單辨識模型**: claude sonnet

---

## 附錄 A: 主程式入口結構 (main.py)

```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import socketio

# FastAPI 應用
app = FastAPI()

# Socket.IO 伺服器
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# 靜態資源與模板
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Socket.IO 事件處理
@sio.event
async def connect(sid, environ):
    pass

@sio.event
async def disconnect(sid):
    pass

# 頁面路由
@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/order")
async def order_page(request: Request):
    return templates.TemplateResponse("order.html", {"request": request})

@app.get("/manager")
async def manager_page(request: Request):
    return templates.TemplateResponse("manager.html", {"request": request})

# API 路由
@app.get("/api/today")
async def get_today():
    from app.data import get_today_info
    return get_today_info()

@app.post("/api/chat")
async def chat(request: Request):
    from app.ai import call_ai
    data = await request.json()
    return await call_ai(data["username"], data["message"], data.get("is_manager", False))

# ... 其他 API 路由
```

---

## 附錄 B: 完整 API 回應範例

### POST /api/chat

**請求**:
```json
{
  "username": "小明",
  "message": "我要點珍珠奶茶 L 杯",
  "is_manager": false
}
```

**回應**:
```json
{
  "message": "好的！已經幫你點了珍珠奶茶 L 杯 $60，估計熱量約 400 大卡。今天還想加點什麼嗎？",
  "actions": [
    {
      "type": "create_order",
      "data": {
        "store_id": "coco",
        "items": [
          {
            "id": "item-1",
            "name": "珍珠奶茶",
            "price": 60,
            "size": "L",
            "quantity": 1,
            "calories": 400
          }
        ]
      }
    }
  ]
}
```

### POST /api/recognize-menu

**請求**:
```json
{
  "store_id": "coco",
  "image_base64": "data:image/jpeg;base64,..."
}
```

**回應**:
```json
{
  "recognized_menu": {
    "categories": [...]
  },
  "diff": {
    "added": [{"name": "新品項", ...}],
    "modified": [{"name": "修改品項", "changes": {"price": {"old": 40, "new": 45}}}],
    "removed": [{"name": "舊品項", ...}],
    "unchanged": [...]
  },
  "existing_menu": {
    "categories": [...]
  }
}
```

---

*文件版本: 1.0*
*最後更新: 2025-12-08*
