# Tasks

## 1. 更新 Prompts

- [x] 1.1 修改 `data/system/prompts/jaba.json` 中的 `user_prompt`
  - 將「成熟穩重的大叔」改為「親切可愛」的個性描述
  - 加入「不使用性別代稱」的指示
  - 加入「參考使用者 profile 偏好」的指示
  - 加入 `update_user_profile` 動作說明
- [x] 1.2 修改 `manager_prompt`
  - 同樣調整個性描述
  - 語氣更親切
- [x] 1.3 更新 `greeting` 欄位為「嗨！哇係呷爸，今天想吃什麼呢？」

## 2. 更新前端歡迎詞

- [x] 2.1 修改 `templates/order.html` 中的歡迎訊息
  - 將「嗨 ${username}！我是呷爸」改為「嗨！哇係呷爸」
  - 保持簡潔友善
- [x] 2.2 修改 `templates/manager.html` 中的歡迎訊息
  - 語氣更親切

## 3. 實作 Profile 增強功能

- [x] 3.1 在 `app/data.py` 新增 `get_user_profile(username)` 函數
- [x] 3.2 在 `app/data.py` 新增 `update_user_profile(username, updates)` 函數
- [x] 3.3 在 `app/claude.py` 的 `build_context()` 中加入使用者 profile
- [x] 3.4 在 `app/claude.py` 新增 `_update_user_profile()` action handler
- [x] 3.5 在 `execute_action()` 中加入 `update_user_profile` 分支

## 4. 驗證與測試

- [x] 4.1 手動測試新的歡迎訊息顯示
- [x] 4.2 測試 profile 更新功能
- [x] 4.3 測試呷爸能正確讀取使用者偏好
- [x] 4.4 測試呷爸稱呼使用者時不使用性別代稱
