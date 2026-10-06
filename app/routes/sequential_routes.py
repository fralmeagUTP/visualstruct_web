"""Routes for the sequential structures module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from app.services.help_service import HelpService
from app.services.session_service import SessionService
from app.services.structure_service import StructureService

sequential_bp = Blueprint("sequential", __name__, url_prefix="/sequential")


@sequential_bp.get("/")
def sequential_index() -> str:
    """Render the list of sequential structures."""
    structures = StructureService.list_structures()
    return render_template("sequential/index.html", structures=structures)


@sequential_bp.get("/<structure_id>")
def structure_page(structure_id: str) -> str:
    """Render one structure interaction page."""
    try:
        history = SessionService.get_history(structure_id)
        model = StructureService.get_view_model(structure_id, history)
    except KeyError:
        abort(404)

    if structure_id == "stack":
        from app.services.stack_cleanup_session_service import prepared_cleanup
        model["prepared_cleanup_trace"] = prepared_cleanup(model["history"])
        from app.services.stack_push_session_service import prepared_push
        model["prepared_push_trace"] = prepared_push(model["history"])
    if structure_id == "queue":
        from app.services.queue_cleanup_session_service import prepared_cleanup
        model["prepared_cleanup_trace"] = prepared_cleanup(model["history"])
        from app.services.queue_enqueue_session_service import prepared_enqueue
        model["prepared_enqueue_trace"] = prepared_enqueue(model["history"])
        from app.services.queue_dequeue_session_service import prepared_dequeue
        model["prepared_dequeue_trace"] = prepared_dequeue(model["history"], source_code=model["didactic"]["operations"]["desencolar"])
    if structure_id == "priority_queue":
        from app.services.priority_queue_cleanup_session_service import prepared_cleanup
        model["prepared_cleanup_trace"] = prepared_cleanup(model["history"])
        from app.services.priority_queue_enqueue_session_service import prepared_enqueue
        model["prepared_enqueue_trace"] = prepared_enqueue(model["history"], source_code=model["didactic"]["operations"]["encolar"])
        from app.services.priority_queue_dequeue_session_service import prepared_dequeue
        model["prepared_dequeue_trace"] = prepared_dequeue(model["history"], source_code=model["didactic"]["operations"]["desencolar"])
    help_data = HelpService.get_structure_help(structure_id)
    return render_template(
        "sequential/structure.html",
        model=model,
        help_data=help_data,
    )


@sequential_bp.post("/<structure_id>/operate")
def operate_structure(structure_id: str) -> Any:
    """Execute one operation and return JSON response."""
    history = SessionService.get_history(structure_id)
    body = request.get_json(silent=True) or {}
    operation_name = str(body.get("operation", "")).strip()
    payload = body.get("payload", {})

    if not operation_name:
        return jsonify({"success": False, "message": "Debes seleccionar una operación."}), 400
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "El payload enviado es inválido."}), 400

    try:
        result = StructureService.execute_operation(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.save_history(structure_id, result["history"])
    if structure_id == "stack":
        from app.services.stack_cleanup_session_service import remember_cleanup
        remember_cleanup(result)
        from app.services.stack_push_session_service import remember_push
        remember_push(result)
    if structure_id == "queue":
        from app.services.queue_cleanup_session_service import remember_cleanup
        remember_cleanup(result)
        from app.services.queue_enqueue_session_service import remember_enqueue
        remember_enqueue(result)
        from app.services.queue_dequeue_session_service import remember_dequeue
        remember_dequeue(result)
    if structure_id == "priority_queue":
        from app.services.priority_queue_cleanup_session_service import remember_cleanup
        remember_cleanup(result)
        from app.services.priority_queue_enqueue_session_service import remember_enqueue
        remember_enqueue(result)
        from app.services.priority_queue_dequeue_session_service import remember_dequeue
        remember_dequeue(result)
    return jsonify(result), (200 if result["success"] else 400)


@sequential_bp.post("/<structure_id>/reset")
def reset_structure(structure_id: str) -> Any:
    """Reset one structure state in user session."""
    try:
        StructureService.get_structure(structure_id)
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    SessionService.clear_history(structure_id)
    if structure_id == "stack":
        from app.services.stack_cleanup_session_service import forget_cleanup
        forget_cleanup()
        from app.services.stack_push_session_service import forget_push
        forget_push()
    if structure_id == "queue":
        from app.services.queue_cleanup_session_service import forget_cleanup
        forget_cleanup()
        from app.services.queue_enqueue_session_service import forget_enqueue
        forget_enqueue()
        from app.services.queue_dequeue_session_service import forget_dequeue
        forget_dequeue()
    if structure_id == "priority_queue":
        from app.services.priority_queue_cleanup_session_service import forget_cleanup
        forget_cleanup()
        from app.services.priority_queue_enqueue_session_service import forget_enqueue
        forget_enqueue()
        from app.services.priority_queue_dequeue_session_service import forget_dequeue
        forget_dequeue()
    model = StructureService.get_view_model(structure_id, [])
    return jsonify(
        {
            "success": True,
            "message": "La estructura fue reiniciada.",
            "visual_state": model["visual_state"],
            "history": [],
        }
    )
