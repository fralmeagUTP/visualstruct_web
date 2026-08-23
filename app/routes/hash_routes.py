"""Routes for hash-table module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from app.services.hash_help_service import HashHelpService
from app.services.hash_structure_service import HashStructureService
from app.services.session_service import SessionService

hash_bp = Blueprint("hash", __name__, url_prefix="/hash")


@hash_bp.post("/compare-capacities")
def compare_capacities() -> Any:
    """Compare fixed capacities without changing the session table."""
    body = request.get_json(silent=True) or {}
    try:
        result = HashStructureService.compare_capacities(
            body.get("entries"), body.get("success_key"), body.get("absent_key"),
        )
    except (TypeError, ValueError) as error:
        return jsonify({"success": False, "message": str(error)}), 400
    return jsonify(result)


@hash_bp.get("/")
def hash_index() -> str:
    """Render hash structures cards page."""
    structures = HashStructureService.list_structures()
    return render_template("hash/index.html", structures=structures)


@hash_bp.get("/<structure_id>")
def structure_page(structure_id: str) -> str:
    """Render one hash structure interaction page."""
    session_key = f"hash::{structure_id}"
    try:
        history = SessionService.get_history(session_key)
        model = HashStructureService.get_view_model(structure_id, history)
    except KeyError:
        abort(404)

    help_data = HashHelpService.get_structure_help(structure_id)
    return render_template(
        "hash/structure.html",
        model=model,
        help_data=help_data,
    )


@hash_bp.post("/<structure_id>/operate")
def operate_structure(structure_id: str) -> Any:
    """Execute one hash operation and return JSON response."""
    session_key = f"hash::{structure_id}"
    history = SessionService.get_history(session_key)
    body = request.get_json(silent=True) or {}
    operation_name = str(body.get("operation", "")).strip()
    payload = body.get("payload", {})

    if not operation_name:
        return jsonify({"success": False, "message": "Debes seleccionar una operacion."}), 400
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "El payload enviado es invalido."}), 400

    try:
        result = HashStructureService.execute_operation(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.save_history(session_key, result["history"])
    return jsonify(result), (200 if result["success"] else 400)


@hash_bp.post("/<structure_id>/reset")
def reset_structure(structure_id: str) -> Any:
    """Reset one hash structure state in user session."""
    session_key = f"hash::{structure_id}"
    try:
        HashStructureService.get_structure(structure_id)
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.clear_history(session_key)
    model = HashStructureService.get_view_model(structure_id, [])
    return jsonify(
        {
            "success": True,
            "message": "La estructura fue reiniciada.",
            "visual_state": model["visual_state"],
            "history": [],
        }
    )
