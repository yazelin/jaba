"""AI CLI Provider 模組 - 支援多種 CLI 工具"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..data import DATA_DIR


@dataclass
class CommandResult:
    """CLI 命令建構結果"""
    cmd: list[str]
    cwd: str


class BaseProvider(ABC):
    """CLI Provider 抽象基底類別

    注意：不再使用 CLI 內建的 session 機制，每次呼叫都是獨立對話。
    對話歷史由 app/data.py 的 get_ai_chat_history() 等函數管理。
    """

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
        session_info=None  # 保留參數向後相容，但不再使用
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
