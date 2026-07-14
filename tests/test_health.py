from conftest import client

def test_login_success():
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "123456",
        "role": "merchant",
    })
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert body["role"] == "merchant"

def test_login_wrong_password():
    resp = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "wrong_password",
        "role": "merchant",
    })
    assert resp.status_code == 401

def test_login_nonexistent_user():
    resp = client.post("/api/auth/login", json={
        "username": "nobody",
        "password": "123456",
        "role": "user",
    })
    assert resp.status_code == 401

def test_unauthorized_access():
    """不带 token 访问需要登录的接口，应返回 401"""
    resp = client.get("/api/products/my/favorites")
    assert resp.status_code == 401

def test_user_cannot_access_merchant():
    """普通用户访问商家接口，应返回 403"""
    from conftest import login_user
    token = login_user()
    resp = client.post("/api/ai/copy", json={
        "product_id": 1, "style": "professional"
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
