from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.schemas import OrderCreate, OrderOut
from app.utils.security import get_current_user, require_merchant

router = APIRouter()


def _serialize_order(order: Order) -> dict:
    return {
        "id": order.id,
        "user_id": order.user_id,
        "status": order.status,
        "total_amount": order.total_amount,
        "address": order.address,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "items": [
            {
                "id": i.id,
                "product_id": i.product_id,
                "quantity": i.quantity,
                "price": i.price,
                "spec": i.spec,
            }
            for i in order.items
        ],
    }


@router.post("/checkout", response_model=OrderOut)
def checkout(payload: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    total = 0.0
    order = Order(user_id=current_user.id, status="pending", total_amount=0.0, address=payload.address or "")
    db.add(order)
    db.flush()
    for item in payload.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or product.status != "on":
            raise HTTPException(status_code=400, detail=f"商品不存在或已下架: {item.product_id}")
        if product.stock < item.quantity:
            raise HTTPException(status_code=400, detail=f"库存不足: {product.name}")
        product.stock -= item.quantity
        db.add(OrderItem(order_id=order.id, product_id=item.product_id, quantity=item.quantity, price=product.price, spec=item.spec or ""))
        total += product.price * item.quantity
    order.total_amount = total
    db.commit()
    db.refresh(order)
    return _serialize_order(order)


@router.get("/my", response_model=List[OrderOut])
def my_orders(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == current_user.id).order_by(desc(Order.created_at)).all()
    return [_serialize_order(o) for o in orders]


@router.get("/all/list", response_model=List[OrderOut])
def all_orders(db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    orders = db.query(Order).order_by(desc(Order.created_at)).all()
    return [_serialize_order(o) for o in orders]


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id and current_user.role != "merchant":
        raise HTTPException(status_code=403, detail="无权查看")
    return _serialize_order(order)


@router.post("/{order_id}/pay")
def pay_order(order_id: int, method: str = "wechat", db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="订单状态不可支付")
    order.status = "paid"
    db.commit()
    return {"ok": True, "status": order.status, "method": method}


@router.post("/{order_id}/ship")
def ship_order(order_id: int, db: Session = Depends(get_db), _: User = Depends(require_merchant)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != "paid":
        raise HTTPException(status_code=400, detail="订单状态不可发货")
    order.status = "shipped"
    db.commit()
    return {"ok": True, "status": order.status}


@router.post("/{order_id}/complete")
def complete_order(order_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.user_id != current_user.id and current_user.role != "merchant":
        raise HTTPException(status_code=403, detail="无权操作")
    if order.status != "shipped":
        raise HTTPException(status_code=400, detail="订单状态不可完成")
    order.status = "completed"
    db.commit()
    return {"ok": True, "status": order.status}
