from __future__ import annotations

import json
import urllib.request
import urllib.error
from collections import Counter

from backend.schemas.requests import (
    CopyGenerationRequest,
    GuideRecommendationRequest,
    LiveScriptRequest,
    ReviewAnalysisRequest,
)
from backend.services.base import BaseAIService


class DeepSeekAIService(BaseAIService):
    """通过 DeepSeek API（OpenAI 兼容格式）调用真实大模型。"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._model = model

    # ------------------------------------------------------------------
    # 核心工具方法
    # ------------------------------------------------------------------

    def _call_api(self, system_prompt: str, user_prompt: str) -> str:
        """发请求到 DeepSeek，返回模型生成的原始文本。"""
        url = f"{self._base_url}/v1/chat/completions"
        body = json.dumps({
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=body,
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result["choices"][0]["message"]["content"]

    @staticmethod
    def _parse_json(raw: str) -> dict:
        """尽力从模型输出中提取 JSON。失败返回空 dict 让调用方 fallback。"""
        text = raw.strip()
        # 去掉 ```json ... ``` 包裹
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:]) if len(lines) > 1 else text
            if text.endswith("```"):
                text = text[:-3]
        # 直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        # 兜底：找第一个 { 和最后一个 }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end + 1])
            except json.JSONDecodeError:
                pass
        return {}

    def capabilities(self) -> dict[str, object]:
        return {
            "mode": "deepseek",
            "model": self._model,
            "features": [
                {"key": "copy_generation", "name": "商品文案生成", "endpoint": "/api/copy/generate"},
                {"key": "shopping_guide", "name": "智能导购推荐", "endpoint": "/api/guide/recommend"},
                {"key": "review_analysis", "name": "评论情感分析", "endpoint": "/api/reviews/analyze"},
                {"key": "live_script", "name": "直播脚本生成", "endpoint": "/api/scripts/live"},
            ],
        }

    # ------------------------------------------------------------------
    # 四个业务方法
    # ------------------------------------------------------------------

    def generate_copy(self, payload: CopyGenerationRequest) -> dict:
        system_prompt = (
            "你是一个资深的电商文案专家，擅长撰写高转化率的商品文案。"
            "你必须只返回一个 JSON 对象，不要包含任何解释、markdown 标记或其他文字。"
        )
        selling_points_str = (
            "、".join(payload.selling_points) if payload.selling_points else "舒适体验、稳定品质"
        )
        user_prompt = f"""请为以下商品生成营销文案，严格按照 JSON 格式返回：

商品名称：{payload.product_name}
目标人群：{payload.audience}
语气风格：{payload.tone}
核心卖点：{selling_points_str}

返回的 JSON 格式：
{{
  "title": "吸引眼球的商品标题（15字以内）",
  "selling_points": ["卖点1的详细描述", "卖点2的详细描述"],
  "detail_copy": "一段完整的详情页文案（80-150字）",
  "ad_slogan": "一句朗朗上口的广告语（20字以内）"
}}"""

        try:
            raw = self._call_api(system_prompt, user_prompt)
            result = self._parse_json(raw)
            if result:
                return result
        except Exception:
            pass

        # fallback
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

    def recommend(self, payload: GuideRecommendationRequest) -> dict:
        system_prompt = (
            "你是一个专业的电商导购顾问，擅长根据用户需求给出可解释的推荐。"
            "你必须只返回一个 JSON 对象，不要包含任何解释、markdown 标记或其他文字。"
        )
        products_str = "、".join(payload.products) if payload.products else "高性价比基础款、品质升级款、礼赠套装款"
        user_prompt = f"""请根据以下信息进行导购推荐，严格按照 JSON 格式返回：

用户需求：{payload.user_need}
预算范围：{payload.budget}
候选商品：{products_str}

返回的 JSON 格式：
{{
  "recommended_product": "首推商品名称",
  "reason": "推荐理由（结合用户需求和预算，50字以内）",
  "alternatives": ["备选商品1", "备选商品2"],
  "guide_message": "一条实用的购买建议（30字以内）"
}}"""

        try:
            raw = self._call_api(system_prompt, user_prompt)
            result = self._parse_json(raw)
            if result:
                return result
        except Exception:
            pass

        # fallback
        products = payload.products or ["高性价比基础款", "品质升级款", "礼赠套装款"]
        primary = products[0]
        return {
            "user_need": payload.user_need,
            "budget": payload.budget,
            "recommended_product": primary,
            "reason": f"{primary}最贴近「{payload.user_need}」，并能兼顾预算：{payload.budget}。",
            "alternatives": products[1:3],
            "guide_message": "建议优先确认使用场景、尺寸/规格和售后，再比较赠品与到货时效。",
        }

    def analyze_reviews(self, payload: ReviewAnalysisRequest) -> dict:
        system_prompt = (
            "你是一个专业的电商评论分析师，擅长从用户评论中提炼情绪、关键词和优化建议。"
            "你必须只返回一个 JSON 对象，不要包含任何解释、markdown 标记或其他文字。"
        )
        reviews_text = "\n".join(f"- {r}" for r in payload.reviews)
        user_prompt = f"""请分析以下商品评论，严格按照 JSON 格式返回：

商品名称：{payload.product_name}
评论列表：
{reviews_text}

返回的 JSON 格式：
{{
  "sentiment": {{"positive": 正整数, "neutral": 非负整数, "negative": 非负整数}},
  "top_keywords": ["关键词1", "关键词2", ...共4-6个],
  "pain_points": ["差评痛点1", "差评痛点2", ...最多3条],
  "optimization_suggestions": ["优化建议1", "优化建议2"]
}}
注意：sentiment 三个数字之和必须等于评论总数。"""

        try:
            raw = self._call_api(system_prompt, user_prompt)
            result = self._parse_json(raw)
            if result and "sentiment" in result:
                return result
        except Exception:
            pass

        # fallback：使用和 Mock 一致的关键词词典法
        POSITIVE_WORDS = {"好", "舒服", "推荐", "喜欢", "稳定", "清爽", "划算", "精致", "快"}
        NEGATIVE_WORDS = {"差", "慢", "贵", "坏", "退", "失望", "异味", "粗糙", "卡"}

        def _sentiment(r: str) -> str:
            pos = sum(w in r for w in POSITIVE_WORDS)
            neg = sum(w in r for w in NEGATIVE_WORDS)
            if pos > neg:
                return "positive"
            if neg > pos:
                return "negative"
            return "neutral"

        counts = Counter(_sentiment(r) for r in payload.reviews)
        pain_points = [r for r in payload.reviews if _sentiment(r) == "negative"][:3]

        all_words: list[str] = []
        for r in payload.reviews:
            all_words.extend(w for w in POSITIVE_WORDS | NEGATIVE_WORDS if w in r)
        keywords = [w for w, _ in Counter(all_words).most_common(6)]

        return {
            "product_name": payload.product_name,
            "total": len(payload.reviews),
            "sentiment": {
                "positive": counts["positive"],
                "neutral": counts["neutral"],
                "negative": counts["negative"],
            },
            "top_keywords": keywords,
            "pain_points": pain_points,
            "optimization_suggestions": [
                "将高频好评词加入详情页首屏和短视频口播。",
                "把差评痛点转化为售前提醒、FAQ 或售后承诺。",
            ],
        }

    def generate_live_script(self, payload: LiveScriptRequest) -> dict:
        system_prompt = (
            "你是一个专业的直播带货策划，擅长设计高转化的直播脚本和互动话术。"
            "你必须只返回一个 JSON 对象，不要包含任何解释、markdown 标记或其他文字。"
        )
        highlights_str = "、".join(payload.highlights) if payload.highlights else "核心卖点、适用场景、限时权益"
        user_prompt = f"""请为以下商品设计直播脚本，严格按照 JSON 格式返回：

商品名称：{payload.product_name}
直播时长：{payload.duration_minutes} 分钟
语气风格：{payload.tone}
商品亮点：{highlights_str}

返回的 JSON 格式（segments 数组必须有 3 个元素，minutes 之和等于总时长）：
{{
  "segments": [
    {{"name": "开场引入", "minutes": 1, "script": "开场话术"}},
    {{"name": "卖点讲解", "minutes": {max(payload.duration_minutes - 2, 1)}, "script": "核心讲解内容"}},
    {{"name": "互动转化", "minutes": 1, "script": "引导互动和促单话术"}}
  ],
  "interaction_questions": ["互动问题1", "互动问题2", "互动问题3"]
}}"""

        try:
            raw = self._call_api(system_prompt, user_prompt)
            result = self._parse_json(raw)
            if result and "segments" in result:
                return result
        except Exception:
            pass

        # fallback
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
