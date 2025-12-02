"""Claude CLI 整合模組"""
import subprocess
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from . import data


def get_system_prompt(is_manager: bool = False) -> str:
    """取得系統提示詞"""
    prompt_data = data.get_jiaba_prompt()
    base_prompt = prompt_data.get("system_prompt", "")

    if is_manager:
        return f"""{base_prompt}

你現在是管理員模式，可以執行以下額外動作：
- set_today_store: 設定今日店家 (data: {{"store_id": "...", "store_name": "..."}})
- create_store: 新增店家 (data: {{"id": "...", "name": "...", "phone": "...", "address": "...", "description": "..."}})
- update_store: 更新店家資訊 (data: {{"store_id": "...", ...欄位}})
- update_menu: 更新菜單 (data: {{"store_id": "...", "categories": [...]}})
- mark_paid: 標記已付款 (data: {{"username": "...", "date": "..."}})
- query_payments: 查詢付款狀態 (data: {{"date": "..."}})
- query_all_orders: 查詢所有訂單 (data: {{"date": "..."}})

請用繁體中文回應。"""

    return f"""{base_prompt}

請用繁體中文回應。回應格式必須是 JSON：
{{"message": "給使用者的訊息", "action": {{"type": "動作類型", "data": {{...}}}} 或 null}}

如果不需要執行動作，action 可以是 null。"""


def build_context(username: str, is_manager: bool = False) -> dict:
    """建立 AI 上下文"""
    today_info = data.get_today_info()
    stores = data.get_active_stores()

    context = {
        "today": date.today().isoformat(),
        "today_store": today_info,
        "available_stores": [{"id": s["id"], "name": s["name"]} for s in stores],
    }

    if today_info.get("store_id"):
        menu = data.get_menu(today_info["store_id"])
        if menu:
            context["menu"] = menu

    if not is_manager:
        context["username"] = username
        user_order = data.get_user_order(username)
        if user_order:
            context["current_order"] = user_order

    if is_manager:
        summary = data.get_daily_summary()
        if summary:
            context["today_summary"] = summary
        payments = data.get_payments()
        if payments:
            context["payments"] = payments

    return context


def call_claude(
    username: str,
    message: str,
    is_manager: bool = False
) -> dict:
    """呼叫 Claude CLI"""
    # 確保使用者存在
    data.ensure_user(username)

    # 取得或建立 session
    session_id = data.get_session_id(username)
    system_prompt = get_system_prompt(is_manager)
    context = build_context(username, is_manager)

    # 組合完整訊息
    context_str = json.dumps(context, ensure_ascii=False, indent=2)
    full_message = f"""[系統上下文]
{context_str}

[使用者訊息]
{message}

請以 JSON 格式回應：{{"message": "...", "action": {{"type": "...", "data": {{...}}}} 或 null}}"""

    # 建立命令
    cmd = ["claude", "-p"]

    if session_id:
        cmd.extend(["--resume", session_id])
    else:
        cmd.extend(["--append-system-prompt", system_prompt])

    cmd.append(full_message)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(data.DATA_DIR.parent)
        )

        response_text = result.stdout.strip()

        # 嘗試從輸出中提取 session ID
        # Claude CLI 會在輸出中包含 session 資訊
        if not session_id and result.stderr:
            # 嘗試解析 session ID
            session_match = re.search(r'session[:\s]+([a-f0-9-]+)', result.stderr, re.I)
            if session_match:
                new_session_id = session_match.group(1)
                data.save_session_id(username, new_session_id)

        # 嘗試解析 JSON 回應
        try:
            # 尋找 JSON 內容
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                response = json.loads(json_match.group())
                return response
            else:
                return {
                    "message": response_text,
                    "action": None
                }
        except json.JSONDecodeError:
            return {
                "message": response_text,
                "action": None
            }

    except subprocess.TimeoutExpired:
        return {
            "message": "抱歉，回應超時了，請再試一次。",
            "action": None,
            "error": "timeout"
        }
    except Exception as e:
        return {
            "message": f"發生錯誤：{str(e)}",
            "action": None,
            "error": str(e)
        }


def execute_action(username: str, action: dict) -> dict:
    """執行 AI 請求的動作"""
    if not action:
        return {"success": True}

    action_type = action.get("type")
    action_data = action.get("data", {})

    try:
        if action_type == "create_order":
            return _create_order(username, action_data)
        elif action_type == "update_order":
            return _update_order(username, action_data)
        elif action_type == "cancel_order":
            return _cancel_order(username, action_data)
        elif action_type == "set_today_store":
            return _set_today_store(action_data)
        elif action_type == "create_store":
            return _create_store(action_data)
        elif action_type == "update_store":
            return _update_store(action_data)
        elif action_type == "update_menu":
            return _update_menu(action_data)
        elif action_type == "mark_paid":
            return _mark_paid(action_data)
        else:
            return {"success": True, "message": "No action needed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _create_order(username: str, action_data: dict) -> dict:
    """建立訂單"""
    from datetime import datetime

    today_info = data.get_today_info()
    if not today_info.get("store_id"):
        return {"success": False, "error": "今日尚未設定店家"}

    items = action_data.get("items", [])
    menu = data.get_menu(today_info["store_id"])

    # 補充品項資訊
    enriched_items = []
    total = 0
    for item in items:
        item_id = item.get("id")
        quantity = item.get("quantity", 1)
        note = item.get("note", "")

        # 從菜單找價格和名稱
        menu_item = None
        if menu:
            for cat in menu.get("categories", []):
                for mi in cat.get("items", []):
                    if mi["id"] == item_id:
                        menu_item = mi
                        break

        if menu_item:
            enriched_items.append({
                "id": item_id,
                "name": menu_item["name"],
                "price": menu_item["price"],
                "quantity": quantity,
                "note": note
            })
            total += menu_item["price"] * quantity

    order = {
        "date": date.today().isoformat(),
        "username": username,
        "store_id": today_info["store_id"],
        "store_name": today_info["store_name"],
        "items": enriched_items,
        "total": total,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }

    data.save_user_order(username, order)
    summary = data.update_daily_summary_with_order(username, order)

    return {
        "success": True,
        "order": order,
        "summary": summary,
        "event": "order_created"
    }


def _update_order(username: str, action_data: dict) -> dict:
    """更新訂單"""
    # 類似 create_order，但更新現有訂單
    return _create_order(username, action_data)


def _cancel_order(username: str, action_data: dict) -> dict:
    """取消訂單"""
    order_date = action_data.get("date", date.today().isoformat())
    order = data.get_user_order(username, order_date)

    if not order:
        return {"success": False, "error": "找不到訂單"}

    # 從彙整中移除
    summary = data.get_daily_summary(order_date)
    if summary:
        summary["orders"] = [o for o in summary["orders"] if o["username"] != username]
        # 重新計算
        item_counts = {}
        for o in summary["orders"]:
            for item in o["items"]:
                name = item["name"]
                qty = item.get("quantity", 1)
                item_counts[name] = item_counts.get(name, 0) + qty
        summary["item_summary"] = [{"name": k, "quantity": v} for k, v in item_counts.items()]
        summary["grand_total"] = sum(o["total"] for o in summary["orders"])
        data.save_daily_summary(summary)

    # 刪除使用者訂單檔案
    order_file = data.DATA_DIR / "users" / username / "orders" / f"{order_date}.json"
    if order_file.exists():
        order_file.unlink()

    return {
        "success": True,
        "event": "order_cancelled",
        "summary": summary
    }


def _set_today_store(action_data: dict) -> dict:
    """設定今日店家"""
    store_id = action_data.get("store_id")
    store_name = action_data.get("store_name")

    if not store_id:
        return {"success": False, "error": "缺少 store_id"}

    # 如果沒有提供 store_name，從店家資料取得
    if not store_name:
        store = data.get_store(store_id)
        if store:
            store_name = store["name"]
        else:
            return {"success": False, "error": "找不到店家"}

    today_info = data.set_today_store(store_id, store_name)
    return {"success": True, "today": today_info, "event": "store_changed"}


def _create_store(action_data: dict) -> dict:
    """新增店家"""
    from datetime import datetime

    store_id = action_data.get("id")
    if not store_id:
        return {"success": False, "error": "缺少店家 ID"}

    info = {
        "id": store_id,
        "name": action_data.get("name", store_id),
        "phone": action_data.get("phone", ""),
        "address": action_data.get("address", ""),
        "description": action_data.get("description", ""),
        "active": True,
        "created_at": datetime.now().isoformat()
    }

    data.save_store(store_id, info)

    # 建立空菜單
    menu = {
        "store_id": store_id,
        "updated_at": datetime.now().isoformat(),
        "categories": []
    }
    data.save_menu(store_id, menu)

    return {"success": True, "store": info}


def _update_store(action_data: dict) -> dict:
    """更新店家資訊"""
    store_id = action_data.get("store_id")
    if not store_id:
        return {"success": False, "error": "缺少 store_id"}

    info = data.get_store(store_id)
    if not info:
        return {"success": False, "error": "找不到店家"}

    # 更新欄位
    for key in ["name", "phone", "address", "description", "active"]:
        if key in action_data:
            info[key] = action_data[key]

    data.save_store(store_id, info)
    return {"success": True, "store": info}


def _update_menu(action_data: dict) -> dict:
    """更新菜單"""
    from datetime import datetime

    store_id = action_data.get("store_id")
    if not store_id:
        return {"success": False, "error": "缺少 store_id"}

    categories = action_data.get("categories")
    if categories is None:
        return {"success": False, "error": "缺少 categories"}

    menu = {
        "store_id": store_id,
        "updated_at": datetime.now().isoformat(),
        "categories": categories
    }

    data.save_menu(store_id, menu)
    return {"success": True, "menu": menu}


def _mark_paid(action_data: dict) -> dict:
    """標記已付款"""
    from datetime import datetime

    username = action_data.get("username")
    order_date = action_data.get("date", date.today().isoformat())

    if not username:
        return {"success": False, "error": "缺少 username"}

    payments = data.get_payments(order_date)
    if not payments:
        return {"success": False, "error": "找不到付款記錄"}

    record = next((r for r in payments["records"] if r["username"] == username), None)
    if not record:
        return {"success": False, "error": "找不到該使用者的付款記錄"}

    record["paid"] = True
    record["paid_at"] = datetime.now().isoformat()

    # 重新計算總額
    payments["total_collected"] = sum(r["amount"] for r in payments["records"] if r["paid"])
    payments["total_pending"] = sum(r["amount"] for r in payments["records"] if not r["paid"])

    data.save_payments(payments)
    return {"success": True, "payments": payments}
