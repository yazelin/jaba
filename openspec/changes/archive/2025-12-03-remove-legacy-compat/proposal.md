# Proposal: remove-legacy-compat

## Why
目前程式碼中有大量「向後相容」的分支處理，導致：
1. 程式碼冗餘，維護困難
2. 同一功能有兩套邏輯路徑
3. 資料格式不一致

這些向後相容的目的是支援舊格式，但既然新格式本來就能處理所有情況，就不需要保留舊邏輯。

## What Changes

### 1. 店家格式統一
- `today.json`：移除頂層 `store_id`、`store_name`，只保留 `stores[]` 陣列
- 前端：只使用 `stores[]` 渲染，移除 `todayInfo.store_name` 分支

### 2. 訂單檔案格式統一
- 移除舊格式 `{date}.json` 的支援
- 只保留新格式 `{date}-{timestamp}.json`
- 目前所有訂單已是新格式，無需遷移

### 3. AI Action 格式統一
- prompt 只告訴 AI 使用 `actions` 陣列格式
- 移除 `action` 單一動作的處理邏輯
- `main.py` 只處理 `actions` 陣列

### 4. API 回應清理
- `/api/today`：移除 `store` 向後相容欄位

### 5. CSS 清理
- 移除「舊版兩欄」相關註解

## Scope
- `app/data.py`
- `app/claude.py`
- `main.py`
- `templates/index.html`
- `templates/order.html`
- `templates/manager.html`
- `static/css/style.css`

## Out of Scope
- 舊資料遷移（現有資料已是新格式）
