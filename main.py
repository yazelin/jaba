"""jaba (呷爸) - AI 午餐訂便當系統"""
import socketio
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from datetime import datetime

from app import data
from app import claude

# 建立 Socket.IO 伺服器
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# 建立 FastAPI 應用
app = FastAPI(title="jaba - 呷爸 AI 午餐訂便當系統")

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
    """取得今日資訊（支援多店家）"""
    today_info = data.get_today_info()
    summary = data.get_daily_summary()

    # 加入所有今日店家的詳細資訊和菜單
    stores_detail = []
    if today_info.get("stores"):
        for store_ref in today_info["stores"]:
            store_id = store_ref.get("store_id")
            store_info = data.get_store(store_id)
            menu_info = data.get_menu(store_id)
            if store_info:
                stores_detail.append({
                    "store": store_info,
                    "menu": menu_info
                })

    # 向後相容：保留單店家欄位
    store_info = None
    if today_info.get("store_id"):
        store_info = data.get_store(today_info["store_id"])

    return {
        "today": today_info,
        "store": store_info,  # 向後相容
        "stores": stores_detail,  # 多店家資訊
        "summary": summary
    }


@app.get("/api/stores")
async def get_stores():
    """取得店家列表"""
    return data.get_active_stores()


@app.get("/api/stores/all")
async def get_all_stores_with_menus():
    """取得所有店家與菜單（管理員用）"""
    stores = data.get_stores()
    result = []
    for store in stores:
        menu = data.get_menu(store["id"])
        result.append({
            "store": store,
            "menu": menu
        })
    return result


@app.get("/api/menu/{store_id}")
async def get_menu(store_id: str):
    """取得店家菜單"""
    menu = data.get_menu(store_id)
    if not menu:
        return JSONResponse({"error": "找不到菜單"}, status_code=404)
    return menu


@app.get("/api/payments")
async def get_payments():
    """取得今日付款狀態"""
    payments = data.get_payments()
    return payments or {"records": [], "total_collected": 0, "total_pending": 0}


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

    # 執行動作（支援單一 action 或多個 actions）
    action = response.get("action")
    actions = response.get("actions")
    action_result = None
    action_results = None

    # 優先處理 actions 陣列
    if actions and isinstance(actions, list):
        action_results = claude.execute_actions(username, actions, is_manager)

        # 廣播每個動作的事件
        for result in action_results:
            if result.get("success") and result.get("event"):
                event_type = result["event"]
                event_data = {
                    "username": username,
                    "summary": result.get("summary"),
                    "today": result.get("today"),
                    "store_name": result.get("store_name"),
                }
                await broadcast_event(event_type, event_data)
    elif action:
        # 向後相容：單一 action
        action_result = claude.execute_action(username, action, is_manager)

        # 廣播事件
        if action_result.get("success") and action_result.get("event"):
            event_type = action_result["event"]
            event_data = {
                "username": username,
                "summary": action_result.get("summary"),
                "today": action_result.get("today"),
                "store_name": action_result.get("store_name"),
            }
            await broadcast_event(event_type, event_data)

    return {
        "message": response.get("message", ""),
        "action": action,
        "actions": actions,
        "action_result": action_result,
        "action_results": action_results
    }


@app.get("/api/chat/messages")
async def get_chat_messages():
    """取得今日聊天記錄"""
    messages = data.get_chat_messages()
    return {"messages": messages}


@app.post("/api/chat/send")
async def send_chat_message(request: Request):
    """發送聊天訊息"""
    body = await request.json()
    username = body.get("username", "").strip()
    content = body.get("content", "").strip()

    if not username:
        return JSONResponse({"error": "請輸入名稱"}, status_code=400)
    if not content:
        return JSONResponse({"error": "請輸入訊息內容"}, status_code=400)

    # 儲存訊息
    message = data.save_chat_message(username, content)

    # 廣播給所有連線者
    await sio.emit("chat_message", message)

    return {"success": True, "message": message}


@app.post("/api/verify-admin")
async def verify_admin(request: Request):
    """驗證管理員密碼"""
    body = await request.json()
    password = body.get("password", "")

    config = data.get_config()
    if password == config.get("admin_password"):
        return {"success": True}
    return {"success": False, "error": "密碼錯誤"}


@app.post("/api/recognize-menu")
async def recognize_menu(request: Request):
    """辨識菜單圖片"""
    import re
    import hashlib

    body = await request.json()
    store_id = body.get("store_id")
    store_name = body.get("store_name")
    image_base64 = body.get("image")

    if not image_base64:
        return JSONResponse({"error": "請提供圖片"}, status_code=400)

    # 如果是新店家，先建立
    if not store_id and store_name:
        # 產生 store_id：先嘗試從英數字產生，若為空則用 hash
        ascii_id = re.sub(r'[^a-z0-9-]', '-', store_name.lower())
        ascii_id = re.sub(r'-+', '-', ascii_id).strip('-')
        if ascii_id:
            store_id = ascii_id
        else:
            # 中文店名：用名稱的 hash 前 8 碼
            name_hash = hashlib.md5(store_name.encode('utf-8')).hexdigest()[:8]
            store_id = f"store-{name_hash}"

        # 建立店家
        info = {
            "id": store_id,
            "name": store_name,
            "phone": "",
            "address": "",
            "description": "",
            "note": "",
            "active": True,
            "created_at": datetime.now().isoformat()
        }
        data.save_store(store_id, info)

    if not store_id:
        return JSONResponse({"error": "請選擇店家或輸入新店家名稱"}, status_code=400)

    # 呼叫 AI 辨識
    result = claude.recognize_menu_image(image_base64)

    if result.get("error"):
        return JSONResponse({"error": result["error"]}, status_code=500)

    return {
        "success": True,
        "store_id": store_id,
        "recognized_menu": result.get("menu"),
        "warnings": result.get("warnings", [])
    }


@app.post("/api/save-menu")
async def save_menu(request: Request):
    """直接儲存菜單（管理員用）"""
    from datetime import datetime

    body = await request.json()
    store_id = body.get("store_id")
    categories = body.get("categories")

    if not store_id:
        return JSONResponse({"error": "請指定店家"}, status_code=400)
    if categories is None:
        return JSONResponse({"error": "請提供菜單內容"}, status_code=400)

    # 確認店家存在
    store = data.get_store(store_id)
    if not store:
        return JSONResponse({"error": "找不到店家"}, status_code=404)

    # 儲存菜單
    menu = {
        "store_id": store_id,
        "updated_at": datetime.now().isoformat(),
        "categories": categories
    }
    data.save_menu(store_id, menu)

    return {"success": True, "menu": menu}


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
