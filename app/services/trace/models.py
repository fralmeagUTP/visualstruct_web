"""Stable semantic model for one execution-trace step."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class TraceStep:
    """Immutable trace step independent from frontend presentation details."""

    line_index: int | None
    line_text: str
    event: str
    stage: str
    before_state: dict[str, Any]
    after_state: dict[str, Any]
    console: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.line_index is not None and (not isinstance(self.line_index, int) or self.line_index < 0):
            raise ValueError("line_index debe ser un entero no negativo o None.")
        for name, value in (("line_text", self.line_text), ("event", self.event), ("stage", self.stage)):
            if not isinstance(value, str):
                raise TypeError(f"{name} debe ser texto.")
        if not self.event.strip():
            raise ValueError("event no puede estar vacío.")
        if not self.stage.strip():
            raise ValueError("stage no puede estar vacío.")
        if not isinstance(self.before_state, dict) or not isinstance(self.after_state, dict):
            raise TypeError("before_state y after_state deben ser diccionarios.")
        if not isinstance(self.console, tuple) or not all(isinstance(item, str) for item in self.console):
            raise TypeError("console debe ser una tupla de textos.")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata debe ser un diccionario.")

    @classmethod
    def from_legacy(cls, step: dict[str, Any]) -> "TraceStep":
        """Convert the current public step shape into the semantic contract."""
        if not isinstance(step, dict):
            raise TypeError("Cada paso legado debe ser un diccionario.")
        debug = step.get("debug")
        debug_data = debug if isinstance(debug, dict) else {}
        console_raw = step.get("console", ())
        if isinstance(console_raw, list):
            console = tuple(str(item) for item in console_raw)
        elif isinstance(console_raw, tuple):
            console = tuple(str(item) for item in console_raw)
        else:
            console = ()
        metadata = {
            "step_index": step.get("step_index"),
            "delay_ms": step.get("delay_ms"),
            "debug": deepcopy(debug_data),
            "legacy_step": deepcopy(step),
        }
        return cls(
            line_index=step.get("line_index"),
            line_text=step.get("line_text", ""),
            event=str(step.get("event_type") or "line"),
            stage=str(debug_data.get("stage") or step.get("phase") or "progress"),
            before_state=deepcopy(step.get("state_snapshot")),
            after_state=deepcopy(step.get("state_after")),
            console=console,
            metadata=metadata,
        )
