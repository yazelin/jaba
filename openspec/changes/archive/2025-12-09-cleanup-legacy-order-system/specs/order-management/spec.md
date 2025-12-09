# order-management Spec Delta

## REMOVED Requirements

### Requirement: 彈性訂餐
移除：個人訂單系統不再使用，改用群組訂單。

### Requirement: 訂單永久保留
移除：個人訂單檔案不再建立。

### Requirement: 每日訂單彙整
移除：`orders/{date}/summary.json` 不再使用，群組訂單有自己的摘要機制。

### Requirement: 付款記錄
移除：獨立付款系統 `orders/{date}/payments.json` 不再使用，改用群組 session 內的付款追蹤。

### Requirement: 訂單取消權限
移除：個人訂單取消功能不再使用。

### Requirement: 訂單品項尺寸
保留但移至群組訂單：群組點餐仍支援尺寸。

### Requirement: 訂單品項移除
移除：個人訂單移除功能不再使用，群組訂單有 `group_remove_item`。

### Requirement: 訂單修改邏輯
移除：個人訂單修改不再使用。

### Requirement: 付款狀態獨立按鈕
移除：獨立付款系統按鈕不再需要，超級管理員面板已有群組付款管理。

### Requirement: 付款狀態前端顯示
移除：獨立付款狀態顯示不再需要。

### Requirement: 特價品項訂單計價
保留：此邏輯在群組訂單中仍然使用。

### Requirement: 訂單品項促銷資訊記錄
保留：此邏輯在群組訂單中仍然使用。
