"""Configuration policy for periodic session checkpoints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class CheckpointPolicy:
    """Validated checkpoint scheduling configuration."""

    enabled: bool = False
    interval: int = 50
    max_per_structure: int = 1

    @classmethod
    def from_config(cls, config: Mapping[str, Any]) -> "CheckpointPolicy":
        """Build a policy from Flask-compatible configuration values."""
        enabled = config.get("ENABLE_CHECKPOINTS", False)
        interval = config.get("CHECKPOINT_INTERVAL", 50)
        max_per_structure = config.get("CHECKPOINT_MAX_PER_STRUCTURE", 1)

        if type(enabled) is not bool:
            raise ValueError("ENABLE_CHECKPOINTS debe ser un valor booleano.")
        if type(interval) is not int or interval <= 0:
            raise ValueError("CHECKPOINT_INTERVAL debe ser un entero mayor que cero.")
        if type(max_per_structure) is not int or max_per_structure <= 0:
            raise ValueError(
                "CHECKPOINT_MAX_PER_STRUCTURE debe ser un entero mayor que cero."
            )
        return cls(
            enabled=enabled,
            interval=interval,
            max_per_structure=max_per_structure,
        )

    def should_create(self, *, history_offset: int, operation_mutates: bool) -> bool:
        """Return whether a confirmed operation reaches a checkpoint boundary."""
        if type(history_offset) is not int or history_offset < 0:
            raise ValueError("history_offset debe ser un entero no negativo.")
        return (
            self.enabled
            and operation_mutates
            and history_offset > 0
            and history_offset % self.interval == 0
        )
