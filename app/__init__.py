"""Application factory for the data structures visualizer."""

from __future__ import annotations

from pathlib import Path

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from cachelib.file import FileSystemCache

try:
    from flask_session import Session
except ImportError:  # pragma: no cover - fallback for minimal environments
    Session = None

from app.config import Config
from app.routes.hash_routes import hash_bp
from app.routes.graph_routes import graph_bp
from app.routes.hierarchical_routes import hierarchical_bp
from app.routes.help_routes import help_bp
from app.routes.main_routes import main_bp
from app.routes.sequential_routes import sequential_bp
from app.routes.sorting_routes import sorting_api_bp, sorting_bp


def create_app(config_class: type[Config] = Config) -> Flask:
    """Create and configure the Flask application."""
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
        static_url_path="/static",
    )
    app.config.from_object(config_class)
    _configure_session_backend(app)
    _configure_proxy_headers(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(sequential_bp)
    app.register_blueprint(hierarchical_bp)
    app.register_blueprint(graph_bp)
    app.register_blueprint(hash_bp)
    app.register_blueprint(sorting_bp)
    app.register_blueprint(sorting_api_bp)
    app.register_blueprint(help_bp)

    return app


def _configure_session_backend(app: Flask) -> None:
    """Configure Flask session storage backend."""
    if Session is None:
        app.logger.warning(
            "Flask-Session no esta instalado; se usa sesion por cookie firmada."
        )
        return

    session_type = str(app.config.get("SESSION_TYPE", "cachelib")).lower()

    if session_type == "cachelib":
        cache_dir = str(app.config.get("SESSION_CACHE_DIR"))
        threshold = int(app.config.get("SESSION_CACHE_THRESHOLD", 10000))
        mode = int(app.config.get("SESSION_CACHE_MODE", 0o600))
        app.config["SESSION_CACHELIB"] = FileSystemCache(
            cache_dir=cache_dir,
            threshold=threshold,
            mode=mode,
        )
    elif session_type == "redis":
        redis_url = app.config.get("SESSION_REDIS_URL")
        if redis_url:
            try:
                from redis import Redis

                app.config["SESSION_REDIS"] = Redis.from_url(redis_url)
            except Exception as exc:  # pragma: no cover
                app.logger.warning(
                    "No se pudo configurar Redis para sesiones (%s). "
                    "Se mantiene SESSION_TYPE=%s.",
                    exc,
                    session_type,
                )
    Session(app)


def _configure_proxy_headers(app: Flask) -> None:
    """Apply ProxyFix when app runs behind reverse proxy."""
    if not app.config.get("ENABLE_PROXY_FIX", True):
        return
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=1,
        x_proto=1,
        x_host=1,
        x_port=1,
    )
