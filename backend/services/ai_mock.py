from __future__ import annotations
from backend.services.base import BaseAIService

from collections import Counter

from backend.schemas.requests import (
    CopyGenerationRequest,
    GuideRecommendationRequest,
    LiveScriptRequest,
    ReviewAnalysisRequest,
)


POSITIVE_WORDS = {"好", "舒服", "推荐", "喜欢", "稳定", "清爽", "划算", "精致", "快"}
NEGATIVE_WORDS = {"差", "慢", "贵", "坏", "退", "失望", "异味", "粗糙", "卡"}


class MockAIService(BaseAIService):
    """Deterministic service used before real model/provider integration."""

    def capabilities(self) -> dict[str, object]:
        return {
            "mode": "mock",
            "features": [
                {
                    "key": "copy_generation",
                    "name": "商品文案生成",
                    "endpoint": "/api/copy/generate",
                },
                {
                    "key": "shopping_guide",
                    "name": "智能导购推荐",
                    "endpoint": "/api/guide/recommend",
                },
                {
                    "key": "review_analysis",
                    "name": "评论情感分析",
                    "endpoint": "/api/reviews/analyze",
                },
                {
                    "key": "live_script",
                    "name": "直播脚本生成",
                    "endpoint": "/api/scripts/live",
                },
            ],
        }

    def generate_copy(self, payload: CopyGenerationRequest) -> dict[str, object]:
        points = payload.selling_points or ["舒适体验", "稳定品质", "适合日常使用"]
        return {
            "product_name": payload.product_name,
            "tone": payload.tone,
            "title": f"{payload.product_name}｜为{payload.audience}打造的{payload.tone}之选",
            "selling_points": [f"{point}：让购买理由更清晰可感知" for point in points],
            "detail_copy": (
                f"{payload.product_name}聚焦{payload.audience}的真实使用场景，"
                f"围绕{points[0]}建立第一购买心智，并通过细节呈现降低决策成本。"
            ),
            "ad_slogan": f"把{points[0]}带回家，从今天开始升级体验。",
        }

    def recommend(self, payload: GuideRecommendationRequest) -> dict[str, object]:
        products = payload.products or ["高性价比基础款", "品质升级款", "礼赠套装款"]
        primary = products[0]
        return {
            "user_need": payload.user_need,
            "budget": payload.budget,
            "recommended_product": primary,
            "reason": f"{primary}最贴近“{payload.user_need}”，并能兼顾预算：{payload.budget}。",
            "alternatives": products[1:3],
            "guide_message": "建议优先确认使用场景、尺寸/规格和售后，再比较赠品与到货时效。",
        }

    def analyze_reviews(self, payload: ReviewAnalysisRequest) -> dict[str, object]:
        sentiment_counts = Counter(self._sentiment(review) for review in payload.reviews)
        pain_points = [
            review for review in payload.reviews if self._sentiment(review) == "negative"
        ][:3]
        return {
            "product_name": payload.product_name,
            "total": len(payload.reviews),
            "sentiment": {
                "positive": sentiment_counts["positive"],
                "neutral": sentiment_counts["neutral"],
                "negative": sentiment_counts["negative"],
            },
            "top_keywords": self._keywords(payload.reviews),
            "pain_points": pain_points,
            "optimization_suggestions": [
                "将高频好评词加入详情页首屏和短视频口播。",
                "把差评痛点转化为售前提醒、FAQ 或售后承诺。",
            ],
        }

    def generate_live_script(self, payload: LiveScriptRequest) -> dict[str, object]:
        highlights = payload.highlights or ["核心卖点", "适用场景", "限时权益"]
        return {
            "product_name": payload.product_name,
            "duration_minutes": payload.duration_minutes,
            "tone": payload.tone,
            "segments": [
                {
                    "name": "开场引入",
                    "minutes": 1,
                    "script": f"今天重点看{payload.product_name}，先用一个真实场景说明它解决什么问题。",
                },
                {
                    "name": "卖点讲解",
                    "minutes": max(payload.duration_minutes - 2, 1),
                    "script": "、".join(highlights) + "，按使用前后对比讲清楚。",
                },
                {
                    "name": "互动转化",
                    "minutes": 1,
                    "script": "引导用户留言使用场景，并回答规格、价格、售后三类问题。",
                },
            ],
            "interaction_questions": [
                "你最关注这个商品的哪个使用场景？",
                "需要我对比基础款和升级款吗？",
                "还有哪些规格问题想现场确认？",
            ],
        }

    def _sentiment(self, review: str) -> str:
        positive_score = sum(word in review for word in POSITIVE_WORDS)
        negative_score = sum(word in review for word in NEGATIVE_WORDS)
        if positive_score > negative_score:
            return "positive"
        if negative_score > positive_score:
            return "negative"
        return "neutral"

    def _keywords(self, reviews: list[str]) -> list[str]:
        words = []
        for review in reviews:
            words.extend(word for word in POSITIVE_WORDS | NEGATIVE_WORDS if word in review)
        return [word for word, _count in Counter(words).most_common(6)]
