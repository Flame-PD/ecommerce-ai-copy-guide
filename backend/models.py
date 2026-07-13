"""SQLAlchemy ORM 模型 —— 5 张表的定义。

表关系速览：
    Product (1) ──< (N) Review
    Product (1) ──< (N) GenerationTask
    GenerationTask (1) ──< (N) RecommendationRecord
    Session (1) ──< (N) RecommendationRecord
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import JSON, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """SQLAlchemy 声明式基类。"""
    pass


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ──────────────────────────────────────────────────────────────
# 1. Product（商品表）
# ──────────────────────────────────────────────────────────────

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    source_url: Mapped[Optional[str]] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    reviews: Mapped[List["Review"]] = relationship(back_populates="product", cascade="all, delete-orphan")
    generation_tasks: Mapped[List["GenerationTask"]] = relationship(back_populates="product")


# ──────────────────────────────────────────────────────────────
# 2. Review（评论表）
# ──────────────────────────────────────────────────────────────

class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("products.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sentiment: Mapped[Optional[str]] = mapped_column(String(10))
    source: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    product: Mapped["Product"] = relationship(back_populates="reviews")


# ──────────────────────────────────────────────────────────────
# 3. GenerationTask（生成记录表）⭐ 核心
# ──────────────────────────────────────────────────────────────

class GenerationTask(Base):
    __tablename__ = "generation_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(20), nullable=False)
    request_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    result_output: Mapped[dict] = mapped_column(JSON, nullable=False)
    ai_provider: Mapped[Optional[str]] = mapped_column(String(30))
    ai_model: Mapped[Optional[str]] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="success")
    product_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("products.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    product: Mapped[Optional["Product"]] = relationship(back_populates="generation_tasks")
    recommendation_record: Mapped[Optional["RecommendationRecord"]] = relationship(
        back_populates="task", uselist=False
    )


# ──────────────────────────────────────────────────────────────
# 4. Session（会话表）
# ──────────────────────────────────────────────────────────────

class Session(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_key: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    context: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    recommendation_records: Mapped[List["RecommendationRecord"]] = relationship(
        back_populates="session"
    )


# ──────────────────────────────────────────────────────────────
# 5. RecommendationRecord（推荐记录表）
# ──────────────────────────────────────────────────────────────

class RecommendationRecord(Base):
    __tablename__ = "recommendation_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("generation_tasks.id"))
    session_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("sessions.id"))
    user_need: Mapped[str] = mapped_column(Text, nullable=False)
    budget: Mapped[Optional[str]] = mapped_column(String(50))
    recommended_product: Mapped[Optional[str]] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow)

    task: Mapped[Optional["GenerationTask"]] = relationship(
        back_populates="recommendation_record"
    )
    session: Mapped[Optional["Session"]] = relationship(
        back_populates="recommendation_records"
    )
