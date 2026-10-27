"""Routes for sorting module."""

from __future__ import annotations

from typing import Any

from flask import Blueprint, abort, jsonify, render_template, request, session, current_app

from app.services.session_service import SessionService
from app.services.sorting_help_service import SortingHelpService
from app.services.sorting_structure_service import SortingStructureService
from app.services.sorting_main_program import build_sorting_main

sorting_bp = Blueprint("sorting", __name__, url_prefix="/sorting")
sorting_api_bp = Blueprint("sorting_api", __name__, url_prefix="/api/ordenamiento")

_STRUCTURE_ID = "sorting_array"
_SESSION_KEY = "sorting::sorting_array"



def _describe_counting_trace(trace: dict[str, Any], key: str) -> dict[str, Any]:
    if hasattr(trace, "page_source"): del trace.page_source
    trace["trace_id"] = key
    trace["page_url"] = f"/api/ordenamiento/traces/{key}/page"
    trace["export_url"] = f"/api/ordenamiento/traces/{key}/export"
    if trace.get("schema") == "counting-paged-trace/v1":
        trace["manifest"].update(trace_id=key, page_url=trace["page_url"], export_url=trace["export_url"], codec=trace["manifest"].get("codec", "counting-sparse-tape/v1"), ttl_seconds=900)
    return trace


def _bind_counting_trace(trace: dict[str, Any] | None) -> dict[str, Any] | None:
    if not trace or not hasattr(trace, "page_source"): return trace
    from secrets import token_urlsafe
    from app.services.counting_trace_service import get_counting_store
    owner = session.get("counting_owner")
    if owner is None:
        owner = token_urlsafe(24)
        session["counting_owner"] = owner
    source = trace.page_source
    key = get_counting_store().register(owner, source)
    return _describe_counting_trace(trace, key)


def _history_fingerprint(history) -> str:
    import hashlib, json
    return hashlib.sha256(json.dumps(history,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")).hexdigest()


def _saved_counting_source(strict: bool = False):
    from app.services.counting_trace_service import get_counting_store
    error_saved = session.get("counting_error_latest")
    saved = error_saved or session.get("counting_latest")
    if not saved: return None
    history = SessionService.get_history(_SESSION_KEY)
    if error_saved:
        if saved["history_fingerprint"] != _history_fingerprint(history): return None
    elif len(history) != saved["history_size"] or not history or history[-1].get("operation") != "run" or history[-1].get("payload", {}).get("algorithm_id") != saved.get("algorithm_id", "counting_sort"): return None
    try: return saved["trace_id"], get_counting_store().get(session.get("counting_owner"), saved["trace_id"])
    except (KeyError, TimeoutError):
        if strict: raise
        return None

def _session_view_model() -> dict[str, Any]:
    """Persist legacy materialization once, retaining accepted normalized history."""
    history = SessionService.get_history(_SESSION_KEY)
    model = SortingStructureService.get_view_model(_STRUCTURE_ID, history)
    if model["history"] != history:
        SessionService.save_history(_SESSION_KEY, model["history"])
    saved = _saved_counting_source()
    if saved:
        key, source = saved
        model["execution_trace"] = _describe_counting_trace(source.trace(), key)
        model["execution_mode"] = session["counting_error_latest"]["mode"] if source.error_info else model["history"][-1]["payload"]["mode"]
    return model


@sorting_bp.get("/")
def sorting_index() -> str:
    """Render sorting module index page."""
    structures = SortingStructureService.list_structures()
    return render_template("sorting/index.html", structures=structures)


@sorting_bp.get("/visualizador")
def sorting_view() -> str:
    """Render sorting visualizer page."""
    model = _session_view_model()
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
            counting_allocator=current_app.config.get("COUNTING_QA_ALLOCATOR") if current_app.testing and operation_name == "run" else None,
            radix_allocator=current_app.config.get("RADIX_QA_ALLOCATOR") if current_app.testing and operation_name == "run" else None,
        )
    except KeyError:
        abort(404)

    try:
        if result.get("execution_trace"):
            result["execution_trace"] = _bind_counting_trace(result["execution_trace"])
    except ValueError as error:
        previous = SortingStructureService.get_view_model(_STRUCTURE_ID, history)
        return jsonify(success=False, message=str(error), visual_state=previous["visual_state"], history=previous["history"], main_c=previous["main_c"]), 400
    if result.get("success"):
        session.pop("counting_error_latest", None)
    elif operation_name == "run" and result.get("execution_trace", {}).get("trace_id"):
        session["counting_error_latest"] = {"trace_id": result["execution_trace"]["trace_id"], "history_fingerprint": _history_fingerprint(result.get("history",history)), "mode": payload.get("mode","step_by_step"), "algorithm_id": result["execution_trace"]["operation_name"]}
    if operation_name == "run" and result.get("success") and result.get("execution_trace", {}).get("trace_id"):
        session["counting_latest"] = {"trace_id": result["execution_trace"]["trace_id"], "history_size": len(result["history"]), "algorithm_id": result["execution_trace"]["operation_name"]}
    result["main_c"] = build_sorting_main(result.get("history", history))
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
    for side in ("left", "right"):
        result[side]["trace"] = _bind_counting_trace(result[side]["trace"])
    return jsonify(result), 200


@sorting_api_bp.post("/step")
def api_step() -> tuple[Any, int]:
    body = request.get_json(silent=True) or {}
    try:
        saved = _saved_counting_source(strict=True) if not body.get("algorithm_id") or body["algorithm_id"] in {"counting_sort", "binsort", "radixsort"} else None
    except KeyError: return jsonify(success=False, message="Traza no disponible; la navegacion no reejecuta Counting."), 404
    except TimeoutError as error: return jsonify(success=False, message=str(error)), 410
    if saved:
        key, source = saved
        if body.get("algorithm_id") and body["algorithm_id"] != source.final_state["algorithm"]:
            return jsonify(success=False, message="La traza guardada corresponde a otro algoritmo."), 409
        try:
            direction = body.get("direction", "next")
            if direction not in {"next", "prev", "previous"}: raise ValueError("Direccion no valida.")
            cursor = int(body.get("cursor", -1)) + (1 if direction == "next" else -1)
            cursor = max(0, min(cursor, len(source.tape)-1))
            trace = _describe_counting_trace(source.trace(), key)
            frame = source.frame(cursor, dense=trace.get("schema") != "counting-paged-trace/v1")
            history = SessionService.get_history(_SESSION_KEY)
            return jsonify(success=True, message=f"Paso {cursor+1}/{len(source.tape)}.", cursor=cursor, total_steps=len(source.tape), step=frame, visual_state=frame["state_after"], execution_trace=trace, history=history, main_c=build_sorting_main(history)), 200
        except (ValueError, TypeError) as error: return jsonify(success=False, message=str(error)), 400
    selected = body.get("algorithm_id") or next((entry.get("payload", {}).get("algorithm_id") for entry in reversed(SessionService.get_history(_SESSION_KEY)) if entry.get("payload", {}).get("algorithm_id")), None)
    if selected in {"binsort", "radixsort"}:
        return jsonify(success=False, message="No hay traza guardada del algoritmo; ejecute Run antes de navegar."), 404
    payload = {
        "direction": body.get("direction", "next"),
        "cursor": body.get("cursor", -1),
        "algorithm_id": body.get("algorithm_id", ""),
    }
    return _execute("step", payload)


@sorting_api_bp.get("/state")
def api_state() -> tuple[Any, int]:
    model = _session_view_model()
    return (
        jsonify(
            {
                "success": True,
                "visual_state": model["visual_state"],
                "history": model["history"],
                "main_c": model["main_c"],
                "algorithms": model["algorithms"],
            }
        ),
        200,
    )


@sorting_api_bp.post("/reset")
def api_reset() -> tuple[Any, int]:
    from app.services.counting_trace_service import get_counting_store
    get_counting_store().revoke(session.get("counting_owner"))
    session.pop("counting_latest", None)
    session.pop("counting_error_latest", None)
    session.pop("counting_owner", None)
    SessionService.clear_history(_SESSION_KEY)
    model = SortingStructureService.get_view_model(_STRUCTURE_ID, [])
    return (
        jsonify(
            {
                "success": True,
                "message": "Estado de ordenamiento reiniciado.",
                "visual_state": model["visual_state"],
                "history": [],
                "main_c": model["main_c"],
                "algorithms": model["algorithms"],
            }
        ),
        200,
    )


@sorting_api_bp.get("/traces/<trace_id>/page")
def api_counting_page(trace_id: str) -> tuple[Any, int]:
    """Decode an owned immutable page; never dispatch sort or append history."""
    from app.services.counting_trace_service import get_counting_store
    try:
        source = get_counting_store().get(session.get("counting_owner"), trace_id)
        start = int(request.args.get("start", "0"))
        limit = int(request.args.get("limit", "64"))
        if request.args.get("concept"):
            start = source.locate(request.args["concept"], int(request.args.get("occurrence", "1")))
            limit = 1
            if start is None:
                return jsonify(success=True, trace_id=trace_id, schema="counting-trace-page/v1", start=0, end=0, step_count=len(source.tape), steps=[]), 200
        page = source.page(start, limit)
        page.update(success=True, trace_id=trace_id)
        return jsonify(page), 200
    except KeyError: return jsonify(success=False, message="Traza no disponible para esta sesion."), 404
    except TimeoutError as error: return jsonify(success=False, message=str(error)), 410
    except (ValueError, TypeError) as error: return jsonify(success=False, message=str(error)), 400


@sorting_api_bp.get("/traces/<trace_id>/export")
def api_counting_export(trace_id: str) -> tuple[Any, int]:
    """Export compact records without expanding zeros or re-running Counting."""
    from app.services.counting_trace_service import get_counting_store
    try:
        source = get_counting_store().get(session.get("counting_owner"), trace_id)
        return jsonify(success=True, trace_id=trace_id, compact_trace=source.compact_export()), 200
    except KeyError: return jsonify(success=False, message="Traza no disponible para esta sesion."), 404
    except TimeoutError as error: return jsonify(success=False, message=str(error)), 410
