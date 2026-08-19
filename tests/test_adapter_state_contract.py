"""Contract tests for checkpoint-capable adapters."""

from __future__ import annotations

import json
from typing import Any

import pytest

from app.adapters.base_adapter import BaseAdapter


class _ContractAdapter(BaseAdapter):
    def __init__(self) -> None:
        self.values: list[int] = []

    def create(self) -> None:
        self.values = []

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.values.append(int(payload["value"]))
        return {"result": None}

    def to_visual_state(self) -> dict[str, Any]:
        return {"items": list(self.values)}

    def reset(self) -> None:
        self.create()

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return []

    def export_state(self) -> dict[str, Any]:
        return {"values": list(self.values)}

    def import_state(self, state: dict[str, Any]) -> None:
        candidate = state.get("values")
        if not isinstance(candidate, list) or any(type(value) is not int for value in candidate):
            raise ValueError("invalid state")
        self.values = list(candidate)


def test_state_contract_round_trip_is_json_compatible() -> None:
    source = _ContractAdapter()
    source.values = [3, 1, 4]

    serialized = json.loads(json.dumps(source.export_state()))
    restored = _ContractAdapter()
    restored.import_state(serialized)

    assert restored.export_state() == source.export_state()
    assert restored.to_visual_state() == source.to_visual_state()
    assert restored.adapter_version() == "1"


def test_default_contract_requires_explicit_adapter_implementation() -> None:
    class _IncompleteAdapter(_ContractAdapter):
        export_state = BaseAdapter.export_state
        import_state = BaseAdapter.import_state

    adapter = _IncompleteAdapter()
    with pytest.raises(NotImplementedError):
        adapter.export_state()
    with pytest.raises(NotImplementedError):
        adapter.import_state({})
