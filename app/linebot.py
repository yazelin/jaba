"""LINE Bot 整合模組 - 處理 LINE Webhook 事件"""
import os
from typing import Callable, Awaitable

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import (
    Configuration,
    AsyncApiClient,
    AsyncMessagingApi,
    ReplyMessageRequest,
    TextMessage,
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    LeaveEvent,
    UnfollowEvent,
)
from linebot.v3.exceptions import InvalidSignatureError

# 從環境變數載入設定
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")
REGISTER_SECRET = os.environ.get("REGISTER_SECRET")

# 檢查是否已設定 LINE Bot
LINE_BOT_ENABLED = bool(CHANNEL_SECRET and CHANNEL_ACCESS_TOKEN)

# 初始化 LINE Bot SDK（僅在有設定時）
handler: WebhookHandler | None = None
configuration: Configuration | None = None

if LINE_BOT_ENABLED:
    configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(CHANNEL_SECRET)

# 觸發關鍵字
TRIGGER_KEYWORDS = ["jaba 呷爸", "呷爸", "點餐", "jaba"]


def verify_signature(body: str, signature: str) -> bool:
    """驗證 LINE 簽章"""
    if not handler:
        return False
    try:
        handler.handle(body, signature)
        return True
    except InvalidSignatureError:
        return False


async def get_user_display_name(
    source_type: str,
    user_id: str,
    group_id: str | None = None,
    room_id: str | None = None
) -> str:
    """取得使用者的 LINE 顯示名稱"""
    if not configuration:
        return user_id

    try:
        async with AsyncApiClient(configuration) as api_client:
            messaging_api = AsyncMessagingApi(api_client)

            if source_type == "group" and group_id:
                profile = await messaging_api.get_group_member_profile(group_id, user_id)
            elif source_type == "room" and room_id:
                profile = await messaging_api.get_room_member_profile(room_id, user_id)
            else:
                profile = await messaging_api.get_profile(user_id)

            return profile.display_name
    except Exception:
        return user_id


async def get_group_name(group_id: str) -> str:
    """取得群組名稱"""
    if not configuration or not group_id:
        return ""

    try:
        async with AsyncApiClient(configuration) as api_client:
            messaging_api = AsyncMessagingApi(api_client)
            summary = await messaging_api.get_group_summary(group_id)
            return summary.group_name
    except Exception:
        return ""


async def reply_message(reply_token: str, text: str):
    """回覆訊息"""
    if not configuration or not text or not text.strip():
        return

    try:
        async with AsyncApiClient(configuration) as api_client:
            messaging_api = AsyncMessagingApi(api_client)
            await messaging_api.reply_message(
                ReplyMessageRequest(
                    reply_token=reply_token,
                    messages=[TextMessage(text=text)]
                )
            )
    except Exception as e:
        print(f"回覆訊息失敗: {e}")


def get_source_info(event: MessageEvent) -> tuple[str, str, str | None, str | None]:
    """取得來源資訊

    Returns:
        (source_type, source_id, group_id, room_id)
    """
    source = event.source
    source_type = source.type
    user_id = source.user_id

    if source_type == "group":
        return "group", source.group_id, source.group_id, None
    elif source_type == "room":
        return "group", source.room_id, None, source.room_id
    else:
        return "user", user_id, None, None


def should_respond(
    source_type: str,
    user_text: str,
    is_ordering: bool
) -> tuple[bool, str]:
    """判斷是否應該回應此訊息

    Returns:
        (should_respond, cleaned_message)
    """
    # 1對1 聊天：永遠回應
    if source_type == "user":
        return True, user_text

    text_stripped = user_text.strip()

    if is_ordering:
        # 點餐中：所有訊息都轉發
        return True, user_text
    else:
        # 非點餐中：只回應特定指令
        if text_stripped in ["開單", "菜單"]:
            return True, user_text

        # 檢查是否為啟用密碼
        if REGISTER_SECRET and text_stripped == REGISTER_SECRET:
            return True, user_text

        # 檢查是否為 @ mention（呼叫幫助）
        text_lower = text_stripped.lower()
        for keyword in TRIGGER_KEYWORDS:
            if text_lower in [keyword.lower(), f"@{keyword.lower()}"]:
                return True, "help"

        return False, user_text


def generate_help_message(
    source_type: str,
    is_registered: bool,
    is_ordering: bool
) -> str:
    """產生幫助訊息"""
    lines = ["🍱 呷爸 - AI 午餐訂便當助手", ""]

    if source_type == "group":
        if is_registered:
            lines.append("✅ 狀態：已啟用")
            if is_ordering:
                lines.append("🛒 點餐中")
                lines.append("")
                lines.append("【可用指令】")
                lines.append("• 直接說出餐點即可點餐")
                lines.append("• 「+1」或「我也要」跟單")
                lines.append("• 「收單」或「結單」結束點餐")
                lines.append("• 「菜單」查看今日菜單")
                lines.append("• 「目前訂單」查看訂單狀況")
            else:
                lines.append("💤 未在點餐中")
                lines.append("")
                lines.append("【可用指令】")
                lines.append("• 「開單」開始群組點餐")
                lines.append("• 「菜單」查看今日菜單")
        else:
            lines.append("⚠️ 狀態：未啟用")
            lines.append("")
            lines.append("請輸入啟用密碼以啟用點餐功能")
    else:
        if is_registered:
            lines.append("✅ 狀態：已啟用")
            lines.append("")
            lines.append("【偏好設定】")
            lines.append("• 告訴我你的稱呼（如「叫我小明」）")
            lines.append("• 告訴我飲食偏好（如「我不吃辣」）")
            lines.append("")
            lines.append("💡 要點餐請加入 LINE 群組，說「開單」開始！")
        else:
            lines.append("⚠️ 狀態：未啟用")
            lines.append("")
            lines.append("請輸入啟用密碼以啟用偏好設定功能")

    return "\n".join(lines)


async def handle_special_command(
    command: str,
    source_type: str,
    source_id: str,
    user_id: str,
    group_id: str | None,
    room_id: str | None,
    check_whitelist: Callable[[str], dict],
    register_whitelist: Callable[[str, str, str, str, str], Awaitable[dict]],
) -> str | None:
    """處理特殊指令，回傳回應訊息或 None"""
    cmd = command.strip()
    cmd_lower = cmd.lower()

    # 幫助請求
    if cmd == "help":
        whitelist_check = check_whitelist(source_id)
        is_registered = whitelist_check.get("registered", False)
        # is_ordering 由外部傳入更好，這裡先設為 False
        return generate_help_message(source_type, is_registered, False)

    # 移除觸發關鍵字前綴
    cmd_without_keyword = cmd
    for keyword in TRIGGER_KEYWORDS:
        if cmd_lower.startswith(keyword.lower()):
            cmd_without_keyword = cmd[len(keyword):].strip()
            break

    # 啟用密碼
    if REGISTER_SECRET and cmd_without_keyword == REGISTER_SECRET:
        # 取得名稱
        if source_type == "user":
            name = await get_user_display_name("user", user_id)
        else:
            name = await get_group_name(group_id) if group_id else ""

        # 取得啟用者資訊
        activator_name = await get_user_display_name(
            source_type, user_id, group_id, room_id
        )

        id_type = "user" if source_type == "user" else "group"
        result = await register_whitelist(
            id_type, source_id, name, user_id, activator_name
        )

        if result.get("success"):
            if result.get("already_registered"):
                if id_type == "group":
                    return "✅ 此群組已啟用，可以直接使用點餐功能！\n\n說「開單」開始群組點餐"
                else:
                    return "✅ 已啟用！你可以在這裡設定個人偏好。\n\n要點餐請加入群組喔！"
            else:
                if id_type == "group":
                    return "🎉 群組啟用成功！\n\n說「開單」開始群組點餐\n說「收單」或「結單」結束並顯示訂單摘要\n說「菜單」查看今日菜單"
                else:
                    return "🎉 啟用成功！\n\n你可以在這裡設定個人偏好：\n• 告訴我你的稱呼（如「叫我小明」）\n• 告訴我飲食偏好（如「我不吃辣」）\n\n💡 要點餐請加入 LINE 群組！"
        else:
            return f"❌ 啟用失敗：{result.get('message', '未知錯誤')}"

    # ID 查詢指令
    cmd_without_keyword_lower = cmd_without_keyword.lower()
    if cmd_without_keyword_lower in ["id", "群組id", "groupid", "userid"]:
        if group_id:
            return f"📋 ID 資訊\n\n群組 ID:\n{group_id}\n\n你的用戶 ID:\n{user_id}"
        elif room_id:
            return f"📋 ID 資訊\n\n聊天室 ID:\n{room_id}\n\n你的用戶 ID:\n{user_id}"
        else:
            return f"📋 ID 資訊\n\n你的用戶 ID:\n{user_id}"

    return None
