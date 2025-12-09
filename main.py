"""jaba (呷爸) - AI 午餐訂便當系統"""
import socketio
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from datetime import datetime

from app import data
from app import ai

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
async def get_today(username: str = None):
    """取得今日資訊"""
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

    # 取得使用者偏好稱呼
    preferred_name = None
    if username:
        profile = data.get_user_profile(username)
        if profile:
            preferred_name = profile.get("preferences", {}).get("preferred_name")

    return {
        "today": today_info,
        "stores": stores_detail,
        "summary": summary,
        "preferred_name": preferred_name
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


@app.post("/api/refund")
async def mark_refund(request: Request):
    """標記已退款"""
    body = await request.json()
    username = body.get("username")

    if not username:
        return JSONResponse({"error": "缺少 username"}, status_code=400)

    result = ai._mark_refunded({"username": username})

    if result.get("success"):
        await broadcast_event("payment_updated", {"username": username})

    return result


@app.post("/api/mark-paid")
async def mark_paid(request: Request):
    """標記已付款"""
    body = await request.json()
    username = body.get("username")

    if not username:
        return JSONResponse({"error": "缺少 username"}, status_code=400)

    result = ai._mark_paid({"username": username})

    if result.get("success"):
        await broadcast_event("payment_updated", {"username": username})

    return result


@app.post("/api/chat")
async def chat(request: Request):
    """與 AI 對話"""
    import time
    t_api_start = time.time()

    body = await request.json()
    username = body.get("username", "").strip()
    message = body.get("message", "").strip()
    is_manager = body.get("is_manager", False)

    if not username:
        return JSONResponse({"error": "請輸入名稱"}, status_code=400)
    if not message:
        return JSONResponse({"error": "請輸入訊息"}, status_code=400)

    # 呼叫 AI（非同步，不阻塞其他請求）
    response = await ai.call_ai(username, message, is_manager)

    t_ai_done = time.time()

    # 執行動作
    actions = response.get("actions", [])
    action_results = []

    if actions:
        action_results = ai.execute_actions(username, actions, is_manager)

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

                # 店家變更時，在團體聊天室新增系統訊息
                if event_type == "store_changed" and result.get("store_name"):
                    store_name = result.get("store_name")
                    msg = data.save_system_message(f"今日店家已設定：{store_name}，可以開始訂餐囉！")
                    await sio.emit("chat_message", msg)

    t_api_end = time.time()

    # 取得 AI 內部的時間資訊
    ai_timings = response.get("_timings", {})

    return {
        "message": response.get("message", ""),
        "actions": actions,
        "action_results": action_results,
        "error": response.get("error"),
        "_debug": {
            "provider": response.get("_provider"),
            "model": response.get("_model"),
            "timings": {
                **ai_timings,
                "actions": round(t_api_end - t_ai_done, 3),
                "api_total": round(t_api_end - t_api_start, 3)
            }
        }
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


@app.post("/api/session/reset")
async def reset_session(request: Request):
    """重置使用者的對話歷史"""
    body = await request.json()
    username = body.get("username", "").strip()
    is_manager = body.get("is_manager", False)

    if not username:
        return JSONResponse({"error": "請輸入名稱"}, status_code=400)

    # 清除對話歷史
    cleared = data.clear_ai_chat_history(username, is_manager)
    return {"success": True, "cleared": cleared}


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
    is_new_store = False
    if not store_id and store_name:
        is_new_store = True
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

    # 取得現有菜單（用於差異比對）
    existing_menu = None if is_new_store else data.get_menu(store_id)

    # 呼叫 AI 辨識（非同步，不阻塞其他請求）
    result = await ai.recognize_menu_image(image_base64)

    if result.get("error"):
        return JSONResponse({"error": result["error"]}, status_code=500)

    recognized_menu = result.get("menu")

    # 進行差異比對
    diff = ai.compare_menus(existing_menu, recognized_menu)

    return {
        "success": True,
        "store_id": store_id,
        "is_new_store": is_new_store,
        "recognized_menu": recognized_menu,
        "existing_menu": existing_menu,
        "diff": diff,
        "warnings": result.get("warnings", [])
    }


@app.post("/api/store/{store_id}/toggle")
async def toggle_store_active(store_id: str):
    """切換店家啟用狀態"""
    store = data.get_store(store_id)
    if not store:
        return JSONResponse({"error": "找不到店家"}, status_code=404)

    # 切換狀態
    store["active"] = not store.get("active", True)
    data.save_store(store_id, store)

    return {"success": True, "active": store["active"]}


@app.post("/api/save-menu")
async def save_menu(request: Request):
    """直接儲存菜單（管理員用）

    支援兩種模式：
    1. 完整覆蓋模式：提供 categories 直接覆蓋整個菜單
    2. 差異模式：提供 diff_mode=True, apply_items, remove_items 進行選擇性更新
    """
    from datetime import datetime

    body = await request.json()
    store_id = body.get("store_id")
    categories = body.get("categories")
    diff_mode = body.get("diff_mode", False)
    apply_items = body.get("apply_items", [])  # 要新增/修改的品項
    remove_items = body.get("remove_items", [])  # 要刪除的品項 ID

    if not store_id:
        return JSONResponse({"error": "請指定店家"}, status_code=400)

    # 確認店家存在
    store = data.get_store(store_id)
    if not store:
        return JSONResponse({"error": "找不到店家"}, status_code=404)

    if diff_mode:
        # 差異模式：基於現有菜單進行更新
        existing_menu = data.get_menu(store_id) or {"categories": []}
        existing_categories = existing_menu.get("categories", [])

        # 建立品項索引（以 id 為 key）
        item_map = {}
        for cat in existing_categories:
            for item in cat.get("items", []):
                item_map[item.get("id")] = {"item": item, "category": cat}

        # 移除指定的品項
        for item_id in remove_items:
            if item_id in item_map:
                cat = item_map[item_id]["category"]
                cat["items"] = [i for i in cat.get("items", []) if i.get("id") != item_id]
                del item_map[item_id]

        # 新增/更新品項
        for apply_data in apply_items:
            item = apply_data.get("item")
            category_name = apply_data.get("category", "一般")

            if not item:
                continue

            item_id = item.get("id")

            if item_id and item_id in item_map:
                # 更新現有品項
                old_item = item_map[item_id]["item"]
                old_item.update(item)
            else:
                # 新增品項：找到或建立分類
                target_cat = None
                for cat in existing_categories:
                    if cat.get("name") == category_name:
                        target_cat = cat
                        break

                if not target_cat:
                    target_cat = {"name": category_name, "items": []}
                    existing_categories.append(target_cat)

                target_cat["items"].append(item)
                if item_id:
                    item_map[item_id] = {"item": item, "category": target_cat}

        # 移除空的分類
        existing_categories = [cat for cat in existing_categories if cat.get("items")]

        menu = {
            "store_id": store_id,
            "updated_at": datetime.now().isoformat(),
            "categories": existing_categories
        }
    else:
        # 完整覆蓋模式
        if categories is None:
            return JSONResponse({"error": "請提供菜單內容"}, status_code=400)

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


# === LINE Bot 白名單 API ===

def get_linebot_whitelist() -> dict:
    """取得 LINE Bot 白名單"""
    whitelist_file = data.DATA_DIR / "linebot" / "whitelist.json"
    if whitelist_file.exists():
        return data.read_json(whitelist_file)
    return {"users": [], "groups": []}


def save_linebot_whitelist(whitelist: dict):
    """儲存 LINE Bot 白名單"""
    linebot_dir = data.DATA_DIR / "linebot"
    linebot_dir.mkdir(parents=True, exist_ok=True)
    data.write_json(linebot_dir / "whitelist.json", whitelist)


@app.post("/api/linebot/register")
async def linebot_register(request: Request):
    """註冊 LINE Bot 使用者或群組"""
    body = await request.json()
    id_type = body.get("type")  # "user" 或 "group"
    id_value = body.get("id")
    name = body.get("name", "")

    if not id_type or not id_value:
        return JSONResponse({"error": "缺少 type 或 id"}, status_code=400)

    whitelist = get_linebot_whitelist()

    if id_type == "user":
        # 檢查是否已註冊
        existing = next((u for u in whitelist["users"] if u["id"] == id_value), None)
        if existing:
            return {"success": True, "message": "已經註冊過了", "already_registered": True}
        whitelist["users"].append({
            "id": id_value,
            "name": name,
            "registered_at": datetime.now().isoformat()
        })
    elif id_type == "group":
        existing = next((g for g in whitelist["groups"] if g["id"] == id_value), None)
        if existing:
            return {"success": True, "message": "此群組已經註冊過了", "already_registered": True}
        whitelist["groups"].append({
            "id": id_value,
            "name": name,
            "registered_at": datetime.now().isoformat()
        })
    else:
        return JSONResponse({"error": "type 必須是 user 或 group"}, status_code=400)

    save_linebot_whitelist(whitelist)
    return {"success": True, "message": "註冊成功"}


@app.get("/api/linebot/whitelist")
async def linebot_get_whitelist():
    """取得白名單"""
    return get_linebot_whitelist()


@app.get("/api/linebot/check/{id_value}")
async def linebot_check(id_value: str):
    """檢查是否在白名單中"""
    whitelist = get_linebot_whitelist()

    # 檢查使用者
    for user in whitelist["users"]:
        if user["id"] == id_value:
            return {"registered": True, "type": "user", "name": user.get("name")}

    # 檢查群組
    for group in whitelist["groups"]:
        if group["id"] == id_value:
            return {"registered": True, "type": "group", "name": group.get("name")}

    return {"registered": False}


@app.delete("/api/linebot/unregister")
async def linebot_unregister(request: Request):
    """取消註冊"""
    body = await request.json()
    id_value = body.get("id")

    if not id_value:
        return JSONResponse({"error": "缺少 id"}, status_code=400)

    whitelist = get_linebot_whitelist()

    # 從使用者列表移除
    whitelist["users"] = [u for u in whitelist["users"] if u["id"] != id_value]
    # 從群組列表移除
    whitelist["groups"] = [g for g in whitelist["groups"] if g["id"] != id_value]

    save_linebot_whitelist(whitelist)
    return {"success": True, "message": "已取消註冊"}


# === 啟動應用 ===

if __name__ == "__main__":
    import uvicorn
    config = data.get_config()
    port = config.get("server_port", 8098)
    uvicorn.run(socket_app, host="0.0.0.0", port=port)
