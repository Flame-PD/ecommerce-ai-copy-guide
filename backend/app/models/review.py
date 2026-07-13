from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, func
from app.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    rating = Column(Integer, default=5)
    content = Column(Text, default="")
    sentiment = Column(String(16), default="neutral")  # positive / neutral / negative
    created_at = Column(DateTime, server_default=func.now())
