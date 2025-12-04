# ai-integration Spec Delta

## ADDED Requirements

### Requirement: 非同步 AI CLI 執行

系統 SHALL 使用非同步方式執行 AI CLI 命令，避免阻塞其他請求。

#### Scenario: 非同步執行 AI 對話
- **GIVEN** 使用者發送對話訊息
- **WHEN** 後端呼叫 AI CLI
- **THEN** 使用 `asyncio.create_subprocess_exec()` 非同步執行
- **AND** 其他使用者的請求不受影響

#### Scenario: 非同步執行菜單辨識
- **GIVEN** 管理員上傳菜單圖片
- **WHEN** 後端呼叫 AI 辨識
- **THEN** 使用 `asyncio.create_subprocess_exec()` 非同步執行
- **AND** 其他使用者可正常載入頁面和聊天

#### Scenario: 處理超時
- **GIVEN** AI CLI 執行中
- **WHEN** 超過設定的 timeout 時間
- **THEN** 使用 `asyncio.wait_for()` 取消任務
- **AND** 回傳超時錯誤訊息
