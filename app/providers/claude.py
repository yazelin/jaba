"""Claude CLI Provider"""
import json
import re
from pathlib import Path

from . import BaseProvider, CommandResult, DATA_DIR


class ClaudeProvider(BaseProvider):
    """Claude CLI Provider 實作

    注意：不再使用 Claude CLI 的 session 機制（--resume, --session-id）。
    對話歷史由 app/data.py 的 get_ai_chat_history() 等函數管理。
    """

    @property
    def name(self) -> str:
        return "claude"

    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_info=None  # 保留參數向後相容，但不再使用
    ) -> CommandResult:
        """建構 Claude CLI 對話命令

        Claude CLI 特點：
        - 使用 -p 進行非互動式對話
        - 使用 --system-prompt 傳遞系統提示
        - 不使用 --resume / --session-id（每次都是新對話，歷史由我們管理）
        """
        cmd = ["claude", "-p", "--model", model, "--system-prompt", system_prompt, prompt]

        return CommandResult(
            cmd=cmd,
            cwd=str(DATA_DIR.parent)
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
