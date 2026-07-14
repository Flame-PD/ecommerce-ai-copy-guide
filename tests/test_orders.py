from conftest import client, login_user, login_merchant

def test_checkout_and_pay_flow():
    """完整下单流程：结算 → 支付 → 发货 → 完成"""
    u_token = login_user()
    m_token = login_merchant()

    # 1. 结算
    resp = client.post("/api/orders/checkout", json={
        "items": [{"product_id": 1, "quantity": 1}],
        "address": "测试地址 北京市朝阳区",
    }, headers={"Authorization": f"Bearer {u_token}"})
    assert resp.status_code == 200, f"checkout failed: {resp.text}"
    order_id = resp.json()["id"]

    # 2. 支付（只有下单用户自己能支付）
    resp = client.post(f"/api/orders/{order_id}/pay",
                       headers={"Authorization": f"Bearer {u_token}"})
    assert resp.status_code == 200, f"pay failed: {resp.text}"

    # 3. 发货（商家操作）
    resp = client.post(f"/api/orders/{order_id}/ship",
                       headers={"Authorization": f"Bearer {m_token}"})
    assert resp.status_code == 200, f"ship failed: {resp.text}"

    # 4. 完成
    resp = client.post(f"/api/orders/{order_id}/complete",
                       headers={"Authorization": f"Bearer {u_token}"})
    assert resp.status_code == 200, f"complete failed: {resp.text}"

def test_my_orders():
    """查看我的订单"""
    token = login_user()
    resp = client.get("/api/orders/my",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_all_orders_merchant():
    """商家查看全部订单"""
    token = login_merchant()
    resp = client.get("/api/orders/all/list",
                      headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200

def test_orders_require_auth():
    """未登录不能下单"""
    resp = client.post("/api/orders/checkout", json={
        "items": [{"product_id": 1, "quantity": 1}],
        "address": "test",
    })
    assert resp.status_code == 401
