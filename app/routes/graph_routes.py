"""Routes for the graph structures module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from app.services.graph_help_service import GraphHelpService
from app.services.graph_structure_service import GraphStructureService
from app.services.session_service import SessionService

graph_bp = Blueprint("graph", __name__, url_prefix="/graph")


@graph_bp.get("/")
def graph_index() -> str:
    """Render graph structures cards page."""
    structures = GraphStructureService.list_structures()
    return render_template("graph/index.html", structures=structures)


@graph_bp.get("/<structure_id>")
def structure_page(structure_id: str) -> str:
    """Render one graph structure interaction page."""
    session_key = f"graph::{structure_id}"
    try:
        history = SessionService.get_history(session_key)
        model = GraphStructureService.get_view_model(structure_id, history)
    except KeyError:
        abort(404)

    help_data = GraphHelpService.get_structure_help(structure_id)
    return render_template(
        "graph/structure.html",
        model=model,
        help_data=help_data,
    )


@graph_bp.post("/<structure_id>/operate")
def operate_structure(structure_id: str) -> Any:
    """Execute one graph operation and return JSON response."""
    session_key = f"graph::{structure_id}"
    history = SessionService.get_history(session_key)
    body = request.get_json(silent=True) or {}
    operation_name = str(body.get("operation", "")).strip()
    payload = body.get("payload", {})

    if not operation_name:
        return jsonify({"success": False, "message": "Debes seleccionar una operacion."}), 400
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "El payload enviado es invalido."}), 400

    try:
        result = GraphStructureService.execute_operation(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.save_history(session_key, result["history"])
    return jsonify(result), (200 if result["success"] else 400)


@graph_bp.post("/<structure_id>/reset")
def reset_structure(structure_id: str) -> Any:
    """Reset one graph structure state in user session."""
    session_key = f"graph::{structure_id}"
    try:
        GraphStructureService.get_structure(structure_id)
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.clear_history(session_key)
    model = GraphStructureService.get_view_model(structure_id, [])
    return jsonify(
        {
            "success": True,
            "message": "La estructura fue reiniciada.",
            "visual_state": model["visual_state"],
            "history": [],
        }
    )
