# group-order-api Specification

## Purpose
TBD - created by archiving change refactor-super-admin-panel. Update Purpose after archive.
## Requirements
### Requirement: 群組列表 API
系統 SHALL 提供 API 讓超級管理員取得所有已啟用群組的列表。

#### Scenario: 取得群組列表
- **WHEN** 呼叫 `GET /api/super-admin/groups`
- **THEN** 回傳所有已啟用群組的列表
- **AND** 每個群組包含：id、name、activated_at、成員數、訂單統計

#### Scenario: 回傳格式
- **GIVEN** 有已啟用的群組
- **WHEN** 呼叫群組列表 API
- **THEN** 回傳格式如下：
  ```json
  {
    "groups": [
      {
        "id": "Cxxxxxxxxxxxxxxxxx",
        "name": "午餐群組",
        "activated_at": "2025-12-09T10:00:00",
        "member_count": 5,
        "order_count": 3,
        "total_amount": 255
      }
    ]
  }
  ```

### Requirement: 群組訂單查詢 API
系統 SHALL 提供 API 讓超級管理員查詢指定群組的訂單。

#### Scenario: 取得群組訂單
- **WHEN** 呼叫 `GET /api/super-admin/groups/{group_id}/orders`
- **THEN** 回傳該群組的所有訂單
- **AND** 訂單按使用者分組

#### Scenario: 回傳格式
- **GIVEN** 群組有訂單
- **WHEN** 呼叫群組訂單 API
- **THEN** 回傳格式如下：
  ```json
  {
    "group_id": "Cxxxxxxxxxxxxxxxxx",
    "group_name": "午餐群組",
    "status": "ended",
    "orders": [
      {
        "line_user_id": "Uxxxxxxxxxxxxxxxxx",
        "display_name": "王小明",
        "items": [
          {"name": "雞腿便當", "quantity": 1, "price": 85, "subtotal": 85, "note": ""}
        ],
        "total": 85
      }
    ],
    "payments": {...},
    "summary": {
      "order_count": 3,
      "total_amount": 255,
      "paid_amount": 85,
      "pending_amount": 170
    }
  }
  ```

#### Scenario: 群組不存在
- **WHEN** 呼叫不存在的群組 ID
- **THEN** 回傳 404 錯誤
- **AND** 錯誤訊息為「群組不存在」

### Requirement: 代理點餐 API
系統 SHALL 提供 API 讓超級管理員代替群組成員建立訂單。

#### Scenario: 建立代理訂單
- **WHEN** 呼叫 `POST /api/super-admin/groups/{group_id}/orders`
- **AND** body 包含 `line_user_id`、`display_name`、`items`
- **THEN** 為該使用者建立訂單
- **AND** 回傳建立的訂單資料

#### Scenario: 請求格式
- **GIVEN** 代理點餐請求
- **THEN** body 格式如下：
  ```json
  {
    "line_user_id": "Uxxxxxxxxxxxxxxxxx",
    "display_name": "王小明",
    "items": [
      {"name": "雞腿便當", "quantity": 1, "note": ""}
    ]
  }
  ```

#### Scenario: 新使用者代理點餐
- **GIVEN** line_user_id 不存在於系統中
- **WHEN** 代理點餐
- **THEN** 自動建立使用者 profile
- **AND** 建立訂單

### Requirement: 訂單修改 API
系統 SHALL 提供 API 讓超級管理員修改使用者訂單。

#### Scenario: 修改訂單
- **WHEN** 呼叫 `PUT /api/super-admin/groups/{group_id}/orders/{user_id}`
- **AND** body 包含 `items`
- **THEN** 更新該使用者的訂單品項
- **AND** 重新計算總額
- **AND** 更新付款記錄（若有變動）

#### Scenario: 請求格式
- **GIVEN** 修改訂單請求
- **THEN** body 格式如下：
  ```json
  {
    "items": [
      {"name": "排骨便當", "quantity": 2, "note": "不要酸菜"}
    ]
  }
  ```

### Requirement: 訂單刪除 API
系統 SHALL 提供 API 讓超級管理員刪除使用者訂單。

#### Scenario: 刪除訂單
- **WHEN** 呼叫 `DELETE /api/super-admin/groups/{group_id}/orders/{user_id}`
- **THEN** 刪除該使用者在該群組的訂單
- **AND** 更新付款記錄（若已付款則標記待退款）

#### Scenario: 使用者無訂單
- **WHEN** 刪除不存在的使用者訂單
- **THEN** 回傳 404 錯誤

### Requirement: 付款標記 API
系統 SHALL 提供 API 讓超級管理員標記付款狀態。

#### Scenario: 標記已付款
- **WHEN** 呼叫 `POST /api/super-admin/groups/{group_id}/payments/{user_id}/mark-paid`
- **THEN** 設定 `paid=true`
- **AND** 設定 `paid_amount` 為當前 `amount`
- **AND** 清除 `note`
- **AND** 記錄 `paid_at` 時間

#### Scenario: 標記已退款
- **WHEN** 呼叫 `POST /api/super-admin/groups/{group_id}/payments/{user_id}/refund`
- **THEN** 設定 `paid_amount` 為 `amount`
- **AND** 設定 `paid=true`（若 amount > 0）
- **AND** 清除待退備註

### Requirement: 驗證超級管理員權限
所有 `/api/super-admin/*` API SHALL 驗證管理員權限。

#### Scenario: 未驗證存取
- **GIVEN** 未通過管理員驗證
- **WHEN** 呼叫任何 super-admin API
- **THEN** 回傳 401 錯誤

#### Scenario: 已驗證存取
- **GIVEN** 已通過管理員密碼驗證
- **WHEN** 呼叫 super-admin API
- **THEN** 正常執行並回傳結果

