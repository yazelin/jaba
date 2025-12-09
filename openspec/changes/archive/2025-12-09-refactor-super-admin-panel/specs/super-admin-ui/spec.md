# super-admin-ui Specification

## Purpose
超級管理員後台介面，用於管理多個 LINE 群組的訂單、使用者和付款狀態。

## ADDED Requirements

### Requirement: 群組選擇器
超級管理員後台 SHALL 提供群組選擇器，讓管理員切換要管理的群組。

#### Scenario: 顯示群組列表
- **GIVEN** 管理員登入超級管理員後台
- **WHEN** 頁面載入完成
- **THEN** 顯示下拉選單列出所有已啟用的 LINE 群組
- **AND** 每個選項顯示群組名稱和成員數

#### Scenario: 切換群組
- **WHEN** 管理員從下拉選單選擇一個群組
- **THEN** 載入並顯示該群組的訂單列表
- **AND** 載入該群組的付款狀態
- **AND** 更新訂單統計資訊

#### Scenario: 無群組時顯示提示
- **GIVEN** 沒有任何已啟用的 LINE 群組
- **WHEN** 頁面載入
- **THEN** 顯示「尚無已啟用的群組」提示訊息

### Requirement: 群組訂單列表
超級管理員後台 SHALL 顯示選定群組的所有訂單，按使用者分組。

#### Scenario: 顯示訂單列表
- **GIVEN** 選擇了一個群組
- **WHEN** 該群組有訂單
- **THEN** 按使用者 display_name 分組顯示訂單
- **AND** 每個使用者區塊顯示：姓名、品項列表、小計金額

#### Scenario: 顯示品項詳情
- **GIVEN** 使用者有訂單
- **WHEN** 顯示訂單品項
- **THEN** 顯示品項名稱、數量、單價、小計
- **AND** 若有備註（如「無糖去冰」）則顯示備註

#### Scenario: 空訂單提示
- **GIVEN** 選擇的群組沒有訂單
- **WHEN** 顯示訂單列表區域
- **THEN** 顯示「該群組尚無訂單」提示

### Requirement: 訂單編輯功能
超級管理員後台 SHALL 允許管理員編輯任何使用者的訂單。

#### Scenario: 開啟編輯對話框
- **GIVEN** 訂單列表中有使用者訂單
- **WHEN** 管理員點擊該使用者的「編輯」按鈕
- **THEN** 開啟編輯對話框
- **AND** 顯示該使用者的所有品項

#### Scenario: 修改品項數量
- **GIVEN** 開啟了編輯對話框
- **WHEN** 管理員修改品項數量
- **AND** 點擊「儲存」
- **THEN** 更新訂單品項數量
- **AND** 重新計算小計和總額

#### Scenario: 刪除品項
- **GIVEN** 開啟了編輯對話框
- **WHEN** 管理員點擊品項旁的「刪除」
- **THEN** 從訂單中移除該品項
- **AND** 若無剩餘品項則刪除整筆訂單

### Requirement: 訂單刪除功能
超級管理員後台 SHALL 允許管理員刪除使用者的整筆訂單。

#### Scenario: 刪除訂單確認
- **WHEN** 管理員點擊使用者訂單的「刪除」按鈕
- **THEN** 顯示確認對話框
- **AND** 顯示將被刪除的訂單內容

#### Scenario: 確認刪除
- **GIVEN** 顯示刪除確認對話框
- **WHEN** 管理員點擊「確認刪除」
- **THEN** 刪除該使用者在該群組的所有訂單
- **AND** 更新訂單列表顯示
- **AND** 更新付款記錄（若已付款則標記待退款）

### Requirement: 代理點餐功能
超級管理員後台 SHALL 允許管理員代替群組成員新增訂單。

#### Scenario: 開啟代理點餐
- **WHEN** 管理員點擊「代理點餐」按鈕
- **THEN** 開啟代理點餐對話框
- **AND** 顯示使用者選擇下拉選單
- **AND** 顯示今日菜單品項選擇

#### Scenario: 選擇代理對象
- **GIVEN** 開啟代理點餐對話框
- **WHEN** 管理員選擇使用者
- **THEN** 下拉選單顯示該群組所有曾經點過餐的成員
- **AND** 可輸入新使用者名稱

#### Scenario: 新增代理訂單
- **GIVEN** 已選擇使用者和餐點
- **WHEN** 管理員點擊「確認點餐」
- **THEN** 為該使用者建立訂單
- **AND** 更新訂單列表顯示
- **AND** 建立/更新付款記錄

### Requirement: 付款狀態管理
超級管理員後台 SHALL 顯示選定群組的付款狀態並提供付款操作。

#### Scenario: 顯示付款狀態列表
- **GIVEN** 選擇了一個群組
- **WHEN** 該群組有訂單
- **THEN** 顯示每個使用者的付款狀態
- **AND** 顯示：姓名、應付金額、已付金額、狀態標籤

#### Scenario: 顯示付款狀態標籤
- **GIVEN** 使用者付款記錄
- **WHEN** `paid=false` 且 `paid_amount=0`
- **THEN** 顯示灰色「未付」標籤

#### Scenario: 顯示已付款標籤
- **GIVEN** 使用者付款記錄
- **WHEN** `paid=true` 且無待退備註
- **THEN** 顯示綠色「已付」標籤

#### Scenario: 顯示待補款標籤
- **GIVEN** 使用者付款記錄
- **WHEN** `paid=false` 且 `paid_amount > 0`
- **THEN** 顯示橘色「待補 $X」標籤

#### Scenario: 顯示待退款標籤
- **GIVEN** 使用者付款記錄
- **WHEN** `paid_amount > amount`
- **THEN** 顯示藍色「待退 $X」標籤

#### Scenario: 標記已付款
- **WHEN** 管理員點擊「確認付款」按鈕
- **THEN** 設定 `paid=true`
- **AND** 設定 `paid_amount` 為當前 `amount`
- **AND** 更新狀態標籤顯示

#### Scenario: 標記已退款
- **WHEN** 管理員點擊「確認退款」按鈕
- **THEN** 調整 `paid_amount` 為 `amount`
- **AND** 清除待退備註
- **AND** 更新狀態標籤顯示

### Requirement: 訂單統計資訊
超級管理員後台 SHALL 顯示選定群組的訂單統計。

#### Scenario: 顯示訂單統計
- **GIVEN** 選擇了一個群組
- **WHEN** 該群組有訂單
- **THEN** 顯示：總訂單數、總金額、已收金額、待收金額

#### Scenario: 顯示品項統計
- **GIVEN** 選擇了一個群組
- **WHEN** 該群組有訂單
- **THEN** 顯示品項統計列表
- **AND** 每個品項顯示名稱和總數量

## ADDED Requirements

### Requirement: 使用者識別
系統 SHALL 使用 LINE User ID 作為使用者唯一識別，profile.json 中記錄 display_name 作為顯示名稱。

#### Scenario: 建立 LINE 使用者
- **WHEN** LINE 使用者首次點餐
- **THEN** 建立 `data/users/{line_user_id}/profile.json`
- **AND** profile 包含 `line_user_id` 和 `display_name` 欄位

#### Scenario: Profile 結構
- **GIVEN** LINE 使用者的 profile.json
- **THEN** 包含以下結構：
  ```json
  {
    "line_user_id": "Uxxxxxxxxxxxxxxxxx",
    "display_name": "王小明",
    "created_at": "建立時間",
    "preferences": {
      "dietary_restrictions": [],
      "allergies": [],
      "drink_preferences": [],
      "notes": ""
    }
  }
  ```

#### Scenario: 讀取使用者名稱
- **GIVEN** 呼叫 `get_user_profile(line_user_id)`
- **WHEN** 使用者存在
- **THEN** 回傳 profile 資料
- **AND** 可從 `display_name` 取得顯示名稱
