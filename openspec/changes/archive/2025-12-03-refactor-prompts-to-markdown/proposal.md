# Proposal: refactor-prompts-to-markdown

## Why
目前 `jaba.json` 中的 `user_prompt` 和 `manager_prompt` 是用 `\n` 分隔的長字串，非常難閱讀和維護。

另外 `capabilities` 和 `greeting` 欄位已經沒有在程式碼中使用。

## What Changes
1. 將 `user_prompt` 內容獨立成 `user_prompt.md`
2. 將 `manager_prompt` 內容獨立成 `manager_prompt.md`
3. 修改 `get_jaba_prompt()` 從 `.md` 檔案載入 prompt
4. 移除 `jaba.json` 中未使用的 `capabilities` 和 `greeting` 欄位
5. 簡化 `jaba.json` 只保留 `name` 和 `role`（或直接刪除，因為也沒用到）

## Scope
- `data/system/prompts/jaba.json` - 簡化或移除
- `data/system/prompts/user_prompt.md` - 新增
- `data/system/prompts/manager_prompt.md` - 新增
- `app/data.py` - 修改 `get_jaba_prompt()` 讀取邏輯

## Out of Scope
- 修改 prompt 內容本身
