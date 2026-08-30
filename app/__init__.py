"""
AI Resume & Portfolio Builder - Flask Application Factory
"""
import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

# ─── Extensions (initialised without app) ────────────────────────────────────
db = SQLAlchemy()
csrf = CSRFProtect()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "60 per hour"],
    storage_uri="memory://",   # explicit in-memory storage – suppresses UserWarning
)


def create_app(config_name: str = "development") -> Flask:
    """Application factory."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # ── Config ──────────────────────────────────────────────────────────────
    from app.config import config_map
    app.config.from_object(config_map[config_name])

    # ── Extensions ──────────────────────────────────────────────────────────
    db.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # ── Logging ─────────────────────────────────────────────────────────────
    _setup_logging(app)

    # ── Blueprints ──────────────────────────────────────────────────────────
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.profile import profile_bp
    from app.routes.resume import resume_bp
    from app.routes.cover_letter import cover_letter_bp
    from app.routes.portfolio import portfolio_bp
    from app.routes.main import main_bp
    from app.routes.parser import parser_bp
    from app.routes.settings import settings_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(profile_bp, url_prefix="/profile")
    app.register_blueprint(resume_bp, url_prefix="/resume")
    app.register_blueprint(cover_letter_bp, url_prefix="/cover-letter")
    app.register_blueprint(portfolio_bp, url_prefix="/portfolio")
    app.register_blueprint(parser_bp, url_prefix="/parser")
    app.register_blueprint(settings_bp, url_prefix="/settings")

    # ── DB creation ─────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    # ── Error handlers ──────────────────────────────────────────────────────
    _register_error_handlers(app)

    return app


def _setup_logging(app: Flask) -> None:
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=5)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )
    handler.setFormatter(formatter)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template("errors/500.html"), 500

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Rate limit exceeded. Please slow down."}), 429
