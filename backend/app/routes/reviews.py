from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List
import io
import re
import pandas as pd
from docx import Document
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.review import Review
from app.models.order import Order
from app.schemas import ReviewCreate, ReviewOut, SentimentStats
from app.utils.security import get_current_user, require_merchant
from app.services import sentiment_service

router = APIRouter()


@router.post("", response_model=ReviewOut)
def create_review(payload: ReviewCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == payload.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if payload.order_id:
        order = db.query(Order).filter(Order.id == payload.order_id, Order.user_id == current_user.id).first()
        if not order:
            raise HTTPException(status_code=403, detail="无权评价该订单")
    sentiment = sentiment_service.analyze(payload.content)
    review = Review(
        user_id=current_user.id,
        product_id=payload.product_id,
        order_id=payload.order_id,
        rating=payload.rating,
        content=payload.content,
        sentiment=sentiment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/product/{product_id}", response_model=List[ReviewOut])
def product_reviews(product_id: int, sentiment: str = None, db: Session = Depends(get_db)):
    q = db.query(Review).filter(Review.product_id == product_id)
    if sentiment:
        q = q.filter(Review.sentiment == sentiment)
    return q.order_by(desc(Review.created_at)).all()


@router.get("/my", response_model=List[ReviewOut])
def my_reviews(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Review).filter(Review.user_id == current_user.id).order_by(desc(Review.created_at)).all()


@router.get("/stats/{product_id}", response_model=SentimentStats)
def review_stats(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    result = sentiment_service.batch_analyze([{"content": r.content, "rating": r.rating} for r in reviews])
    return SentimentStats(**result)


@router.post("/analyze")
def analyze_upload(
    file: UploadFile = File(...),
    product_id: int = None,
    db: Session = Depends(get_db),
    _: User = Depends(require_merchant),
):
    ext = file.filename.split(".")[-1].lower()
    content = file.file.read()
    texts = []
    if ext == "txt" or ext == "md":
        texts = [t.strip() for t in content.decode("utf-8", errors="ignore").split("\n") if t.strip()]
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(content))
        col = "content" if "content" in df.columns else df.columns[0]
        texts = [str(t).strip() for t in df[col].dropna().tolist()]
    elif ext == "docx":
        doc = Document(io.BytesIO(content))
        texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    else:
        raise HTTPException(status_code=400, detail="不支持的文件格式")

    reviews = [{"content": t, "rating": 5} for t in texts]
    result = sentiment_service.batch_analyze(reviews)
    if product_id:
        for t in texts:
            sentiment = sentiment_service.analyze(t)
            db.add(Review(user_id=1, product_id=product_id, rating=5, content=t, sentiment=sentiment))
        db.commit()
    return {"ok": True, "count": len(texts), "stats": result}
