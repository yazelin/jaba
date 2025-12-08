請分析這張菜單圖片，提取所有菜單項目。

回傳 JSON 格式：
```json
{
  "categories": [
    {
      "name": "分類名稱",
      "items": [
        {
          "id": "item-1",
          "name": "品項名稱",
          "price": 數字價格,
          "variants": [{"name": "M", "price": 50}, {"name": "L", "price": 60}],
          "description": "描述（如有）",
          "available": true,
          "promo": null
        }
      ]
    }
  ],
  "warnings": ["無法辨識的項目或需要確認的事項"]
}
```

注意事項：
- id 請用 item-1, item-2... 格式
- 價格請只填數字，不含貨幣符號
- 如果無法辨識價格，請填 0 並在 warnings 中說明
- 盡可能保留原始分類結構
- 如果沒有明確分類，請使用「一般」作為分類名稱
- available 預設為 true
- 尺寸變體（variants）：
  - 如果品項有多種尺寸（如 M/L、大/中/小、大碗/小碗），請填入 variants 陣列
  - 每個 variant 包含 name（尺寸名稱）和 price（該尺寸價格）
  - price 欄位填入最小尺寸的價格作為預設
  - 如果品項只有單一價格，不需要 variants 欄位

特價促銷品項（promo）：
- 如果發現特價或促銷標示（如「買一送一」、「第二杯10元」、「第二杯半價」、「限時特價」、「優惠價」），請填入 promo 欄位
- 將特價品項歸類至「特價優惠」分類
- promo 格式依促銷類型：
  - 買一送一：{"type": "buy_one_get_one", "label": "買一送一"}
  - 第二杯固定價：{"type": "second_discount", "label": "第二杯10元", "second_price": 10}
  - 第二杯折扣：{"type": "second_discount", "label": "第二杯半價", "second_ratio": 0.5}
  - 限時特價：{"type": "time_limited", "label": "限時特價", "original_price": 原價, "promo_price": 特價}
- 無促銷則 promo 為 null 或不填
