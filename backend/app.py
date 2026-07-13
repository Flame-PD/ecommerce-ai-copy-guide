from __future__ import annotations

from flask import Flask, jsonify

from backend.api.routes import api_bp
from backend.config import AppConfig
from backend.database import init_db


def create_app(config: AppConfig | None = None) -> Flask:
    app_config = config or AppConfig.from_env()
    app = Flask(__name__)
    app.json.ensure_ascii = False
    app.config["APP_CONFIG"] = app_config

    if app_config.database_url:
        init_db(app_config.database_url)

    @app.get("/health")
    def health() -> tuple[dict[str, object], int]:
        return {
            "status": "ok",
            "service": "ecommerce-ai-copy-guide",
            "version": "0.1.0",
            "runtime": app_config.public_summary(),
        }, 200

    @app.errorhandler(404)
    def not_found(_error: Exception):
        return jsonify({"error": "not_found", "message": "The requested endpoint does not exist."}), 404

    @app.errorhandler(500)
    def server_error(_error: Exception):
        return jsonify({"error": "server_error", "message": "Unexpected server error."}), 500

    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return response

    app.register_blueprint(api_bp, url_prefix="/api")
    return app


app = create_app()
