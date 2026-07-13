from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.knowledge import KnowledgeItem
from app.schemas import KnowledgeItemCreate, KnowledgeItemOut
from app.utils.security import require_merchant
from app.services import rag_service

router = APIRouter()


@router.get("", response_model=List[KnowledgeItemOut])
def list_items(product_id: int = None, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    q = db.query(KnowledgeItem)
    if product_id:
        q = q.filter(KnowledgeItem.product_id == product_id)
    return q.order_by(desc(KnowledgeItem.created_at)).all()


@router.post("", response_model=KnowledgeItemOut)
def create_item(payload: KnowledgeItemCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    item = KnowledgeItem(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    text = f"问题：{item.question}\n回答：{item.answer}"
    eid = rag_service.add_knowledge(text, {
        "product_id": item.product_id,
        "question": item.question,
        "category": item.category,
    })
    item.embedding_id = eid
    db.commit()
    db.refresh(item)
    return item


@router.post("/sync/{product_id}")
def sync_product_knowledge(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    items = db.query(KnowledgeItem).filter(KnowledgeItem.product_id == product_id).all()
    data = {
        "id": product.id,
        "name": product.name,
        "category": product.category,
        "description": product.description,
        "price": product.price,
        "specs": product.specs or [],
        "knowledge_items": [{"question": i.question, "answer": i.answer} for i in items],
    }
    pairs = rag_service.sync_product_knowledge(data)
    for text, meta in pairs:
        rag_service.add_knowledge(text, meta)
    return {"ok": True, "count": len(pairs)}


@router.put("/{item_id}", response_model=KnowledgeItemOut)
def update_item(item_id: int, payload: KnowledgeItemCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    for k, v in payload.model_dump().items():
        setattr(item, k, v)
    db.commit()
    db.refresh(item)
    if item.embedding_id:
        rag_service.delete_knowledge(item.embedding_id)
    text = f"问题：{item.question}\n回答：{item.answer}"
    item.embedding_id = rag_service.add_knowledge(text, {
        "product_id": item.product_id,
        "question": item.question,
        "category": item.category,
    })
    db.commit()
    return item


@router.delete("/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    item = db.query(KnowledgeItem).filter(KnowledgeItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="知识条目不存在")
    if item.embedding_id:
        rag_service.delete_knowledge(item.embedding_id)
    db.delete(item)
    db.commit()
    return {"ok": True}
