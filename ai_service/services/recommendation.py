"""Product recommendation engine based on embedding similarity.

Encodes the query product and compares it against all indexed products
in the vector store.  Returns the most similar products above the
configured similarity threshold.

Uses the :class:`Retriever` high-level API — never accesses the vector
store directly — and shares the embedding service to avoid duplicate
model loading.
"""

from __future__ import annotations

import re
from typing import List, Optional

from ai_service.config.settings import get_settings
from ai_service.models.request import RecommendRequest
from ai_service.models.response import RecommendResponse, RecommendedProduct
from ai_service.rag.retriever import Retriever
from ai_service.utils.logger import logger

# Matches "产品名称：value" to extract the product name value
_NAME_PATTERN = re.compile(r"^产品名称[：:]\s*(.+)")


def _extract_product_name(text: str) -> str:
    """Extract the product name from a flattened document chunk.

    The first line of each chunk is ``产品名称：…``.  This helper strips
    the label prefix and returns just the product name.

    Parameters
    ----------
    text : str
        A document chunk whose first line is ``产品名称：xxx``.

    Returns
    -------
    str
        The bare product name, or a fallback if extraction fails.
    """
    first_line = text.split("\n")[0] if text else ""
    m = _NAME_PATTERN.match(first_line)
    return m.group(1).strip() if m else (first_line or "未知产品")


class RecommendationEngine:
    """Recommend similar products via embedding similarity.

    The engine requires a pre-populated :class:`Retriever` (with product
    data already ingested).  It delegates to :meth:`Retriever.retrieve`
    so embedding and search happen through the standard RAG pipeline.

    Parameters
    ----------
    retriever : Retriever
        Pre-populated retriever with the product catalogue.
    """

    def __init__(self, retriever: Retriever) -> None:
        self._retriever = retriever
        self._settings = get_settings()

    # ------------------------------------------------------------------
    def recommend(self, request: RecommendRequest) -> RecommendResponse:
        """Find products similar to the given product.

        Parameters
        ----------
        request : RecommendRequest
            Product info and the desired number of recommendations.

        Returns
        -------
        RecommendResponse
            Ranked list of recommended products.

        Raises
        ------
        RuntimeError
            If the vector store has not been populated.
        """
        logger.info(
            "RecommendationEngine | product='{}' top_n={}",
            request.product_name,
            request.top_n,
        )

        # 1. Build query text & retrieve via the standard RAG pipeline
        query_text = self._build_query_text(request)
        _, sources = self._retriever.retrieve(query_text, top_k=request.top_n * 2)

        # 2. Filter by threshold & deduplicate
        seen: set[str] = set()
        recommendations: List[RecommendedProduct] = []

        for src in sources:
            if len(recommendations) >= request.top_n:
                break
            score = src["score"]
            if score < self._settings.SIMILARITY_THRESHOLD:
                continue
            name = _extract_product_name(src["text"])
            if name in seen:
                continue
            seen.add(name)
            recommendations.append(
                RecommendedProduct(
                    product_name=name,
                    similarity_score=round(float(score), 4),
                    features=self._extract_field(src["text"], "特点"),
                    category=self._extract_field(src["text"], "类目"),
                )
            )

        logger.info("RecommendationEngine done | {} recommendations", len(recommendations))
        return RecommendResponse(recommendations=recommendations)

    # ------------------------------------------------------------------
    @staticmethod
    def _build_query_text(request: RecommendRequest) -> str:
        """Build a dense query string from request fields.

        Parameters
        ----------
        request : RecommendRequest
            Input product data.

        Returns
        -------
        str
            Human-readable query embedding input.
        """
        return (
            f"产品名称：{request.product_name}\n"
            f"产品特点：{request.features}\n"
            f"产品类目：{request.category}"
        )

    # ------------------------------------------------------------------
    @staticmethod
    def _extract_field(text: str, label: str) -> Optional[str]:
        """Extract a field value from a flattened document chunk.

        Parameters
        ----------
        text : str
            Document chunk with ``label：value`` lines.
        label : str
            The Chinese label to look for (e.g. ``"特点"``).

        Returns
        -------
        str or None
            The value if found, otherwise ``None``.
        """
        pattern = re.compile(rf"^{re.escape(label)}[：:]\s*(.+)", re.MULTILINE)
        m = pattern.search(text)
        return m.group(1).strip() if m else None
