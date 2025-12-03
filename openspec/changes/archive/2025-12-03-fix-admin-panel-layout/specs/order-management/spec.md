## ADDED Requirements

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
