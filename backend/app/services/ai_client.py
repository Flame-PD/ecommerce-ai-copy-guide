"""HTTP client adapter for the AI Intelligent Service Layer.

Calls the standalone AI service (FastAPI, port 8000) from the backend.
Every method mirrors an endpoint in ``ai_service/gateway/router.py``
and falls back gracefully when the AI service is unreachable.

Usage::

    from app.services.ai_client import AIClient

    client = AIClient()
    result = client.generate_titles(product_name="...", features="...", category="...")
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------

class AIClient:
    """Thin HTTP wrapper around the AI service REST API.

    Parameters
    ----------
    base_url : str, optional
        Root URL of the AI service.  Defaults to ``AI_SERVICE_URL`` in config.
    timeout : int, optional
        Request timeout in seconds.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: int = 90) -> None:
        settings = get_settings()
        self._base_url = (base_url or settings.ai_service_url).rstrip("/")
        self._timeout = timeout
        self._enabled = bool(self._base_url) and settings.ai_service_enabled
        logger.info(
            "AIClient initialised | url={} enabled={}", self._base_url, self._enabled
        )

    # ------------------------------------------------------------------
    # Low-level helpers
    # ------------------------------------------------------------------

    def _post(self, path: str, json_data: dict) -> Optional[dict]:
        """POST to the AI service and return the JSON body, or ``None`` on failure."""
        if not self._enabled:
            logger.debug("AIClient disabled — skipping {}", path)
            return None
        url = f"{self._base_url}{path}"
        try:
            resp = httpx.post(url, json=json_data, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except httpx.ConnectError:
            logger.warning("AI service unreachable at {} — is it running?", self._base_url)
            return None
        except httpx.HTTPStatusError as exc:
            logger.error("AI service error {} {}: {}", exc.response.status_code, path, exc.response.text[:200])
            return None
        except Exception:
            logger.exception("Unexpected error calling AI service {}", path)
            return None

    def _get(self, path: str) -> Optional[dict]:
        """GET from the AI service."""
        if not self._enabled:
            return None
        url = f"{self._base_url}{path}"
        try:
            resp = httpx.get(url, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except Exception:
            logger.exception("AI service GET {} failed", path)
            return None

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health(self) -> Optional[dict]:
        """Check whether the AI service is alive."""
        return self._get("/api/v1/health")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest(self, products: List[Dict[str, Any]]) -> Optional[dict]:
        """Load product data into the AI service's RAG knowledge base.

        Parameters
        ----------
        products : list[dict]
            A list of product dicts.  Each dict should contain at minimum
            ``name``, ``features``, and ``category``.

        Returns
        -------
        dict or None
            ``{"status": "ok", "chunks_indexed": N}`` or ``None`` on failure.
        """
        return self._post("/api/v1/ingest", products)

    # ------------------------------------------------------------------
    # 1. Product Title
    # ------------------------------------------------------------------

    def generate_titles(
        self,
        product_name: str,
        features: str,
        category: str,
    ) -> Optional[List[str]]:
        """Generate 5 optimised product titles.

        Returns
        -------
        list[str] or None
            Five title strings, or ``None`` on failure.
        """
        data = self._post(
            "/api/v1/title",
            {
                "product_name": product_name,
                "features": features,
                "category": category,
            },
        )
        if data is None:
            return None
        return data.get("titles", [])

    # ------------------------------------------------------------------
    # 2. Product Description
    # ------------------------------------------------------------------

    def generate_description(
        self,
        product_name: str,
        features: str,
        category: str,
        specifications: str = "",
        target_audience: str = "通用",
    ) -> Optional[str]:
        """Generate a Markdown product description.

        Returns
        -------
        str or None
            Markdown text, or ``None`` on failure.
        """
        data = self._post(
            "/api/v1/description",
            {
                "product_name": product_name,
                "features": features,
                "category": category,
                "specifications": specifications,
                "target_audience": target_audience,
            },
        )
        if data is None:
            return None
        return data.get("description", "")

    # ------------------------------------------------------------------
    # 3. RAG Chat
    # ------------------------------------------------------------------

    def chat(
        self,
        question: str,
        product_ids: Optional[List[str]] = None,
    ) -> Optional[dict]:
        """Query the RAG-powered shopping assistant.

        Returns
        -------
        dict or None
            ``{"answer": …, "has_relevant_info": …, "related_products": …, "sources": …}``
        """
        body: Dict[str, Any] = {"question": question}
        if product_ids:
            body["product_ids"] = product_ids
        return self._post("/api/v1/chat", body)

    # ------------------------------------------------------------------
    # 4. Sentiment Analysis
    # ------------------------------------------------------------------

    def analyse_sentiment(self, reviews: List[str]) -> Optional[dict]:
        """Analyse the sentiment of product reviews.

        Returns
        -------
        dict or None
            ``{"positive_rate": …, "negative_rate": …, "key_complaints": …, "summary": …}``
        """
        return self._post("/api/v1/sentiment", {"reviews": reviews})

    # ------------------------------------------------------------------
    # 5. Recommendation
    # ------------------------------------------------------------------

    def recommend(
        self,
        product_name: str,
        features: str,
        category: str,
        top_n: int = 5,
    ) -> Optional[List[dict]]:
        """Get similar product recommendations.

        Returns
        -------
        list[dict] or None
            List of ``{"product_name": …, "similarity_score": …}`` dicts.
        """
        data = self._post(
            "/api/v1/recommend",
            {
                "product_name": product_name,
                "features": features,
                "category": category,
                "top_n": top_n,
            },
        )
        if data is None:
            return None
        return data.get("recommendations", [])

    # ------------------------------------------------------------------
    # 6. Livestream Script
    # ------------------------------------------------------------------

    def generate_livestream(
        self,
        product_name: str,
        features: str,
        category: str,
        promotion: str = "",
        target_audience: str = "通用",
    ) -> Optional[dict]:
        """Generate a full livestream sales script.

        Returns
        -------
        dict or None
            ``{"script": …, "estimated_total_duration": …, "key_talking_points": …}``
        """
        return self._post(
            "/api/v1/livestream",
            {
                "product_name": product_name,
                "features": features,
                "category": category,
                "promotion": promotion,
                "target_audience": target_audience,
            },
        )


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

_client: Optional[AIClient] = None


def get_ai_client() -> AIClient:
    """Return a cached :class:`AIClient` singleton."""
    global _client
    if _client is None:
        _client = AIClient()
    return _client
