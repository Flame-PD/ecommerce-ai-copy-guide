"""Livestream script generation service.

Produces a complete live-selling script covering opening, product intro,
selling points, audience interaction, promotion, and closing.
"""

from __future__ import annotations

from typing import Optional

from ai_service.llm.dispatcher import LLMDispatcher
from ai_service.models.request import LivestreamRequest
from ai_service.models.response import LivestreamResponse
from ai_service.utils.helpers import extract_json
from ai_service.utils.logger import logger
from ai_service.utils.prompt_loader import PromptLoader


class LivestreamScriptGenerator:
    """Generate a full livestream sales script.

    Parameters
    ----------
    dispatcher : LLMDispatcher, optional
        Injected dispatcher.
    prompt_loader : PromptLoader, optional
        Injected prompt loader.
    """

    def __init__(
        self,
        dispatcher: Optional[LLMDispatcher] = None,
        prompt_loader: Optional[PromptLoader] = None,
    ) -> None:
        self._dispatcher = dispatcher or LLMDispatcher()
        self._loader = prompt_loader or PromptLoader()

    # ------------------------------------------------------------------
    def generate(self, request: LivestreamRequest) -> LivestreamResponse:
        """Generate a livestream script.

        Parameters
        ----------
        request : LivestreamRequest
            Product info, promotion details, and target audience.

        Returns
        -------
        LivestreamResponse
            Complete script, estimated duration, and key talking points.
        """
        logger.info(
            "LivestreamScriptGenerator | product='{}'",
            request.product_name,
        )

        prompt = self._loader.render(
            "livestream",
            product_name=request.product_name,
            features=request.features,
            promotion=request.promotion or "限时优惠，详情请咨询客服",
            target_audience=request.target_audience or "通用",
            category=request.category,
        )

        raw = self._dispatcher.generate(prompt)
        data = extract_json(raw)

        logger.info("LivestreamScriptGenerator done | {} chars", len(data.get("script", "")))
        return LivestreamResponse(
            script=data.get("script", raw),
            estimated_total_duration=data.get("estimated_total_duration", "约4分30秒"),
            key_talking_points=data.get("key_talking_points", []),
        )
