## ADDED Requirements

### Requirement: 多店家支援
系統 SHALL 支援多家便當店，每家店在 `data/stores/{store-id}/` 有獨立目錄。

#### Scenario: 列出可用店家
- **WHEN** 查詢可用店家
- **THEN** 回傳所有 active 為 true 的店家

### Requirement: 店家資訊儲存
系統 SHALL 在 info.json 儲存店家 id、name、phone、address、active 等欄位。

#### Scenario: 停用店家
- **WHEN** 管理員停用某店家
- **THEN** 將 active 設為 false，訂餐時不顯示

### Requirement: JSON 菜單結構
系統 SHALL 使用 menu.json 儲存結構化菜單，含分類與菜品項目。

#### Scenario: AI 讀取菜單
- **WHEN** AI 需要介紹菜單
- **THEN** 讀取 menu.json 的 categories 與 items

#### Scenario: 選擇性圖片
- **WHEN** 菜品有圖片
- **THEN** image 欄位存相對路徑；無則為 null
