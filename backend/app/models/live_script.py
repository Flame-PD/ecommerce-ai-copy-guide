from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from app.database import Base


class LiveScript(Base):
    __tablename__ = "live_scripts"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    title = Column(String(255), default="")
    style = Column(String(64), default="professional")
    content = Column(Text, default="")
    created_at = Column(DateTime, server_default=func.now())
