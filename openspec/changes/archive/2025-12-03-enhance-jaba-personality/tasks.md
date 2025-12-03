# Tasks: enhance-jaba-personality

## Implementation Tasks

1. [x] **更新 `user_prompt` - 呷爸個性、健康提醒與卡路里估算**
   - 檔案：`data/system/prompts/jaba.json`
   - 調整為成熟穩重大叔形象
   - 加入健康飲食提醒邏輯
   - 加入卡路里估算邏輯（點餐時估算並顯示總卡路里）

2. [x] **更新 `manager_prompt` - 呷爸個性與店家建議**
   - 檔案：`data/system/prompts/jaba.json`
   - 調整為成熟穩重大叔形象
   - 加入店家建議邏輯（當今日未設定店家時）

3. [x] **擴充管理員 context - 提供歷史訂餐資訊**
   - 檔案：`app/claude.py` 的 `build_context()`
   - 當 `is_manager=True` 時，提供過去 N 天的店家記錄
   - 讓 AI 能分析並給出建議

4. [x] **修改訂單資料結構 - 儲存卡路里**
   - 檔案：`app/claude.py` 的 `_create_order()`
   - AI 回傳的 items 包含 `calories` 欄位
   - 儲存每個品項的估算卡路里
   - 計算並儲存 `total_calories`

5. [x] **修改前端 UI - 顯示卡路里**
   - 檔案：`templates/order.html`（或相關模板）
   - 在「我的訂單」區域顯示各餐點的卡路里
   - 顯示總卡路里

6. [x] **驗證修改**
   - 程式碼結構驗證完成
   - `jaba.json` 包含正確的 `user_prompt` 和 `manager_prompt`
   - `claude.py` 正確處理卡路里儲存和歷史店家記錄
   - `order.html` 正確顯示卡路里資訊
   - 注意：如需實際測試，請清除管理員 session 以載入新 prompt
