from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, or_
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.chat_history import ChatHistory
from app.models.knowledge import KnowledgeItem
from app.schemas import ChatMessage, ChatOut
from app.utils.security import get_current_user, require_merchant
from app.services import rag_service, ai_service
from app.services.ai_client import get_ai_client
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


def _build_product_context(products: list) -> str:
    parts = []
    for p in products:
        if not p:
            continue
        specs = ", ".join(p.specs) if p.specs else "无"
        parts.append(
            f"商品名称：{p.name}\n分类：{p.category or '未分类'}\n价格：¥{p.price}\n"
            f"库存：{p.stock}\n规格：{specs}\n描述：{p.description or '暂无描述'}"
        )
    return "\n\n".join(parts)


def _search_db_products(payload: ChatMessage, db: Session) -> list:
    """Search products in the database by keyword or product_id."""
    if payload.product_id:
        product = db.query(Product).filter(Product.id == payload.product_id, Product.status == "on").first()
        return [product] if product else []
    keyword = payload.message.strip()
    return db.query(Product).filter(
        Product.status == "on",
        or_(
            Product.name.contains(keyword),
            Product.category.contains(keyword),
            Product.description.contains(keyword),
        )
    ).order_by(desc(Product.created_at)).limit(5).all()


@router.post("/ask")
def ask(payload: ChatMessage, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # -- 1) Try AI service RAG first -------------------------------------------
    ai = get_ai_client()
    ai_answer = ai.chat(payload.message)

    if ai_answer is not None and ai_answer.get("has_relevant_info"):
        answer = ai_answer["answer"]
        references = ai_answer.get("sources") or []
        logger.info("Chat answered via AI service RAG")
        record = ChatHistory(
            user_id=current_user.id,
            product_id=payload.product_id,
            role="user",
            message=payload.message,
            response=answer,
        )
        db.add(record)
        db.commit()
        return {"answer": answer, "references": references}

    # -- 2) Fall back to local DB + TF-IDF + DeepSeek -------------------------
    logger.info("AI service RAG unavailable or no relevant info — using local fallback")
    products = _search_db_products(payload, db)
    product_context = _build_product_context(products)

    docs = rag_service.search_knowledge(payload.message, top_k=5, product_id=payload.product_id)
    rag_context = "\n\n".join([f"Q: {d['metadata'].get('question', '')}\nA: {d['document']}" for d in docs])

    context_parts = []
    if product_context:
        context_parts.append(f"【店铺当前在售商品信息】\n{product_context}")
    if rag_context:
        context_parts.append(f"【知识库参考】\n{rag_context}")
    full_context = "\n\n".join(context_parts)

    messages = [{"role": "user", "content": payload.message}]
    answer = ai_service.chat_with_context(messages, full_context)

    record = ChatHistory(
        user_id=current_user.id,
        product_id=payload.product_id,
        role="user",
        message=payload.message,
        response=answer,
    )
    db.add(record)
    db.commit()
    return {"answer": answer, "references": docs}


# -- Sync endpoint: push DB products to AI service RAG ------------------------

@router.post("/sync-to-ai-service")
def sync_products_to_ai_service(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    """Push all 'on' products from the database to the AI service's RAG store."""
    products = db.query(Product).filter(Product.status == "on").all()
    if not products:
        return {"status": "ok", "message": "没有需要同步的商品"}

    payload = []
    for p in products:
        payload.append({
            "name": p.name,
            "category": p.category or "",
            "description": p.description or "",
            "features": p.ai_selling_points or p.description or "",
            "specifications": ", ".join(p.specs) if p.specs else "",
            "price": str(p.price) if p.price else "",
            "target_audience": "通用",
        })

    ai = get_ai_client()
    result = ai.ingest(payload)
    if result is None:
        return {"status": "error", "message": "AI 服务不可用，请确认服务已启动"}
    return result


@router.get("/history", response_model=List[ChatOut])
def history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(desc(ChatHistory.created_at)).limit(50).all()


@router.get("/merchant/history")
def merchant_history(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    rows = (
        db.query(ChatHistory.message, func.count(ChatHistory.id).label("count"))
        .group_by(ChatHistory.message)
        .order_by(desc("count"))
        .limit(30)
        .all()
    )
    return [{"message": m, "count": c} for m, c in rows]
