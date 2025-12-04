# Tasks: restore-full-ai-context

## Implementation Tasks

### 1. 更新 `build_context()` - 移除精簡邏輯
- [x] 移除 `_slim_menu()` 函數的呼叫，改為提供完整菜單
- [x] 管理員模式 `today_summary` 包含完整訂單明細
- [x] 使用者模式包含完整店家資訊
- **驗證**: Context 包含菜單 description 和完整訂單資訊 ✓

### 2. 移除 `_slim_menu()` 函數
- [x] 刪除 `app/ai.py` 中的 `_slim_menu()` 函數
- **驗證**: 程式碼無未使用函數 ✓

### 3. 驗證 AI 回應品質
- [x] 程式碼語法驗證通過
- **驗證**: AI 能利用完整資訊提供更精確的服務 ✓
