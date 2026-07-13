from abc import ABC, abstractmethod
from backend.schemas.requests import (
    CopyGenerationRequest,
    GuideRecommendationRequest,
    LiveScriptRequest,
    ReviewAnalysisRequest,
)


class BaseAIService(ABC):
    """所有 AI Service 的统一接口。Mock 和 DeepSeek 都要实现这些方法。"""

    def capabilities(self) -> dict[str, object]:
        """返回当前服务的能力清单。子类可重写以提供更具体的信息。"""
        return {
            "mode": "base",
            "features": [
                {"key": "copy_generation", "name": "商品文案生成", "endpoint": "/api/copy/generate"},
                {"key": "shopping_guide", "name": "智能导购推荐", "endpoint": "/api/guide/recommend"},
                {"key": "review_analysis", "name": "评论情感分析", "endpoint": "/api/reviews/analyze"},
                {"key": "live_script", "name": "直播脚本生成", "endpoint": "/api/scripts/live"},
            ],
        }

    @abstractmethod
    def generate_copy(self, payload: CopyGenerationRequest) -> dict: ...

    @abstractmethod
    def recommend(self, payload: GuideRecommendationRequest) -> dict: ...

    @abstractmethod
    def analyze_reviews(self, payload: ReviewAnalysisRequest) -> dict: ...

    @abstractmethod
    def generate_live_script(self, payload: LiveScriptRequest) -> dict: ...
