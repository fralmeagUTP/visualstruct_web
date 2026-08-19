"""Tests for versioned session checkpoint envelopes."""

from __future__ import annotations

from typing import Any

import pytest

from app.adapters.base_adapter import BaseAdapter
from app.services.checkpoints import (
    CheckpointChecksumError,
    CheckpointCompatibilityError,
    CheckpointFormatError,
    create_checkpoint,
    validate_checkpoint,
)


class _StateAdapter(BaseAdapter):
    STATE_VERSION = "stack-v1"

    def __init__(self) -> None:
        self.values = [2, 3]

    def create(self) -> None:
        self.values = []

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {}

    def to_visual_state(self) -> dict[str, Any]:
        return {"items": self.values}

    def reset(self) -> None:
        self.create()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return []

    def export_state(self) -> dict[str, Any]:
        return {"values": list(self.values)}

    def import_state(self, state: dict[str, Any]) -> None:
        self.values = list(state["values"])


def _checkpoint_dict() -> dict[str, Any]:
    return create_checkpoint(
        structure_id="stack", history_offset=50, adapter=_StateAdapter()
    ).to_dict()


def test_checkpoint_round_trip_has_stable_checksum_and_detached_state() -> None:
    first = _checkpoint_dict()
    second = _checkpoint_dict()
    assert first == second
    assert len(first["checksum"]) == 64

    validated = validate_checkpoint(
        first,
        expected_structure_id="stack",
        expected_adapter_version="stack-v1",
    )
    first["state"]["values"].append(99)
    assert validated.state == {"values": [2, 3]}
    assert validated.history_offset == 50


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("schema_version", 2, CheckpointCompatibilityError),
        ("structure_id", "queue", CheckpointCompatibilityError),
        ("adapter_version", "stack-v2", CheckpointCompatibilityError),
        ("history_offset", -1, CheckpointFormatError),
        ("checksum", "bad", CheckpointFormatError),
    ],
)
def test_checkpoint_rejects_incompatible_or_invalid_fields(
    field: str, value: Any, error: type[ValueError]
) -> None:
    checkpoint = _checkpoint_dict()
    checkpoint[field] = value
    with pytest.raises(error):
        validate_checkpoint(
            checkpoint,
            expected_structure_id="stack",
            expected_adapter_version="stack-v1",
        )


def test_checkpoint_rejects_tampering() -> None:
    checkpoint = _checkpoint_dict()
    checkpoint["state"]["values"].append(5)
    with pytest.raises(CheckpointChecksumError):
        validate_checkpoint(
            checkpoint,
            expected_structure_id="stack",
            expected_adapter_version="stack-v1",
        )


def test_checkpoint_rejects_missing_and_extra_fields() -> None:
    missing = _checkpoint_dict()
    missing.pop("state")
    with pytest.raises(CheckpointFormatError):
        validate_checkpoint(
            missing,
            expected_structure_id="stack",
            expected_adapter_version="stack-v1",
        )

    extra = _checkpoint_dict()
    extra["unsafe"] = "value"
    with pytest.raises(CheckpointFormatError):
        validate_checkpoint(
            extra,
            expected_structure_id="stack",
            expected_adapter_version="stack-v1",
        )


def test_checkpoint_creation_rejects_non_json_state() -> None:
    adapter = _StateAdapter()
    adapter.export_state = lambda: {"invalid": object()}  # type: ignore[method-assign]
    with pytest.raises(CheckpointFormatError):
        create_checkpoint(structure_id="stack", history_offset=0, adapter=adapter)
