"""Claude CLI 整合模組"""
import subprocess
import json
import re
import uuid
from datetime import date
from pathlib import Path
from typing import Any

from . import data


def get_system_prompt(is_manager: bool = False) -> str:
    """取得系統提示詞"""
    prompt_data = data.get_jaba_prompt()

    if is_manager:
        # 管理員模式：載入 manager_prompt
        base_prompt = prompt_data.get("manager_prompt", "")
        return f"""{base_prompt}

請用繁體中文回應。"""

    # 一般使用者模式：載入 user_prompt（已包含完整的動作說明和格式）
    base_prompt = prompt_data.get("user_prompt", "")
    return f"""{base_prompt}

請用繁體中文回應。"""


def build_context(username: str, is_manager: bool = False) -> dict:
    """建立 AI 上下文"""
    today_info = data.get_today_info()
    stores = data.get_active_stores()

    context = {
        "today": date.today().isoformat(),
        "today_store": today_info,
        "available_stores": [{"id": s["id"], "name": s["name"], "note": s.get("note", "")} for s in stores],
    }

    # 支援多店家：提供所有今日店家的菜單
    today_stores = today_info.get("stores", [])
    if today_stores:
        context["today_menus"] = {}
        for store_ref in today_stores:
            store_id = store_ref.get("store_id")
            store_info = data.get_store(store_id)
            menu = data.get_menu(store_id)
            if menu:
                context["today_menus"][store_id] = {
                    "store_name": store_ref.get("store_name", ""),
                    "note": store_info.get("note", "") if store_info else "",
                    "menu": menu
                }

    if not is_manager:
        context["username"] = username
        # 取得使用者 profile（包含偏好設定）
        profile = data.get_user_profile(username)
        if profile:
            context["user_profile"] = profile.get("preferences", {})
        # 取得使用者所有訂單
        user_orders = data.get_user_orders(username)
        if user_orders:
            context["current_orders"] = user_orders

    if is_manager:
        summary = data.get_daily_summary()
        if summary:
            context["today_summary"] = summary
        payments = data.get_payments()
        if payments:
            context["payments"] = payments
        # 提供過去 7 天的店家歷史記錄，供 AI 建議今日店家
        context["recent_store_history"] = _get_recent_store_history(7)

    return context


def _get_recent_store_history(days: int = 7) -> list:
    """取得過去 N 天的店家訂餐記錄"""
    from datetime import timedelta
    history = []
    today = date.today()

    for i in range(1, days + 1):
        past_date = today - timedelta(days=i)
        date_str = past_date.isoformat()
        summary = data.get_daily_summary(date_str)
        if summary and summary.get("store_name"):
            history.append({
                "date": date_str,
                "store_id": summary.get("store_id"),
                "store_name": summary.get("store_name"),
                "order_count": len(summary.get("orders", [])),
                "grand_total": summary.get("grand_total", 0)
            })

    return history


def call_claude(
    username: str,
    message: str,
    is_manager: bool = False
) -> dict:
    """呼叫 Claude CLI"""
    # 確保使用者存在
    data.ensure_user(username)

    # 取得或建立 session（管理員和一般模式分開）
    session_id = data.get_session_id(username, is_manager)
    system_prompt = get_system_prompt(is_manager)
    context = build_context(username, is_manager)

    # 組合完整訊息
    context_str = json.dumps(context, ensure_ascii=False, indent=2)
    full_message = f"""[系統上下文]
{context_str}

[使用者訊息]
{message}

請以 JSON 格式回應：
{{"message": "你的回應訊息", "actions": [{{"type": "動作類型", "data": {{...}}}}, ...] }}

如果不需要執行動作，actions 可以是空陣列 []。
如果需要執行多個步驟，在 actions 陣列中一次回傳所有動作。"""

    # 取得模型設定
    ai_config = data.get_ai_config()
    model = ai_config.get("chat", {}).get("model", "haiku")

    # 建立命令（Claude CLI 支援直接使用 sonnet/opus/haiku 等簡稱）
    cmd = ["claude", "-p", "--model", model, "--system-prompt", system_prompt]

    if session_id:
        # 後續對話：恢復 session（會自動帶入之前的對話歷史）
        cmd.extend(["--resume", session_id])
    else:
        # 首次對話：生成 UUID 並建立 session
        new_session_id = str(uuid.uuid4())
        data.save_session_id(username, new_session_id, is_manager)
        cmd.extend(["--session-id", new_session_id])

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
                    "actions": []
                }
        except json.JSONDecodeError:
            return {
                "message": response_text,
                "actions": []
            }

    except subprocess.TimeoutExpired:
        return {
            "message": "抱歉，回應超時了，請再試一次。",
            "actions": [],
            "error": "timeout"
        }
    except Exception as e:
        return {
            "message": f"發生錯誤：{str(e)}",
            "actions": [],
            "error": str(e)
        }


def execute_actions(username: str, actions: list, is_manager: bool = False) -> list:
    """執行多個 AI 請求的動作，回傳結果陣列"""
    if not actions:
        return []

    results = []
    for action in actions:
        result = execute_action(username, action, is_manager)
        results.append(result)
    return results


def execute_action(username: str, action: dict, is_manager: bool = False) -> dict:
    """執行單一 AI 請求的動作"""
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
            return _cancel_order(username, action_data, is_manager)
        elif action_type == "set_today_store":
            return _set_today_store(action_data)
        elif action_type == "add_today_store":
            return _add_today_store(action_data)
        elif action_type == "remove_today_store":
            return _remove_today_store(action_data)
        elif action_type == "create_store":
            return _create_store(action_data)
        elif action_type == "update_store":
            return _update_store(action_data)
        elif action_type == "update_menu":
            return _update_menu(action_data)
        elif action_type == "update_item_variants":
            return _update_item_variants(action_data)
        elif action_type == "mark_paid":
            return _mark_paid(action_data)
        elif action_type == "mark_refunded":
            return _mark_refunded(action_data)
        elif action_type == "clear_all_orders":
            return _clear_all_orders(action_data)
        elif action_type == "clean_history_orders":
            return _clean_history_orders(action_data)
        elif action_type == "reset_session":
            return _reset_session(username, is_manager)
        elif action_type == "update_user_profile":
            return _update_user_profile(username, action_data)
        elif action_type == "remove_item":
            return _remove_item(username, action_data)
        else:
            return {"success": True, "message": "No action needed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _create_order(username: str, action_data: dict) -> dict:
    """建立訂單"""
    from datetime import datetime

    today_info = data.get_today_info()
    today_stores = today_info.get("stores", [])

    if not today_stores:
        return {"success": False, "error": "今日尚未設定店家"}

    # 支援多店家：從 action_data 取得指定的 store_id
    store_id = action_data.get("store_id")
    store_name = action_data.get("store_name")
    items = action_data.get("items", [])

    # 輔助函數：從菜單中查找品項（支援 id 或 name 匹配）
    def find_menu_item(menu, item_id, item_name):
        if not menu:
            return None
        for cat in menu.get("categories", []):
            for mi in cat.get("items", []):
                # 優先用 id 匹配
                if item_id and mi.get("id") == item_id:
                    return mi
                # 其次用 name 匹配（支援部分匹配）
                if item_name and (mi.get("name") == item_name or item_name in mi.get("name", "")):
                    return mi
        return None

    # 如果沒有指定店家，嘗試從所有今日店家的菜單中找到品項
    if not store_id and today_stores:
        for item in items:
            item_id = item.get("id")
            item_name = item.get("name", "")

            for store_ref in today_stores:
                sid = store_ref.get("store_id")
                menu = data.get_menu(sid)
                found = find_menu_item(menu, item_id, item_name)
                if found:
                    store_id = sid
                    store_name = store_ref.get("store_name", "")
                    break
            if store_id:
                break

    # 如果還是沒有店家，使用第一個店家作為預設
    if not store_id and today_stores:
        store_id = today_stores[0]["store_id"]
        store_name = today_stores[0].get("store_name", "")

    if not store_id:
        return {"success": False, "error": "找不到對應的店家"}

    # 驗證店家是否在今日列表中
    if today_stores:
        valid_store = next((s for s in today_stores if s["store_id"] == store_id), None)
        if not valid_store:
            return {"success": False, "error": f"店家 {store_id} 不在今日營業列表中"}
        if not store_name:
            store_name = valid_store.get("store_name", "")

    menu = data.get_menu(store_id)

    # 補充品項資訊
    enriched_items = []
    total = 0
    not_found_items = []

    total_calories = 0
    for item in items:
        item_id = item.get("id")
        item_name = item.get("name", "")
        quantity = item.get("quantity", 1)
        note = item.get("note", "")
        size = item.get("size", "")  # 尺寸（如 M, L）
        calories = item.get("calories", 0)  # AI 估算的卡路里

        # 從菜單找價格和名稱
        menu_item = find_menu_item(menu, item_id, item_name)

        if menu_item:
            # 決定價格：如果有指定尺寸且菜單有 variants，查找對應價格
            price = menu_item["price"]  # 預設價格
            if size and menu_item.get("variants"):
                variant = next((v for v in menu_item["variants"] if v["name"] == size), None)
                if variant:
                    price = variant["price"]

            enriched_items.append({
                "id": menu_item.get("id", item_id or item_name),
                "name": menu_item["name"],
                "price": price,
                "quantity": quantity,
                "size": size if size else None,
                "note": note,
                "calories": calories
            })
            total += price * quantity
            total_calories += calories * quantity
        else:
            not_found_items.append(item_name or item_id)

    # 如果有找不到的品項，回報警告但仍然建立訂單
    warning = ""
    if not_found_items:
        warning = f"（注意：以下品項在菜單中找不到：{', '.join(not_found_items)}）"

    order = {
        "date": date.today().isoformat(),
        "username": username,
        "store_id": store_id,
        "store_name": store_name,
        "items": enriched_items,
        "total": total,
        "total_calories": total_calories,
        "status": "confirmed",
        "created_at": datetime.now().isoformat()
    }

    # 如果沒有有效品項，回報錯誤
    if not enriched_items:
        return {
            "success": False,
            "error": f"無法建立訂單：找不到符合的菜單品項。{warning}" if warning else "無法建立訂單：找不到符合的菜單品項"
        }

    # 儲存訂單並取得 order_id
    order_id = data.save_user_order(username, order)
    order["order_id"] = order_id
    summary = data.update_daily_summary_with_order(username, order)

    result = {
        "success": True,
        "order": order,
        "order_id": order_id,
        "summary": summary,
        "event": "order_created"
    }

    if warning:
        result["warning"] = warning

    return result


def _update_order(username: str, action_data: dict) -> dict:
    """更新訂單"""
    # 類似 create_order，但更新現有訂單
    return _create_order(username, action_data)


def _update_payments_after_cancel(username: str, order_date: str) -> None:
    """取消訂單後更新付款記錄"""
    payments = data.get_payments(order_date)
    if not payments:
        return

    # 取得使用者剩餘的訂單總額
    remaining_orders = data.get_user_orders(username, order_date)
    new_total = sum(o.get("total", 0) for o in remaining_orders) if remaining_orders else 0

    record = next((r for r in payments["records"] if r["username"] == username), None)
    if not record:
        return

    paid_amount = record.get("paid_amount", 0)

    # 更新或移除付款記錄
    if new_total == 0:
        if paid_amount > 0:
            # 有付過款，保留記錄並標記待退
            record["amount"] = 0
            record["note"] = f"待退 ${paid_amount}"
        else:
            # 沒付過款，直接移除
            payments["records"] = [r for r in payments["records"] if r["username"] != username]
    else:
        # 更新金額
        record["amount"] = new_total
        # 如果有付過款，智慧更新狀態
        if paid_amount > 0:
            if new_total > paid_amount:
                record["paid"] = False
                record["note"] = f"已付 ${paid_amount}，待補 ${new_total - paid_amount}"
            elif new_total < paid_amount:
                record["paid"] = True
                record["note"] = f"待退 ${paid_amount - new_total}"
            else:
                record["paid"] = True
                record["note"] = None

    # 重新計算總額（基於 paid_amount）
    payments["total_collected"] = sum(r.get("paid_amount", 0) for r in payments["records"])
    payments["total_pending"] = sum(r["amount"] for r in payments["records"]) - payments["total_collected"]

    data.save_payments(payments)


def _cancel_order(username: str, action_data: dict, is_manager: bool = False) -> dict:
    """取消訂單（支援指定 order_id 或使用者）"""
    target_username = action_data.get("username", username)
    order_date = action_data.get("date", date.today().isoformat())
    order_id = action_data.get("order_id")

    # 權限檢查：非管理員只能取消自己的訂單
    if not is_manager and target_username != username:
        return {"success": False, "error": "只能取消自己的訂單"}

    # 如果有指定 order_id，取消特定訂單
    if order_id:
        deleted = data.delete_user_order(target_username, order_id)
        if not deleted:
            return {"success": False, "error": "找不到訂單"}

        # 從彙整中移除該筆訂單
        summary = data.get_daily_summary(order_date)
        if summary:
            summary["orders"] = [o for o in summary["orders"] if o.get("order_id") != order_id]
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

        # 更新付款記錄
        _update_payments_after_cancel(target_username, order_date)

        return {
            "success": True,
            "event": "order_cancelled",
            "username": target_username,
            "order_id": order_id,
            "summary": summary
        }

    # 沒有 order_id 時，取消該使用者所有訂單
    orders = data.get_user_orders(target_username, order_date)
    if not orders:
        return {"success": False, "error": "找不到訂單"}

    # 刪除所有訂單檔案
    for order in orders:
        oid = order.get("order_id")
        if oid:
            data.delete_user_order(target_username, oid)

    # 從彙整中移除
    summary = data.get_daily_summary(order_date)
    if summary:
        summary["orders"] = [o for o in summary["orders"] if o["username"] != target_username]
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

    # 更新付款記錄
    _update_payments_after_cancel(target_username, order_date)

    return {
        "success": True,
        "event": "order_cancelled",
        "username": target_username,
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
    return {
        "success": True,
        "today": today_info,
        "store_name": store_name,
        "event": "store_changed"
    }


def _add_today_store(action_data: dict) -> dict:
    """新增今日店家（支援多店家）"""
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

    today_info = data.add_today_store(store_id, store_name)
    return {
        "success": True,
        "today": today_info,
        "store_name": store_name,
        "event": "store_changed"
    }


def _remove_today_store(action_data: dict) -> dict:
    """從今日列表移除店家"""
    store_id = action_data.get("store_id")

    if not store_id:
        return {"success": False, "error": "缺少 store_id"}

    today_info = data.remove_today_store(store_id)
    return {
        "success": True,
        "today": today_info,
        "event": "store_changed"
    }


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
        "note": action_data.get("note", ""),
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
    for key in ["name", "phone", "address", "description", "note", "active"]:
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


def _update_item_variants(action_data: dict) -> dict:
    """更新菜單品項的尺寸變體"""
    from datetime import datetime

    store_id = action_data.get("store_id")
    item_id = action_data.get("item_id")
    item_name = action_data.get("item_name")
    variants = action_data.get("variants")  # 完整的 variants 陣列
    add_variant = action_data.get("add_variant")  # 新增單一尺寸 {"name": "L", "price": 60}
    remove_variant = action_data.get("remove_variant")  # 移除尺寸名稱 "L"
    update_variant = action_data.get("update_variant")  # 更新單一尺寸 {"name": "L", "price": 65}

    if not store_id:
        return {"success": False, "error": "缺少 store_id"}

    if not item_id and not item_name:
        return {"success": False, "error": "缺少 item_id 或 item_name"}

    menu = data.get_menu(store_id)
    if not menu:
        return {"success": False, "error": "找不到菜單"}

    # 找到品項
    target_item = None
    for cat in menu.get("categories", []):
        for item in cat.get("items", []):
            if (item_id and item.get("id") == item_id) or \
               (item_name and (item.get("name") == item_name or item_name in item.get("name", ""))):
                target_item = item
                break
        if target_item:
            break

    if not target_item:
        return {"success": False, "error": f"找不到品項：{item_id or item_name}"}

    # 執行更新
    if variants is not None:
        # 完整覆蓋 variants
        if variants:
            target_item["variants"] = variants
        else:
            # 空陣列表示刪除所有 variants
            target_item.pop("variants", None)

    elif add_variant:
        # 新增單一尺寸
        if "variants" not in target_item:
            target_item["variants"] = []
        # 檢查是否已存在
        existing = next((v for v in target_item["variants"] if v["name"] == add_variant["name"]), None)
        if existing:
            existing["price"] = add_variant["price"]
        else:
            target_item["variants"].append(add_variant)

    elif remove_variant:
        # 移除尺寸
        if "variants" in target_item:
            target_item["variants"] = [v for v in target_item["variants"] if v["name"] != remove_variant]
            if not target_item["variants"]:
                del target_item["variants"]

    elif update_variant:
        # 更新單一尺寸價格
        if "variants" in target_item:
            existing = next((v for v in target_item["variants"] if v["name"] == update_variant["name"]), None)
            if existing:
                existing["price"] = update_variant["price"]
            else:
                return {"success": False, "error": f"找不到尺寸：{update_variant['name']}"}
        else:
            return {"success": False, "error": "該品項沒有尺寸變體"}

    # 儲存菜單
    menu["updated_at"] = datetime.now().isoformat()
    data.save_menu(store_id, menu)

    return {
        "success": True,
        "item": target_item,
        "message": f"已更新「{target_item['name']}」的尺寸價格"
    }


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
    record["paid_amount"] = record["amount"]  # 設定已付金額
    record["note"] = None  # 清除備註

    # 重新計算總額（基於 paid_amount）
    payments["total_collected"] = sum(r.get("paid_amount", 0) for r in payments["records"])
    payments["total_pending"] = sum(r["amount"] for r in payments["records"]) - payments["total_collected"]

    data.save_payments(payments)
    return {"success": True, "event": "payment_updated", "payments": payments}


def _mark_refunded(action_data: dict) -> dict:
    """標記已退款（確認已退還多付的金額）"""
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

    paid_amount = record.get("paid_amount", 0)
    if paid_amount == 0:
        return {"success": False, "error": "該使用者沒有已付款項"}

    amount = record.get("amount", 0)

    if amount > 0:
        # 還有訂單：確認退款後，paid_amount 調整為等於 amount（多付的已退）
        record["paid"] = True
        record["paid_amount"] = amount
        record["note"] = None
    else:
        # 沒有訂單了：移除記錄
        payments["records"] = [r for r in payments["records"] if r["username"] != username]

    # 重新計算總額
    payments["total_collected"] = sum(r.get("paid_amount", 0) for r in payments["records"])
    payments["total_pending"] = sum(r["amount"] for r in payments["records"]) - payments["total_collected"]

    data.save_payments(payments)
    return {"success": True, "event": "payment_updated", "payments": payments, "message": f"已確認退款給 {username}"}


def _clear_all_orders(action_data: dict) -> dict:
    """清除今日所有訂單"""
    order_date = action_data.get("date", date.today().isoformat())

    # 清除每日彙整
    summary = data.get_daily_summary(order_date)
    if summary:
        # 取得所有訂購者
        usernames = [o["username"] for o in summary.get("orders", [])]

        # 清除每個使用者的訂單檔案
        for username in usernames:
            order_file = data.DATA_DIR / "users" / username / "orders" / f"{order_date}.json"
            if order_file.exists():
                order_file.unlink()

        # 重設彙整
        summary["orders"] = []
        summary["item_summary"] = []
        summary["grand_total"] = 0
        data.save_daily_summary(summary)

    # 處理付款記錄
    payments = data.get_payments(order_date)
    if payments:
        # 保留有 paid_amount > 0 的記錄（待退款）
        new_records = []
        for record in payments["records"]:
            paid_amount = record.get("paid_amount", 0)
            if paid_amount > 0:
                # 有付過款，保留記錄並標記待退
                record["amount"] = 0
                record["note"] = f"待退 ${paid_amount}"
                new_records.append(record)
            # paid_amount = 0 的記錄直接移除

        payments["records"] = new_records
        # 重新計算總額
        payments["total_collected"] = sum(r.get("paid_amount", 0) for r in payments["records"])
        payments["total_pending"] = sum(r["amount"] for r in payments["records"]) - payments["total_collected"]
        data.save_payments(payments)

    return {
        "success": True,
        "event": "orders_cleared",
        "message": f"已清除 {order_date} 所有訂單"
    }


def _clean_history_orders(action_data: dict) -> dict:
    """清除指定日期之前的歷史訂單"""
    before_date = action_data.get("before_date")

    if not before_date:
        return {"success": False, "error": "缺少 before_date 參數"}

    deleted_count = 0

    # 清除 data/orders/ 下的舊日期資料夾
    orders_dir = data.DATA_DIR / "orders"
    if orders_dir.exists():
        for date_dir in orders_dir.iterdir():
            if date_dir.is_dir() and date_dir.name < before_date:
                # 刪除整個日期資料夾
                import shutil
                shutil.rmtree(date_dir)
                deleted_count += 1

    # 清除各使用者的舊訂單
    users_dir = data.DATA_DIR / "users"
    if users_dir.exists():
        for user_dir in users_dir.iterdir():
            if user_dir.is_dir():
                orders_subdir = user_dir / "orders"
                if orders_subdir.exists():
                    for order_file in orders_subdir.glob("*.json"):
                        # 檔名格式為 {date}.json
                        file_date = order_file.stem
                        if file_date < before_date:
                            order_file.unlink()
                            deleted_count += 1

    return {
        "success": True,
        "message": f"已清除 {before_date} 之前的 {deleted_count} 筆歷史資料"
    }


def _reset_session(username: str, is_manager: bool) -> dict:
    """重置對話 session，讓下次對話重新開始"""
    cleared = data.clear_session_id(username, is_manager)
    mode = "管理員" if is_manager else "一般"
    if cleared:
        return {
            "success": True,
            "message": f"已重置{mode}模式的對話記錄，下次對話將重新開始",
            "event": "session_reset"
        }
    else:
        return {
            "success": True,
            "message": f"目前沒有進行中的{mode}模式對話記錄"
        }


def _update_user_profile(username: str, action_data: dict) -> dict:
    """更新使用者偏好設定"""
    profile = data.update_user_profile(username, action_data)
    return {
        "success": True,
        "profile": profile,
        "message": "已更新你的偏好設定",
        "event": "profile_updated"
    }


def _remove_item(username: str, action_data: dict) -> dict:
    """從現有訂單中移除品項"""
    from datetime import datetime

    item_name = action_data.get("item_name", "")
    item_id = action_data.get("item_id")
    quantity_to_remove = action_data.get("quantity", 1)
    order_date = action_data.get("date", date.today().isoformat())

    if not item_name and not item_id:
        return {"success": False, "error": "請指定要移除的品項名稱或 ID"}

    # 取得使用者所有訂單
    user_orders = data.get_user_orders(username, order_date)
    if not user_orders:
        return {"success": False, "error": "目前沒有訂單"}

    # 尋找包含該品項的訂單
    target_order = None
    target_item_idx = None

    for order in user_orders:
        for idx, item in enumerate(order.get("items", [])):
            # 用 id 或 name 匹配
            if (item_id and item.get("id") == item_id) or \
               (item_name and (item.get("name") == item_name or item_name in item.get("name", ""))):
                target_order = order
                target_item_idx = idx
                break
        if target_order:
            break

    if not target_order:
        return {"success": False, "error": f"找不到品項：{item_name or item_id}"}

    order_id = target_order.get("order_id")
    items = target_order.get("items", [])
    target_item = items[target_item_idx]
    current_qty = target_item.get("quantity", 1)

    if quantity_to_remove >= current_qty:
        # 移除整個品項
        items.pop(target_item_idx)
    else:
        # 減少數量
        target_item["quantity"] = current_qty - quantity_to_remove

    # 如果訂單沒有品項了，刪除整筆訂單
    if len(items) == 0:
        data.delete_user_order(username, order_id)

        # 從 daily summary 移除
        summary = data.get_daily_summary(order_date)
        if summary:
            summary["orders"] = [o for o in summary["orders"] if o.get("order_id") != order_id]
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

        # 更新付款記錄
        _update_payments_after_cancel(username, order_date)

        return {
            "success": True,
            "message": f"已移除「{target_item.get('name')}」，訂單已刪除",
            "event": "order_cancelled",
            "username": username,
            "summary": summary
        }

    # 更新訂單
    target_order["items"] = items
    target_order["total"] = sum(item.get("price", 0) * item.get("quantity", 1) for item in items)
    target_order["total_calories"] = sum(item.get("calories", 0) * item.get("quantity", 1) for item in items)

    # 儲存更新的訂單
    data.write_json(data.DATA_DIR / "users" / username / "orders" / f"{order_id}.json", target_order)

    # 更新 daily summary
    summary = data.get_daily_summary(order_date)
    if summary:
        # 更新對應訂單
        for idx, o in enumerate(summary["orders"]):
            if o.get("order_id") == order_id:
                summary["orders"][idx] = {
                    "order_id": order_id,
                    "username": username,
                    "store_id": target_order.get("store_id"),
                    "store_name": target_order.get("store_name"),
                    "items": items,
                    "total": target_order["total"]
                }
                break

        # 重新計算品項統計
        item_counts = {}
        for o in summary["orders"]:
            for item in o["items"]:
                name = item["name"]
                qty = item.get("quantity", 1)
                item_counts[name] = item_counts.get(name, 0) + qty
        summary["item_summary"] = [{"name": k, "quantity": v} for k, v in item_counts.items()]
        summary["grand_total"] = sum(o["total"] for o in summary["orders"])
        data.save_daily_summary(summary)

    # 更新付款記錄
    payments = data.get_payments(order_date)
    if payments:
        user_total = sum(o["total"] for o in data.get_user_orders(username, order_date) or [])
        record = next((r for r in payments["records"] if r["username"] == username), None)
        if record:
            record["amount"] = user_total
            # 重新計算總額
            payments["total_collected"] = sum(r.get("paid_amount", 0) for r in payments["records"])
            payments["total_pending"] = sum(r["amount"] for r in payments["records"]) - payments["total_collected"]
            data.save_payments(payments)

    return {
        "success": True,
        "message": f"已從訂單移除「{target_item.get('name')}」",
        "event": "order_updated",
        "order": target_order,
        "summary": summary
    }


def recognize_menu_image(image_base64: str) -> dict:
    """使用 Claude Vision 辨識菜單圖片"""
    import base64
    import os
    import time

    # 將 base64 圖片存為暫存檔
    # 移除 data URL 前綴（如果有）
    if ',' in image_base64:
        image_base64 = image_base64.split(',')[1]

    try:
        image_data = base64.b64decode(image_base64)
    except Exception as e:
        return {"error": f"圖片解碼失敗：{str(e)}"}

    # 建立暫存檔（放在專案目錄內確保 Claude CLI 可存取）
    temp_dir = data.DATA_DIR / "temp"
    temp_dir.mkdir(exist_ok=True)
    temp_path = str(temp_dir / f"menu_temp_{int(time.time())}.jpg")

    with open(temp_path, 'wb') as f:
        f.write(image_data)

    try:
        # 從檔案讀取 prompt
        prompt_data = data.get_jaba_prompt()
        prompt = prompt_data.get("menu_recognition_prompt", "請分析這張菜單圖片，提取所有菜單項目並回傳 JSON 格式。")

        # 取得模型設定
        ai_config = data.get_ai_config()
        model = ai_config.get("menu_recognition", {}).get("model", "sonnet")

        # 使用 Claude CLI 分析圖片
        # Claude CLI 支援直接使用 sonnet/opus/haiku 等簡稱
        full_prompt = f"請先使用 Read 工具讀取圖片 {temp_path}，然後{prompt}"
        cmd = [
            "claude", "-p", full_prompt,
            "--model", model,
            "--tools", "Read",
            "--allowedTools", "Read",
            "--dangerously-skip-permissions"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,  # 圖片辨識可能需要較長時間
            cwd=str(data.DATA_DIR.parent)
        )

        response_text = result.stdout.strip()
        error_text = result.stderr.strip()

        # 檢查是否有錯誤
        if result.returncode != 0:
            error_msg = error_text or response_text or "未知錯誤"
            return {"error": f"Claude CLI 執行失敗：{error_msg}"}

        if not response_text:
            return {"error": f"Claude 沒有回應。stderr: {error_text or '(無)'}"}

        # 嘗試解析 JSON 回應
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            try:
                menu_data = json.loads(json_match.group())
                return {
                    "menu": menu_data,
                    "warnings": menu_data.get("warnings", [])
                }
            except json.JSONDecodeError as e:
                return {"error": f"AI 回應格式錯誤：{str(e)}。回應內容：{response_text[:200]}..."}
        else:
            # 顯示 AI 實際回應以便診斷
            preview = response_text[:300] if len(response_text) > 300 else response_text
            return {"error": f"AI 回應不包含預期的 JSON 格式。回應內容：{preview}"}

    except subprocess.TimeoutExpired:
        return {"error": "辨識超時，請稍後再試"}
    except Exception as e:
        return {"error": f"辨識失敗：{str(e)}"}
    finally:
        # 清理暫存檔
        if os.path.exists(temp_path):
            os.unlink(temp_path)
