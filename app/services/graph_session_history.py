"""Read-only legacy access and lossless canonical graph history persistence."""
from copy import deepcopy
from flask import session
from app.services.session_service import SESSION_KEY, SESSION_RECORD_VERSION


def read_graph_history(key="graph::graph"):
    histories = session.get(SESSION_KEY, {})
    raw = histories.get(key, []) if isinstance(histories, dict) else []
    return deepcopy(raw.get("history", []) if isinstance(raw, dict) else raw)


def save_graph_history(key, history):
    # A graph replay needs its complete prefix; never silently truncate commands.
    histories = deepcopy(session.get(SESSION_KEY, {}))
    if not isinstance(histories, dict):
        histories = {}
    histories[key] = {"schema_version": SESSION_RECORD_VERSION,
                      "history": deepcopy(history), "checkpoint": None}
    session[SESSION_KEY] = histories
    session.modified = True
