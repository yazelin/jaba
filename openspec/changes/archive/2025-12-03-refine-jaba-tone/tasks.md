# Tasks

## 1. 更新 Prompts

- [x] 1.1 修改 `data/system/prompts/jaba.json` 中的 `user_prompt`
  - 加入「使用我們代替你」的指示
  - 加入「不要說根據記錄等機械化用語」的指示
  - 調整對話範例
- [x] 1.2 修改 `manager_prompt`
  - 同樣加入「使用我們」的指示
  - 調整建議語氣

## 2. 更新前端歡迎詞

- [x] 2.1 修改 `templates/order.html` 中的歡迎訊息
  - 改成「我們」風格
- [x] 2.2 修改 `templates/manager.html` 中的歡迎訊息
  - 改成「我們」風格

## 3. 驗證

- [x] 3.1 測試呷爸對話不使用機械化用語
- [x] 3.2 測試呷爸使用「我們」的參與感用語
