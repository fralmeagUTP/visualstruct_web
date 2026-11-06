"""Routes for hash-table module."""

from __future__ import annotations

from typing import Any

import hashlib
import json

from flask import Blueprint, abort, jsonify, render_template, request, session

from app.domain.hash.snapshot_pool import compact_hash_trace
from app.services.hash_help_service import HashHelpService
from app.services.hash_structure_service import HashStructureService
from app.services import hash_journal_service
from app.services.session_service import SessionService, SESSION_KEY, SessionHistoryLimitError

hash_bp = Blueprint("hash", __name__, url_prefix="/hash")


@hash_bp.before_request
def _validate_json_body() -> Any:
    """Reject malformed/non-object payloads before any session state is read."""
    if request.endpoint in {'hash.operate_structure', 'hash.compare_capacities'}:
        if not isinstance(request.get_json(silent=True), dict):
            return jsonify(success=False, message="El cuerpo enviado debe ser un objeto JSON válido."), 400
    return None


def _read_record(session_key, *, include_checkpoint=False):
    # Hash suspension must inspect even legacy records without migrating storage.
    raw = session.get(SESSION_KEY, {})
    stored = raw.get(session_key, []) if isinstance(raw, dict) else []
    if isinstance(stored, dict) and not include_checkpoint:
        stored = {**stored, "checkpoint": None}
    record, _ = SessionService._record(stored)
    return record


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
        history = _read_record(session_key)["history"]
        model = HashStructureService.get_view_model(structure_id, history)
    except KeyError:
        abort(404)

    model["main_c"] = hash_journal_service.get_main(session_key, history)
    model['console_output'] = hash_journal_service.get_stdout(session_key, history)
    checkpoint = _read_record(session_key, include_checkpoint=True)["checkpoint"]
    digest = hashlib.sha256(json.dumps(history, sort_keys=True).encode()).hexdigest()
    if not model["visual_state"].get("suspended") and checkpoint and checkpoint.get("schema") == "hash-trace/v1" and checkpoint.get("history_digest") == digest:
        model["execution_trace"] = checkpoint.get("trace")
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
    history = _read_record(session_key)["history"]
    body = request.get_json(silent=True) or {}
    operation_name = str(body.get("operation", "")).strip()
    payload = body.get("payload", {})

    if not operation_name:
        return jsonify({"success": False, "message": "Debes seleccionar una operación."}), 400
    if not isinstance(payload, dict):
        return jsonify({"success": False, "message": "El payload enviado es inválido."}), 400

    try:
        result = HashStructureService.execute_operation(
            structure_id=structure_id,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        return jsonify({"success": False, "message": "La estructura solicitada no existe."}), 404

    try:
        SessionService.validate_history_capacity(result["history"], history)
    except SessionHistoryLimitError as error:
        previous = HashStructureService.get_view_model(structure_id, history)
        return jsonify(success=False, preserve_session=True, message=str(error),
                       history=history, visual_state=previous["visual_state"],
                       main_c=hash_journal_service.get_main(session_key, history)), 409

    if result.get("preserve_session"):
        result["main_c"] = hash_journal_service.get_main(session_key, history)
        return jsonify(result), 400
    result["main_c"] = hash_journal_service.record_journal(session_key, history, result["history"], operation_name, payload, result)
    if result.get("execution_trace"):
        result["execution_trace"] = compact_hash_trace(result["execution_trace"])
    SessionService.save_history(session_key, result["history"])
    persisted_history = _read_record(session_key)["history"]
    if persisted_history == result["history"] and result.get("execution_trace"):
        SessionService.save_checkpoint(session_key, {"schema": "hash-trace/v1",
            "history_digest": hashlib.sha256(json.dumps(persisted_history, sort_keys=True).encode()).hexdigest(),
            "trace": result["execution_trace"]})
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
    hash_journal_service.clear_journal(session_key)
    model = HashStructureService.get_view_model(structure_id, [])
    return jsonify(
        {
            "success": True,
            "message": "La estructura fue reiniciada.",
            "visual_state": model["visual_state"],
            "history": [],
            "main_c": model["main_c"],
            "console_output": "",
        }
    )
