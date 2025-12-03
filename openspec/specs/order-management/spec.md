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
系統 SHALL 在 `orders/{date}/payments.json` 記錄付款狀態。

#### Scenario: 標記已付款
- **WHEN** 管理員標記某人已付款
- **THEN** 更新 paid 為 true 並記錄時間

#### Scenario: 查看未付款
- **WHEN** 管理員查看未付款清單
- **THEN** 列出 paid 為 false 的紀錄

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

