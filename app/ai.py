"""AI CLI 整合模組 - 支援多種 CLI Provider"""
import asyncio
import subprocess
import json
import base64
import os
import time
from datetime import date, datetime
from pathlib import Path

from . import data
from .providers import get_provider


def get_system_prompt(is_manager: bool = False, group_ordering: bool = False) -> str:
    """取得系統提示詞"""
    prompt_data = data.get_jaba_prompt()

    if group_ordering:
        # 群組點餐模式：載入 group_ordering_prompt
        base_prompt = prompt_data.get("group_ordering_prompt", "")
        return f"""{base_prompt}

請用繁體中文回應。"""

    if is_manager:
        # 管理員模式：載入 manager_prompt
        base_prompt = prompt_data.get("manager_prompt", "")
        return f"""{base_prompt}

請用繁體中文回應。"""

    # 一般使用者模式：載入 user_prompt
    base_prompt = prompt_data.get("user_prompt", "")
    return f"""{base_prompt}

請用繁體中文回應。"""


def build_context(
    username: str,
    is_manager: bool = False,
    group_ordering: bool = False,
    group_id: str | None = None,
    session_orders: list | None = None
) -> dict:
    """建立 AI 上下文"""
    today_info = data.get_today_info()
    today_stores = today_info.get("stores", [])

    # 群組點餐模式
    if group_ordering:
        # 取得當前使用者的偏好
        profile = data.get_user_profile(username)
        user_profile = None
        if profile:
            user_profile = profile.get("preferences", {})

        context = {
            "today": date.today().isoformat(),
            "today_stores": today_stores,
            "username": username,  # 當前發訊息的人
            "user_profile": user_profile,  # 當前使用者的偏好
            "group_ordering": True,
            "session_orders": session_orders or [],  # 群組目前的訂單
        }

        # 提供今日店家的菜單
        if today_stores:
            context["menus"] = {}
            for store_ref in today_stores:
                store_id = store_ref.get("store_id")
                menu = data.get_menu(store_id)
                if menu:
                    context["menus"][store_id] = {
                        "name": store_ref.get("store_name", ""),
                        "menu": menu
                    }

        return context

    # 個人模式：完整 context
    profile = data.get_user_profile(username)
    preferred_name = None
    if profile:
        preferred_name = profile.get("preferences", {}).get("preferred_name")

    context = {
        "today": date.today().isoformat(),
        "today_stores": today_stores,
        "username": username,
        "preferred_name": preferred_name,
        "group_ordering": False,
    }

    # 提供今日店家的完整菜單（包含 description 供呷爸參考）
    if today_stores:
        context["menus"] = {}
        for store_ref in today_stores:
            store_id = store_ref.get("store_id")
            menu = data.get_menu(store_id)
            if menu:
                context["menus"][store_id] = {
                    "name": store_ref.get("store_name", ""),
                    "menu": menu  # 完整菜單資訊
                }

    if not is_manager:
        # 使用者模式：加入偏好和訂單
        if profile:
            context["user_profile"] = profile.get("preferences", {})
        user_orders = data.get_user_orders(username)
        if user_orders:
            context["current_orders"] = user_orders

    if is_manager:
        # 管理員模式：需要店家列表來設定今日店家
        stores = data.get_active_stores()
        context["available_stores"] = [{"id": s["id"], "name": s["name"]} for s in stores]

        # 完整 today_summary，包含訂單明細供管理員查看
        summary = data.get_daily_summary()
        if summary:
            context["today_summary"] = summary  # 完整訂單明細

        payments = data.get_payments()
        if payments:
            context["payments"] = payments

        # 提供過去 7 天的店家歷史記錄
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


def _format_chat_history(history: list[dict]) -> str:
    """格式化對話歷史為 prompt 可讀格式"""
    if not history:
        return "(無先前對話)"

    lines = []
    for msg in history:
        role = "使用者" if msg["role"] == "user" else "助手"
        lines.append(f"{role}: {msg['content']}")

    return "\n".join(lines)


def _format_group_chat_history(history: list[dict]) -> str:
    """格式化群組對話歷史為 prompt 可讀格式（包含使用者名稱）"""
    if not history:
        return "(本次點餐尚無對話)"

    lines = []
    for msg in history:
        if msg["role"] == "user":
            username = msg.get("username", "未知")
            lines.append(f"{username}: {msg['content']}")
        else:
            lines.append(f"呷爸: {msg['content']}")

    return "\n".join(lines)


async def call_ai(
    username: str,
    message: str,
    is_manager: bool = False,
    group_ordering: bool = False,
    group_id: str | None = None
) -> dict:
    """呼叫 AI CLI（支援多種 Provider）

    使用自管理的對話歷史，不依賴 CLI session 機制。
    每次呼叫組合：系統上下文 + 對話歷史 + 當前訊息。
    使用 asyncio 非同步執行，不阻塞其他請求。
    """
    timings = {}
    t_start = time.time()

    # 確保使用者存在
    data.ensure_user(username)

    # 取得 AI 設定
    ai_config = data.get_ai_config()
    chat_config = ai_config.get("chat", {})
    provider_name = chat_config.get("provider", "claude")
    model = chat_config.get("model", "haiku")

    # 取得 provider
    provider = get_provider(provider_name)

    # 取得對話歷史
    if group_ordering and group_id:
        # 群組點餐：使用群組共享對話歷史（保留更多訊息）
        history = data.get_group_chat_history(group_id, max_messages=50)
        history_str = _format_group_chat_history(history)
    else:
        # 個人模式：使用個人對話歷史
        history = data.get_ai_chat_history(username, is_manager)
        history_str = _format_chat_history(history)

    t_prep = time.time()
    timings["prepare"] = round(t_prep - t_start, 3)

    # 群組點餐時取得 session_orders
    session_orders = None
    if group_ordering and group_id:
        from main import get_group_session
        session = get_group_session(group_id)
        if session:
            session_orders = session.get("orders", [])

    system_prompt = get_system_prompt(is_manager, group_ordering)
    context = build_context(username, is_manager, group_ordering, group_id, session_orders)

    # 組合完整訊息（包含對話歷史）
    context_str = json.dumps(context, ensure_ascii=False, indent=2)

    full_message = f"""[系統上下文]
{context_str}

[對話歷史]
{history_str}

[當前訊息]
{message}

請以 JSON 格式回應：
{{"message": "你的回應訊息", "actions": [{{"type": "動作類型", "data": {{...}}}}, ...] }}

如果不需要執行動作，actions 可以是空陣列 []。
如果需要執行多個步驟，在 actions 陣列中一次回傳所有動作。"""

    t_build = time.time()
    timings["build_prompt"] = round(t_build - t_prep, 3)

    # 使用 provider 建構命令（不使用 session）
    cmd_result = provider.build_chat_command(model, full_message, system_prompt, None)

    # 先儲存使用者訊息到歷史
    if group_ordering and group_id:
        data.append_group_chat_history(group_id, username, "user", message)
    else:
        data.append_ai_chat_history(username, "user", message, is_manager)

    try:
        t_cli_start = time.time()

        # 使用 asyncio 非同步執行 subprocess，不阻塞 event loop
        proc = await asyncio.create_subprocess_exec(
            *cmd_result.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cmd_result.cwd
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(),
            timeout=120
        )
        stdout = stdout_bytes.decode('utf-8') if stdout_bytes else ''
        stderr = stderr_bytes.decode('utf-8') if stderr_bytes else ''

        t_cli_end = time.time()
        timings["cli_call"] = round(t_cli_end - t_cli_start, 3)

        # 使用 provider 解析回應
        response = provider.parse_response(stdout, stderr, proc.returncode)

        t_parse = time.time()
        timings["parse"] = round(t_parse - t_cli_end, 3)

        # 儲存 AI 回應到歷史（只保存 message，不保存 actions）
        ai_message = response.get("message", "")
        if ai_message:
            if group_ordering and group_id:
                data.append_group_chat_history(group_id, username, "assistant", ai_message)
            else:
                data.append_ai_chat_history(username, "assistant", ai_message, is_manager)

        t_end = time.time()
        timings["save_history"] = round(t_end - t_parse, 3)
        timings["total"] = round(t_end - t_start, 3)

        # 加入時間資訊到回應
        response["_timings"] = timings
        response["_provider"] = provider_name
        response["_model"] = model

        return response

    except asyncio.TimeoutError:
        return {
            "message": "抱歉，回應超時了，請再試一次。",
            "actions": [],
            "error": "timeout",
            "_timings": timings
        }
    except Exception as e:
        return {
            "message": f"發生錯誤：{str(e)}",
            "actions": [],
            "error": str(e),
            "_timings": timings
        }


def compare_menus(existing_menu: dict | None, recognized_menu: dict) -> dict:
    """比對現有菜單與辨識結果的差異

    Args:
        existing_menu: 現有菜單（可為 None 表示新店家）
        recognized_menu: AI 辨識出的菜單

    Returns:
        {
            "added": [...],      # 新辨識出的品項（現有菜單沒有）
            "modified": [...],   # 名稱相同但內容不同
            "unchanged": [...],  # 完全相同
            "removed": [...]     # 現有菜單有但新辨識沒有的
        }
    """
    def normalize_name(name: str) -> str:
        """正規化品項名稱（去除空白、標點）以提高匹配率"""
        import re
        return re.sub(r'[\s\-_\(\)（）]', '', name.lower())

    def items_equal(item1: dict, item2: dict) -> bool:
        """比較兩個品項是否相同（名稱、價格、variants、promo）"""
        if item1.get("price") != item2.get("price"):
            return False
        # 比較 variants
        v1 = item1.get("variants") or []
        v2 = item2.get("variants") or []
        if len(v1) != len(v2):
            return False
        for va, vb in zip(sorted(v1, key=lambda x: x.get("name", "")),
                         sorted(v2, key=lambda x: x.get("name", ""))):
            if va.get("name") != vb.get("name") or va.get("price") != vb.get("price"):
                return False
        # 比較 promo
        p1 = item1.get("promo")
        p2 = item2.get("promo")
        if p1 != p2:
            return False
        return True

    def get_item_changes(old_item: dict, new_item: dict) -> list:
        """取得品項的變更詳情"""
        changes = []
        if old_item.get("price") != new_item.get("price"):
            changes.append(f"價格 ${old_item.get('price')} → ${new_item.get('price')}")
        # variants 變更
        old_variants = {v["name"]: v["price"] for v in (old_item.get("variants") or [])}
        new_variants = {v["name"]: v["price"] for v in (new_item.get("variants") or [])}
        if old_variants != new_variants:
            changes.append("尺寸價格變更")
        # promo 變更
        if old_item.get("promo") != new_item.get("promo"):
            old_label = (old_item.get("promo") or {}).get("label", "無")
            new_label = (new_item.get("promo") or {}).get("label", "無")
            changes.append(f"促銷 {old_label} → {new_label}")
        return changes

    # 建立現有品項的索引（按正規化名稱）
    existing_items = {}
    if existing_menu and existing_menu.get("categories"):
        for cat in existing_menu["categories"]:
            for item in cat.get("items", []):
                key = normalize_name(item.get("name", ""))
                existing_items[key] = {
                    "item": item,
                    "category": cat.get("name", "")
                }

    # 建立辨識品項的索引
    recognized_items = {}
    if recognized_menu and recognized_menu.get("categories"):
        for cat in recognized_menu["categories"]:
            for item in cat.get("items", []):
                key = normalize_name(item.get("name", ""))
                recognized_items[key] = {
                    "item": item,
                    "category": cat.get("name", "")
                }

    added = []
    modified = []
    unchanged = []
    removed = []

    # 比對辨識結果
    for key, rec_data in recognized_items.items():
        rec_item = rec_data["item"]
        if key in existing_items:
            exist_data = existing_items[key]
            exist_item = exist_data["item"]
            if items_equal(exist_item, rec_item):
                unchanged.append({
                    "item": rec_item,
                    "category": rec_data["category"]
                })
            else:
                changes = get_item_changes(exist_item, rec_item)
                modified.append({
                    "old_item": exist_item,
                    "new_item": rec_item,
                    "category": rec_data["category"],
                    "changes": changes
                })
        else:
            added.append({
                "item": rec_item,
                "category": rec_data["category"]
            })

    # 找出現有菜單有但辨識結果沒有的品項
    for key, exist_data in existing_items.items():
        if key not in recognized_items:
            removed.append({
                "item": exist_data["item"],
                "category": exist_data["category"]
            })

    return {
        "added": added,
        "modified": modified,
        "unchanged": unchanged,
        "removed": removed
    }


async def recognize_menu_image(image_base64: str) -> dict:
    """使用 AI Vision 辨識菜單圖片

    使用 asyncio 非同步執行，不阻塞其他請求。
    """
    # 移除 data URL 前綴（如果有）
    if ',' in image_base64:
        image_base64 = image_base64.split(',')[1]

    try:
        image_data = base64.b64decode(image_base64)
    except Exception as e:
        return {"error": f"圖片解碼失敗：{str(e)}"}

    # 建立暫存檔
    temp_dir = data.DATA_DIR.parent / "temp"
    temp_dir.mkdir(exist_ok=True)
    temp_path = str(temp_dir / f"menu_temp_{int(time.time())}.jpg")

    with open(temp_path, 'wb') as f:
        f.write(image_data)

    try:
        # 從檔案讀取 prompt
        prompt_data = data.get_jaba_prompt()
        prompt = prompt_data.get("menu_recognition_prompt", "請分析這張菜單圖片，提取所有菜單項目並回傳 JSON 格式。")

        # 取得 AI 設定
        ai_config = data.get_ai_config()
        menu_config = ai_config.get("menu_recognition", {})
        provider_name = menu_config.get("provider", "claude")
        model = menu_config.get("model", "sonnet")

        # 取得 provider
        provider = get_provider(provider_name)

        # 使用 provider 建構菜單辨識命令
        cmd_result = provider.build_menu_command(model, prompt, temp_path)

        # 使用 asyncio 非同步執行 subprocess，不阻塞 event loop
        proc = await asyncio.create_subprocess_exec(
            *cmd_result.cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cmd_result.cwd
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(),
            timeout=300  # 圖片辨識可能需要較長時間
        )
        response_text = (stdout_bytes.decode('utf-8') if stdout_bytes else '').strip()
        error_text = (stderr_bytes.decode('utf-8') if stderr_bytes else '').strip()

        # 檢查是否有錯誤
        if proc.returncode != 0:
            error_msg = error_text or response_text or "未知錯誤"
            return {"error": f"{provider_name.upper()} CLI 執行失敗：{error_msg}"}

        if not response_text:
            return {"error": f"AI 沒有回應。stderr: {error_text or '(無)'}"}

        # 嘗試解析 JSON 回應
        import re
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

    except asyncio.TimeoutError:
        return {"error": "辨識超時，請稍後再試"}
    except Exception as e:
        return {"error": f"辨識失敗：{str(e)}"}
    finally:
        # 清理暫存檔
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def execute_actions(
    username: str,
    actions: list,
    is_manager: bool = False,
    group_id: str | None = None
) -> list:
    """執行多個 AI 請求的動作，回傳結果陣列"""
    if not actions:
        return []

    results = []
    for action in actions:
        result = execute_action(username, action, is_manager, group_id)
        results.append(result)
    return results


def execute_action(
    username: str,
    action: dict,
    is_manager: bool = False,
    group_id: str | None = None
) -> dict:
    """執行單一 AI 請求的動作"""
    if not action:
        return {"success": True}

    action_type = action.get("type")
    action_data = action.get("data", {})

    try:
        # 群組訂單操作（獨立於個人訂單）
        if action_type == "group_create_order" and group_id:
            from main import group_create_order
            items = action_data.get("items", [])
            return group_create_order(group_id, username, items)

        elif action_type == "group_remove_item" and group_id:
            from main import group_remove_item
            item_name = action_data.get("item_name", "")
            quantity = action_data.get("quantity", 1)
            return group_remove_item(group_id, username, item_name, quantity)

        elif action_type == "group_cancel_order" and group_id:
            from main import group_cancel_order
            return group_cancel_order(group_id, username)

        elif action_type == "group_update_order" and group_id:
            from main import group_update_order
            old_item = action_data.get("old_item", "")
            new_item = action_data.get("new_item", {})
            return group_update_order(group_id, username, old_item, new_item)

        # 個人訂單操作
        elif action_type == "create_order":
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


def calculate_promo_price(item: dict, quantity: int) -> tuple[int, int, str | None]:
    """計算促銷價格

    Args:
        item: 菜單品項（含 promo 欄位）
        quantity: 數量

    Returns:
        (實際金額, 折扣金額, 促銷標籤)
    """
    promo = item.get("promo")
    base_price = item.get("price", 0)

    if not promo:
        return base_price * quantity, 0, None

    promo_type = promo.get("type")
    label = promo.get("label", "")

    if promo_type == "buy_one_get_one":
        # 買一送一：每兩杯收一杯錢（2杯$50=$50，3杯$50=$100）
        actual = ((quantity + 1) // 2) * base_price
        original = base_price * quantity
        return actual, original - actual, label

    elif promo_type == "second_discount":
        # 第二杯折扣
        pairs = quantity // 2
        remainder = quantity % 2
        second_price = promo.get("second_price")

        if second_price is not None:
            # 固定價格
            actual = pairs * (base_price + second_price) + remainder * base_price
        else:
            # 折扣比例
            ratio = promo.get("second_ratio", 1.0)
            actual = pairs * (base_price + int(base_price * ratio)) + remainder * base_price

        original = base_price * quantity
        return actual, original - actual, label

    elif promo_type == "time_limited":
        # 限時特價：直接使用促銷價
        promo_price = promo.get("promo_price", base_price)
        actual = promo_price * quantity
        original = base_price * quantity
        return actual, original - actual, label

    return base_price * quantity, 0, None


def _create_order(username: str, action_data: dict) -> dict:
    """建立訂單"""
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
            base_price = menu_item["price"]  # 預設價格
            if size and menu_item.get("variants"):
                variant = next((v for v in menu_item["variants"] if v["name"] == size), None)
                if variant:
                    base_price = variant["price"]

            # 計算促銷價格
            promo = menu_item.get("promo")
            item_for_calc = {"price": base_price, "promo": promo}
            actual_price, discount, promo_label = calculate_promo_price(item_for_calc, quantity)

            enriched_item = {
                "id": menu_item.get("id", item_id or item_name),
                "name": menu_item["name"],
                "price": base_price,
                "quantity": quantity,
                "size": size if size else None,
                "note": note,
                "calories": calories,
                "subtotal": actual_price
            }

            # 如果有促銷，記錄促銷資訊
            if promo:
                enriched_item["promo_type"] = promo.get("type")
                enriched_item["promo_label"] = promo_label
                enriched_item["discount"] = discount

            enriched_items.append(enriched_item)
            total += actual_price
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
    """重置對話記錄，讓下次對話重新開始"""
    # 清除對話歷史
    cleared = data.clear_ai_chat_history(username, is_manager)
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
