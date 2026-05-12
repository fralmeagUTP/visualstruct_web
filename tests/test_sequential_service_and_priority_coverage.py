"""Targeted coverage tests for sequential service and priority adapter branches."""

from __future__ import annotations

import pytest

from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.domain.sequential import ElementoNoEncontradoError, PosicionInvalidaError, TADError
from app.services import structure_service as structure_service_module
from app.services.structure_service import StructureService


def test_structure_service_get_structure_raises_for_unknown() -> None:
    with pytest.raises(KeyError):
        StructureService.get_structure("unknown_structure")


def test_structure_service_rebuild_adapter_skips_invalid_history_entries() -> None:
    history = [
        {"operation": "apilar", "payload": {"value": "10"}},
        {"operation": 123, "payload": {}},
        {"operation": "apilar", "payload": "not_dict"},
        {"operation": "desapilar", "payload": {}},
        {"operation": "desapilar", "payload": {}},
        {"operation": "apilar", "payload": {"value": "20"}},
    ]

    adapter, valid = StructureService._rebuild_adapter("stack", history)
    assert [step["operation"] for step in valid] == ["apilar", "desapilar", "apilar"]
    assert adapter.to_visual_state()["items"] == [{"value": 20}]


def test_structure_service_didactic_error_branches() -> None:
    assert "inv" in StructureService._didactic_error(PosicionInvalidaError("x")).lower()
    assert StructureService._didactic_error(ElementoNoEncontradoError("no existe")) == "no existe"
    assert StructureService._didactic_error(TADError("error base")) == "error base"
    assert "inesperado" in StructureService._didactic_error(Exception("boom")).lower()


def test_structure_service_didactic_content_c_first_fallback(monkeypatch) -> None:
    monkeypatch.setattr(
        structure_service_module.CCodeService,
        "get_structure_data",
        staticmethod(lambda _structure_id: None),
    )

    data = StructureService._didactic_content("stack")
    assert data["code_title"] == "Codigo C"
    assert "no disponible" in data["default_operation"].lower()


def test_structure_service_didactic_content_pseudocode_fallback(monkeypatch) -> None:
    monkeypatch.setattr(
        structure_service_module.CCodeService,
        "get_structure_data",
        staticmethod(lambda _structure_id: None),
    )

    data = StructureService._didactic_content("binary_heap")
    assert "record" in data
    assert "operations" in data
    assert "code_title" not in data


def test_structure_service_execute_operation_unsupported_branch() -> None:
    result = StructureService.execute_operation(
        structure_id="stack",
        operation_name="operacion_que_no_existe",
        payload={},
        history=[],
    )
    assert result["success"] is False
    assert "no est" in result["message"].lower()


def test_priority_queue_adapter_execute_extra_branches_and_reset() -> None:
    adapter = PriorityQueueAdapter()
    adapter.execute("encolar", {"value": "10", "priority": "1"})

    # Force "frente" branch where priority metadata is unavailable.
    adapter._peek_highest_priority_value = lambda _expected_value: None  # type: ignore[method-assign]
    front = adapter.execute("frente", {})
    assert front["result"] == 10
    assert "prioridad" not in front["message"].lower()

    clear = adapter.execute("limpiar", {})
    assert "limpi" in clear["message"].lower()
    assert adapter.to_visual_state()["empty"] is True

    adapter.execute("encolar", {"value": "99", "priority": "9"})
    adapter.reset()
    assert adapter.to_visual_state()["size"] == 0

    with pytest.raises(ValueError):
        adapter.execute("operacion_no_valida", {})


def test_priority_queue_adapter_private_fallback_paths() -> None:
    adapter = PriorityQueueAdapter()

    # _remove_highest_priority_ordered_item: empty list and forced invalid index
    assert adapter._remove_highest_priority_ordered_item(1) is None
    adapter._ordered_items = [{"value": 5, "priority": 2, "order": 0}]
    adapter._find_out_index = lambda _items: -1  # type: ignore[method-assign]
    assert adapter._remove_highest_priority_ordered_item(5) is None

    # Restore helper and cover fallback-by-value branch and fallback-pop branch.
    adapter._find_out_index = PriorityQueueAdapter._find_out_index  # type: ignore[method-assign]
    adapter._ordered_items = [
        {"value": 10, "priority": 1, "order": 0},
        {"value": 20, "priority": 2, "order": 1},
    ]
    assert adapter._remove_highest_priority_ordered_item(20) == 2
    adapter._ordered_items = [{"value": 30, "priority": 1, "order": 0}]
    assert adapter._remove_highest_priority_ordered_item(999) == 1

    # _peek_highest_priority_value: empty, forced invalid index, mismatch and hit.
    adapter._ordered_items = []
    assert adapter._peek_highest_priority_value(1) is None

    adapter._ordered_items = [{"value": 40, "priority": 4, "order": 0}]
    adapter._find_out_index = lambda _items: -1  # type: ignore[method-assign]
    assert adapter._peek_highest_priority_value(40) is None

    adapter._find_out_index = PriorityQueueAdapter._find_out_index  # type: ignore[method-assign]
    assert adapter._peek_highest_priority_value(999) is None
    assert adapter._peek_highest_priority_value(40) == 4
