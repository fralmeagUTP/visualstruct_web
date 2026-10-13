"""Help identifier contract for all five modules."""
from __future__ import annotations
import pytest
from app.services.c_code_service import CCodeService

REGISTERED = [("sequential", n) for n in ["stack", "queue", "priority_queue", "linked_list", "circular_list", "sublist"]] + [("hierarchical", n) for n in ["abb", "avl", "red_black", "binary_heap"]] + [("graph", "graph"), ("hash", "hash_table"), ("sorting", "sorting_array")]

@pytest.mark.parametrize("module,structure", REGISTERED)
def test_registered_help_remains_available(client, module: str, structure: str) -> None:
    assert client.get(f"/help/{module}/{structure}").status_code == 200

@pytest.mark.parametrize("module", ["sequential", "hierarchical", "graph", "hash", "sorting"])
def test_unknown_and_wrong_module_help_return_404(client, module: str) -> None:
    assert client.get(f"/help/{module}/unknown").status_code == 404
    wrong = "stack" if module != "sequential" else "graph"
    assert client.get(f"/help/{module}/{wrong}").status_code == 404

@pytest.mark.parametrize("module,structure", REGISTERED)
def test_registered_help_without_c_keeps_placeholder(client, monkeypatch, module: str, structure: str) -> None:
    monkeypatch.setattr(CCodeService, "get_structure_data", staticmethod(lambda _structure: None))
    response = client.get(f"/help/{module}/{structure}")
    assert response.status_code == 200
    assert b"No hay estructura C documentada" in response.data
