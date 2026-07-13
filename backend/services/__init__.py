from backend.services.base import BaseAIService
from backend.services.ai_mock import MockAIService
from backend.services.ai_deepseek import DeepSeekAIService


def create_ai_service(config) -> BaseAIService:
    """根据 .env 中的 AI_PROVIDER 配置，返回对应的 AI 服务实例。"""
    if config.ai_provider == "deepseek" and config.ai_api_key:
        return DeepSeekAIService(
            api_key=config.ai_api_key,
            base_url=config.ai_base_url,
            model=config.ai_model or "deepseek-chat",
        )
    return MockAIService()


__all__ = ["BaseAIService", "MockAIService", "DeepSeekAIService", "create_ai_service"]
