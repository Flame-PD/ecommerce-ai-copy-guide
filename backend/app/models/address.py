from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func, Boolean
from app.database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(64), default="")
    phone = Column(String(32), default="")
    detail = Column(String(512), default="")
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
