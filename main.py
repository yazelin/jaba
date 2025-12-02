"""jiaba - AI 午餐訂便當系統"""
import socketio
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path

from app import data
from app import claude

# 建立 Socket.IO 伺服器
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# 建立 FastAPI 應用
app = FastAPI(title="jiaba - AI 午餐訂便當系統")

# 包裝成 ASGI 應用
socket_app = socketio.ASGIApp(sio, app)

# 靜態檔案
app.mount("/static", StaticFiles(directory="static"), name="static")

# 確保資料目錄存在
data.ensure_data_dirs()


# === Socket.IO 事件 ===

@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")


@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")


async def broadcast_event(event: str, event_data: dict):
    """廣播事件給所有連線的客戶端"""
    await sio.emit(event, event_data)


# === API 路由 ===

@app.get("/", response_class=HTMLResponse)
async def index():
    """今日看板首頁"""
    return Path("templates/index.html").read_text(encoding="utf-8")


@app.get("/order", response_class=HTMLResponse)
async def order_page():
    """訂餐頁"""
    return Path("templates/order.html").read_text(encoding="utf-8")


@app.get("/manager", response_class=HTMLResponse)
async def manager_page():
    """管理頁"""
    return Path("templates/manager.html").read_text(encoding="utf-8")


@app.get("/api/today")
async def get_today():
    """取得今日資訊"""
    today_info = data.get_today_info()
    summary = data.get_daily_summary()
    return {
        "today": today_info,
        "summary": summary
    }


@app.get("/api/stores")
async def get_stores():
    """取得店家列表"""
    return data.get_active_stores()


@app.get("/api/menu/{store_id}")
async def get_menu(store_id: str):
    """取得店家菜單"""
    menu = data.get_menu(store_id)
    if not menu:
        return JSONResponse({"error": "找不到菜單"}, status_code=404)
    return menu


@app.post("/api/chat")
async def chat(request: Request):
    """與 AI 對話"""
    body = await request.json()
    username = body.get("username", "").strip()
    message = body.get("message", "").strip()
    is_manager = body.get("is_manager", False)

    if not username:
        return JSONResponse({"error": "請輸入名稱"}, status_code=400)
    if not message:
        return JSONResponse({"error": "請輸入訊息"}, status_code=400)

    # 呼叫 Claude
    response = claude.call_claude(username, message, is_manager)

    # 執行動作
    action = response.get("action")
    action_result = None
    if action:
        action_result = claude.execute_action(username, action)

        # 廣播事件
        if action_result.get("success") and action_result.get("event"):
            event_type = action_result["event"]
            event_data = {
                "username": username,
                "summary": action_result.get("summary"),
                "today": action_result.get("today"),
            }
            await broadcast_event(event_type, event_data)

    return {
        "message": response.get("message", ""),
        "action": action,
        "action_result": action_result
    }


@app.post("/api/verify-admin")
async def verify_admin(request: Request):
    """驗證管理員密碼"""
    body = await request.json()
    password = body.get("password", "")

    config = data.get_config()
    if password == config.get("admin_password"):
        return {"success": True}
    return {"success": False, "error": "密碼錯誤"}


@app.post("/api/upload-image/{store_id}")
async def upload_image(store_id: str, file: UploadFile = File(...)):
    """上傳菜品圖片"""
    store = data.get_store(store_id)
    if not store:
        return JSONResponse({"error": "找不到店家"}, status_code=404)

    # 儲存圖片
    images_dir = data.DATA_DIR / "stores" / store_id / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    file_path = images_dir / file.filename
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)

    return {"success": True, "path": f"images/{file.filename}"}


# === 啟動應用 ===

if __name__ == "__main__":
    import uvicorn
    config = data.get_config()
    port = config.get("server_port", 8098)
    uvicorn.run(socket_app, host="0.0.0.0", port=port)
