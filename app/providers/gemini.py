"""Gemini CLI Provider"""
import json
import re
from pathlib import Path

from . import BaseProvider, CommandResult, DATA_DIR


class GeminiProvider(BaseProvider):
    """Gemini CLI Provider 實作

    注意：不再使用 Gemini CLI 的 session 機制（--resume）。
    對話歷史由 app/data.py 的 get_ai_chat_history() 等函數管理。
    """

    # 預設模型（當 ai_config 未指定時使用）
    DEFAULT_CHAT_MODEL = "gemini-2.5-flash-lite"

    @property
    def name(self) -> str:
        return "gemini"

    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_info=None  # 保留參數向後相容，但不再使用
    ) -> CommandResult:
        """建構 Gemini CLI 對話命令

        Gemini CLI 特點：
        - 無 --system-prompt，需併入 prompt 開頭
        - 使用 -m 指定模型
        - 不使用 -o json（讓 AI 直接回應我們 prompt 要求的 JSON 格式）
        - 不使用 --resume（每次都是新對話，歷史由我們管理）
        """
        # 將 system prompt 併入 prompt 開頭
        full_prompt = f"{system_prompt}\n\n{prompt}"

        # 使用指定模型，若未指定則用預設值
        actual_model = model or self.DEFAULT_CHAT_MODEL
        cmd = ["gemini", "-m", actual_model, full_prompt]

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
        """建構 Gemini CLI 菜單辨識命令

        Gemini CLI 使用 @檔名 語法引用圖片，需在圖片所在目錄執行。
        """
        image_filename = Path(image_path).name
        image_dir = str(Path(image_path).parent)

        # 使用 @檔名 語法讓 Gemini 直接分析圖片
        full_prompt = f"@{image_filename} {prompt}"
        cmd = [
            "gemini", "-m", model,
            "-y",  # YOLO mode - 自動確認
            full_prompt
        ]

        return CommandResult(
            cmd=cmd,
            cwd=image_dir
        )

    def parse_response(self, stdout: str, stderr: str, return_code: int) -> dict:
        """解析 Gemini CLI 回應

        Gemini 回應可能包含 markdown code block，需要清理。
        解析失敗時會回傳 AI 的實際回應供診斷。
        """
        response_text = stdout.strip()

        if not response_text:
            if return_code != 0:
                return {
                    "message": f"CLI 執行失敗：{stderr or '未知錯誤'}",
                    "actions": [],
                    "error": "cli_error"
                }
            return {
                "message": stderr or "AI 沒有回應",
                "actions": [],
                "error": "no_response"
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
                # AI 沒有回傳 JSON，直接用回應作為 message
                return {
                    "message": response_text,
                    "actions": []
                }
        except json.JSONDecodeError:
            # 解析失敗時回傳 AI 的實際回應供診斷
            return {
                "message": response_text[:300],
                "actions": [],
                "error": "parse_error",
                "raw_response": response_text[:500]
            }
