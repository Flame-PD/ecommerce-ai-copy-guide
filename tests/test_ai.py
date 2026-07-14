from conftest import client, login_merchant

def test_ai_copy_generation():
    """AI 文案生成——依赖已存在的商品 1"""
    token = login_merchant()
    resp = client.post("/api/ai/copy", json={
        "product_id": 1,
        "style": "professional",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    result = resp.json()["result"]
    assert "title" in result

def test_ai_script_generation():
    """AI 直播脚本生成"""
    token = login_merchant()
    resp = client.post("/api/ai/script", json={
        "product_id": 1,
        "style": "professional",
        "platform": "live",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_ai_script_list():
    """查看已生成的脚本列表"""
    token = login_merchant()
    resp = client.get("/api/ai/scripts",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_ai_copy_requires_merchant():
    """非商家不能调 AI 接口"""
    resp = client.post("/api/ai/copy", json={
        "product_id": 1, "style": "professional",
    })
    assert resp.status_code == 401
