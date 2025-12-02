## MODIFIED Requirements

### Requirement: AI 動作執行
系統 SHALL 根據 AI 回應的 action 執行對應操作並廣播事件。管理員模式 SHALL 支援 `cancel_order`、`clear_all_orders`、`clean_history_orders` 動作。

#### Scenario: 執行建立訂單
- **WHEN** AI 回應 action.type 為 create_order
- **THEN** 建立訂單、更新彙整、廣播 order_created

#### Scenario: 執行取消訂單（管理員）
- **WHEN** 管理員模式下 AI 回應 action.type 為 cancel_order
- **THEN** 刪除指定訂單、更新彙整、廣播 order_cancelled

#### Scenario: 執行清除所有訂單（管理員）
- **WHEN** 管理員模式下 AI 回應 action.type 為 clear_all_orders
- **THEN** 刪除今日所有訂單、清空彙整、廣播 orders_cleared

#### Scenario: 使用者無訂單時的回應
- **WHEN** 使用者詢問「我訂了什麼」但當日無訂單
- **THEN** AI 回覆「你今天還沒有訂餐喔」

## ADDED Requirements

### Requirement: 菜單圖片辨識
系統 SHALL 支援上傳菜單圖片，透過 AI 辨識並自動建立菜單資料。

#### Scenario: 上傳菜單圖片辨識
- **WHEN** 管理員上傳菜單圖片
- **THEN** AI 分析圖片內容
- **AND** 回傳辨識出的品項名稱、價格、分類

#### Scenario: 確認辨識結果
- **WHEN** AI 回傳辨識結果
- **THEN** 管理員可確認或修改後儲存為菜單

### Requirement: 訂餐頁開場白
系統 SHALL 在訂餐頁開始對話時，由 AI 主動提供今日店家資訊與菜單重點。

#### Scenario: 呷爸主動介紹
- **WHEN** 使用者進入訂餐頁開始對話
- **THEN** 呷爸主動介紹今日店家名稱、備註說明、推薦菜色
