"""AI CLI Provider 模組 - 支援多種 CLI 工具"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from ..data import SessionInfo, DATA_DIR


@dataclass
class CommandResult:
    """CLI 命令建構結果"""
    cmd: list[str]
    cwd: str
    new_session_id: str | None = None  # Claude 用：新建的 UUID
    is_new_session: bool = False  # 是否為新 session（用於 Gemini 事後追蹤）


class BaseProvider(ABC):
    """CLI Provider 抽象基底類別"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider 名稱"""
        pass

    @abstractmethod
    def build_chat_command(
        self,
        model: str,
        prompt: str,
        system_prompt: str,
        session_info: SessionInfo | None
    ) -> CommandResult:
        """建構對話命令"""
        pass

    @abstractmethod
    def build_menu_command(
        self,
        model: str,
        prompt: str,
        image_path: str
    ) -> CommandResult:
        """建構菜單辨識命令"""
        pass

    @abstractmethod
    def parse_response(self, stdout: str, stderr: str, return_code: int) -> dict:
        """解析 CLI 回應"""
        pass

    @abstractmethod
    def get_session_info_after_call(
        self,
        is_new_session: bool,
        return_code: int,
        is_manager: bool
    ) -> SessionInfo | None:
        """呼叫後取得 session 資訊（如 Gemini 需事後追蹤）"""
        pass

    @abstractmethod
    def delete_session(self, session_info: SessionInfo) -> bool:
        """刪除 session"""
        pass


def get_provider(provider_name: str) -> BaseProvider:
    """根據名稱取得 provider 實例"""
    from .claude import ClaudeProvider
    from .gemini import GeminiProvider

    providers = {
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
    }
    provider_class = providers.get(provider_name, ClaudeProvider)
    return provider_class()
