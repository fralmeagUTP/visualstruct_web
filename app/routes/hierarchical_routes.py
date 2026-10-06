"""Routes for the hierarchical structures module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from app.services.hierarchical_help_service import HierarchicalHelpService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.session_service import SessionService

hierarchical_bp = Blueprint("hierarchical", __name__, url_prefix="/hierarchical")


@hierarchical_bp.get("/")
def hierarchical_index() -> str:
    """Render hierarchical structures cards page."""
    structures = HierarchicalStructureService.list_structures()
    return render_template("hierarchical/index.html", structures=structures)


@hierarchical_bp.get("/<structure_id>")
def structure_page(structure_id: str) -> str:
    """Render one hierarchical structure interaction page."""
    session_key = f"hierarchical::{structure_id}"
    try:
        history = SessionService.get_history(session_key)
        model = HierarchicalStructureService.get_view_model(structure_id, history)
    except KeyError:
        abort(404)

    help_data = HierarchicalHelpService.get_structure_help(structure_id)
    return render_template(
        "hierarchical/structure.html",
        model=model,
        help_data=help_data,
    )


@hierarchical_bp.post("/<structure_id>/operate")
def operate_structure(structure_id: str) -> Any:
    """Execute one hierarchical operation and return JSON response."""
    session_key = f"hierarchical::{structure_id}"
    history = SessionService.get_history(session_key)
    body = request.get_json(silent=True) or {}
    operation_name = str(body.get("operation", "")).strip()
    payload = body.get("payload", {})

    if not operation_name:
        return jsonify({"success": False, "message": "Debes seleccionar una operación."}), 400
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "El payload enviado es inválido."}), 400

    try:
        result = HierarchicalStructureService.execute_operation(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.save_history(session_key, result["history"])
    return jsonify(result), (200 if result["success"] else 400)


@hierarchical_bp.post("/<structure_id>/reset")
def reset_structure(structure_id: str) -> Any:
    """Reset one hierarchical structure state in user session."""
    session_key = f"hierarchical::{structure_id}"
    try:
        HierarchicalStructureService.get_structure(structure_id)
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.clear_history(session_key)
    model = HierarchicalStructureService.get_view_model(structure_id, [])
    return jsonify(
        {
            "success": True,
            "message": "La estructura fue reiniciada.",
            "visual_state": model["visual_state"],
            "history": [],
        }
    )


@hierarchical_bp.post("/compare")
def compare_structures() -> Any:
    """Compare two isolated hierarchical executions over one immutable input."""
    body=request.get_json(silent=True) or {}
    try:
        result=HierarchicalStructureService.compare_structures(str(body.get("kind", "")),body.get("values"))
    except ValueError as error:
        return jsonify({"success":False,"message":str(error)}),400
    return jsonify({"success":True,**result})
