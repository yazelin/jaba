"""Claude CLI Provider"""
import json
import re
import uuid
from datetime import datetime

from . import BaseProvider, CommandResult, DATA_DIR
from ..data import SessionInfo


class ClaudeProvider(BaseProvider):
    """Claude CLI Provider 實作"""

    @property
    def name(self) -> str:
        return "claude"

    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_info: SessionInfo | None
    ) -> CommandResult:
        """建構 Claude CLI 對話命令

        Claude CLI 特點：
        - 使用 -p 進行非互動式對話
        - 使用 --system-prompt 傳遞系統提示
        - Session 使用 UUID，透過 --session-id 和 --resume 管理
        """
        cmd = ["claude", "-p", "--model", model, "--system-prompt", system_prompt]
        new_session_id = None
        is_new_session = False

        if session_info and session_info.session_id:
            # 後續對話：恢復 session
            cmd.extend(["--resume", session_info.session_id])
        else:
            # 首次對話：生成 UUID 並建立 session
            new_session_id = str(uuid.uuid4())
            cmd.extend(["--session-id", new_session_id])
            is_new_session = True

        cmd.append(prompt)

        return CommandResult(
            cmd=cmd,
            cwd=str(DATA_DIR.parent),
            new_session_id=new_session_id,
            is_new_session=is_new_session
        )

    def build_menu_command(
        self,
        model: str,
        prompt: str,
        image_path: str
    ) -> CommandResult:
        """建構 Claude CLI 菜單辨識命令

        使用 Read 工具讓 Claude 讀取圖片
        """
        full_prompt = f"請先使用 Read 工具讀取圖片 {image_path}，然後{prompt}"
        cmd = [
            "claude", "-p", full_prompt,
            "--model", model,
            "--tools", "Read",
            "--allowedTools", "Read",
            "--dangerously-skip-permissions"
        ]

        return CommandResult(
            cmd=cmd,
            cwd=str(DATA_DIR.parent)
        )

    def parse_response(self, stdout: str, stderr: str, return_code: int) -> dict:
        """解析 Claude CLI 回應

        Claude 回應通常直接是 JSON 或需要從中提取 JSON
        """
        response_text = stdout.strip()

        if not response_text:
            if return_code != 0:
                return {
                    "message": f"CLI 執行失敗：{stderr or '未知錯誤'}",
                    "actions": [],
                    "error": stderr or "unknown"
                }
            return {
                "message": "AI 沒有回應",
                "actions": []
            }

        try:
            # 移除 markdown code block（如 ```json ... ```）
            clean_text = re.sub(r'^```(?:json)?\s*', '', response_text)
            clean_text = re.sub(r'\s*```$', '', clean_text).strip()

            # 尋找 JSON 內容
            json_match = re.search(r'\{[\s\S]*\}', clean_text)
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

    def get_session_info_after_call(
        self,
        is_new_session: bool,
        return_code: int,
        is_manager: bool
    ) -> SessionInfo | None:
        """Claude 在建構命令時就已經生成 session_id，不需要事後追蹤"""
        # Claude 的 session_id 在 build_chat_command 時就已經設定
        # 透過 CommandResult.new_session_id 回傳，由 call_ai 處理
        return None

    def delete_session(self, session_info: SessionInfo) -> bool:
        """Claude CLI 不需要刪除遠端 session"""
        # Claude 的 session 是本地管理，不需要呼叫 CLI 刪除
        return True
