"""Compatibility boundary between semantic trace steps and public legacy JSON."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.trace.models import TraceStep


class LegacyTraceAdapter:
    """Convert trace steps without losing frontend-specific extension fields."""

    @staticmethod
    def to_semantic(raw_steps: list[dict[str, Any]]) -> list[TraceStep]:
        if not isinstance(raw_steps, list):
            raise TypeError("raw_steps debe ser una lista.")
        return [TraceStep.from_legacy(step) for step in raw_steps]

    @staticmethod
    def to_public(step: TraceStep, *, step_index: int | None = None) -> dict[str, Any]:
        """Return the exact original step when it came from the legacy boundary."""
        original = step.metadata.get("legacy_step")
        if isinstance(original, dict):
            return deepcopy(original)

        index = step_index if step_index is not None else step.metadata.get("step_index", 0)
        public: dict[str, Any] = {
            "step_index": int(index or 0),
            "line_index": step.line_index,
            "line_text": step.line_text,
            "event_type": step.event,
            "phase": step.stage,
            "delay_ms": int(step.metadata.get("delay_ms") or 170),
            "state_snapshot": deepcopy(step.before_state),
            "state_after": deepcopy(step.after_state),
        }
        debug = step.metadata.get("debug")
        if isinstance(debug, dict) and debug:
            public["debug"] = deepcopy(debug)
        if step.console:
            public["console"] = list(step.console)
        return public

    @classmethod
    def round_trip(cls, raw_steps: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Normalize and project steps back to their public representation."""
        return [cls.to_public(step, step_index=index) for index, step in enumerate(cls.to_semantic(raw_steps))]

