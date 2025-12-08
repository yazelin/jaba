## Context

目前系統的菜單辨識功能會完全覆蓋現有菜單，使用者無法：
1. 看到新舊菜單的差異
2. 選擇性地更新部分品項
3. 刪除已停售的品項
4. 正確處理特價促銷品項的計價

本設計涵蓋差異比對、選擇性更新、以及特價品項的資料結構與計價邏輯。

## Goals / Non-Goals

**Goals:**
- 提供直覺的差異預覽介面，讓使用者快速理解變更內容
- 支援選擇性更新，避免意外覆蓋想保留的品項
- 建立可擴充的特價計價架構，支援常見促銷類型
- 確保訂單金額計算正確反映促銷折扣

**Non-Goals:**
- 不支援複雜的組合促銷（如：滿額折扣、跨品項組合）
- 不支援促銷有效期限管理（由管理員手動控制）
- 不支援促銷自動到期移除

## Decisions

### 1. 特價品項資料結構

在菜單品項中新增 `promo` 欄位：

```json
{
  "id": "item-promo-1",
  "name": "珍珠奶茶（買一送一）",
  "price": 50,
  "description": "買一送一優惠",
  "available": true,
  "promo": {
    "type": "buy_one_get_one",
    "label": "買一送一"
  }
}
```

**三種促銷類型：**

```json
// 買一送一：兩杯收一杯價
{
  "type": "buy_one_get_one",
  "label": "買一送一"
}

// 第二杯折扣：第二杯固定價格或折數
{
  "type": "second_discount",
  "label": "第二杯10元",
  "second_price": 10
}
// 或
{
  "type": "second_discount",
  "label": "第二杯半價",
  "second_ratio": 0.5
}

// 限時特價：直接降價
{
  "type": "time_limited",
  "label": "限時特價",
  "original_price": 60,
  "promo_price": 45
}
```

**理由：**
- 將促銷資訊與品項綁定，簡化資料管理
- `label` 欄位用於前端顯示，讓使用者理解促銷內容
- 不同類型使用不同參數，保持結構清晰

### 2. 訂單計價邏輯

訂單品項儲存時記錄促銷資訊，計價時根據類型計算：

```python
def calculate_promo_price(item: dict, quantity: int) -> int:
    promo = item.get("promo")
    base_price = item.get("price", 0)

    if not promo:
        return base_price * quantity

    promo_type = promo.get("type")

    if promo_type == "buy_one_get_one":
        # 每兩杯收一杯錢（2杯$50=$50），奇數杯多收一杯（3杯$50=$100）
        return ((quantity + 1) // 2) * base_price

    elif promo_type == "second_discount":
        # 第二杯折扣：奇數杯第一杯原價，偶數杯依折扣
        pairs = quantity // 2
        remainder = quantity % 2
        second_price = promo.get("second_price")
        if second_price is not None:
            return pairs * (base_price + second_price) + remainder * base_price
        else:
            ratio = promo.get("second_ratio", 1.0)
            return pairs * (base_price + int(base_price * ratio)) + remainder * base_price

    elif promo_type == "time_limited":
        # 限時特價直接使用促銷價
        return promo.get("promo_price", base_price) * quantity

    return base_price * quantity
```

### 3. 差異比對演算法

比對邏輯以品項名稱為主鍵：

```python
def compare_menus(existing: dict, recognized: dict) -> dict:
    """
    回傳:
    {
      "added": [...],      # 新辨識出的品項（現有菜單沒有）
      "modified": [...],   # 名稱相同但內容不同（價格、促銷等）
      "unchanged": [...],  # 完全相同
      "removed": [...]     # 現有菜單有但新辨識沒有的（可能已停售）
    }
    """
```

比對欄位：`name`, `price`, `variants`, `promo`

### 4. 差異預覽 UI 設計

```
┌─────────────────────────────────────────────────┐
│ 📋 菜單差異預覽                                  │
├─────────────────────────────────────────────────┤
│ ✅ 新增品項 (3)                                  │
│   ☑ 🟢 芋頭鮮奶茶  $65                          │
│   ☑ 🟢 葡萄柚綠茶  $70                          │
│   ☑ 🟢 珍珠奶茶（買一送一）$50 [買一送一]        │
├─────────────────────────────────────────────────┤
│ ⚠️ 修改品項 (2)                                  │
│   ☑ 🟡 阿薩姆奶茶  $40 → $45                    │
│   ☑ 🟡 茉莉綠茶    M $30 → M $32                │
├─────────────────────────────────────────────────┤
│ 🗑️ 可刪除品項 (1)                               │
│   ☐ 🔴 冬瓜茶      $25  (新菜單中未出現)        │
├─────────────────────────────────────────────────┤
│        [取消]                    [套用選取項目]  │
└─────────────────────────────────────────────────┘
```

- 新增品項預設勾選
- 修改品項預設勾選
- 刪除品項預設不勾選（避免誤刪）

### 5. 儲存模式

新增 `diff_mode` 參數：

```json
POST /api/save-menu
{
  "store_id": "coco",
  "diff_mode": true,
  "apply_items": ["item-1", "item-2"],  // 要新增/修改的品項 ID
  "remove_items": ["item-old-1"]        // 要刪除的品項 ID
}
```

當 `diff_mode=true` 時，只處理指定的變更，保留其他品項。

## Risks / Trade-offs

| 風險 | 緩解措施 |
|------|----------|
| AI 辨識品項名稱不一致導致誤判為新品項 | 使用模糊比對（去除空白、標點）提高匹配率 |
| 促銷類型判斷錯誤 | 提供手動編輯促銷類型的 UI |
| 計價邏輯複雜導致 Bug | 每種類型獨立測試，顯示計價明細讓使用者驗證 |

## Open Questions

1. 是否需要支援「同品項不同尺寸有不同促銷」？
   - 目前設計：促銷掛在品項層級，所有尺寸共用
   - 可考慮：未來可擴充為 variant 層級的促銷

2. 第二杯折扣的「第二杯」判定：
   - 目前設計：同一品項的第 2, 4, 6... 杯享折扣
   - 可考慮：跨品項（同分類）的第二杯折扣
