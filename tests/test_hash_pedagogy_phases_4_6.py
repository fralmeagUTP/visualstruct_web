"""Acceptance coverage for hash pedagogy phases 4 through 6."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from app.adapters.hash_table_adapter import HashTableAdapter
from app.domain.hash.pedagogy import INT_MAX, INT_MIN, build_hash_frame, c_remainder


def _state(capacity: int, entries: list[tuple[int, int]]) -> dict:
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": capacity})
    for key, value in entries:
        adapter.execute("insert", {"key": key, "value": value})
    return adapter.to_visual_state()


@pytest.mark.parametrize("key", [0, -1, INT_MIN, INT_MAX])
def test_c_remainder_and_bucket_match_for_integer_boundaries(key: int) -> None:
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": 7})
    adapter.execute("insert", {"key": key, "value": key})
    expected = (c_remainder(key, 7) + 7) % 7
    assert adapter.to_visual_state()["buckets"][expected]["entries"][0]["key"] == key


def test_visual_snapshot_exposes_distribution_stable_addresses_and_links() -> None:
    state = _state(3, [(1, 10), (4, 40), (7, 70)])
    meta = state["metadata"]
    assert meta["occupied_buckets"] == 1
    assert meta["collisions"] == 2
    assert meta["max_chain_length"] == 3
    assert meta["chain_lengths"] == [0, 3, 0]
    chain = state["buckets"][1]["entries"]
    assert [node["address"] for node in chain] == ["0xHASH-7", "0xHASH-4", "0xHASH-1"]
    assert [node["next"] for node in chain] == ["0xHASH-4", "0xHASH-1", "NULL"]


def test_update_preserves_count_address_collision_and_skips_allocation() -> None:
    before = _state(3, [(1, 10), (4, 40)])
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": 3})
    adapter.execute("insert", {"key": 1, "value": 10})
    adapter.execute("insert", {"key": 4, "value": 40})
    adapter.execute("insert", {"key": 4, "value": 99})
    after = adapter.to_visual_state()
    assert after["metadata"]["size"] == before["metadata"]["size"]
    assert after["metadata"]["collisions"] == before["metadata"]["collisions"]
    assert after["buckets"][1]["entries"][0]["address"] == before["buckets"][1]["entries"][0]["address"]
    frame = build_hash_frame(operation_name="insert", payload={"key": 4, "value": 99}, step={"line_index": 0, "line_text": "actual->valor = valor;", "state_snapshot": before, "state_after": after}, source_lines=["actual->valor = valor;"], success=True)
    assert frame["memory"]["allocation_attempted"] is False
    assert frame["memory"]["allocated"] == []


def test_controlled_malloc_failure_keeps_state_and_history_unchanged(client) -> None:
    client.post("/hash/hash_table/operate", json={"operation": "create_table", "payload": {"capacity": 3}})
    before = client.get("/hash/hash_table").get_data(as_text=True)
    response = client.post("/hash/hash_table/operate", json={"operation": "insert", "payload": {"key": 1, "value": 10, "simulate_allocation_failure": True}})
    assert response.status_code == 400
    data = response.get_json()
    assert data["visual_state"]["metadata"]["size"] == 0
    assert "malloc" in data["message"]
    assert all(step["payload"].get("simulate_allocation_failure") is not True for step in data["history"])
    assert any(step["pedagogy"]["memory"]["allocation_failed"] for step in data["execution_trace"]["steps"])
    assert before


@pytest.mark.parametrize(
    ("key", "position", "comparisons"),
    [(7, "head", 1), (4, "middle", 2), (1, "tail", 3), (10, "absent", 3)],
)
def test_search_distinguishes_chain_position_and_observed_cost(key: int, position: str, comparisons: int) -> None:
    state = _state(3, [(1, 10), (4, 40), (7, 70)])
    frame = build_hash_frame(operation_name="get", payload={"key": key}, step={"line_index": 0, "line_text": "while (actual != NULL) {", "state_snapshot": state, "state_after": deepcopy(state)}, source_lines=["while (actual != NULL) {"], success=position != "absent")
    assert frame["chain"]["position_kind"] == position
    assert frame["cost"]["comparisons"] == comparisons
    assert frame["cost"]["nodes_visited"] == comparisons
    assert "no tiempo real" in frame["cost"]["unit"]
    assert "factor de carga" in frame["cost"]["depends_on"]


def test_contains_declares_real_search_equivalence(client) -> None:
    response = client.post("/hash/hash_table/operate", json={"operation": "contains", "payload": {"key": 9}})
    source = response.get_json()["execution_trace"]["source_code"]
    assert "return th_buscar(tabla, clave, &dummy_valor);" in source


def test_real_trace_visits_each_collision_and_takes_found_branch(client) -> None:
    client.post("/hash/hash_table/operate", json={"operation": "create_table", "payload": {"capacity": 3}})
    for key in (1, 4, 7):
        client.post("/hash/hash_table/operate", json={"operation": "insert", "payload": {"key": key, "value": key * 10}})
    data = client.post("/hash/hash_table/operate", json={"operation": "get", "payload": {"key": 1}}).get_json()
    lines = [step["line_text"].strip() for step in data["execution_trace"]["steps"]]
    assert lines.count("if (actual->clave == clave) {") == 3
    assert "*valor = actual->valor;" in lines
    assert lines[-1] == "return true;"
    comparison_frames = [step["pedagogy"] for step in data["execution_trace"]["steps"] if "actual->clave == clave" in step["line_text"]]
    assert [frame["pointers"]["actual"] for frame in comparison_frames] == ["0xHASH-7", "0xHASH-4", "0xHASH-1"]


def test_page_has_views_minimap_fields_and_malloc_control(client) -> None:
    html = client.get("/hash/hash_table").get_data(as_text=True)
    assert 'id="hash-bucket-filter"' in html
    assert 'id="hash-minimap"' in html
    assert 'id="hash-show-addresses"' in html
    source = Path("static/js/hash.js").read_text(encoding="utf-8")
    for token in ("Residuo C", "Bucket final", "allocation_failed", "position_kind", "hash-minimap-cell"):
        assert token in source
