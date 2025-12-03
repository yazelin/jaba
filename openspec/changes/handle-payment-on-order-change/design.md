# Design: handle-payment-on-order-change

## 問題分析

### 現有流程
```
建立訂單 → 新增付款記錄 (paid=false, amount=X)
標記付款 → 更新付款記錄 (paid=true)
修改訂單 → 更新付款記錄 (amount=Y) ← 問題：paid 狀態沒變
```

### 期望流程
```
建立訂單 → 新增付款記錄 (paid=false, amount=X)
標記付款 → 更新付款記錄 (paid=true, paid_amount=X)
修改訂單 → 智慧更新付款狀態：
  - 金額增加 → paid=false, note="已付 $X，待補 $Y"
  - 金額減少 → paid=true, note="待退 $Z"
```

## 設計決策

### 1. 為什麼用 `paid_amount` 而非每次重新計算？

**選項 A：記錄 `paid_amount`**
- 優點：明確知道實際收了多少錢
- 優點：可以處理「部分付款」的情況
- 缺點：多一個欄位要維護

**選項 B：假設 paid=true 時就是付了 `amount`**
- 優點：不需要新欄位
- 缺點：修改訂單後無法知道原本付了多少

**決定：選擇 A**，因為需要準確計算差額。

### 2. 金額減少時為什麼維持 `paid=true`？

考量實務情況：
- 使用者已經付了錢，只是多付了
- 管理員需要退款，但這是額外操作
- 統計上這筆訂單算「已收款」

如果改成 `paid=false`：
- 會混淆「完全沒付」和「多付待退」
- 統計會錯誤

### 3. 前端顯示設計

| 狀態 | 顏色 | 顯示文字 |
|------|------|----------|
| 未付 | 灰色 | 未付 |
| 已付 | 綠色 | 已付 |
| 部分已付 | 橘色 | 待補 $X |
| 待退款 | 藍色 | 待退 $X |

判斷邏輯：
```javascript
if (!record.paid && record.paid_amount > 0) {
  // 部分已付
} else if (record.paid && record.note?.startsWith('待退')) {
  // 待退款
} else if (record.paid) {
  // 已付
} else {
  // 未付
}
```

## 資料結構

### payments.json 擴充
```json
{
  "date": "2025-12-03",
  "records": [
    {
      "username": "亞澤",
      "amount": 150,        // 應付金額
      "paid": false,        // 付款狀態
      "paid_amount": 100,   // 實際已付金額 (新增)
      "paid_at": "...",     // 付款時間
      "note": "已付 $100，待補 $50"  // 備註
    }
  ],
  "total_collected": 100,   // 已收金額
  "total_pending": 50       // 待收金額
}
```

### 總額計算邏輯調整
```python
# 已收金額 = 所有 paid_amount 的總和
total_collected = sum(r.get("paid_amount", 0) for r in records)

# 待收金額 = 應付總額 - 已收金額
total_pending = sum(r["amount"] for r in records) - total_collected
```

## 邊界情況

### 1. 訂單取消
- 如果已付款，設定 `note="待退 $X"`
- `paid_amount` 保留，表示曾經收過這筆錢

### 2. 多次修改訂單
- 每次都基於 `paid_amount` 計算差額
- 例：付了 100 → 改成 150（待補 50）→ 又改成 120（待補 20）

### 3. 手動標記付款
- 標記付款時，`paid_amount = amount`
- 清除 note

### 4. 取消後重新訂餐
- 保留原本的 `paid_amount`
- 例：付了 100 → 取消（待退 100）→ 又訂了 80
- 結果：`paid_amount=100`, `amount=80`, `note="待退 $20"`

### 5. 清除所有訂單
- 如果有人已付款（`paid_amount > 0`），不能直接清空
- 將 `amount` 設為 0，保留 `paid_amount`，設定 `note="待退 $X"`
- 需要新增「標記已退款」功能
- 管理員退款後標記已退款，該記錄才會被移除

### 6. 標記已退款
- 新增 `mark_refunded` action
- 執行後：移除該付款記錄（或設定 `paid_amount=0`, `note=null`）
- 只有 `amount=0` 且有待退款時才能執行

### 7. paid_amount 初始值
- 新使用者訂餐時，`paid_amount = 0`
- 統一用數字 0，不用 null
