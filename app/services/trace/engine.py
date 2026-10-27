"""Validation engine for semantic and legacy execution traces."""

from __future__ import annotations

from time import perf_counter
import copy as _copy_module
from copy import deepcopy
from typing import Any

from app.services.observability import emit_operational_event
from app.services.trace.compatibility import LegacyTraceAdapter
from app.services.trace.models import TraceStep
from app.services.trace.strategies import LegacyTraceStrategy, SortingTraceStrategy, TraceStrategyRegistry


_SORTING_NORMALIZER = LegacyTraceStrategy.normalize_steps
_SORTING_RESOLVER = TraceStrategyRegistry.resolve.__func__

_SORTING_PROJECTOR = LegacyTraceAdapter.to_public
_SORTING_PROJECTOR_CODE = _SORTING_PROJECTOR.__code__
_SORTING_CONVERTER = TraceStep.from_legacy.__func__
_SORTING_CONVERTER_CODE = _SORTING_CONVERTER.__code__
_SORTING_MODEL_INIT = TraceStep.__init__
_SORTING_MODEL_POST_INIT = TraceStep.__post_init__
_SORTING_MODEL_INIT_CODE = TraceStep.__init__.__code__
_SORTING_MODEL_POST_INIT_CODE = TraceStep.__post_init__.__code__
_SORTING_DEEPCOPY = deepcopy
_SORTING_DEEPCOPY_CODE = deepcopy.__code__
_SORTING_DEEPCOPY_DEFAULTS = deepcopy.__defaults__
_SORTING_KEEP_ALIVE = _copy_module._keep_alive
_SORTING_KEEP_ALIVE_CODE = _SORTING_KEEP_ALIVE.__code__
_SORTING_KEEP_ALIVE_DEFAULTS = _SORTING_KEEP_ALIVE.__defaults__
_SORTING_COPY_DISPATCH = {
    value_type: (_copy_module._deepcopy_dispatch.get(value_type), _copy_module._deepcopy_dispatch.get(value_type).__code__, _copy_module._deepcopy_dispatch.get(value_type).__defaults__)
    for value_type in (dict, list, str, int, float, bool, type(None))
}


def _identity_projection_available() -> bool:
    """Only elide a known identity copy, retaining the current projection fallback."""
    projector = LegacyTraceAdapter.to_public
    converter = getattr(TraceStep.from_legacy, "__func__", None)
    defaults = getattr(projector, "__kwdefaults__", None)
    return (
        projector is _SORTING_PROJECTOR
        and projector.__code__ is _SORTING_PROJECTOR_CODE
        and type(defaults) is dict
        and defaults.get("copy_value") is _SORTING_DEEPCOPY
        and converter is _SORTING_CONVERTER
        and converter.__code__ is _SORTING_CONVERTER_CODE
        and TraceStep.__init__ is _SORTING_MODEL_INIT
        and TraceStep.__post_init__ is _SORTING_MODEL_POST_INIT
        and TraceStep.__init__.__code__ is _SORTING_MODEL_INIT_CODE
        and TraceStep.__post_init__.__code__ is _SORTING_MODEL_POST_INIT_CODE
        and _plain_json is _SORTING_PLAIN_JSON
        and _plain_json.__code__ is _SORTING_PLAIN_JSON_CODE
        and _borrow is _SORTING_BORROW
        and _borrow.__code__ is _SORTING_BORROW_CODE
        and _copy_module.deepcopy is _SORTING_DEEPCOPY
        and _SORTING_DEEPCOPY.__code__ is _SORTING_DEEPCOPY_CODE
        and _SORTING_DEEPCOPY.__defaults__ is _SORTING_DEEPCOPY_DEFAULTS
        and _copy_module._keep_alive is _SORTING_KEEP_ALIVE
        and _SORTING_KEEP_ALIVE.__code__ is _SORTING_KEEP_ALIVE_CODE
        and _SORTING_KEEP_ALIVE.__defaults__ is _SORTING_KEEP_ALIVE_DEFAULTS
        and all(_copy_module._deepcopy_dispatch.get(key) is value and value.__code__ is code and value.__defaults__ is defaults for key, (value, code, defaults) in _SORTING_COPY_DISPATCH.items())
    )



def _plain_json(value: Any, active: set[int] | None = None, depth: int = 0) -> bool:
    """Restrict borrowing to built-in JSON data; preserve legacy handling otherwise."""
    if type(value) in (str, int, float, bool, type(None)):
        return True
    if type(value) not in (dict, list) or depth > 80:
        return False
    if type(value) is dict and any(type(key) is not str for key in value):
        return False
    active = set() if active is None else active
    identity = id(value)
    if identity in active:
        return False
    active.add(identity)
    values = value.values() if type(value) is dict else value
    try:
        return all(_plain_json(item, active, depth + 1) for item in values)
    finally:
        active.remove(identity)


_SORTING_PLAIN_JSON = _plain_json
_SORTING_PLAIN_JSON_CODE = _plain_json.__code__


def _borrow(value: Any) -> Any:
    return value


_SORTING_BORROW = _borrow
_SORTING_BORROW_CODE = _borrow.__code__


class _ReadonlySortingSteps:
    """Borrow one already checked native-JSON step at a time for invariant checks."""

    def __init__(self, raw_steps: list[dict[str, Any]]) -> None:
        self.raw_steps = raw_steps

    def __len__(self) -> int:
        return len(self.raw_steps)

    def __getitem__(self, index: int) -> TraceStep:
        return TraceStep.from_legacy(self.raw_steps[index], copy_value=_borrow)


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
    def validate_legacy_trace(cls, trace: dict[str, Any], *, copy_value=deepcopy) -> list[TraceStep]:
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
            if LegacyTraceAdapter.round_trip(raw_steps, copy_value=copy_value) != raw_steps:
                raise TraceContractError("La adaptación de compatibilidad modificó el esquema público.")
            steps = strategy.normalize_steps(raw_steps, copy_value=copy_value) if strategy.family == "graph" else strategy.normalize_steps(raw_steps)
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

    @classmethod
    def validate_legacy_trace_readonly(cls, trace: dict[str, Any]) -> None:
        """Validate generated Sorting JSON incrementally when no copied result is needed.

        The normal API still returns independent copied semantic steps. Special
        types or a replaced family normalizer use that original API unchanged.
        """
        started = perf_counter()
        if type(trace) is not dict or getattr(TraceStrategyRegistry.resolve, "__func__", None) is not _SORTING_RESOLVER:
            cls.validate_legacy_trace(trace)
            return
        structure_id = trace.get("structure_id")
        raw_steps = trace.get("steps")
        try:
            strategy = TraceStrategyRegistry.resolve(structure_id) if type(structure_id) is str else None
        except KeyError:
            strategy = None
        eligible = (
            type(strategy) is SortingTraceStrategy
            and strategy.family == "sorting"
            and getattr(strategy.normalize_steps, "__func__", None) is _SORTING_NORMALIZER
            and type(raw_steps) is list
            and all(_plain_json(step) for step in raw_steps)
            and _plain_json(trace.get("final_state"))
            and _plain_json(trace.get("source_code"))
        )
        if not eligible:
            cls.validate_legacy_trace(trace)
            return
        try:
            # All semantic conversion errors precede round-trip comparison,
            # exactly as in to_semantic's eager list conversion.
            for raw in raw_steps:
                TraceStep.from_legacy(raw, copy_value=_borrow)
            # For exact native JSON, the original converter borrows raw as
            # metadata["legacy_step"] and the original projector only deep-copies
            # it. Its value equals raw (including shared aliases and NaN identity).
            # All semantic errors have already been checked in the eager order.
            # Replaced converters/projectors/copiers keep the existing full loop.
            if not _identity_projection_available():
                changed = False
                for index, raw in enumerate(raw_steps):
                    semantic = TraceStep.from_legacy(raw, copy_value=_borrow)
                    projected = LegacyTraceAdapter.to_public(semantic, step_index=index)
                    if not changed and projected != raw:
                        changed = True
                    del projected, semantic
                if changed:
                    raise TraceContractError("La adaptación de compatibilidad modificó el esquema público.")
            # Reuse the complete existing final/continuity/source validator and
            # its error order; the view retains no per-trace semantic list.
            cls.validate_steps(_ReadonlySortingSteps(raw_steps), trace.get("final_state"), str(trace.get("source_code") or ""))
        except (KeyError, TypeError, ValueError) as error:
            emit_operational_event(
                "trace_validation",
                outcome="error",
                duration_ms=(perf_counter() - started) * 1000,
                structure_id=structure_id,
                strategy=strategy.family,
                step_count=len(raw_steps),
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
            strategy=strategy.family,
            step_count=len(raw_steps),
        )
