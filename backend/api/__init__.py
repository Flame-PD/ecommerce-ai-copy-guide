# from backend.api.routes import api_bp

# __all__ = ["api_bp"]

from backend.services.base import BaseAIService
from backend.services.ai_mock import MockAIService
from backend.services.ai_deepseek import DeepSeekAIService


def create_ai_service(config) -> BaseAIService:
    """根据配置选择用哪个 AI 服务。config 是 AppConfig 实例。"""
    if config.ai_provider == "deepseek" and config.ai_api_key:
        return DeepSeekAIService(
            api_key=config.ai_api_key,
            base_url=config.ai_base_url,
            model=config.ai_model,
        )
    return MockAIService()


__all__ = ["MockAIService", "DeepSeekAIService", "BaseAIService", "create_ai_service"]
