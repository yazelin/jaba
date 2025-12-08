# Change: 菜單辨識差異比對與特價品項管理

## Why
當使用者重新辨識菜單圖片時，目前系統會完全覆蓋現有菜單，使用者無法看到新舊差異、選擇性更新部分品項，也無法刪除已停售的品項。此外，菜單中常見的特價促銷品項（如買一送一、第二杯10元、限時特價）缺乏專門的分類和計價邏輯支援。

## What Changes

### 1. 菜單差異比對功能
- 菜單辨識完成後，自動比對新舊菜單差異
- 顯示差異預覽介面：新增品項、修改品項、可刪除品項
- 支援選擇性更新：使用者勾選要套用的變更

### 2. 特價品項資料結構與計價邏輯
- 菜單品項新增 `promo` 欄位，記錄促銷類型與計價規則
- 支援三種特價類型：
  - `buy_one_get_one`: 買一送一（數量 2 收 1 份價格）
  - `second_discount`: 第二杯折扣（第二杯固定價或折數）
  - `time_limited`: 限時特價（直接降價）
- 訂單建立時根據 `promo` 欄位自動計算正確金額

### 3. 特價優惠分類
- AI 辨識時自動識別特價品項，歸入「特價優惠」分類
- 特價品項顯示促銷標籤和計價說明

## Impact
- Affected specs: `menu-management`, `admin-ui`, `order-management`
- Affected code:
  - `app/ai.py` (差異比對邏輯)
  - `app/data.py` (訂單計價邏輯)
  - `templates/manager.html` (差異預覽 UI)
  - `data/system/jaba_prompt.json` (AI 辨識 prompt)
