# Proposal: enable-disable-store-via-ai

## Why
目前 `_update_store` API 已經支援修改 `active` 欄位，但 AI 的 manager_prompt 沒有明確告知這個功能。管理員無法透過 AI 來啟用或停用店家。

## What Changes
在 `manager_prompt` 中補充說明：
- `update_store` 可以設定 `active: true/false` 來啟用或停用店家
- 停用的店家不會出現在一般使用者的店家列表中

## Scope
- `data/system/prompts/jaba.json` - 更新 manager_prompt

## Out of Scope
- 修改 API（已經支援）
- 新增管理介面按鈕
