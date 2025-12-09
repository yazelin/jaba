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
    group_id = body.get("group_id")  # 群組點餐時傳入
    line_user_id = body.get("line_user_id")  # LINE User ID（群組點餐時傳入）
    display_name = body.get("display_name") or username  # LINE 顯示名稱

    if not username and not display_name:
        return JSONResponse({"error": "請輸入名稱"}, status_code=400)
    if not message:
        return JSONResponse({"error": "請輸入訊息"}, status_code=400)

    # 處理群組點餐指令
    message_lower = message.strip().lower()
    session_action = None

    if group_id:
        # 檢查是否為開始/結束點餐指令
        if message == "開單":
            if is_group_ordering(group_id):
                return {
                    "message": "⚠️ 此群組已經在點餐中了！\n\n直接說出你要點的餐點即可。",
                    "session_action": None
                }
            # 開始群組點餐
            session = start_group_session(group_id, {
                "line_user_id": line_user_id or "",
                "display_name": display_name
            })
            # 清空群組對話歷史（確保對話是這次點餐的內容）
            data.clear_group_chat_history(group_id)

            # 廣播群組點餐開始事件
            await broadcast_event("group_session_started", {
                "group_id": group_id,
                "started_by": display_name or username
            })

            # 取得今日菜單摘要
            menu_text = _get_today_menu_summary()

            return {
                "message": f"🍱 開始群組點餐！\n\n{menu_text}\n\n直接說出餐點即可，說「收單」或「結單」結束點餐。",
                "session_action": "started"
            }

        # 查詢菜單（群組點餐中或未點餐都可以查）
        if message == "菜單":
            menu_text = _get_today_menu_summary()
            return {
                "message": menu_text if menu_text else "今日尚未設定店家菜單",
                "session_action": None
            }

        if message_lower in ["收單", "結單"]:
            if not is_group_ordering(group_id):
                return {
                    "message": "⚠️ 目前沒有進行中的點餐。\n\n說「開單」開始群組點餐。",
                    "session_action": None
                }
            # 結束群組點餐並產生摘要
            session = end_group_session(group_id)
            summary_text = generate_session_summary(session)

            # 廣播群組點餐結束事件
            await broadcast_event("group_session_ended", {
                "group_id": group_id,
                "order_count": len(session.get("orders", [])),
                "total_amount": sum(o.get("total", 0) for o in session.get("orders", []))
            })

            return {
                "message": f"✅ 點餐結束！\n\n{summary_text}",
                "session_action": "ended"
            }

        # 查詢群組目前訂單
        if message_lower in ["目前訂單", "訂單", "查看訂單", "訂單狀況", "點了什麼"]:
            if is_group_ordering(group_id):
                session = get_group_session(group_id)
                summary_text = generate_session_summary(session)
                return {
                    "message": f"📋 目前點餐狀況\n\n{summary_text}",
                    "session_action": None
                }

    # 判斷是否為群組點餐模式
    group_ordering = False
    group_name = None
    if group_id and is_group_ordering(group_id):
        group_ordering = True
        # 取得群組名稱（從 whitelist）
        whitelist = get_linebot_whitelist()
        group_info = next((g for g in whitelist.get("groups", []) if g["id"] == group_id), None)
        if group_info:
            group_name = group_info.get("name") or f"群組 ...{group_id[-8:]}"

    # 呼叫 AI（非同步，不阻塞其他請求）
    response = await ai.call_ai(
        username, message, is_manager, group_ordering, group_id,
        line_user_id if group_ordering else None,
        display_name if group_ordering else None,
        group_name if group_ordering else None
    )

    t_ai_done = time.time()

    # 廣播群組對話更新事件（Socket.IO）
    if group_ordering and group_id and group_name:
        ai_message = response.get("message", "")
        # 廣播使用者訊息
        await broadcast_event("board_chat_message", {
            "group_name": group_name,
            "username": username,
            "role": "user",
            "content": message
        })
        await broadcast_event("group_chat_updated", {
            "group_id": group_id,
            "message": {
                "username": username,
                "role": "user",
                "content": message
            }
        })
        # 廣播呷爸回覆
        if ai_message:
            await broadcast_event("board_chat_message", {
                "group_name": group_name,
                "username": "呷爸",
                "role": "assistant",
                "content": ai_message
            })
            await broadcast_event("group_chat_updated", {
                "group_id": group_id,
                "message": {
                    "username": "呷爸",
                    "role": "assistant",
                    "content": ai_message
                }
            })

    # 執行動作
    actions = response.get("actions", [])
    action_results = []

    if actions:
        # 群組模式傳入 group_id 和使用者資訊，讓 execute_actions 處理群組訂單
        action_results = ai.execute_actions(
            username, actions, is_manager,
            group_id if group_ordering else None,
            line_user_id if group_ordering else None,
            display_name if group_ordering else None
        )

        # 廣播每個動作的事件
        if group_ordering:
            # 群組模式：廣播訂單更新事件
            for result in action_results:
                if result.get("success"):
                    session = get_group_session(group_id)
                    await broadcast_event("group_order_updated", {
                        "group_id": group_id,
                        "user": display_name or username,
                        "order_count": len(session.get("orders", [])) if session else 0,
                        "total_amount": sum(o.get("total", 0) for o in session.get("orders", [])) if session else 0
                    })
                    break  # 只發送一次事件
        else:
            # 個人模式：廣播各類事件
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


@app.get("/api/board/chat")
async def get_board_chat():
    """取得看板用的所有群組聚合對話（當日）"""
    messages = data.get_board_chat_messages(max_messages=50)
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


# === LINE Bot 群組點餐 Session ===

def get_group_session(group_id: str) -> dict | None:
    """取得群組點餐 session"""
    session_file = data.DATA_DIR / "linebot" / "sessions" / f"{group_id}.json"
    if session_file.exists():
        return data.read_json(session_file)
    return None


def save_group_session(group_id: str, session: dict):
    """儲存群組點餐 session"""
    sessions_dir = data.DATA_DIR / "linebot" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    data.write_json(sessions_dir / f"{group_id}.json", session)


def is_group_ordering(group_id: str) -> bool:
    """檢查群組是否在點餐中"""
    session = get_group_session(group_id)
    if session and session.get("status") == "ordering":
        return True
    return False


def start_group_session(group_id: str, started_by: dict) -> dict:
    """開始群組點餐 session

    Args:
        started_by: 啟動者資訊，包含 line_user_id 和 display_name
    """
    session = {
        "group_id": group_id,
        "status": "ordering",
        "started_at": datetime.now().isoformat(),
        "started_by": {
            "line_user_id": started_by.get("line_user_id", started_by.get("user_id", "")),
            "display_name": started_by.get("display_name", "")
        },
        "orders": [],
        "payments": {}
    }
    save_group_session(group_id, session)
    return session


def end_group_session(group_id: str) -> dict | None:
    """結束群組點餐 session，回傳含訂單摘要的 session"""
    session = get_group_session(group_id)
    if session:
        session["status"] = "ended"
        session["ended_at"] = datetime.now().isoformat()
        save_group_session(group_id, session)
    return session


def add_order_to_session(group_id: str, line_user_id: str, display_name: str, order: dict) -> bool:
    """將訂單加入群組 session

    Args:
        group_id: 群組 ID
        line_user_id: LINE User ID
        display_name: LINE 顯示名稱
        order: 訂單資料（包含 items, total 等）

    Returns:
        是否成功加入
    """
    session = get_group_session(group_id)
    if not session or session.get("status") != "ordering":
        return False

    # 建立簡化的訂單記錄
    order_record = {
        "line_user_id": line_user_id,
        "display_name": display_name,
        "order_id": order.get("order_id"),
        "store_name": order.get("store_name"),
        "items": [
            {
                "name": item.get("name"),
                "quantity": item.get("quantity", 1),
                "price": item.get("price"),
                "subtotal": item.get("subtotal"),
                "note": item.get("note", "")
            }
            for item in order.get("items", [])
        ],
        "total": order.get("total", 0),
        "created_at": order.get("created_at")
    }

    session["orders"].append(order_record)

    # 更新付款記錄
    _update_session_payment(session, line_user_id, display_name)

    save_group_session(group_id, session)
    return True


def _update_session_payment(session: dict, line_user_id: str, display_name: str) -> None:
    """更新 session 中某使用者的付款記錄

    Args:
        session: 群組 session
        line_user_id: LINE User ID
        display_name: LINE 顯示名稱
    """
    # 確保 payments 欄位存在
    if "payments" not in session:
        session["payments"] = {}

    # 計算該使用者的總金額
    user_total = sum(
        order.get("total", 0)
        for order in session.get("orders", [])
        if order.get("line_user_id") == line_user_id
    )

    # 取得或建立付款記錄
    if line_user_id in session["payments"]:
        payment = session["payments"][line_user_id]
        old_amount = payment.get("amount", 0)
        paid_amount = payment.get("paid_amount", 0)
        payment["amount"] = user_total
        payment["display_name"] = display_name

        # 智慧更新付款狀態
        if paid_amount > 0 and old_amount != user_total:
            if user_total > paid_amount:
                payment["paid"] = False
                payment["note"] = f"已付 ${paid_amount}，待補 ${user_total - paid_amount}"
            elif user_total < paid_amount:
                payment["paid"] = True
                payment["note"] = f"待退 ${paid_amount - user_total}"
            else:
                payment["paid"] = True
                payment["note"] = ""
    else:
        session["payments"][line_user_id] = {
            "display_name": display_name,
            "amount": user_total,
            "paid": False,
            "paid_amount": 0,
            "paid_at": None,
            "note": ""
        }


def _get_today_menu_summary() -> str:
    """取得今日菜單摘要（簡潔格式，供群組點餐使用）

    Returns:
        格式化的菜單摘要文字
    """
    today_info = data.get_today_info()
    today_stores = today_info.get("stores", [])

    if not today_stores:
        return ""

    lines = ["📋 今日菜單"]

    for store_ref in today_stores:
        store_id = store_ref.get("store_id")
        store_name = store_ref.get("store_name", store_id)
        menu = data.get_menu(store_id)

        if not menu:
            continue

        lines.append(f"\n【{store_name}】")

        for cat in menu.get("categories", []):
            cat_name = cat.get("name", "")
            items = cat.get("items", [])

            if not items:
                continue

            # 分類標題
            if cat_name:
                lines.append(f"▸ {cat_name}")

            # 每個品項一行
            for item in items:
                name = item.get("name")
                price = item.get("price")
                variants = item.get("variants", [])

                if variants:
                    # 有尺寸變體（如 M/L）
                    var_strs = [f"{v.get('size', '')}${v.get('price', 0)}" for v in variants]
                    lines.append(f"  {name} {'/'.join(var_strs)}")
                elif price:
                    lines.append(f"  {name} ${price}")
                else:
                    lines.append(f"  {name}")

    return "\n".join(lines) if len(lines) > 1 else ""


def generate_session_summary(session: dict) -> str:
    """產生群組點餐摘要

    Args:
        session: 群組 session 資料

    Returns:
        格式化的訂單摘要文字
    """
    orders = session.get("orders", [])

    if not orders:
        return "📋 本次點餐沒有任何訂單"

    # 依使用者分組（優先使用 line_user_id，其次 username 作為向後相容）
    user_orders = {}
    user_display_names = {}
    for order in orders:
        user_key = order.get("line_user_id") or order.get("username", "未知")
        display_name = order.get("display_name") or order.get("username", "未知")
        if user_key not in user_orders:
            user_orders[user_key] = []
            user_display_names[user_key] = display_name
        user_orders[user_key].append(order)

    # 統計品項
    item_counts = {}
    grand_total = 0

    lines = ["📋 點餐摘要", ""]

    # 各人訂單
    for user_key, user_order_list in user_orders.items():
        display_name = user_display_names.get(user_key, "未知")
        user_total = 0
        user_items = []
        for order in user_order_list:
            for item in order.get("items", []):
                name = item.get("name")
                qty = item.get("quantity", 1)
                subtotal = item.get("subtotal", 0)
                note = item.get("note", "")

                # 組合品項顯示（包含備註）
                item_text = f"  • {name}"
                if note:
                    item_text += f"（{note}）"
                if qty > 1:
                    item_text += f" x{qty}"
                item_text += f" ${subtotal}"
                user_items.append(item_text)
                user_total += subtotal

                # 統計總品項（包含備註作為區分）
                item_key = f"{name}（{note}）" if note else name
                if item_key not in item_counts:
                    item_counts[item_key] = 0
                item_counts[item_key] += qty

        lines.append(f"👤 {display_name}（${user_total}）")
        lines.extend(user_items)
        lines.append("")
        grand_total += user_total

    # 品項統計
    lines.append("📦 品項統計")
    for name, count in sorted(item_counts.items(), key=lambda x: -x[1]):
        lines.append(f"  • {name} x{count}")

    lines.append("")
    lines.append(f"💰 總金額：${grand_total}")
    lines.append(f"👥 共 {len(user_orders)} 人點餐")

    return "\n".join(lines)


# === 群組訂單操作（獨立於個人訂單）===

def group_create_order(group_id: str, line_user_id: str, display_name: str, items: list) -> dict:
    """群組點餐：建立訂單（只儲存在 session 中）

    Args:
        group_id: 群組 ID
        line_user_id: LINE User ID
        display_name: LINE 顯示名稱
        items: 品項列表 [{"name": "...", "quantity": 1, "note": "..."}]

    Returns:
        {"success": True, "order": {...}} 或 {"success": False, "error": "..."}
    """
    session = get_group_session(group_id)
    if not session or session.get("status") != "ordering":
        return {"success": False, "error": "群組不在點餐中"}

    # 取得今日店家菜單
    today_info = data.get_today_info()
    today_stores = today_info.get("stores", [])

    if not today_stores:
        return {"success": False, "error": "今日尚未設定店家"}

    # 查找品項價格
    enriched_items = []
    total = 0

    for item in items:
        item_name = item.get("name", "")
        quantity = item.get("quantity", 1)
        note = item.get("note", "")

        # 從菜單找價格
        price = 0
        found = False
        for store_ref in today_stores:
            store_id = store_ref.get("store_id")
            menu = data.get_menu(store_id)
            if menu:
                for cat in menu.get("categories", []):
                    for mi in cat.get("items", []):
                        if mi.get("name") == item_name or item_name in mi.get("name", ""):
                            price = mi.get("price", 0)
                            found = True
                            break
                    if found:
                        break
            if found:
                break

        subtotal = price * quantity
        enriched_items.append({
            "name": item_name,
            "quantity": quantity,
            "price": price,
            "subtotal": subtotal,
            "note": note
        })
        total += subtotal

    # 建立訂單記錄
    order = {
        "line_user_id": line_user_id,
        "display_name": display_name,
        "items": enriched_items,
        "total": total,
        "created_at": datetime.now().isoformat()
    }

    # 加入 session
    session["orders"].append(order)

    # 更新付款記錄
    _update_session_payment(session, line_user_id, display_name)

    save_group_session(group_id, session)

    return {"success": True, "order": order}


def group_remove_item(group_id: str, line_user_id: str, item_name: str, quantity: int = 1) -> dict:
    """群組點餐：移除品項

    Args:
        group_id: 群組 ID
        line_user_id: LINE User ID
        item_name: 品項名稱
        quantity: 移除數量

    Returns:
        {"success": True} 或 {"success": False, "error": "..."}
    """
    session = get_group_session(group_id)
    if not session or session.get("status") != "ordering":
        return {"success": False, "error": "群組不在點餐中"}

    # 找到該使用者的訂單
    display_name = None
    for order in session["orders"]:
        if order.get("line_user_id") != line_user_id:
            continue

        display_name = order.get("display_name", "")

        # 找到品項
        for i, item in enumerate(order.get("items", [])):
            if item.get("name") == item_name or item_name in item.get("name", ""):
                current_qty = item.get("quantity", 1)
                if quantity >= current_qty:
                    # 移除整個品項
                    order["items"].pop(i)
                else:
                    # 減少數量
                    item["quantity"] = current_qty - quantity
                    item["subtotal"] = item.get("price", 0) * item["quantity"]

                # 重新計算總額
                order["total"] = sum(it.get("subtotal", 0) for it in order.get("items", []))

                # 如果訂單沒有品項了，移除整筆訂單
                if not order["items"]:
                    session["orders"].remove(order)

                # 更新付款記錄
                if display_name:
                    _update_session_payment(session, line_user_id, display_name)

                save_group_session(group_id, session)
                return {"success": True}

    return {"success": False, "error": f"找不到品項：{item_name}"}


def group_cancel_order(group_id: str, line_user_id: str) -> dict:
    """群組點餐：取消使用者的所有訂單

    Args:
        group_id: 群組 ID
        line_user_id: LINE User ID

    Returns:
        {"success": True} 或 {"success": False, "error": "..."}
    """
    session = get_group_session(group_id)
    if not session or session.get("status") != "ordering":
        return {"success": False, "error": "群組不在點餐中"}

    # 取得該使用者的 display_name
    display_name = None
    for order in session["orders"]:
        if order.get("line_user_id") == line_user_id:
            display_name = order.get("display_name", "")
            break

    # 移除該使用者的所有訂單
    original_count = len(session["orders"])
    session["orders"] = [o for o in session["orders"] if o.get("line_user_id") != line_user_id]

    if len(session["orders"]) == original_count:
        return {"success": False, "error": "你目前沒有訂單"}

    # 更新付款記錄（金額會變成 0）
    if display_name:
        _update_session_payment(session, line_user_id, display_name)

    save_group_session(group_id, session)
    return {"success": True}


def group_update_order(group_id: str, line_user_id: str, display_name: str, old_item: str, new_item: dict) -> dict:
    """群組點餐：修改訂單（替換品項）

    Args:
        group_id: 群組 ID
        line_user_id: LINE User ID
        display_name: LINE 顯示名稱
        old_item: 原品項名稱
        new_item: 新品項 {"name": "...", "quantity": 1}

    Returns:
        {"success": True} 或 {"success": False, "error": "..."}
    """
    # 先移除舊品項
    result = group_remove_item(group_id, line_user_id, old_item, quantity=999)
    if not result.get("success"):
        return result

    # 新增新品項
    return group_create_order(group_id, line_user_id, display_name, [new_item])


# === 超級管理員 API ===

@app.get("/api/super-admin/groups")
async def super_admin_get_groups():
    """取得所有已啟用群組列表（超級管理員用）

    回傳格式：
    {
        "groups": [
            {
                "id": "Cxxxxxxxxxxxxxxxxx",
                "name": "午餐群組",
                "activated_at": "2025-12-09T10:00:00",
                "member_count": 5,
                "order_count": 3,
                "total_amount": 255
            }
        ]
    }
    """
    whitelist = get_linebot_whitelist()
    groups = []

    for group in whitelist.get("groups", []):
        group_id = group.get("id")
        session = get_group_session(group_id)

        # 計算訂單統計
        order_count = 0
        total_amount = 0
        member_ids = set()

        if session:
            orders = session.get("orders", [])
            for order in orders:
                user_id = order.get("line_user_id") or order.get("username")
                if user_id:
                    member_ids.add(user_id)
                total_amount += order.get("total", 0)
            order_count = len(orders)

        groups.append({
            "id": group_id,
            "name": group.get("name", ""),
            "activated_at": group.get("registered_at"),
            "member_count": len(member_ids),
            "order_count": order_count,
            "total_amount": total_amount
        })

    return {"groups": groups}


@app.get("/api/super-admin/groups/{group_id}/orders")
async def super_admin_get_group_orders(group_id: str):
    """取得指定群組的訂單（超級管理員用）

    回傳格式：
    {
        "group_id": "Cxxxxxxxxxxxxxxxxx",
        "group_name": "午餐群組",
        "status": "ended",
        "orders": [
            {
                "line_user_id": "Uxxxxxxxxxxxxxxxxx",
                "display_name": "王小明",
                "items": [...],
                "total": 85
            }
        ],
        "payments": {...},
        "summary": {...}
    }
    """
    # 確認群組存在
    whitelist = get_linebot_whitelist()
    group_info = next((g for g in whitelist.get("groups", []) if g["id"] == group_id), None)

    if not group_info:
        return JSONResponse({"error": "群組不存在"}, status_code=404)

    session = get_group_session(group_id)

    if not session:
        return {
            "group_id": group_id,
            "group_name": group_info.get("name", ""),
            "status": "no_session",
            "orders": [],
            "payments": {},
            "summary": {
                "order_count": 0,
                "total_amount": 0,
                "paid_amount": 0,
                "pending_amount": 0
            }
        }

    # 整理訂單（依使用者分組）
    user_orders = {}
    for order in session.get("orders", []):
        user_id = order.get("line_user_id") or order.get("username", "")
        display_name = order.get("display_name") or order.get("username", "")

        if user_id not in user_orders:
            user_orders[user_id] = {
                "line_user_id": user_id,
                "display_name": display_name,
                "items": [],
                "total": 0
            }

        # 合併品項
        for item in order.get("items", []):
            user_orders[user_id]["items"].append(item)
        user_orders[user_id]["total"] += order.get("total", 0)

    orders_list = list(user_orders.values())

    # 計算統計
    total_amount = sum(o["total"] for o in orders_list)
    payments = session.get("payments", {})
    paid_amount = sum(p.get("paid_amount", 0) for p in payments.values())

    return {
        "group_id": group_id,
        "group_name": group_info.get("name", ""),
        "status": session.get("status", "unknown"),
        "orders": orders_list,
        "payments": payments,
        "summary": {
            "order_count": len(orders_list),
            "total_amount": total_amount,
            "paid_amount": paid_amount,
            "pending_amount": total_amount - paid_amount
        }
    }


@app.get("/api/super-admin/groups/{group_id}/chat")
async def super_admin_get_group_chat(group_id: str):
    """取得指定群組的對話記錄（超級管理員用）

    回傳格式：
    {
        "group_id": "Cxxxxxxxxxxxxxxxxx",
        "group_name": "午餐群組",
        "messages": [
            {"username": "林亞澤", "role": "user", "content": "我要雞腿便當", "timestamp": "..."},
            {"username": "呷爸", "role": "assistant", "content": "好喔...", "timestamp": "..."}
        ]
    }
    """
    # 取得群組名稱
    whitelist = get_linebot_whitelist()
    group_info = next((g for g in whitelist.get("groups", []) if g["id"] == group_id), None)
    group_name = group_info.get("name", "") if group_info else ""

    # 取得對話記錄
    messages = data.get_group_chat_history(group_id, max_messages=50)

    return {
        "group_id": group_id,
        "group_name": group_name,
        "messages": messages
    }


@app.post("/api/super-admin/groups/{group_id}/orders")
async def super_admin_create_proxy_order(group_id: str, request: Request):
    """代理點餐（超級管理員用）

    請求格式：
    {
        "line_user_id": "Uxxxxxxxxxxxxxxxxx",
        "display_name": "王小明",
        "items": [
            {"name": "雞腿便當", "quantity": 1, "note": ""}
        ]
    }
    """
    body = await request.json()
    line_user_id = body.get("line_user_id")
    display_name = body.get("display_name", "")
    items = body.get("items", [])

    if not line_user_id:
        return JSONResponse({"error": "缺少 line_user_id"}, status_code=400)
    if not items:
        return JSONResponse({"error": "缺少品項"}, status_code=400)

    # 確認群組存在且在點餐中
    session = get_group_session(group_id)
    if not session:
        return JSONResponse({"error": "群組沒有進行中的點餐"}, status_code=400)
    if session.get("status") != "ordering":
        return JSONResponse({"error": "群組點餐已結束"}, status_code=400)

    # 確保使用者存在
    data.ensure_user_by_line_id(line_user_id, display_name)

    # 建立訂單
    result = group_create_order(group_id, line_user_id, display_name, items)
    return result


@app.put("/api/super-admin/groups/{group_id}/orders/{user_id}")
async def super_admin_update_order(group_id: str, user_id: str, request: Request):
    """修改使用者訂單（超級管理員用）

    請求格式：
    {
        "items": [
            {"name": "排骨便當", "quantity": 2, "note": "不要酸菜"}
        ]
    }
    """
    body = await request.json()
    items = body.get("items", [])

    if not items:
        return JSONResponse({"error": "缺少品項"}, status_code=400)

    session = get_group_session(group_id)
    if not session:
        return JSONResponse({"error": "群組沒有點餐記錄"}, status_code=404)

    # 找到該使用者的訂單並取得 display_name
    display_name = None
    for order in session.get("orders", []):
        if order.get("line_user_id") == user_id:
            display_name = order.get("display_name", "")
            break

    if display_name is None:
        return JSONResponse({"error": "找不到該使用者的訂單"}, status_code=404)

    # 先取消原訂單
    group_cancel_order(group_id, user_id)

    # 重新建立訂單
    result = group_create_order(group_id, user_id, display_name, items)
    return result


@app.delete("/api/super-admin/groups/{group_id}/orders/{user_id}")
async def super_admin_delete_order(group_id: str, user_id: str):
    """刪除使用者訂單（超級管理員用）"""
    session = get_group_session(group_id)
    if not session:
        return JSONResponse({"error": "群組沒有點餐記錄"}, status_code=404)

    # 檢查使用者是否有訂單
    has_order = any(o.get("line_user_id") == user_id for o in session.get("orders", []))
    if not has_order:
        return JSONResponse({"error": "找不到該使用者的訂單"}, status_code=404)

    # 取消訂單
    result = group_cancel_order(group_id, user_id)

    # 如果已付款，標記待退款
    payments = session.get("payments", {})
    if user_id in payments:
        payment = payments[user_id]
        paid_amount = payment.get("paid_amount", 0)
        if paid_amount > 0:
            payment["note"] = f"待退 ${paid_amount}"
            payment["amount"] = 0
            save_group_session(group_id, session)

    return result


@app.post("/api/super-admin/groups/{group_id}/payments/{user_id}/mark-paid")
async def super_admin_mark_paid(group_id: str, user_id: str):
    """標記已付款（超級管理員用）"""
    session = get_group_session(group_id)
    if not session:
        return JSONResponse({"error": "群組沒有點餐記錄"}, status_code=404)

    payments = session.get("payments", {})
    if user_id not in payments:
        return JSONResponse({"error": "找不到該使用者的付款記錄"}, status_code=404)

    payment = payments[user_id]
    payment["paid"] = True
    payment["paid_amount"] = payment.get("amount", 0)
    payment["paid_at"] = datetime.now().isoformat()
    payment["note"] = ""

    save_group_session(group_id, session)
    return {"success": True, "payment": payment}


@app.post("/api/super-admin/groups/{group_id}/payments/{user_id}/refund")
async def super_admin_mark_refund(group_id: str, user_id: str):
    """標記已退款（超級管理員用）"""
    session = get_group_session(group_id)
    if not session:
        return JSONResponse({"error": "群組沒有點餐記錄"}, status_code=404)

    payments = session.get("payments", {})
    if user_id not in payments:
        return JSONResponse({"error": "找不到該使用者的付款記錄"}, status_code=404)

    payment = payments[user_id]
    current_amount = payment.get("amount", 0)

    # 退款後，paid_amount 調整為等於 amount
    payment["paid_amount"] = current_amount
    if current_amount > 0:
        payment["paid"] = True
    payment["note"] = ""

    save_group_session(group_id, session)
    return {"success": True, "payment": payment}


# === LINE Bot 白名單 API ===

@app.post("/api/linebot/register")
async def linebot_register(request: Request):
    """註冊 LINE Bot 使用者或群組"""
    body = await request.json()
    id_type = body.get("type")  # "user" 或 "group"
    id_value = body.get("id")
    name = body.get("name", "")
    activated_by = body.get("activated_by", {})  # 啟用者資訊

    if not id_type or not id_value:
        return JSONResponse({"error": "缺少 type 或 id"}, status_code=400)

    whitelist = get_linebot_whitelist()

    # 建立基本資料
    entry = {
        "id": id_value,
        "name": name,
        "registered_at": datetime.now().isoformat()
    }

    # 如果有啟用者資訊，加入記錄
    if activated_by and activated_by.get("user_id"):
        entry["activated_by"] = {
            "user_id": activated_by.get("user_id", ""),
            "display_name": activated_by.get("display_name", "")
        }

    if id_type == "user":
        # 檢查是否已註冊
        existing = next((u for u in whitelist["users"] if u["id"] == id_value), None)
        if existing:
            # 更新名稱（如果有提供）
            if name and name != existing.get("name"):
                existing["name"] = name
                save_linebot_whitelist(whitelist)
            return {"success": True, "message": "已經註冊過了", "already_registered": True}
        whitelist["users"].append(entry)
    elif id_type == "group":
        existing = next((g for g in whitelist["groups"] if g["id"] == id_value), None)
        if existing:
            # 更新群組名稱（如果有提供）
            if name and name != existing.get("name"):
                existing["name"] = name
                save_linebot_whitelist(whitelist)
            return {"success": True, "message": "此群組已經註冊過了", "already_registered": True}
        whitelist["groups"].append(entry)
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

    # 清除相關資料
    sessions_dir = data.DATA_DIR / "linebot" / "sessions"
    session_file = sessions_dir / f"{id_value}.json"
    chat_file = sessions_dir / f"{id_value}-chat.json"

    if session_file.exists():
        session_file.unlink()
    if chat_file.exists():
        chat_file.unlink()

    return {"success": True, "message": "已取消註冊"}


@app.get("/api/linebot/session/{group_id}")
async def linebot_get_session(group_id: str):
    """檢查群組是否在點餐中"""
    ordering = is_group_ordering(group_id)
    if ordering:
        session = get_group_session(group_id)
        return {
            "ordering": True,
            "started_at": session.get("started_at"),
            "started_by": session.get("started_by")
        }
    return {"ordering": False}


# === 啟動應用 ===

if __name__ == "__main__":
    import uvicorn
    config = data.get_config()
    port = config.get("server_port", 8098)
    uvicorn.run(socket_app, host="0.0.0.0", port=port)
