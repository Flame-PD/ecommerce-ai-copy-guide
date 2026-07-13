from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.chat_history import ChatHistory
from app.models.knowledge import KnowledgeItem
from app.schemas import ChatMessage, ChatOut
from app.utils.security import get_current_user, require_merchant
from app.services import rag_service, ai_service

router = APIRouter()


@router.post("/ask")
def ask(payload: ChatMessage, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product_name = ""
    if payload.product_id:
        product = db.query(Product).filter(Product.id == payload.product_id).first()
        if product:
            product_name = product.name

    docs = rag_service.search_knowledge(payload.message, top_k=5, product_id=payload.product_id)
    context = "\n\n".join([f"Q: {d['metadata'].get('question', '')}\nA: {d['document']}" for d in docs])
    messages = [{"role": "user", "content": payload.message}]
    answer = ai_service.chat_with_context(messages, context)

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
