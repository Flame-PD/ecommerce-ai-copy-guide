from __future__ import annotations

from pydantic import BaseModel, Field


class CopyGenerationRequest(BaseModel):
    product_name: str = Field(min_length=1, examples=["云感护腰办公椅"])
    audience: str = Field(default="都市白领", min_length=1)
    tone: str = Field(default="专业可信", min_length=1)
    selling_points: list[str] = Field(default_factory=list, max_length=8)


class GuideRecommendationRequest(BaseModel):
    user_need: str = Field(min_length=1, examples=["预算 300 元以内，送给经常加班的朋友"])
    budget: str = Field(default="未限定")
    products: list[str] = Field(default_factory=list, max_length=10)


class ReviewAnalysisRequest(BaseModel):
    product_name: str = Field(default="示例商品")
    reviews: list[str] = Field(min_length=1, max_length=30)


class LiveScriptRequest(BaseModel):
    product_name: str = Field(min_length=1)
    duration_minutes: int = Field(default=5, ge=1, le=120)
    tone: str = Field(default="热情自然", min_length=1)
    highlights: list[str] = Field(default_factory=list, max_length=8)
