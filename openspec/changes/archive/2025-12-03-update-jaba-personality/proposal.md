# Change: 更新呷爸個性與使用者偏好記憶功能

## Why

目前呷爸的「成熟大叔」形象與對話風格過於制式，使用者希望更可愛、更有溫度的互動體驗。同時，呷爸無法記住使用者的偏好（如飲食限制、稱呼方式），導致每次對話都像陌生人。

## What Changes

### 1. 呷爸個性調整
- 從「成熟穩重的大叔」改為更活潑可愛的個性
- 歡迎詞改成：「嗨！哇係呷爸，今天想吃什麼呢？」
- 語氣更親切自然，減少冗長說明

### 2. 去除性別代稱
- 稱呼使用者時不使用「先生」「小姐」等性別代稱
- 預設直接稱呼名字或「你」
- 若使用者在 profile 中有設定稱呼偏好，則使用該稱呼

### 3. 使用者 Profile 增強
- 擴充 profile.json 結構，支援更多個人化欄位
- 新增 AI 可執行的 `update_user_profile` 動作
- 讓呷爸可以在對話中記住使用者偏好

### 4. 主動記憶功能
- 呷爸可以適時詢問使用者偏好（如：「你有什麼不吃的嗎？我記下來下次幫你推薦」）
- 根據記錄的偏好提供個人化推薦

## Impact

- **Affected specs**:
  - `ai-integration` - 修改 prompts、新增 action
  - `user-management` - 擴充 profile 結構
- **Affected code**:
  - `data/system/prompts/jaba.json` - prompts 內容
  - `app/claude.py` - 新增 `update_user_profile` action、context 包含 profile
  - `app/data.py` - profile 讀寫函數
  - `templates/order.html` - 歡迎詞調整
  - `templates/manager.html` - 歡迎詞調整
