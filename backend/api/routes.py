from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from backend.schemas.requests import (
    CopyGenerationRequest,
    GuideRecommendationRequest,
    LiveScriptRequest,
    ReviewAnalysisRequest,
)
from backend.services.ai_mock import MockAIService

api_bp = Blueprint("api", __name__)
service = MockAIService()


def _parse_payload(model):
    try:
        return model.model_validate(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return jsonify({"error": "validation_error", "details": exc.errors()}), 400


@api_bp.get("/capabilities")
def capabilities():
    return jsonify(service.capabilities())


@api_bp.post("/copy/generate")
def generate_copy():
    payload = _parse_payload(CopyGenerationRequest)
    if isinstance(payload, tuple):
        return payload
    return jsonify(service.generate_copy(payload))


@api_bp.post("/guide/recommend")
def recommend():
    payload = _parse_payload(GuideRecommendationRequest)
    if isinstance(payload, tuple):
        return payload
    return jsonify(service.recommend(payload))


@api_bp.post("/reviews/analyze")
def analyze_reviews():
    payload = _parse_payload(ReviewAnalysisRequest)
    if isinstance(payload, tuple):
        return payload
    return jsonify(service.analyze_reviews(payload))


@api_bp.post("/scripts/live")
def generate_live_script():
    payload = _parse_payload(LiveScriptRequest)
    if isinstance(payload, tuple):
        return payload
    return jsonify(service.generate_live_script(payload))
