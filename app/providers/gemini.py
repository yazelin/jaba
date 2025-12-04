"""Gemini CLI Provider"""
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from . import BaseProvider, CommandResult, DATA_DIR
from ..data import SessionInfo


class GeminiProvider(BaseProvider):
    """Gemini CLI Provider 實作"""

    @property
    def name(self) -> str:
        return "gemini"

    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_info: SessionInfo | None
    ) -> CommandResult:
        """建構 Gemini CLI 對話命令

        Gemini CLI 特點：
        - 無 --system-prompt，需併入 prompt 開頭
        - 使用 -m 指定模型
        - 不使用 -o json（讓 AI 直接回應我們 prompt 要求的 JSON 格式）
        - Session 使用索引而非 UUID
        """
        # 將 system prompt 併入 prompt 開頭
        full_prompt = f"{system_prompt}\n\n{prompt}"

        cmd = ["gemini", "-m", model]
        is_new_session = False

        if session_info and session_info.session_index is not None:
            # 後續對話：恢復 session
            cmd.extend(["--resume", str(session_info.session_index)])
        else:
            # 首次對話：不加 --resume，讓 Gemini 自動建立
            is_new_session = True

        cmd.append(full_prompt)

        return CommandResult(
            cmd=cmd,
            cwd=str(DATA_DIR.parent),
            is_new_session=is_new_session
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

        Gemini 回應可能包含 markdown code block，需要清理
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
        """Gemini 需事後呼叫 --list-sessions 追蹤 session 索引"""
        if not is_new_session or return_code != 0:
            return None

        session_index = self._get_latest_session_index()
        if session_index is not None:
            return SessionInfo(
                provider="gemini",
                session_index=session_index,
                is_manager=is_manager,
                created_at=datetime.now().isoformat()
            )
        return None

    def delete_session(self, session_info: SessionInfo) -> bool:
        """刪除 Gemini session"""
        if session_info.session_index is None:
            return True

        try:
            result = subprocess.run(
                ["gemini", "--delete-session", str(session_info.session_index)],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(DATA_DIR.parent)
            )
            return result.returncode == 0
        except Exception:
            return False

    def _get_latest_session_index(self) -> int | None:
        """取得 Gemini 最新 session 的索引編號

        解析 `gemini --list-sessions` 輸出，取得最大索引。
        輸出格式範例：
            Available sessions for this project (2):
              1. models (38 minutes ago) [d1d3142a-...]
              2. {"test": "hello"}  OK (Just now) [e92bed4a-...]

        Returns:
            int: 最大索引編號，或 None 如果沒有 session
        """
        try:
            result = subprocess.run(
                ["gemini", "--list-sessions"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=str(DATA_DIR.parent)
            )

            # Gemini CLI 將 list-sessions 輸出到 stderr
            output = (result.stdout + result.stderr).strip()
            if not output or "Available sessions" not in output:
                return None

            # 解析 session 索引（格式："  1. ...", "  2. ..."）
            max_index = None
            for line in output.split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    # 取得開頭的數字
                    match = re.match(r'^(\d+)\.', line)
                    if match:
                        index = int(match.group(1))
                        if max_index is None or index > max_index:
                            max_index = index

            return max_index

        except Exception:
            return None
