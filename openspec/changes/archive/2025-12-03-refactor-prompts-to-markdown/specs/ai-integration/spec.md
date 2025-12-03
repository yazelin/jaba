# ai-integration Spec Delta

## MODIFIED Requirements

### Requirement: AI 系統提示詞儲存格式
系統 SHALL 將 AI 系統提示詞儲存為獨立的 Markdown 檔案，以提高可讀性和維護性。

#### Scenario: 讀取使用者模式提示詞
- **GIVEN** `data/system/prompts/user_prompt.md` 存在
- **WHEN** 系統呼叫 `get_jaba_prompt()`
- **THEN** 回傳包含 `user_prompt` 欄位的 dict
- **AND** 內容為 `user_prompt.md` 的文字內容

#### Scenario: 讀取管理員模式提示詞
- **GIVEN** `data/system/prompts/manager_prompt.md` 存在
- **WHEN** 系統呼叫 `get_jaba_prompt()`
- **THEN** 回傳包含 `manager_prompt` 欄位的 dict
- **AND** 內容為 `manager_prompt.md` 的文字內容
