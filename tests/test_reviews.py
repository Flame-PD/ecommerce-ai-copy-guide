from conftest import client, login_user, login_merchant

def test_create_review():
    """用户对商品发表评论，自动标注情感"""
    token = login_user()
    resp = client.post("/api/reviews", json={
        "product_id": 1,
        "rating": 5,
        "content": "非常好用，强烈推荐！",
    }, headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["rating"] == 5
    assert body["content"] == "非常好用，强烈推荐！"
    # 情感分析应自动标注
    assert body["sentiment"] in ("positive", "neutral", "negative")

def test_product_reviews():
    """查看商品的评论列表（不需要登录）"""
    resp = client.get("/api/reviews/product/1")
    assert resp.status_code == 200

def test_review_stats():
    """商家查看评论统计数据"""
    token = login_merchant()
    resp = client.get("/api/reviews/stats/1",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    body = resp.json()
    assert "positive" in body
    assert "negative" in body
    assert "avg_rating" in body

def test_review_summary():
    """商家生成 AI 评论总结"""
    token = login_merchant()
    resp = client.post("/api/reviews/summary",
                       json={"product_id": 1},
                       headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

def test_review_requires_auth():
    """未登录不能发表评论"""
    resp = client.post("/api/reviews", json={
        "product_id": 1, "rating": 3, "content": "test",
    })
    assert resp.status_code == 401
