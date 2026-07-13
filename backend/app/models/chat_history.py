from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    role = Column(String(16), default="user")  # user / merchant
    message = Column(Text, default="")
    response = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
