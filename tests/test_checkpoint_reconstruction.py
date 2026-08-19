"""Failure-mode tests for safe checkpoint reconstruction fallback."""

from __future__ import annotations

from typing import Any

import pytest

from app.adapters.base_adapter import AdapterStateError, BaseAdapter
from app.services.checkpoint_reconstruction import prepare_reconstruction
from app.services.checkpoints import create_checkpoint


class _RestorableAdapter(BaseAdapter):
    STATE_VERSION = "stack-v1"

    def __init__(self) -> None:
        self.values: list[int] = []

    def create(self) -> None:
        self.values = []

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {}

    def to_visual_state(self) -> dict[str, Any]:
        return {"items": list(self.values)}

    def reset(self) -> None:
        self.create()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return []

    def export_state(self) -> dict[str, Any]:
        return {"values": list(self.values)}

    def import_state(self, state: dict[str, Any]) -> None:
        values = state.get("values")
        if not isinstance(values, list) or any(type(value) is not int for value in values):
            raise AdapterStateError("invalid values")
        self.values = list(values)


def _valid_checkpoint(offset: int = 2) -> dict[str, Any]:
    adapter = _RestorableAdapter()
    adapter.values = [10, 20]
    return create_checkpoint(
        structure_id="stack", history_offset=offset, adapter=adapter
    ).to_dict()


def test_valid_checkpoint_imports_state_and_skips_prior_history() -> None:
    plan = prepare_reconstruction(
        adapter_factory=_RestorableAdapter,
        structure_id="stack",
        history_length=3,
        raw_checkpoint=_valid_checkpoint(),
    )
    assert plan.checkpoint_used is True
    assert plan.history_offset == 2
    assert plan.fallback_reason is None
    assert plan.adapter.export_state() == {"values": [10, 20]}


@pytest.mark.parametrize(
    ("mutation", "reason"),
    [
        (lambda value: value["state"]["values"].append(99), "checksum"),
        (lambda value: value.__setitem__("schema_version", 99), "compatibility"),
        (lambda value: value.pop("state"), "format"),
        (lambda value: value.__setitem__("checksum", "short"), "format"),
    ],
)
def test_invalid_checkpoint_falls_back_to_fresh_full_replay(mutation, reason: str) -> None:
    checkpoint = _valid_checkpoint()
    mutation(checkpoint)
    plan = prepare_reconstruction(
        adapter_factory=_RestorableAdapter,
        structure_id="stack",
        history_length=3,
        raw_checkpoint=checkpoint,
    )
    assert plan.checkpoint_used is False
    assert plan.history_offset == 0
    assert plan.fallback_reason == reason
    assert plan.adapter.export_state() == {"values": []}


def test_checkpoint_beyond_truncated_history_falls_back_safely() -> None:
    plan = prepare_reconstruction(
        adapter_factory=_RestorableAdapter,
        structure_id="stack",
        history_length=1,
        raw_checkpoint=_valid_checkpoint(offset=2),
    )
    assert plan.checkpoint_used is False
    assert plan.history_offset == 0
    assert plan.fallback_reason == "format"


def test_partial_import_failure_discards_mutated_candidate() -> None:
    created: list[_RestorableAdapter] = []

    class _FailingImportAdapter(_RestorableAdapter):
        def import_state(self, state: dict[str, Any]) -> None:
            self.values.append(999)
            raise AdapterStateError("simulated partial import")

    def factory() -> _RestorableAdapter:
        adapter = _FailingImportAdapter()
        created.append(adapter)
        return adapter

    plan = prepare_reconstruction(
        adapter_factory=factory,
        structure_id="stack",
        history_length=2,
        raw_checkpoint=_valid_checkpoint(),
    )
    assert len(created) == 2
    assert created[0].values == [999]
    assert plan.adapter is created[1]
    assert plan.adapter.export_state() == {"values": []}
    assert plan.fallback_reason == "import"


def test_no_checkpoint_uses_full_replay_without_fallback_error() -> None:
    plan = prepare_reconstruction(
        adapter_factory=_RestorableAdapter,
        structure_id="stack",
        history_length=5,
        raw_checkpoint=None,
    )
    assert plan.history_offset == 0
    assert plan.checkpoint_used is False
    assert plan.fallback_reason is None
