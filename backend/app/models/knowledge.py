from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class KnowledgeItem(Base):
    __tablename__ = "knowledge_items"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    category = Column(String(64), default="common")  # common / size / material / aftersale / activity
    question = Column(String(512), default="")
    answer = Column(Text, default="")
    embedding_id = Column(String(128), default="")
    created_at = Column(DateTime, server_default=func.now())
