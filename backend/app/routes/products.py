from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import json
import io
import pandas as pd
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.favorite import Favorite
from app.models.browse_history import BrowseHistory
from app.schemas import ProductCreate, ProductUpdate, ProductOut, FavoriteOut
from app.utils.security import get_current_user, require_merchant
from app.services import rag_service

router = APIRouter()


@router.get("", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = "on",
    db: Session = Depends(get_db),
):
    q = db.query(Product)
    if status:
        q = q.filter(Product.status == status)
    if category:
        q = q.filter(Product.category == category)
    if keyword:
        q = q.filter(Product.name.contains(keyword))
    return q.order_by(desc(Product.created_at)).all()


@router.get("/categories/list")
def categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).distinct().all()
    return [r[0] for r in rows if r[0]]


@router.get("/my/favorites", response_model=List[FavoriteOut])
def my_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Favorite).filter(Favorite.user_id == current_user.id).all()


@router.get("/my/browse-history")
def browse_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    rows = (
        db.query(BrowseHistory, Product)
        .join(Product, BrowseHistory.product_id == Product.id)
        .filter(BrowseHistory.user_id == current_user.id)
        .order_by(desc(BrowseHistory.created_at))
        .limit(50)
        .all()
    )
    return [{"id": h.id, "product": p, "created_at": h.created_at} for h, p in rows]


@router.post("/import")
def import_products(file: UploadFile = File(...), db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    ext = file.filename.split(".")[-1].lower()
    content = file.file.read()
    if ext == "json":
        data = json.loads(content)
    elif ext in ("xlsx", "xls"):
        df = pd.read_excel(io.BytesIO(content))
        data = df.to_dict(orient="records")
    else:
        raise HTTPException(status_code=400, detail="仅支持json/xlsx")
    count = 0
    for item in data:
        specs = item.get("specs", "")
        if isinstance(specs, str):
            specs = [s.strip() for s in specs.split(",") if s.strip()]
        product = Product(
            name=item.get("name", ""),
            category=item.get("category", ""),
            description=item.get("description", ""),
            price=float(item.get("price", 0) or 0),
            stock=int(item.get("stock", 0) or 0),
            status=item.get("status", "off"),
            specs=specs,
            image_url=item.get("image_url", ""),
        )
        db.add(product)
        count += 1
    db.commit()
    return {"ok": True, "count": count}


@router.get("/export/data")
def export_products(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    products = db.query(Product).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "description": p.description,
            "price": p.price,
            "stock": p.stock,
            "status": p.status,
            "specs": ",".join(p.specs) if p.specs else "",
            "image_url": p.image_url,
            "ai_title": p.ai_title,
            "ai_slogan": p.ai_slogan,
        }
        for p in products
    ]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="商品不存在")
    return p


@router.post("", response_model=ProductOut)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    product = Product(**payload.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(product, k, v)
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    db.delete(product)
    db.commit()
    return {"ok": True}


@router.post("/{product_id}/favorite")
def toggle_favorite(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.product_id == product_id).first()
    if fav:
        db.delete(fav)
        db.commit()
        return {"ok": True, "favorited": False}
    db.add(Favorite(user_id=current_user.id, product_id=product_id))
    db.commit()
    return {"ok": True, "favorited": True}


@router.post("/{product_id}/browse")
def record_browse(product_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.add(BrowseHistory(user_id=current_user.id, product_id=product_id))
    db.commit()
    return {"ok": True}
