# Tasks: async-image-processing

## Implementation Tasks

1. [x] 修改 `app/ai.py` 的 `call_ai()` 函數
   - 改為 `async def call_ai()`
   - 將 `subprocess.run()` 改為 `asyncio.create_subprocess_exec()`
   - 使用 `asyncio.wait_for()` 實作 timeout

2. [x] 修改 `app/ai.py` 的 `recognize_menu_image()` 函數
   - 改為 `async def recognize_menu_image()`
   - 將 `subprocess.run()` 改為 `asyncio.create_subprocess_exec()`
   - 使用 `asyncio.wait_for()` 實作 timeout

3. [x] 更新 `main.py` 中的呼叫
   - `/api/chat` 路由：`await ai.call_ai(...)`
   - `/api/recognize-menu` 路由：`await ai.recognize_menu_image(...)`

4. [x] 測試驗證
   - 同時開兩個瀏覽器視窗
   - 一個執行圖片辨識（長時間任務）
   - 另一個應可正常載入頁面和聊天
