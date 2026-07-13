from backend.app import create_app


def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def test_health():
    response = client().get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_capabilities():
    response = client().get("/api/capabilities")

    assert response.status_code == 200
    assert response.get_json()["mode"] in ("mock", "deepseek")


def test_generate_copy():
    response = client().post(
        "/api/copy/generate",
        json={
            "product_name": "云感护腰办公椅",
            "audience": "久坐办公人群",
            "tone": "专业可信",
            "selling_points": ["护腰支撑", "透气坐垫"],
        },
    )

    body = response.get_json()
    assert response.status_code == 200
    assert body["title"]  # 有标题即可（Mock 模板化 / AI 创意改写均满足）
    assert body["selling_points"]
    assert body["detail_copy"]
    assert body["ad_slogan"]


def test_review_analysis_validation():
    response = client().post("/api/reviews/analyze", json={"reviews": []})

    assert response.status_code == 400
    assert response.get_json()["error"] == "validation_error"
