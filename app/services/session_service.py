"""Session helpers for structure interaction state."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from flask import current_app, session

SESSION_KEY = "sequential_histories"
SESSION_RECORD_VERSION = 1


class SessionService:
    """Provide a thin wrapper over Flask session for histories."""

    @staticmethod
    def _get_histories() -> dict[str, Any]:
        raw = session.get(SESSION_KEY, {})
        if not isinstance(raw, dict):
            raw = {}
        return deepcopy(raw)

    @staticmethod
    def _clean_history(raw_history: Any) -> list[dict[str, Any]]:
        if not isinstance(raw_history, list):
            return []
        return [deepcopy(item) for item in raw_history if isinstance(item, dict)]

    @staticmethod
    def _record(raw_record: Any) -> tuple[dict[str, Any], bool]:
        """Normalize current and legacy values; return record and migration flag."""
        if isinstance(raw_record, list):
            return {
                "schema_version": SESSION_RECORD_VERSION,
                "history": SessionService._clean_history(raw_record),
                "checkpoint": None,
            }, True

        if isinstance(raw_record, Mapping):
            history = SessionService._clean_history(raw_record.get("history"))
            checkpoint = raw_record.get("checkpoint")
            if checkpoint is not None and not isinstance(checkpoint, Mapping):
                checkpoint = None
            normalized = {
                "schema_version": raw_record.get("schema_version"),
                "history": history,
                "checkpoint": deepcopy(checkpoint),
            }
            if normalized["schema_version"] == SESSION_RECORD_VERSION:
                return normalized, False

        return {
            "schema_version": SESSION_RECORD_VERSION,
            "history": [],
            "checkpoint": None,
        }, True

    @staticmethod
    def get_record(structure_id: str) -> dict[str, Any]:
        """Return a versioned record, migrating a legacy history in place.

        A legacy list is retained in full so the caller performs the same full
        replay used before checkpoints existed. No synthetic checkpoint is
        created before that replay succeeds.
        """
        histories = SessionService._get_histories()
        record, migrated = SessionService._record(histories.get(structure_id, []))
        if migrated and structure_id in histories:
            histories[structure_id] = deepcopy(record)
            session[SESSION_KEY] = histories
            session.modified = True
        return deepcopy(record)

    @staticmethod
    def get_history(structure_id: str) -> list[dict[str, Any]]:
        """Return a copy of persisted mutating operations."""
        return SessionService.get_record(structure_id)["history"]

    @staticmethod
    def get_checkpoint(structure_id: str) -> dict[str, Any] | None:
        """Return the untrusted checkpoint envelope stored for a structure."""
        checkpoint = SessionService.get_record(structure_id)["checkpoint"]
        return deepcopy(checkpoint) if isinstance(checkpoint, dict) else None

    @staticmethod
    def save_history(structure_id: str, history: list[dict[str, Any]]) -> None:
        """Persist history for one structure and invalidate its old checkpoint."""
        histories = SessionService._get_histories()
        cleaned_history = SessionService._clean_history(history)
        max_history = int(current_app.config.get("SESSION_MAX_HISTORY", 300))
        if max_history > 0:
            cleaned_history = cleaned_history[-max_history:]
        histories[structure_id] = {
            "schema_version": SESSION_RECORD_VERSION,
            "history": cleaned_history,
            "checkpoint": None,
        }
        session[SESSION_KEY] = histories
        session.modified = True

    @staticmethod
    def save_checkpoint(structure_id: str, checkpoint: dict[str, Any]) -> None:
        """Attach a checkpoint without altering its replay history."""
        histories = SessionService._get_histories()
        record, _ = SessionService._record(histories.get(structure_id, []))
        record["checkpoint"] = deepcopy(checkpoint)
        histories[structure_id] = record
        session[SESSION_KEY] = histories
        session.modified = True

    @staticmethod
    def clear_history(structure_id: str) -> None:
        """Delete history of one structure."""
        histories = SessionService._get_histories()
        histories.pop(structure_id, None)
        session[SESSION_KEY] = histories
        session.modified = True
