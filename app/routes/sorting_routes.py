"""Routes for sorting module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request

from app.services.session_service import SessionService
from app.services.sorting_help_service import SortingHelpService
from app.services.sorting_structure_service import SortingStructureService

sorting_bp = Blueprint("sorting", __name__, url_prefix="/sorting")
sorting_api_bp = Blueprint("sorting_api", __name__, url_prefix="/api/ordenamiento")

_STRUCTURE_ID = "sorting_array"
_SESSION_KEY = "sorting::sorting_array"


@sorting_bp.get("/")
def sorting_index() -> str:
    """Render sorting module index page."""
    structures = SortingStructureService.list_structures()
    return render_template("sorting/index.html", structures=structures)


@sorting_bp.get("/visualizador")
def sorting_view() -> str:
    """Render sorting visualizer page."""
    history = SessionService.get_history(_SESSION_KEY)
    model = SortingStructureService.get_view_model(_STRUCTURE_ID, history)
    help_data = SortingHelpService.get_structure_help(_STRUCTURE_ID)
    return render_template("sorting/structure.html", model=model, help_data=help_data)


@sorting_bp.get("/sorting_array")
def sorting_view_alias() -> Any:
    """Compatibility alias for structure style routes."""
    return sorting_view()


def _execute(operation_name: str, payload: dict[str, Any]) -> tuple[Any, int]:
    history = SessionService.get_history(_SESSION_KEY)
    try:
        result = SortingStructureService.execute_operation(
            structure_id=_STRUCTURE_ID,
            operation_name=operation_name,
            payload=payload,
            history=history,
        )
    except KeyError:
        abort(404)

    SessionService.save_history(_SESSION_KEY, result.get("history", history))
    status = 200 if result.get("success") else 400
    return jsonify(result), status


@sorting_api_bp.post("/create-array")
def api_create_array() -> tuple[Any, int]:
    body = request.get_json(silent=True) or {}
    return _execute("create_array", {"values": body.get("values", "")})


@sorting_api_bp.post("/random-array")
def api_random_array() -> tuple[Any, int]:
    body = request.get_json(silent=True) or {}
    payload = {
        "size": body.get("size", ""),
        "min_value": body.get("min_value", ""),
        "max_value": body.get("max_value", ""),
        "seed": body.get("seed", ""),
    }
    return _execute("generate_random_array", payload)


@sorting_api_bp.post("/algorithm")
def api_select_algorithm() -> tuple[Any, int]:
    body = request.get_json(silent=True) or {}
    return _execute("select_algorithm", {"algorithm_id": body.get("algorithm_id", "")})


@sorting_api_bp.post("/run")
def api_run() -> tuple[Any, int]:
    body = request.get_json(silent=True) or {}
    payload = {
        "mode": body.get("mode", "step_by_step"),
        "algorithm_id": body.get("algorithm_id", ""),
    }
    return _execute("run", payload)


@sorting_api_bp.post("/compare")
def api_compare() -> tuple[Any, int]:
    """Compare two algorithms without mutating the session history."""
    body = request.get_json(silent=True) or {}
    try:
        result = SortingStructureService.compare_algorithms(
            values=body.get("values", ""),
            left_algorithm=str(body.get("left_algorithm", "")),
            right_algorithm=str(body.get("right_algorithm", "")),
        )
    except (ValueError, TypeError) as error:
        return jsonify({"success": False, "message": str(error)}), 400
    return jsonify(result), 200


@sorting_api_bp.post("/step")
def api_step() -> tuple[Any, int]:
    body = request.get_json(silent=True) or {}
    payload = {
        "direction": body.get("direction", "next"),
        "cursor": body.get("cursor", -1),
        "algorithm_id": body.get("algorithm_id", ""),
    }
    return _execute("step", payload)


@sorting_api_bp.get("/state")
def api_state() -> tuple[Any, int]:
    history = SessionService.get_history(_SESSION_KEY)
    model = SortingStructureService.get_view_model(_STRUCTURE_ID, history)
    return (
        jsonify(
            {
                "success": True,
                "visual_state": model["visual_state"],
                "history": history,
                "algorithms": model["algorithms"],
            }
        ),
        200,
    )


@sorting_api_bp.post("/reset")
def api_reset() -> tuple[Any, int]:
    SessionService.clear_history(_SESSION_KEY)
    model = SortingStructureService.get_view_model(_STRUCTURE_ID, [])
    return (
        jsonify(
            {
                "success": True,
                "message": "Estado de ordenamiento reiniciado.",
                "visual_state": model["visual_state"],
                "history": [],
                "algorithms": model["algorithms"],
            }
        ),
        200,
    )
