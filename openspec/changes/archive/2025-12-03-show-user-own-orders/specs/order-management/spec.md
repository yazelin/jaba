# order-management Spec Delta

## ADDED Requirements

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
