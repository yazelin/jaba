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


def get_system_prompt(is_manager: bool = False, group_ordering: bool = False, personal_mode: bool = False) -> str:
    """取得系統提示詞"""
    prompt_data = data.get_jaba_prompt()

    if group_ordering:
        # 群組點餐模式：載入 group_ordering_prompt
        base_prompt = prompt_data.get("group_ordering_prompt", "")
        return f"""{base_prompt}

請用繁體中文回應。"""

    if personal_mode:
        # 個人偏好設定模式：載入 personal_prompt
        base_prompt = prompt_data.get("personal_prompt", "")
        return f"""{base_prompt}

請用繁體中文回應。"""

    # 管理員模式：載入 manager_prompt
    base_prompt = prompt_data.get("manager_prompt", "")
    return f"""{base_prompt}

請用繁體中文回應。"""


def build_context(
    username: str,
    is_manager: bool = False,
    group_ordering: bool = False,
    group_id: str | None = None,
    session_orders: list | None = None,
    line_user_id: str | None = None,
    display_name: str | None = None,
    personal_mode: bool = False
) -> dict:
    """建立 AI 上下文

    Args:
        username: 使用者名稱（舊版相容，個人模式用）
        is_manager: 是否為管理員模式
        group_ordering: 是否為群組點餐模式
        group_id: 群組 ID
        session_orders: 群組訂單列表
        line_user_id: LINE User ID（群組點餐時用於查詢使用者 profile）
        display_name: LINE 顯示名稱（群組點餐時作為 username 傳給 AI）
        personal_mode: 是否為個人偏好設定模式
    """
    today_info = data.get_today_info()
    today_stores = today_info.get("stores", [])

    # 個人偏好設定模式（僅提供使用者偏好資訊，不提供菜單和訂單）
    if personal_mode:
        # 使用 line_user_id 查詢使用者 profile
        profile = None
        if line_user_id:
            profile = data.get_user_by_line_id(line_user_id)
        if not profile:
            profile = data.get_user_profile(username)

        user_profile = {}
        preferred_name = None
        if profile:
            user_profile = profile.get("preferences", {})
            preferred_name = user_profile.get("preferred_name")

        return {
            "mode": "personal_preferences",
            "username": display_name or username,
            "preferred_name": preferred_name,
            "user_profile": user_profile,
        }

    # 群組點餐模式
    if group_ordering:
        # 使用 display_name 作為 AI 看到的 username
        ai_username = display_name or username

        # 取得當前使用者的偏好（優先用 line_user_id 查詢）
        profile = None
        if line_user_id:
            profile = data.get_user_by_line_id(line_user_id)
        if not profile:
            profile = data.get_user_profile(username)

        user_profile = None
        preferred_name = None
        if profile:
            user_profile = profile.get("preferences", {})
            preferred_name = user_profile.get("preferred_name")

        # 決定 AI 應該使用的稱呼（優先用 preferred_name）
        ai_display_name = preferred_name or ai_username

        # 格式化 session_orders，確保使用 display_name
        formatted_orders = []
        for order in (session_orders or []):
            formatted_orders.append({
                "display_name": order.get("display_name") or order.get("username", ""),
                "items": order.get("items", []),
                "total": order.get("total", 0)
            })

        context = {
            "today": date.today().isoformat(),
            "today_stores": today_stores,
            "username": ai_display_name,  # AI 應該用這個名字稱呼使用者
            "user_profile": user_profile,  # 當前使用者的偏好（飲食限制等）
            "group_ordering": True,
            "session_orders": formatted_orders,  # 群組目前的訂單
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
        # 使用者模式：加入偏好
        if profile:
            context["user_profile"] = profile.get("preferences", {})

    if is_manager:
        # 管理員模式：需要店家列表來設定今日店家
        stores = data.get_active_stores()
        context["available_stores"] = [{"id": s["id"], "name": s["name"]} for s in stores]

    return context


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
    group_id: str | None = None,
    line_user_id: str | None = None,
    display_name: str | None = None,
    group_name: str | None = None,
    personal_mode: bool = False
) -> dict:
    """呼叫 AI CLI（支援多種 Provider）

    使用自管理的對話歷史，不依賴 CLI session 機制。
    每次呼叫組合：系統上下文 + 對話歷史 + 當前訊息。
    使用 asyncio 非同步執行，不阻塞其他請求。

    Args:
        username: 使用者名稱（舊版相容）
        message: 使用者訊息
        is_manager: 是否為管理員模式
        group_ordering: 是否為群組點餐模式
        group_id: 群組 ID
        line_user_id: LINE User ID（群組點餐時傳入）
        display_name: LINE 顯示名稱（群組點餐時傳入）
        group_name: 群組名稱（群組點餐時傳入，用於看板聚合對話）
        personal_mode: 是否為個人偏好設定模式
    """
    timings = {}
    t_start = time.time()

    # 確保使用者存在（優先使用 line_user_id）
    if line_user_id and display_name:
        data.ensure_user_by_line_id(line_user_id, display_name)
    elif username:
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
        # 個人模式：使用個人對話歷史（優先用 line_user_id）
        user_key = line_user_id or username
        history = data.get_ai_chat_history(user_key, is_manager)
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

    system_prompt = get_system_prompt(is_manager, group_ordering, personal_mode)
    context = build_context(
        username, is_manager, group_ordering, group_id, session_orders,
        line_user_id, display_name, personal_mode
    )

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
        # 同時儲存到看板聚合對話
        if group_name:
            data.append_to_board_chat(group_name, username, "user", message)
    else:
        data.append_ai_chat_history(user_key, "user", message, is_manager)

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
                # 同時儲存到看板聚合對話（呷爸回覆）
                if group_name:
                    data.append_to_board_chat(group_name, "呷爸", "assistant", ai_message)
            else:
                data.append_ai_chat_history(user_key, "assistant", ai_message, is_manager)

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
    group_id: str | None = None,
    line_user_id: str | None = None,
    display_name: str | None = None,
    personal_mode: bool = False
) -> list:
    """執行多個 AI 請求的動作，回傳結果陣列

    Args:
        username: 使用者名稱（舊版相容用）
        actions: 動作列表
        is_manager: 是否為管理員模式
        group_id: 群組 ID（群組點餐時傳入）
        line_user_id: LINE User ID（群組點餐時傳入）
        display_name: LINE 顯示名稱（群組點餐時傳入）
        personal_mode: 是否為個人偏好設定模式
    """
    if not actions:
        return []

    results = []
    for action in actions:
        result = execute_action(username, action, is_manager, group_id, line_user_id, display_name, personal_mode)
        results.append(result)
    return results


def execute_action(
    username: str,
    action: dict,
    is_manager: bool = False,
    group_id: str | None = None,
    line_user_id: str | None = None,
    display_name: str | None = None,
    personal_mode: bool = False
) -> dict:
    """執行單一 AI 請求的動作

    Args:
        username: 使用者名稱（舊版相容用）
        action: 動作資料
        is_manager: 是否為管理員模式
        group_id: 群組 ID（群組點餐時傳入）
        line_user_id: LINE User ID（群組點餐時傳入）
        display_name: LINE 顯示名稱（群組點餐時傳入）
        personal_mode: 是否為個人偏好設定模式
    """
    if not action:
        return {"success": True}

    action_type = action.get("type")
    action_data = action.get("data", {})

    # 群組點餐使用 line_user_id，否則回退到 username
    user_id = line_user_id or username
    user_display = display_name or username

    # 個人偏好設定模式：只允許 update_user_profile 動作
    if personal_mode and action_type != "update_user_profile":
        return {
            "success": False,
            "error": "個人模式只支援偏好設定功能",
            "message": "要點餐請加入 LINE 群組喔！"
        }

    try:
        # 群組訂單操作（獨立於個人訂單）
        if action_type == "group_create_order" and group_id:
            from main import group_create_order
            items = action_data.get("items", [])
            return group_create_order(group_id, user_id, user_display, items)

        elif action_type == "group_remove_item" and group_id:
            from main import group_remove_item
            item_name = action_data.get("item_name", "")
            quantity = action_data.get("quantity", 1)
            return group_remove_item(group_id, user_id, item_name, quantity)

        elif action_type == "group_cancel_order" and group_id:
            from main import group_cancel_order
            return group_cancel_order(group_id, user_id)

        elif action_type == "group_update_order" and group_id:
            from main import group_update_order
            old_item = action_data.get("old_item", "")
            new_item = action_data.get("new_item", {})
            return group_update_order(group_id, user_id, user_display, old_item, new_item)

        # 店家管理
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
        elif action_type == "reset_session":
            return _reset_session(username, is_manager)
        elif action_type == "update_user_profile":
            # 群組模式下使用 line_user_id，否則使用 username
            return _update_user_profile(user_id, action_data)
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
