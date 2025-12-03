# ui-layout Spec Delta

## ADDED Requirements

### Requirement: 菜單顯示品項尺寸變體
系統 SHALL 在菜單顯示中，當品項有尺寸變體（variants）時，顯示各尺寸名稱和對應價格。

#### Scenario: 管理員查看店家菜單（有尺寸變體）
- **GIVEN** 品項有 variants 陣列（如 M、L 杯）
- **WHEN** 管理員在「所有店家」面板展開店家菜單
- **THEN** 顯示各尺寸名稱和價格（如「M $50 / L $60」）

#### Scenario: 使用者在訂餐頁查看菜單（有尺寸變體）
- **GIVEN** 品項有 variants 陣列
- **WHEN** 使用者在訂餐頁查看菜單
- **THEN** 顯示各尺寸選項
- **AND** 點擊特定尺寸時，以該尺寸的價格下單

#### Scenario: 菜單品項無尺寸變體
- **GIVEN** 品項沒有 variants 陣列
- **WHEN** 顯示該品項
- **THEN** 只顯示預設價格（item.price）

### Requirement: 管理員直接編輯店家菜單
管理員 SHALL 能夠直接編輯現有店家的菜單，不需要重新上傳圖片辨識。

#### Scenario: 點擊編輯按鈕
- **GIVEN** 管理員在「所有店家」面板
- **WHEN** 點擊某店家的「編輯」按鈕
- **THEN** 彈出菜單編輯畫面
- **AND** 載入該店家現有的菜單內容

#### Scenario: 編輯並儲存菜單
- **GIVEN** 管理員在菜單編輯畫面
- **WHEN** 修改品項名稱、價格、尺寸等並儲存
- **THEN** 更新該店家的菜單
- **AND** 關閉編輯畫面
