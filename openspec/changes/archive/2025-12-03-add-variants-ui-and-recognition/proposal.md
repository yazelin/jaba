# Proposal: add-variants-ui-and-recognition

## Why
之前新增了 `variants` 欄位支援尺寸價格，但：
1. AI 菜單辨識不會產生 variants，只輸出單一 price
2. 管理員 UI 只有單一價格欄位，無法編輯 variants
3. AI 管理模式無法透過對話編輯品項的尺寸價格

導致 variants 功能無法實際使用。

## What Changes

### 1. AI 菜單辨識支援 variants
更新辨識 prompt，讓 AI 從菜單圖片提取多尺寸價格：
- 辨識各種尺寸標示：M/L、大/中/小、大碗/小碗 等
- **只在菜單確實有多尺寸時**才輸出 `variants` 陣列
- 適用於飲料、便當、麵食等任何有尺寸區分的品項
- 格式：`[{"name": "M", "price": 50}, {"name": "L", "price": 60}]`
- `price` 欄位填入第一個（最小）尺寸的價格作為預設

### 2. 管理員 UI 支援編輯 variants
在菜單編輯介面增加 variants 編輯功能：
- 每個品項可展開編輯尺寸變體
- 可新增/刪除/修改尺寸名稱和價格
- AI 漏辨識的尺寸可手動補上
- 沒有 variants 時顯示「+ 新增尺寸」按鈕

### 3. AI 對話編輯 variants
管理員可透過對話讓 AI 編輯品項的尺寸價格：
- 新增動作 `update_item_variants`
- 例：「把珍珠奶茶的 L 杯改成 65 元」
- 例：「幫雞腿便當加一個大份的選項，100元」

## Scope
- `app/claude.py`: 更新辨識 prompt、新增 `update_item_variants` 動作
- `templates/manager.html`: 更新菜單編輯 UI
- `static/css/style.css`: 新增 variants 編輯樣式
- `data/system/prompts/jaba.json`: 更新管理員 prompt
