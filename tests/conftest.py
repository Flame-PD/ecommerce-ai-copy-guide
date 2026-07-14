import os

# 强制指向 backend 下的真实数据库，避免 pytest 从根目录跑时建空库
os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(
    os.path.dirname(__file__), "..", "backend", "ecommerce_ai.db"
).replace("\\", "/")

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def login_merchant() -> str:
    """登录商家账号，返回 token"""
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "123456",
        "role": "merchant",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


def login_user() -> str:
    """登录普通用户，返回 token"""
    resp = client.post("/api/auth/login", json={
        "username": "user",
        "password": "123456",
        "role": "user",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]
