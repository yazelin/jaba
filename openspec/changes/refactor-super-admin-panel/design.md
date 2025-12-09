# Design: refactor-super-admin-panel

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      超級管理員後台 (manager.html)                    │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐  ┌────────────────────────┐ │
│  │   店家管理    │  │    對話區域       │  │      群組訂單管理       │ │
│  │              │  │                  │  │ ┌──────────────────┐  │ │
│  │  - 店家列表   │  │  - AI 對話       │  │ │ 群組選擇: [▼]    │  │ │
│  │  - 上傳菜單   │  │  - 管理指令      │  │ ├──────────────────┤  │ │
│  │  - 啟用/停用  │  │  - 代理點餐      │  │ │ 訂單列表         │  │ │
│  │              │  │                  │  │ │ - 王小明: 雞腿x1  │  │ │
│  │              │  │                  │  │ │ - 李大華: 排骨x1  │  │ │
│  │              │  │                  │  │ ├──────────────────┤  │ │
│  │              │  │                  │  │ │ 付款狀態         │  │ │
│  │              │  │                  │  │ │ - 王小明: 已付   │  │ │
│  │              │  │                  │  │ └──────────────────┘  │ │
│  └──────────────┘  └──────────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Structure

### 1. 使用者資料 (`data/users/{line_user_id}/profile.json`)

```json
{
  "line_user_id": "Uxxxxxxxxxxxxxxxxx",
  "display_name": "王小明",
  "created_at": "2025-12-09T10:00:00",
  "preferences": {
    "dietary_restrictions": ["不吃辣"],
    "allergies": [],
    "drink_preferences": ["無糖", "去冰"],
    "notes": ""
  }
}
```

### 2. 群組訂單 (`data/linebot/sessions/{group_id}.json`)

現有結構維持，增加正式訂單管理：

```json
{
  "group_id": "Cxxxxxxxxxxxxxxxxx",
  "status": "ordering|ended",
  "started_at": "2025-12-09T10:00:00",
  "ended_at": "2025-12-09T12:00:00",
  "orders": [
    {
      "line_user_id": "Uxxxxxxxxxxxxxxxxx",
      "display_name": "王小明",
      "items": [
        {"name": "雞腿便當", "quantity": 1, "price": 85, "subtotal": 85, "note": ""}
      ],
      "total": 85,
      "created_at": "2025-12-09T10:30:00"
    }
  ],
  "payments": {
    "Uxxxxxxxxxxxxxxxxx": {
      "amount": 85,
      "paid": false,
      "paid_amount": 0,
      "paid_at": null,
      "note": ""
    }
  }
}
```

### 3. LINE Bot 白名單 (`data/linebot/whitelist.json`)

```json
{
  "groups": [
    {
      "id": "Cxxxxxxxxxxxxxxxxx",
      "name": "午餐群組",
      "activated_at": "2025-12-09T10:00:00",
      "activated_by_id": "Uxxxxxxxxxxxxxxxxx",
      "activated_by_name": "王小明"
    }
  ],
  "users": [...]
}
```

## API Design

### 群組管理 API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/super-admin/groups` | 取得所有已啟用群組列表 |
| GET | `/api/super-admin/groups/{group_id}/orders` | 取得指定群組的訂單 |
| POST | `/api/super-admin/groups/{group_id}/orders` | 代理點餐（新增訂單） |
| PUT | `/api/super-admin/groups/{group_id}/orders/{user_id}` | 修改使用者訂單 |
| DELETE | `/api/super-admin/groups/{group_id}/orders/{user_id}` | 刪除使用者訂單 |
| POST | `/api/super-admin/groups/{group_id}/payments/{user_id}/mark-paid` | 標記已付款 |
| POST | `/api/super-admin/groups/{group_id}/payments/{user_id}/refund` | 標記已退款 |

### 使用者管理 API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/super-admin/users` | 取得所有使用者列表 |
| GET | `/api/super-admin/users/{line_user_id}` | 取得使用者資料 |
| PUT | `/api/super-admin/users/{line_user_id}` | 更新使用者資料 |

## AI Prompt 調整

### Context 傳遞

在 `build_context()` 中，當處理群組訂單時：
- 使用 `display_name` 作為使用者名稱顯示
- `username` 內部仍使用 `line_user_id` 作為識別

```python
def build_context(username, is_manager=False, group_ordering=False, group_id=None):
    context = {
        # ...
        "username": profile.get("display_name", username),  # 顯示名稱
        "user_id": username,  # LINE User ID（內部識別用）
        # ...
    }
```

### Prompt 調整

在 `group_ordering_prompt.md` 和 `user_prompt.md` 中：
- 強調使用 `username` 欄位作為與使用者對話時的稱呼
- 內部操作（如 action data）使用 `user_id` 或由系統自動處理

## 前端設計

### 群組選擇器

```html
<select id="group-selector" onchange="loadGroupOrders()">
  <option value="">選擇群組...</option>
  <option value="Cxxxx">午餐群組 (5人)</option>
  <option value="Cyyyy">研發部 (8人)</option>
</select>
```

### 訂單列表

顯示選定群組的所有訂單，按使用者分組：
- 使用者名稱（display_name）
- 訂單品項列表
- 小計金額
- 操作按鈕（編輯、刪除）

### 代理點餐

透過對話框或表單，選擇使用者後新增訂單：
```
[選擇使用者: 王小明 ▼]
[選擇餐點: 雞腿便當 ▼]
[數量: 1]
[備註: ________]
[確認新增]
```

## 實作順序

1. **Phase 1: 資料結構**
   - 調整 profile.json 結構支援 line_user_id 和 display_name
   - 調整群組訂單結構加入 payments

2. **Phase 2: API**
   - 實作超級管理員 API
   - 調整現有 API 支援新結構

3. **Phase 3: 前端**
   - 新增群組選擇器
   - 重構訂單列表顯示
   - 新增代理點餐功能

4. **Phase 4: AI Prompt**
   - 調整 prompt 使用 display_name
   - 測試對話流程
