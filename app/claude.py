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
    prompt_data = data.get_jaba_prompt()
    base_prompt = prompt_data.get("system_prompt", "")

    if is_manager:
        return f"""{base_prompt}

你現在是管理員模式，可以執行以下額外動作：
- set_today_store: 設定今日唯一店家，會清除其他店家 (data: {{"store_id": "...", "store_name": "..."}})
- add_today_store: 新增今日店家（支援多店家）(data: {{"store_id": "...", "store_name": "..."}})
- remove_today_store: 移除今日某店家 (data: {{"store_id": "..."}})
- create_store: 新增店家 (data: {{"id": "...", "name": "...", "phone": "...", "address": "...", "description": "..."}})
- update_store: 更新店家資訊 (data: {{"store_id": "...", ...欄位}})
- update_menu: 更新菜單 (data: {{"store_id": "...", "categories": [...]}})
- mark_paid: 標記已付款 (data: {{"username": "...", "date": "..."}})
- query_payments: 查詢付款狀態 (data: {{"date": "..."}})
- query_all_orders: 查詢所有訂單 (data: {{"date": "..."}})
- cancel_order: 取消指定使用者的訂單 (data: {{"username": "...", "date": "..."}})
- clear_all_orders: 清除今日所有訂單 (data: {{}})
- clean_history_orders: 清除歷史訂單 (data: {{"before_date": "..."}})

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

    # 向後相容：單店家時也提供 menu 欄位
    if today_info.get("store_id"):
        store = data.get_store(today_info["store_id"])
        if store:
            context["today_store_note"] = store.get("note", "")
        menu = data.get_menu(today_info["store_id"])
        if menu:
            context["menu"] = menu

    if not is_manager:
        context["username"] = username
        # 取得使用者所有訂單
        user_orders = data.get_user_orders(username)
        if user_orders:
            context["current_orders"] = user_orders
            # 向後相容：也提供單一訂單
            context["current_order"] = user_orders[-1]

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

請以 JSON 格式回應：
- 單一動作：{{"message": "...", "action": {{"type": "...", "data": {{...}}}} }}
- 多個動作：{{"message": "...", "actions": [{{"type": "...", "data": {{...}}}}, ...] }}
- 無動作：{{"message": "...", "action": null}}

如果使用者的請求需要執行多個步驟，請使用 actions 陣列一次回傳所有需要執行的動作。"""

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


def execute_actions(username: str, actions: list) -> list:
    """執行多個 AI 請求的動作，回傳結果陣列"""
    if not actions:
        return []

    results = []
    for action in actions:
        result = execute_action(username, action)
        results.append(result)
    return results


def execute_action(username: str, action: dict) -> dict:
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
            return _cancel_order(username, action_data)
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
        elif action_type == "mark_paid":
            return _mark_paid(action_data)
        elif action_type == "clear_all_orders":
            return _clear_all_orders(action_data)
        elif action_type == "clean_history_orders":
            return _clean_history_orders(action_data)
        else:
            return {"success": True, "message": "No action needed"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _create_order(username: str, action_data: dict) -> dict:
    """建立訂單"""
    from datetime import datetime

    today_info = data.get_today_info()
    today_stores = today_info.get("stores", [])

    if not today_stores and not today_info.get("store_id"):
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

    # 如果還是沒有店家，使用預設（第一個店家）
    if not store_id:
        store_id = today_info.get("store_id")
        store_name = today_info.get("store_name")

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

    for item in items:
        item_id = item.get("id")
        item_name = item.get("name", "")
        quantity = item.get("quantity", 1)
        note = item.get("note", "")

        # 從菜單找價格和名稱
        menu_item = find_menu_item(menu, item_id, item_name)

        if menu_item:
            enriched_items.append({
                "id": menu_item.get("id", item_id or item_name),
                "name": menu_item["name"],
                "price": menu_item["price"],
                "quantity": quantity,
                "note": note
            })
            total += menu_item["price"] * quantity
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


def _cancel_order(username: str, action_data: dict) -> dict:
    """取消訂單（支援指定 order_id 或使用者）"""
    target_username = action_data.get("username", username)
    order_date = action_data.get("date", date.today().isoformat())
    order_id = action_data.get("order_id")

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

        return {
            "success": True,
            "event": "order_cancelled",
            "username": target_username,
            "order_id": order_id,
            "summary": summary
        }

    # 沒有 order_id 時，取消該使用者所有訂單（向後相容）
    orders = data.get_user_orders(target_username, order_date)
    if not orders:
        return {"success": False, "error": "找不到訂單"}

    # 刪除所有訂單檔案
    for order in orders:
        oid = order.get("order_id")
        if oid:
            data.delete_user_order(target_username, oid)
        else:
            # 舊格式
            order_file = data.DATA_DIR / "users" / target_username / "orders" / f"{order_date}.json"
            if order_file.exists():
                order_file.unlink()

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

    # 清除付款記錄
    payments = data.get_payments(order_date)
    if payments:
        payments["records"] = []
        payments["total_collected"] = 0
        payments["total_pending"] = 0
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
        # 使用 Claude CLI 分析圖片
        prompt = """請分析這張菜單圖片，提取所有菜單項目。

回傳 JSON 格式：
{
  "categories": [
    {
      "name": "分類名稱",
      "items": [
        {
          "id": "item-1",
          "name": "品項名稱",
          "price": 數字價格,
          "description": "描述（如有）",
          "available": true
        }
      ]
    }
  ],
  "warnings": ["無法辨識的項目或需要確認的事項"]
}

注意事項：
- id 請用 item-1, item-2... 格式
- 價格請只填數字，不含貨幣符號
- 如果無法辨識價格，請填 0 並在 warnings 中說明
- 盡可能保留原始分類結構
- 如果沒有明確分類，請使用「一般」作為分類名稱
- available 預設為 true"""

        # 使用 Claude CLI 分析圖片
        # 使用 --tools 啟用 Read 工具來讀取圖片
        full_prompt = f"請先使用 Read 工具讀取圖片 {temp_path}，然後{prompt}"
        cmd = [
            "claude", "-p", full_prompt,
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
