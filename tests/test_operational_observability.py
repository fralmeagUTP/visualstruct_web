"""Structured logging and metric tests without sensitive user data."""

from __future__ import annotations

import json
import logging
from typing import Any

from app.adapters.base_adapter import BaseAdapter
from app.services.checkpoint_reconstruction import prepare_reconstruction
from app.services.observability import operational_metrics
from app.services.structure_service import StructureService
from app.services.trace import TraceEngine


class _Adapter(BaseAdapter):
    def create(self) -> None:
        return None

    def execute(self, operation_name: str, payload: dict[str, Any]) -> dict[str, Any]:
        return {}

    def to_visual_state(self) -> dict[str, Any]:
        return {}

    def reset(self) -> None:
        return None

    def get_supported_operations(self) -> list[dict[str, Any]]:
        return []


def _events(caplog) -> list[dict[str, Any]]:
    return [
        json.loads(record.message)
        for record in caplog.records
        if record.name == "visualstruct.operations"
    ]


def test_trace_validation_emits_strategy_step_count_and_metrics(caplog) -> None:
    operational_metrics.reset()
    trace = {
        "structure_id": "stack",
        "steps": [
            {
                "step": 1,
                "line_index": 0,
                "action": "safe action",
                "state_snapshot": {},
                "state_after": {"items": [1]},
            }
        ],
        "final_state": {"items": [1]},
    }
    with caplog.at_level(logging.INFO, logger="visualstruct.operations"):
        TraceEngine.validate_legacy_trace(trace)

    event = _events(caplog)[-1]
    assert event["event"] == "trace_validation"
    assert event["outcome"] == "success"
    assert event["strategy"] == "sequential"
    assert event["step_count"] == 1
    assert "state_snapshot" not in caplog.text
    snapshot = operational_metrics.snapshot()
    assert snapshot["counters"]["trace_validation.success"] == 1


def test_reconstruction_fallback_log_omits_checkpoint_and_history(caplog) -> None:
    operational_metrics.reset()
    secret = "cookie-secret-must-not-appear"
    corrupted = {"state": {"cookie": secret}, "checksum": "bad"}
    with caplog.at_level(logging.INFO, logger="visualstruct.operations"):
        plan = prepare_reconstruction(
            adapter_factory=_Adapter,
            structure_id="stack",
            history_length=300,
            raw_checkpoint=corrupted,
        )

    assert plan.fallback_reason == "format"
    event = _events(caplog)[-1]
    assert event["event"] == "state_reconstruction"
    assert event["checkpoint_fallback"] is True
    assert event["checkpoint_used"] is False
    assert event["fallback_reason"] == "format"
    assert event["replay_operations"] == 300
    assert secret not in caplog.text
    assert "cookie" not in caplog.text
    snapshot = operational_metrics.snapshot()
    assert snapshot["counters"]["state_reconstruction.success"] == 1
    assert snapshot["durations"]["state_reconstruction"]["count"] == 1


def test_real_replay_boundary_logs_counts_without_operation_payload(caplog) -> None:
    operational_metrics.reset()
    secret = "value-that-must-not-be-logged"
    history = [{"operation": "apilar", "payload": {"value": secret}}]
    with caplog.at_level(logging.INFO, logger="visualstruct.operations"):
        _, valid_history = StructureService._rebuild_adapter("stack", history)

    assert len(valid_history) == 0  # invalid integer input is omitted by replay
    event = _events(caplog)[-1]
    assert event["event"] == "history_replay"
    assert event["replay_operations"] == 1
    assert event["valid_operations"] == 0
    assert secret not in caplog.text
    assert "payload" not in caplog.text
