"""Safe checkpoint restoration with deterministic full-replay fallback."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable, Mapping

from app.adapters.base_adapter import AdapterStateError, BaseAdapter
from app.services.checkpoints import (
    CheckpointChecksumError,
    CheckpointCompatibilityError,
    CheckpointError,
    CheckpointFormatError,
    validate_checkpoint,
)
from app.services.observability import emit_operational_event


AdapterFactory = Callable[[], BaseAdapter]


@dataclass(frozen=True, slots=True)
class ReconstructionPlan:
    """Trusted starting point from which history replay can continue."""

    adapter: BaseAdapter
    history_offset: int
    checkpoint_used: bool
    fallback_reason: str | None = None


def _fallback_reason(error: Exception) -> str:
    if isinstance(error, CheckpointChecksumError):
        return "checksum"
    if isinstance(error, CheckpointCompatibilityError):
        return "compatibility"
    if isinstance(error, CheckpointFormatError):
        return "format"
    return "import"


def prepare_reconstruction(
    *,
    adapter_factory: AdapterFactory,
    structure_id: str,
    history_length: int,
    raw_checkpoint: Mapping[str, Any] | None,
) -> ReconstructionPlan:
    """Import a compatible checkpoint or return a fresh full-replay plan.

    The candidate adapter is never returned after a failed import. This keeps
    fallback atomic even when a faulty adapter mutates itself before raising.
    """
    started = perf_counter()
    if type(history_length) is not int or history_length < 0:
        raise ValueError("history_length debe ser un entero no negativo.")

    def finish(plan: ReconstructionPlan) -> ReconstructionPlan:
        emit_operational_event(
            "state_reconstruction",
            outcome="success",
            duration_ms=(perf_counter() - started) * 1000,
            structure_id=structure_id,
            history_operations=history_length,
            replay_operations=history_length - plan.history_offset,
            checkpoint_used=plan.checkpoint_used,
            checkpoint_fallback=plan.fallback_reason is not None,
            fallback_reason=plan.fallback_reason,
        )
        return plan

    if raw_checkpoint is None:
        return finish(ReconstructionPlan(
            adapter=adapter_factory(),
            history_offset=0,
            checkpoint_used=False,
        ))

    candidate = adapter_factory()
    try:
        checkpoint = validate_checkpoint(
            raw_checkpoint,
            expected_structure_id=structure_id,
            expected_adapter_version=candidate.adapter_version(),
        )
        if checkpoint.history_offset > history_length:
            raise CheckpointFormatError(
                "La posicion del checkpoint excede el historial disponible."
            )
        candidate.import_state(checkpoint.state)
    except (CheckpointError, AdapterStateError, TypeError, NotImplementedError) as error:
        return finish(ReconstructionPlan(
            adapter=adapter_factory(),
            history_offset=0,
            checkpoint_used=False,
            fallback_reason=_fallback_reason(error),
        ))

    return finish(ReconstructionPlan(
        adapter=candidate,
        history_offset=checkpoint.history_offset,
        checkpoint_used=True,
    ))
