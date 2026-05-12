"""Main routes for the homepage."""

from __future__ import annotations

from pathlib import Path

from flask import Blueprint, jsonify, render_template, send_from_directory

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index() -> str:
    """Render home page."""
    return render_template("index.html")


@main_bp.get("/assets/<path:filename>")
def asset_file(filename: str):
    """Serve static assets stored in the project-level assets directory."""
    project_root = Path(__file__).resolve().parents[2]
    assets_dir = project_root / "assets"
    return send_from_directory(str(assets_dir), filename)


@main_bp.get("/healthz")
def healthz():
    """Liveness endpoint for deployment health checks."""
    return jsonify({"status": "ok"}), 200
