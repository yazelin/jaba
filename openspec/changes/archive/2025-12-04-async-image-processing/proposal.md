# Proposal: async-image-processing

## Problem Statement

目前後端架構有嚴重的阻塞問題：

1. **AI 呼叫使用同步 `subprocess.run()`** - `call_ai()` 和 `recognize_menu_image()` 都使用同步的 subprocess，會阻塞 Python 的 event loop
2. **Uvicorn 單 worker 模式** - 沒有設定多 worker，所有請求都在同一個 process 處理

**結果**：當任何使用者在等待 AI 回應（聊天或圖片辨識）時，其他使用者的所有請求（包括載入頁面、Socket.IO 連線）都會被卡住。

## Proposed Solution

使用 **`asyncio.create_subprocess_exec`** 取代同步的 `subprocess.run()`：

```python
# 現在（阻塞）
result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

# 改成（非阻塞）
proc = await asyncio.create_subprocess_exec(
    *cmd,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE
)
stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
```

### 優點
- 不阻塞 event loop，其他請求可正常處理
- 使用 Python 標準庫，無需額外依賴
- 改動最小，只需修改 subprocess 呼叫方式

## Scope

- 修改 `app/ai.py` 的 `call_ai()` 函數改為 async
- 修改 `app/ai.py` 的 `recognize_menu_image()` 函數改為 async
- 更新 `main.py` 中呼叫這些函數的地方加上 `await`

## Out of Scope

- 背景任務佇列系統
- 前端輪詢機制
- 多 worker 配置（可作為後續優化）

## Dependencies

無新增依賴，使用 Python 標準庫 `asyncio`。
