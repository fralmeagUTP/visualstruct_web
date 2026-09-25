"""Closure matrix for sequential pedagogy phases 7-9."""
from __future__ import annotations

from pathlib import Path
import pytest

from app.services.structure_service import StructureService

SEQUENTIAL_IDS = tuple(StructureService._REGISTRY)


@pytest.mark.parametrize("structure_id", SEQUENTIAL_IDS)
def test_every_operation_returns_a_three_level_canonical_trace(client, structure_id: str) -> None:
    model = StructureService.get_view_model(structure_id, [])
    for operation in model["operations"]:
        client.post(f"/sequential/{structure_id}/reset")
        payload = {field["name"]: "1" for field in operation.get("inputs", [])}
        response = client.post(f"/sequential/{structure_id}/operate", json={"operation": operation["name"], "payload": payload})
        assert response.status_code in {200, 400}
        data = response.get_json(); trace = data["execution_trace"]
        assert trace["steps"]
        assert trace["final_state"] == data["visual_state"]
        for step in trace["steps"]:
            frame = step["pedagogy"]
            assert set(frame["narration"]) == {"basic", "intermediate", "advanced"}
            assert frame["source"]["line_text"] == step["line_text"]
            assert frame["heap_transition"]["dangling_references"] == []
        for previous, current in zip(trace["steps"], trace["steps"][1:]):
            assert previous["state_after"] == current["state_snapshot"]


@pytest.mark.parametrize("structure_id,operation,payload", [
    ("stack", "apilar", {"value": 9}), ("queue", "encolar", {"value": 9}),
    ("priority_queue", "encolar", {"value": 9, "priority": 2}),
    ("linked_list", "insertar_inicio", {"value": 9}),
    ("circular_list", "insertar_inicio", {"value": 9}),
    ("sublist", "insertar_padre", {"parent": 9}),
])
def test_fast_result_equals_last_interpreted_state(client, structure_id, operation, payload) -> None:
    client.post(f"/sequential/{structure_id}/reset")
    data = client.post(f"/sequential/{structure_id}/operate", json={"operation": operation, "payload": payload}).get_json()
    assert data["execution_trace"]["steps"][-1]["state_after"] == data["visual_state"]


def test_comparison_accessibility_help_and_teacher_assets_are_present(client) -> None:
    html = client.get("/sequential/stack").get_data(as_text=True)
    for element_id in ("seq-compare-kind", "seq-compare-run", "seq-compare-progress", "seq-export-image", "seq-export-summary"):
        assert f'id="{element_id}"' in html
    help_html = client.get("/help/sequential/stack").get_data(as_text=True)
    for heading in ("Objetivo", "Estrategia", "Invariante", "Memoria dinámica", "Errores frecuentes", "Glosario contextual"):
        assert heading in help_html
    root = Path(__file__).parents[1]
    assert (root / "docs/qa/sequential-teacher-guide.md").is_file()
    assert (root / "docs/qa/sequential-pedagogy-closure-report.md").is_file()
