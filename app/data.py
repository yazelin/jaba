"""資料存取模組 - JSON 檔案讀寫與目錄操作"""
import json
from pathlib import Path
from datetime import date, datetime
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"


def ensure_data_dirs():
    """確保資料目錄結構存在"""
    dirs = [
        DATA_DIR / "system" / "prompts",
        DATA_DIR / "stores",
        DATA_DIR / "users",
        DATA_DIR / "orders",
        DATA_DIR / "chat",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def read_json(path: Path | str) -> dict | list | None:
    """讀取 JSON 檔案"""
    path = Path(path)
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path | str, data: dict | list) -> None:
    """寫入 JSON 檔案（格式化輸出）"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def list_dirs(path: Path | str) -> list[str]:
    """列出目錄下的子目錄名稱"""
    path = Path(path)
    if not path.exists():
        return []
    return [d.name for d in path.iterdir() if d.is_dir()]


def list_files(path: Path | str, suffix: str = ".json") -> list[str]:
    """列出目錄下的檔案名稱"""
    path = Path(path)
    if not path.exists():
        return []
    return [f.name for f in path.iterdir() if f.is_file() and f.suffix == suffix]


# === 系統設定 ===

def get_config() -> dict:
    """取得系統設定"""
    return read_json(DATA_DIR / "system" / "config.json") or {}


def get_today_info() -> dict:
    """取得今日訂餐資訊（支援多店家）"""
    data = read_json(DATA_DIR / "system" / "today.json") or {}

    # 如果是舊格式（單店家），轉換為新格式
    if data and "stores" not in data and data.get("store_id"):
        data = {
            "date": data.get("date", date.today().isoformat()),
            "stores": [{
                "store_id": data["store_id"],
                "store_name": data.get("store_name", ""),
                "status": data.get("status", "open"),
                "set_by": data.get("set_by", "管理員"),
                "set_at": data.get("set_at", "")
            }],
            # 向後相容：保留單店家欄位
            "store_id": data["store_id"],
            "store_name": data.get("store_name", "")
        }

    return data


def set_today_store(store_id: str, store_name: str, set_by: str = "管理員") -> dict:
    """設定今日店家（向後相容，設定單一店家會清除其他店家）"""
    return add_today_store(store_id, store_name, set_by, clear_others=True)


def add_today_store(store_id: str, store_name: str, set_by: str = "管理員", clear_others: bool = False) -> dict:
    """新增今日店家"""
    today_str = date.today().isoformat()
    data = read_json(DATA_DIR / "system" / "today.json") or {}

    # 確保是新格式
    if "stores" not in data or data.get("date") != today_str:
        data = {"date": today_str, "stores": []}

    # 如果要清除其他店家
    if clear_others:
        data["stores"] = []

    # 檢查是否已存在
    existing = next((s for s in data["stores"] if s["store_id"] == store_id), None)
    if existing:
        # 更新現有店家
        existing["store_name"] = store_name
        existing["set_by"] = set_by
        existing["set_at"] = datetime.now().isoformat()
    else:
        # 新增店家
        data["stores"].append({
            "store_id": store_id,
            "store_name": store_name,
            "status": "open",
            "set_by": set_by,
            "set_at": datetime.now().isoformat()
        })

    # 向後相容：設定第一個店家為預設
    if data["stores"]:
        data["store_id"] = data["stores"][0]["store_id"]
        data["store_name"] = data["stores"][0]["store_name"]

    write_json(DATA_DIR / "system" / "today.json", data)
    return data


def remove_today_store(store_id: str) -> dict:
    """從今日列表移除店家"""
    data = get_today_info()

    if "stores" in data:
        data["stores"] = [s for s in data["stores"] if s["store_id"] != store_id]

        # 更新向後相容欄位
        if data["stores"]:
            data["store_id"] = data["stores"][0]["store_id"]
            data["store_name"] = data["stores"][0]["store_name"]
        else:
            data["store_id"] = None
            data["store_name"] = None

    write_json(DATA_DIR / "system" / "today.json", data)
    return data


def get_jaba_prompt() -> dict:
    """取得 AI 系統提示詞"""
    return read_json(DATA_DIR / "system" / "prompts" / "jaba.json") or {}


def get_ai_config() -> dict:
    """取得 AI 設定"""
    default_config = {
        "chat": {"model": "haiku"},
        "menu_recognition": {"model": "sonnet"}
    }
    config = read_json(DATA_DIR / "system" / "ai_config.json")
    if config:
        # 合併預設值
        for key in default_config:
            if key not in config:
                config[key] = default_config[key]
        return config
    return default_config


# === 店家管理 ===

def get_stores() -> list[dict]:
    """取得所有店家列表"""
    stores = []
    for store_id in list_dirs(DATA_DIR / "stores"):
        info = read_json(DATA_DIR / "stores" / store_id / "info.json")
        if info:
            stores.append(info)
    return stores


def get_active_stores() -> list[dict]:
    """取得所有啟用的店家"""
    return [s for s in get_stores() if s.get("active", True)]


def get_store(store_id: str) -> dict | None:
    """取得店家資訊"""
    return read_json(DATA_DIR / "stores" / store_id / "info.json")


def get_menu(store_id: str) -> dict | None:
    """取得店家菜單"""
    return read_json(DATA_DIR / "stores" / store_id / "menu.json")


def save_store(store_id: str, info: dict) -> None:
    """儲存店家資訊"""
    store_dir = DATA_DIR / "stores" / store_id
    store_dir.mkdir(parents=True, exist_ok=True)
    (store_dir / "images").mkdir(exist_ok=True)
    write_json(store_dir / "info.json", info)


def save_menu(store_id: str, menu: dict) -> None:
    """儲存店家菜單"""
    write_json(DATA_DIR / "stores" / store_id / "menu.json", menu)


# === 使用者管理 ===

def get_user(username: str) -> dict | None:
    """取得使用者資訊"""
    return read_json(DATA_DIR / "users" / username / "profile.json")


def ensure_user(username: str) -> dict:
    """確保使用者存在，不存在則建立"""
    user = get_user(username)
    if user:
        return user

    user_dir = DATA_DIR / "users" / username
    user_dir.mkdir(parents=True, exist_ok=True)
    (user_dir / "orders").mkdir(exist_ok=True)
    (user_dir / "sessions").mkdir(exist_ok=True)

    profile = {
        "username": username,
        "created_at": datetime.now().isoformat(),
        "preferences": {}
    }
    write_json(user_dir / "profile.json", profile)
    return profile


def get_users() -> list[dict]:
    """取得所有使用者列表"""
    users = []
    for username in list_dirs(DATA_DIR / "users"):
        user = get_user(username)
        if user:
            users.append(user)
    return users


def get_session_id(username: str, is_manager: bool = False) -> str | None:
    """取得使用者今日的 session ID（管理員和一般模式分開）"""
    today = date.today().isoformat()
    suffix = "-manager" if is_manager else ""
    session_file = DATA_DIR / "users" / username / "sessions" / f"{today}{suffix}.txt"
    if session_file.exists():
        return session_file.read_text().strip()
    return None


def save_session_id(username: str, session_id: str, is_manager: bool = False) -> None:
    """儲存使用者今日的 session ID（管理員和一般模式分開）"""
    today = date.today().isoformat()
    suffix = "-manager" if is_manager else ""
    session_dir = DATA_DIR / "users" / username / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / f"{today}{suffix}.txt").write_text(session_id)


def clear_session_id(username: str, is_manager: bool = False) -> bool:
    """清除使用者今日的 session ID（用於重新開始對話）"""
    today = date.today().isoformat()
    suffix = "-manager" if is_manager else ""
    session_file = DATA_DIR / "users" / username / "sessions" / f"{today}{suffix}.txt"
    if session_file.exists():
        session_file.unlink()
        return True
    return False


# === 訂單管理 ===

def get_user_order(username: str, order_date: str = None) -> dict | None:
    """取得使用者某日的單一訂單（向後相容，取得最新一筆）"""
    if order_date is None:
        order_date = date.today().isoformat()
    # 先嘗試舊格式
    old_format = read_json(DATA_DIR / "users" / username / "orders" / f"{order_date}.json")
    if old_format:
        return old_format
    # 嘗試新格式（多訂單）
    orders = get_user_orders(username, order_date)
    return orders[-1] if orders else None


def get_user_orders(username: str, order_date: str = None) -> list[dict]:
    """取得使用者某日的所有訂單"""
    if order_date is None:
        order_date = date.today().isoformat()
    orders_dir = DATA_DIR / "users" / username / "orders"
    if not orders_dir.exists():
        return []

    orders = []
    # 舊格式：{date}.json
    old_file = orders_dir / f"{order_date}.json"
    if old_file.exists():
        order = read_json(old_file)
        if order:
            orders.append(order)

    # 新格式：{date}-{timestamp}.json
    for f in orders_dir.glob(f"{order_date}-*.json"):
        order = read_json(f)
        if order:
            orders.append(order)

    # 按建立時間排序
    orders.sort(key=lambda x: x.get("created_at", ""))
    return orders


def save_user_order(username: str, order: dict) -> str:
    """儲存使用者訂單，回傳 order_id"""
    order_date = order.get("date", date.today().isoformat())
    timestamp = datetime.now().strftime("%H%M%S%f")[:10]
    order_id = f"{order_date}-{timestamp}"
    order["order_id"] = order_id
    write_json(DATA_DIR / "users" / username / "orders" / f"{order_id}.json", order)
    return order_id


def delete_user_order(username: str, order_id: str) -> bool:
    """刪除使用者特定訂單"""
    order_file = DATA_DIR / "users" / username / "orders" / f"{order_id}.json"
    if order_file.exists():
        order_file.unlink()
        return True
    return False


def get_daily_summary(order_date: str = None) -> dict | None:
    """取得每日訂單彙整"""
    if order_date is None:
        order_date = date.today().isoformat()
    return read_json(DATA_DIR / "orders" / order_date / "summary.json")


def save_daily_summary(summary: dict) -> None:
    """儲存每日訂單彙整"""
    order_date = summary.get("date", date.today().isoformat())
    order_dir = DATA_DIR / "orders" / order_date
    order_dir.mkdir(parents=True, exist_ok=True)
    write_json(order_dir / "summary.json", summary)


def get_payments(order_date: str = None) -> dict | None:
    """取得付款記錄"""
    if order_date is None:
        order_date = date.today().isoformat()
    return read_json(DATA_DIR / "orders" / order_date / "payments.json")


def save_payments(payments: dict) -> None:
    """儲存付款記錄"""
    order_date = payments.get("date", date.today().isoformat())
    order_dir = DATA_DIR / "orders" / order_date
    order_dir.mkdir(parents=True, exist_ok=True)
    write_json(order_dir / "payments.json", payments)


def update_daily_summary_with_order(username: str, order: dict) -> dict:
    """用訂單更新每日彙整（支援多訂單）"""
    order_date = order.get("date", date.today().isoformat())
    order_id = order.get("order_id")

    summary = get_daily_summary(order_date) or {
        "date": order_date,
        "store_id": order.get("store_id"),
        "store_name": order.get("store_name"),
        "orders": [],
        "item_summary": [],
        "grand_total": 0,
        "updated_at": datetime.now().isoformat()
    }

    # 如果有 order_id，用它來識別；否則用 username（向後相容）
    if order_id:
        summary["orders"] = [o for o in summary["orders"] if o.get("order_id") != order_id]
    else:
        # 舊邏輯：移除該使用者的訂單（只保留最新一筆）
        summary["orders"] = [o for o in summary["orders"] if o["username"] != username]

    # 加入新訂單
    summary["orders"].append({
        "order_id": order_id,
        "username": username,
        "store_id": order.get("store_id"),
        "store_name": order.get("store_name"),
        "items": order["items"],
        "total": order["total"]
    })

    # 重新計算品項統計
    item_counts = {}
    for o in summary["orders"]:
        for item in o["items"]:
            name = item["name"]
            qty = item.get("quantity", 1)
            item_counts[name] = item_counts.get(name, 0) + qty

    summary["item_summary"] = [{"name": k, "quantity": v} for k, v in item_counts.items()]
    summary["grand_total"] = sum(o["total"] for o in summary["orders"])
    summary["updated_at"] = datetime.now().isoformat()

    save_daily_summary(summary)

    # 更新付款記錄
    payments = get_payments(order_date) or {
        "date": order_date,
        "records": [],
        "total_collected": 0,
        "total_pending": 0
    }

    # 計算該使用者所有訂單的總金額
    user_total = sum(o["total"] for o in summary["orders"] if o["username"] == username)

    # 更新或新增付款記錄
    existing = next((r for r in payments["records"] if r["username"] == username), None)
    if existing:
        existing["amount"] = user_total
    else:
        payments["records"].append({
            "username": username,
            "amount": user_total,
            "paid": False,
            "paid_at": None,
            "note": None
        })

    # 重新計算總額
    payments["total_collected"] = sum(r["amount"] for r in payments["records"] if r["paid"])
    payments["total_pending"] = sum(r["amount"] for r in payments["records"] if not r["paid"])

    save_payments(payments)

    return summary


# === 聊天功能 ===

def get_chat_messages(chat_date: str = None) -> list[dict]:
    """取得某日的聊天記錄"""
    if chat_date is None:
        chat_date = date.today().isoformat()
    data = read_json(DATA_DIR / "chat" / f"{chat_date}.json")
    if data:
        return data.get("messages", [])
    return []


def save_chat_message(username: str, content: str) -> dict:
    """儲存新的聊天訊息，回傳新訊息物件"""
    chat_date = date.today().isoformat()
    chat_file = DATA_DIR / "chat" / f"{chat_date}.json"

    data = read_json(chat_file) or {
        "date": chat_date,
        "messages": []
    }

    # 建立新訊息
    new_message = {
        "id": f"{chat_date}-{len(data['messages']) + 1:04d}",
        "username": username,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }

    data["messages"].append(new_message)
    write_json(chat_file, data)

    return new_message
