# order-management Specification

## Purpose
TBD - created by archiving change add-data-architecture. Update Purpose after archive.
## Requirements
### Requirement: 彈性訂餐
系統 SHALL 允許使用者隨時建立訂單，無固定週期限制。

#### Scenario: 建立訂單
- **WHEN** 使用者透過 AI 確認訂單
- **THEN** 建立 `users/{username}/orders/{date}.json`
- **AND** 更新 `orders/{date}/summary.json`

### Requirement: 訂單永久保留
系統 SHALL 永久保留所有訂單紀錄。

#### Scenario: 查詢歷史訂單
- **WHEN** 使用者查詢過去訂單
- **THEN** AI 讀取對應日期的訂單檔案

### Requirement: 每日訂單彙整
系統 SHALL 在 `orders/{date}/summary.json` 維護當日所有訂單彙整。

#### Scenario: 查看當日彙整
- **WHEN** 查看某日訂單
- **THEN** 顯示所有人的訂單與品項統計

### Requirement: 付款記錄
系統 SHALL 在 `orders/{date}/payments.json` 記錄付款狀態，並在訂單金額變動時智慧更新付款狀態。

#### Scenario: 標記已付款
- **WHEN** 管理員標記某人已付款
- **THEN** 更新 `paid` 為 true
- **AND** 設定 `paid_amount` 為當前 `amount`
- **AND** 記錄 `paid_at` 時間
- **AND** 清除 `note`

#### Scenario: 查看未付款
- **WHEN** 管理員查看未付款清單
- **THEN** 列出 `paid` 為 false 的紀錄

#### Scenario: 已付款後訂單金額增加
- **GIVEN** 使用者已標記付款，`paid_amount` 為 100
- **WHEN** 修改訂單導致 `amount` 變為 150
- **THEN** 設定 `paid` 為 false
- **AND** 保留 `paid_amount` 為 100
- **AND** 設定 `note` 為「已付 $100，待補 $50」

#### Scenario: 已付款後訂單金額減少
- **GIVEN** 使用者已標記付款，`paid_amount` 為 100
- **WHEN** 修改訂單導致 `amount` 變為 70
- **THEN** 維持 `paid` 為 true
- **AND** 保留 `paid_amount` 為 100
- **AND** 設定 `note` 為「待退 $30」

#### Scenario: 已付款後訂單金額不變
- **GIVEN** 使用者已標記付款
- **WHEN** 修改訂單但 `amount` 不變
- **THEN** 維持原有付款狀態

#### Scenario: 訂單取消且已付款
- **GIVEN** 使用者已標記付款，`paid_amount` 為 100
- **WHEN** 訂單被取消
- **THEN** 設定 `amount` 為 0
- **AND** 設定 `note` 為「待退 $100」

#### Scenario: 取消後重新訂餐
- **GIVEN** 使用者已付款 100 後取消訂單，`paid_amount` 為 100
- **WHEN** 使用者重新訂餐 80 元
- **THEN** 設定 `amount` 為 80
- **AND** 保留 `paid_amount` 為 100
- **AND** 設定 `note` 為「待退 $20」

#### Scenario: 清除所有訂單（有待退款）
- **GIVEN** 有使用者已付款，`paid_amount` > 0
- **WHEN** 管理員清除所有訂單
- **THEN** 清除訂單記錄
- **AND** 保留有 `paid_amount` > 0 的付款記錄
- **AND** 設定這些記錄的 `amount` 為 0
- **AND** 設定 `note` 為「待退 $X」

#### Scenario: 清除所有訂單（無待退款）
- **GIVEN** 使用者 `paid_amount` = 0（從未付款）
- **WHEN** 管理員清除所有訂單
- **THEN** 清除訂單記錄
- **AND** 移除該使用者的付款記錄

#### Scenario: 標記已退款（無剩餘訂單）
- **GIVEN** 付款記錄 `amount` 為 0 且 `paid_amount` > 0
- **WHEN** 管理員標記已退款
- **THEN** 移除該付款記錄
- **AND** 重新計算 `total_collected` 和 `total_pending`

#### Scenario: 標記已退款（有剩餘訂單）
- **GIVEN** 付款記錄 `amount` > 0 且 `paid_amount` > `amount`（有待退款）
- **WHEN** 管理員標記已退款
- **THEN** 設定 `paid_amount` 為 `amount`（多付的已退還）
- **AND** 設定 `paid` 為 true
- **AND** 清除 `note`
- **AND** 該記錄變成「已付清」狀態

### Requirement: 訂單取消權限
系統 SHALL 限制訂單取消操作的權限，一般用戶只能取消自己的訂單，管理員可取消任何人訂單。

#### Scenario: 一般用戶取消自己訂單
- **WHEN** 一般用戶請求取消自己的訂單
- **THEN** 成功取消訂單並廣播 order_cancelled 事件

#### Scenario: 一般用戶嘗試取消他人訂單
- **WHEN** 一般用戶請求取消其他人的訂單
- **THEN** 回傳錯誤「只能取消自己的訂單」

#### Scenario: 管理員取消任何人訂單
- **WHEN** 管理員請求取消任何人的訂單
- **THEN** 成功取消訂單並廣播 order_cancelled 事件

### Requirement: 訂餐頁使用者視角
訂餐頁面 SHALL 只顯示當前登入使用者自己的訂單。

#### Scenario: 查看自己的訂單
- **GIVEN** 使用者以名稱 "小明" 登入訂餐頁
- **WHEN** 訂單面板載入或更新
- **THEN** 只顯示 username 為 "小明" 的訂單
- **AND** 面板標題顯示「我的訂單」
- **AND** 訂單項目不重複顯示使用者名稱

#### Scenario: 空訂單提示
- **GIVEN** 使用者登入訂餐頁
- **WHEN** 該使用者尚未訂餐
- **THEN** 顯示「你還沒有訂餐」提示

#### Scenario: 即時更新過濾
- **GIVEN** 使用者 "小明" 在訂餐頁
- **WHEN** Socket.IO 收到 order_created 事件
- **AND** 事件中的 username 不是 "小明"
- **THEN** 訂單面板不更新顯示內容

### Requirement: 訂單品項尺寸
系統 SHALL 支援訂單品項指定尺寸，並根據尺寸計算正確價格。

#### Scenario: 指定尺寸建立訂單
- **GIVEN** 使用者點選有變體的飲料品項
- **WHEN** AI 建立訂單
- **THEN** 訂單品項包含 `size` 欄位
- **AND** 系統從 `variants` 查找對應價格

#### Scenario: 未指定尺寸
- **GIVEN** 使用者點選有變體的品項但未指定尺寸
- **WHEN** AI 建立訂單
- **THEN** 使用品項的預設 `price`

### Requirement: 訂單品項移除
系統 SHALL 支援從現有訂單中移除特定品項，而非建立新訂單。

#### Scenario: 移除訂單中的一個品項
- **GIVEN** 使用者有訂單包含 [排骨便當, 味噌湯]
- **WHEN** 使用者說「不要排骨便當」
- **AND** AI 執行 `remove_item` 動作
- **THEN** 從訂單中移除排骨便當
- **AND** 訂單變成只有 [味噌湯]
- **AND** 更新 daily summary
- **AND** 更新 payments 記錄

#### Scenario: 移除訂單中的唯一品項
- **GIVEN** 使用者有訂單只包含 [味噌湯]
- **WHEN** 使用者說「不要湯了」
- **AND** AI 執行 `remove_item` 動作
- **THEN** 刪除整筆訂單
- **AND** 更新 daily summary
- **AND** 更新 payments 記錄

#### Scenario: 減少品項數量
- **GIVEN** 使用者有訂單包含 [雞腿便當 x2]
- **WHEN** 使用者說「少一個雞腿便當」
- **AND** AI 執行 `remove_item` 動作 (quantity: 1)
- **THEN** 訂單變成 [雞腿便當 x1]
- **AND** 重新計算訂單總額

#### Scenario: 跨訂單移除品項
- **GIVEN** 使用者有多筆訂單，其中一筆包含目標品項
- **WHEN** AI 執行 `remove_item` 動作
- **THEN** 從包含該品項的訂單中移除
- **AND** 不影響其他訂單

### Requirement: 訂單修改邏輯
系統 SHALL 根據操作類型選擇正確的處理方式。

#### Scenario: 新增不在現有訂單中的品項
- **GIVEN** 使用者現有訂單不包含品項 X
- **WHEN** 使用者說「加一個 X」
- **THEN** AI 執行 `create_order` 建立新訂單
- **AND** 新訂單包含品項 X

#### Scenario: 移除現有訂單中的品項
- **GIVEN** 使用者現有訂單包含品項 X
- **WHEN** 使用者說「不要 X」
- **THEN** AI 執行 `remove_item` 動作
- **AND** 不執行 `create_order`
- **AND** 不會產生重複品項

### Requirement: 付款狀態獨立按鈕
管理員頁面 SHALL 提供獨立按鈕讓管理員直接更新付款狀態，無需透過 AI 對話。

#### Scenario: 顯示確認付款按鈕（未付款）
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount=0`
- **WHEN** 管理員查看付款面板
- **THEN** 顯示「確認付款」按鈕

#### Scenario: 顯示確認付款按鈕（待補款）
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount > 0`（部分已付）
- **WHEN** 管理員查看付款面板
- **THEN** 顯示「確認付款」按鈕

#### Scenario: 點擊確認付款按鈕
- **WHEN** 管理員點擊「確認付款」按鈕
- **THEN** 呼叫 `/api/mark-paid` API
- **AND** 設定 `paid` 為 true
- **AND** 設定 `paid_amount` 為當前 `amount`
- **AND** 清除 `note`
- **AND** 廣播 `payment_updated` 事件
- **AND** 即時更新付款面板顯示

#### Scenario: 已付款不顯示確認付款按鈕
- **GIVEN** 付款記錄 `paid=true` 且無待補備註
- **WHEN** 管理員查看付款面板
- **THEN** 不顯示「確認付款」按鈕

#### Scenario: 顯示確認退款按鈕
- **GIVEN** 付款記錄有「待退」備註
- **WHEN** 管理員查看付款面板
- **THEN** 顯示「確認退款」按鈕

### Requirement: 付款狀態前端顯示
管理員頁面 SHALL 根據付款狀態顯示不同樣式和資訊。

#### Scenario: 顯示未付款狀態
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount=0`
- **WHEN** 管理員查看付款面板
- **THEN** 顯示灰色「未付」標籤

#### Scenario: 顯示已付款狀態
- **GIVEN** 付款記錄 `paid=true` 且無待退備註
- **WHEN** 管理員查看付款面板
- **THEN** 顯示綠色「已付」標籤

#### Scenario: 顯示部分已付狀態
- **GIVEN** 付款記錄 `paid=false` 且 `paid_amount > 0`
- **WHEN** 管理員查看付款面板
- **THEN** 顯示橘色「待補 $X」標籤
- **AND** 滑鼠懸停顯示備註內容

#### Scenario: 顯示待退款狀態
- **GIVEN** 付款記錄 `paid=true` 且 `note` 包含「待退」
- **WHEN** 管理員查看付款面板
- **THEN** 顯示藍色「待退 $X」標籤

### Requirement: 特價品項訂單計價
系統 SHALL 根據菜單品項的 `promo` 設定，正確計算訂單金額。

#### Scenario: 買一送一計價
- **GIVEN** 品項設定為買一送一，單價 $50
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $50（買一送一，2杯收1杯價）

#### Scenario: 買一送一奇數杯計價
- **GIVEN** 品項設定為買一送一，單價 $50
- **WHEN** 使用者訂購 3 杯
- **THEN** 訂單金額為 $100（第1-2杯買一送一$50 + 第3杯原價$50）

#### Scenario: 第二杯固定價計價
- **GIVEN** 品項設定為第二杯 $10，單價 $50
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $60（$50 + $10）

#### Scenario: 第二杯固定價奇數杯計價
- **GIVEN** 品項設定為第二杯 $10，單價 $50
- **WHEN** 使用者訂購 3 杯
- **THEN** 訂單金額為 $110（$50 + $10 + $50）

#### Scenario: 第二杯半價計價
- **GIVEN** 品項設定為第二杯半價（ratio=0.5），單價 $60
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $90（$60 + $30）

#### Scenario: 限時特價計價
- **GIVEN** 品項設定為限時特價 $45（原價 $60）
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $90（$45 × 2）

#### Scenario: 無促銷正常計價
- **GIVEN** 品項無 `promo` 設定，單價 $50
- **WHEN** 使用者訂購 2 杯
- **THEN** 訂單金額為 $100（$50 × 2）

### Requirement: 訂單品項促銷資訊記錄
系統 SHALL 在訂單品項中記錄促銷資訊，以便查詢和核對。

#### Scenario: 記錄促銷類型
- **GIVEN** 使用者訂購有促銷的品項
- **WHEN** 建立訂單
- **THEN** 訂單品項包含 `promo_type` 欄位
- **AND** 包含 `promo_label` 顯示文字

#### Scenario: 記錄折扣金額
- **GIVEN** 使用者訂購有促銷的品項
- **WHEN** 建立訂單
- **THEN** 訂單品項包含 `discount` 欄位
- **AND** 顯示節省金額

#### Scenario: 訂單明細顯示促銷
- **GIVEN** 訂單包含促銷品項
- **WHEN** 查看訂單明細
- **THEN** 顯示促銷標籤和折扣金額

