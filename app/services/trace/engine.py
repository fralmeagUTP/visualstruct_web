"""Validation engine for semantic and legacy execution traces."""

from __future__ import annotations

from time import perf_counter
from typing import Any

from app.services.observability import emit_operational_event
from app.services.trace.compatibility import LegacyTraceAdapter
from app.services.trace.models import TraceStep
from app.services.trace.strategies import TraceStrategyRegistry


class TraceContractError(ValueError):
    """Raised when a generated trace violates the stable trace contract."""


class TraceEngine:
    """Validate trace invariants while the legacy generator is migrated."""

    @staticmethod
    def validate_steps(
        steps: list[TraceStep], final_state: dict[str, Any], source_code: str = ""
    ) -> None:
        if not steps:
            raise TraceContractError("La traza debe contener al menos un paso.")
        if not isinstance(final_state, dict):
            raise TraceContractError("final_state debe ser un diccionario.")
        if steps[-1].after_state != final_state:
            raise TraceContractError("El estado posterior del último paso no coincide con final_state.")

        for index in range(len(steps) - 1):
            following = steps[index + 1]
            if steps[index].after_state != following.before_state and following.event != "rebase":
                raise TraceContractError(
                    f"Discontinuidad entre los pasos {index} y {index + 1}; se requiere rebase explícito."
                )
        if source_code:
            source_lines = source_code.replace("\r\n", "\n").split("\n")
            for index, step in enumerate(steps):
                if step.line_index is None:
                    continue
                if step.line_index >= len(source_lines):
                    raise TraceContractError(f"line_index fuera de rango en el paso {index}.")
                expected = " ".join(source_lines[step.line_index].strip().split())
                observed = " ".join(step.line_text.strip().split())
                if expected != observed:
                    raise TraceContractError(f"line_text no coincide con source_code en el paso {index}.")

    @classmethod
    def validate_legacy_trace(cls, trace: dict[str, Any]) -> list[TraceStep]:
        """Validate a current public trace without mutating its JSON representation."""
        started = perf_counter()
        structure_id = trace.get("structure_id") if isinstance(trace, dict) else None
        raw_steps = trace.get("steps") if isinstance(trace, dict) else None
        strategy_name = "unknown"
        try:
            if not isinstance(trace, dict):
                raise TraceContractError("La traza debe ser un diccionario.")
            final_state = trace.get("final_state")
            if not isinstance(structure_id, str):
                raise TraceContractError("structure_id debe ser texto.")
            if not isinstance(raw_steps, list):
                raise TraceContractError("steps debe ser una lista.")
            strategy = TraceStrategyRegistry.resolve(structure_id)
            strategy_name = strategy.family
            if LegacyTraceAdapter.round_trip(raw_steps) != raw_steps:
                raise TraceContractError("La adaptación de compatibilidad modificó el esquema público.")
            steps = strategy.normalize_steps(raw_steps)
            cls.validate_steps(steps, final_state, str(trace.get("source_code") or ""))
        except (KeyError, TypeError, ValueError) as error:
            emit_operational_event(
                "trace_validation",
                outcome="error",
                duration_ms=(perf_counter() - started) * 1000,
                structure_id=structure_id if isinstance(structure_id, str) else "unknown",
                strategy=strategy_name,
                step_count=len(raw_steps) if isinstance(raw_steps, list) else 0,
                error_type=type(error).__name__,
            )
            if isinstance(error, TraceContractError):
                raise
            raise TraceContractError(str(error)) from error
        emit_operational_event(
            "trace_validation",
            outcome="success",
            duration_ms=(perf_counter() - started) * 1000,
            structure_id=structure_id,
            strategy=strategy_name,
            step_count=len(steps),
        )
        return steps
