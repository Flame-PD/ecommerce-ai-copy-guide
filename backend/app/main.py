from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, users, products, orders, reviews, ai, chat, knowledge

Base.metadata.create_all(bind=engine)

app = FastAPI(title="电商AI商品文案生成与智能导购助手", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])
app.include_router(products.router, prefix="/api/products", tags=["商品"])
app.include_router(orders.router, prefix="/api/orders", tags=["订单"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["评价"])
app.include_router(ai.router, prefix="/api/ai", tags=["AI生成"])
app.include_router(chat.router, prefix="/api/chat", tags=["智能导购"])
app.include_router(knowledge.router, prefix="/api/knowledge", tags=["知识库"])


@app.get("/api/health")
def health():
    return {"status": "ok"}
