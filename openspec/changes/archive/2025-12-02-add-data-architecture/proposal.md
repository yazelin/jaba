# Change: 建立檔案系統資料架構

## Why
jiaba 系統使用檔案系統而非資料庫儲存資料，需要設計清晰的目錄結構來管理：
- 多家便當店的菜單資訊（含圖文）
- 使用者資料與訂單歷史
- 管理員功能所需的付款記錄
- AI Agent 的系統提示詞

## What Changes
- 建立 `data/` 目錄作為所有資料的根目錄
- 設計 `data/stores/` 存放便當店菜單（支援多店家）
- 設計 `data/users/` 存放使用者資料與訂單
- 設計 `data/orders/` 存放每日訂單彙整
- 設計 `data/system/` 存放 AI 系統提示詞與設定
- 定義各類資料檔案的格式規範

## Impact
- Affected specs: data-storage, user-management, menu-management, order-management
- Affected code: 新增資料存取模組、API 路由
- 這是系統的基礎架構，後續所有功能都將依賴此設計
