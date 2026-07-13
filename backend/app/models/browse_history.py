from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from app.database import Base


class BrowseHistory(Base):
    __tablename__ = "browse_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
