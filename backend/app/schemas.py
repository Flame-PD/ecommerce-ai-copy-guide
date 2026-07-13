from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=6)
    nickname: Optional[str] = ""
    role: Optional[str] = "user"


class UserLogin(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserOut(BaseModel):
    id: int
    username: str
    nickname: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True


class PasswordReset(BaseModel):
    username: str
    new_password: str = Field(..., min_length=6)


class ProductBase(BaseModel):
    name: str
    category: Optional[str] = ""
    description: Optional[str] = ""
    price: float = 0.0
    stock: int = 0
    status: Optional[str] = "off"
    specs: Optional[List[str]] = []
    image_url: Optional[str] = ""


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[str] = None
    specs: Optional[List[str]] = None
    image_url: Optional[str] = None
    ai_title: Optional[str] = None
    ai_selling_points: Optional[str] = None
    ai_detail: Optional[str] = None
    ai_slogan: Optional[str] = None


class ProductOut(ProductBase):
    id: int
    ai_title: Optional[str] = ""
    ai_selling_points: Optional[str] = ""
    ai_detail: Optional[str] = ""
    ai_slogan: Optional[str] = ""
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class KnowledgeItemCreate(BaseModel):
    product_id: Optional[int] = None
    category: Optional[str] = "common"
    question: str
    answer: str


class KnowledgeItemOut(KnowledgeItemCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessage(BaseModel):
    message: str
    product_id: Optional[int] = None


class ChatOut(BaseModel):
    id: int
    message: str
    response: str
    product_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = 1
    spec: Optional[str] = ""


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    address: Optional[str] = ""


class OrderItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float
    spec: str

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    total_amount: float
    address: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    product_id: int
    order_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    content: str


class ReviewOut(BaseModel):
    id: int
    user_id: int
    product_id: int
    order_id: Optional[int]
    rating: int
    content: str
    sentiment: str
    created_at: datetime

    class Config:
        from_attributes = True


class LiveScriptCreate(BaseModel):
    product_id: Optional[int] = None
    title: Optional[str] = ""
    style: Optional[str] = "professional"
    content: str


class LiveScriptOut(LiveScriptCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FavoriteOut(BaseModel):
    id: int
    product_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AddressCreate(BaseModel):
    name: str
    phone: str
    detail: str
    is_default: Optional[bool] = False


class AddressOut(AddressCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class AICopyRequest(BaseModel):
    product_id: int
    style: Optional[str] = "professional"


class AIScriptRequest(BaseModel):
    product_id: int
    style: Optional[str] = "professional"
    platform: Optional[str] = "live"


class AISimpleRequest(BaseModel):
    product_id: Optional[int] = None
    prompt: Optional[str] = ""


class AIResponse(BaseModel):
    result: str


class SentimentStats(BaseModel):
    positive: int
    neutral: int
    negative: int
    avg_rating: float
