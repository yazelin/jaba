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
    """取得今日訂餐資訊"""
    return read_json(DATA_DIR / "system" / "today.json") or {}


def set_today_store(store_id: str, store_name: str, set_by: str = "管理員") -> dict:
    """設定今日店家"""
    today = date.today().isoformat()
    data = {
        "date": today,
        "store_id": store_id,
        "store_name": store_name,
        "status": "open",
        "set_by": set_by,
        "set_at": datetime.now().isoformat()
    }
    write_json(DATA_DIR / "system" / "today.json", data)
    return data


def get_jiaba_prompt() -> dict:
    """取得 AI 系統提示詞"""
    return read_json(DATA_DIR / "system" / "prompts" / "jiaba.json") or {}


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


def get_session_id(username: str) -> str | None:
    """取得使用者今日的 session ID"""
    today = date.today().isoformat()
    session_file = DATA_DIR / "users" / username / "sessions" / f"{today}.txt"
    if session_file.exists():
        return session_file.read_text().strip()
    return None


def save_session_id(username: str, session_id: str) -> None:
    """儲存使用者今日的 session ID"""
    today = date.today().isoformat()
    session_dir = DATA_DIR / "users" / username / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / f"{today}.txt").write_text(session_id)


# === 訂單管理 ===

def get_user_order(username: str, order_date: str = None) -> dict | None:
    """取得使用者某日的訂單"""
    if order_date is None:
        order_date = date.today().isoformat()
    return read_json(DATA_DIR / "users" / username / "orders" / f"{order_date}.json")


def save_user_order(username: str, order: dict) -> None:
    """儲存使用者訂單"""
    order_date = order.get("date", date.today().isoformat())
    write_json(DATA_DIR / "users" / username / "orders" / f"{order_date}.json", order)


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
    """用訂單更新每日彙整"""
    order_date = order.get("date", date.today().isoformat())
    summary = get_daily_summary(order_date) or {
        "date": order_date,
        "store_id": order.get("store_id"),
        "store_name": order.get("store_name"),
        "orders": [],
        "item_summary": [],
        "grand_total": 0,
        "updated_at": datetime.now().isoformat()
    }

    # 移除該使用者舊訂單
    summary["orders"] = [o for o in summary["orders"] if o["username"] != username]

    # 加入新訂單
    summary["orders"].append({
        "username": username,
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

    # 更新或新增付款記錄
    existing = next((r for r in payments["records"] if r["username"] == username), None)
    if existing:
        existing["amount"] = order["total"]
    else:
        payments["records"].append({
            "username": username,
            "amount": order["total"],
            "paid": False,
            "paid_at": None,
            "note": None
        })

    # 重新計算總額
    payments["total_collected"] = sum(r["amount"] for r in payments["records"] if r["paid"])
    payments["total_pending"] = sum(r["amount"] for r in payments["records"] if not r["paid"])

    save_payments(payments)

    return summary
