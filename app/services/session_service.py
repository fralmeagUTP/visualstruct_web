"""Session helpers for structure interaction state."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from flask import current_app, session

SESSION_KEY = "sequential_histories"


class SessionService:
    """Provide a thin wrapper over Flask session for histories."""

    @staticmethod
    def _get_histories() -> dict[str, list[dict[str, Any]]]:
        raw = session.get(SESSION_KEY, {})
        if not isinstance(raw, dict):
            raw = {}
        return deepcopy(raw)

    @staticmethod
    def get_history(structure_id: str) -> list[dict[str, Any]]:
        """Return a copy of persisted mutating operations."""
        histories = SessionService._get_histories()
        history = histories.get(structure_id, [])
        if not isinstance(history, list):
            return []
        return history

    @staticmethod
    def save_history(structure_id: str, history: list[dict[str, Any]]) -> None:
        """Persist history for one structure."""
        histories = SessionService._get_histories()
        cleaned_history = [item for item in history if isinstance(item, dict)]
        max_history = int(current_app.config.get("SESSION_MAX_HISTORY", 300))
        if max_history > 0:
            cleaned_history = cleaned_history[-max_history:]
        histories[structure_id] = cleaned_history
        session[SESSION_KEY] = histories
        session.modified = True

    @staticmethod
    def clear_history(structure_id: str) -> None:
        """Delete history of one structure."""
        histories = SessionService._get_histories()
        histories.pop(structure_id, None)
        session[SESSION_KEY] = histories
        session.modified = True
