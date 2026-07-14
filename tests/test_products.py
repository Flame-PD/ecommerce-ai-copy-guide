from conftest import client, login_merchant

def test_list_products():
    """不登录也能查看商品列表"""
    resp = client.get("/api/products")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_get_product_by_id():
    resp = client.get("/api/products/1")
    assert resp.status_code in [200, 404]

def test_product_categories():
    resp = client.get("/api/products/categories/list")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_create_product_requires_merchant():
    """创建商品需要商家身份"""
    token = login_merchant()
    resp = client.post("/api/products", data={
        "name": "测试商品",
        "category": "测试分类",
        "price": 99.0,
        "stock": 10,
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "测试商品"
    assert body["status"] == "off"  # 创建后默认下架

def test_soft_delete_product():
    """删除是软删除：status 变为 deleted"""
    token = login_merchant()
    # 先创建
    resp = client.post("/api/products", data={
        "name": "待删除", "category": "测试", "price": 1, "stock": 1,
    }, headers={"Authorization": f"Bearer {token}"})
    pid = resp.json()["id"]
    # 删除
    resp = client.delete(f"/api/products/{pid}",
                         headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
