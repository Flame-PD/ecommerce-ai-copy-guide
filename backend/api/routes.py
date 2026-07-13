from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request
from pydantic import ValidationError

from backend.schemas.requests import (
    CopyGenerationRequest,
    GuideRecommendationRequest,
    LiveScriptRequest,
    ReviewAnalysisRequest,
)
from backend.services import create_ai_service
from backend.database import get_db
from backend.models import GenerationTask

api_bp = Blueprint("api", __name__)


# ── 工具函数 ──────────────────────────────────────────────────

def _get_service():
    """每次请求时动态获取 AI 服务实例。"""
    config = current_app.config["APP_CONFIG"]
    return create_ai_service(config)


def _parse_payload(model):
    try:
        return model.model_validate(request.get_json(silent=True) or {})
    except ValidationError as exc:
        return jsonify({"error": "validation_error", "details": exc.errors()}), 400


def _save_task(task_type: str, request_input: dict, result_output: dict):
    """将每次 AI 调用写入 generation_tasks 表。保存失败不影响 API 响应。"""
    try:
        config = current_app.config["APP_CONFIG"]
        db = get_db()
        task = GenerationTask(
            task_type=task_type,
            request_input=request_input,
            result_output=result_output,
            ai_provider=config.ai_provider or "mock",
            ai_model=config.ai_model or "deterministic-template",
            status="success",
        )
        db.add(task)
        db.commit()
    except Exception:
        pass  # 数据库不可用时静默跳过
    finally:
        db.close()


# ── 业务 API ──────────────────────────────────────────────────

@api_bp.get("/capabilities")
def capabilities():
    return jsonify(_get_service().capabilities())


@api_bp.post("/copy/generate")
def generate_copy():
    payload = _parse_payload(CopyGenerationRequest)
    if isinstance(payload, tuple):
        return payload
    result = _get_service().generate_copy(payload)
    _save_task("copy", payload.model_dump(), result)
    return jsonify(result)


@api_bp.post("/guide/recommend")
def recommend():
    payload = _parse_payload(GuideRecommendationRequest)
    if isinstance(payload, tuple):
        return payload
    result = _get_service().recommend(payload)
    _save_task("guide", payload.model_dump(), result)
    return jsonify(result)


@api_bp.post("/reviews/analyze")
def analyze_reviews():
    payload = _parse_payload(ReviewAnalysisRequest)
    if isinstance(payload, tuple):
        return payload
    result = _get_service().analyze_reviews(payload)
    _save_task("review_analysis", payload.model_dump(), result)
    return jsonify(result)


@api_bp.post("/scripts/live")
def generate_live_script():
    payload = _parse_payload(LiveScriptRequest)
    if isinstance(payload, tuple):
        return payload
    result = _get_service().generate_live_script(payload)
    _save_task("live_script", payload.model_dump(), result)
    return jsonify(result)


# ── 历史查询 ──────────────────────────────────────────────────

@api_bp.get("/history")
def list_history():
    """查询历史生成记录。

    Query params:
        task_type   - 筛选类型：copy / guide / review_analysis / live_script
        limit       - 返回条数，默认 20，最大 100
    """
    task_type = request.args.get("task_type")
    limit = min(request.args.get("limit", 20, type=int), 100)

    db = get_db()
    try:
        query = db.query(GenerationTask).order_by(GenerationTask.created_at.desc())
        if task_type:
            query = query.filter(GenerationTask.task_type == task_type)
        tasks = query.limit(limit).all()

        return jsonify([
            {
                "id": t.id,
                "task_type": t.task_type,
                "request_input": t.request_input,
                "result_output": t.result_output,
                "ai_provider": t.ai_provider,
                "ai_model": t.ai_model,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
            }
            for t in tasks
        ])
    finally:
        db.close()
