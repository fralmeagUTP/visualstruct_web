"""Acceptance tests for hash pedagogy phases 1 through 3."""
from pathlib import Path
import json

import pytest

from app.adapters.hash_table_adapter import HashTableAdapter
from app.domain.hash.pedagogy import HASH_FRAME_SCHEMA_VERSION, HASH_GUIDED_EXAMPLES, HASH_LEARNING_CATALOG, build_hash_frame, hash_frame_schema, validate_hash_frame
from app.services.c_code_service import CCodeService


def test_fixed_capacity_integer_contract_and_original_collision_keys():
    adapter = HashTableAdapter(); adapter.execute("create_table", {"capacity": 3})
    for key, value in ((1, 10), (4, 40), (7, 70)):
        adapter.execute("insert", {"key": key, "value": value})
    state = adapter.to_visual_state()
    assert state["metadata"]["capacity_policy"] == "fixed"
    assert state["metadata"]["capacity"] == 3
    assert [item["key"] for item in state["buckets"][1]["entries"]] == [7, 4, 1]
    assert adapter.execute("get", {"key": 4})["result"] == 40
    with pytest.raises(ValueError): adapter.execute("insert", {"key": 2, "value": "texto"})


def test_destroy_is_distinct_from_clear():
    adapter = HashTableAdapter(); adapter.execute("create_table", {"capacity": 3}); adapter.execute("insert", {"key": 1, "value": 10})
    adapter.execute("clear", {})
    assert adapter.to_visual_state()["metadata"]["capacity"] == 3
    adapter.execute("destroy_table", {})
    state = adapter.to_visual_state()
    assert state["metadata"]["capacity"] == 0 and state["metadata"]["size"] == 0
    with pytest.raises(ValueError): adapter.execute("insert", {"key": 2, "value": 20})


def test_hash_frame_contract_exposes_formula_chain_memory_and_invariants():
    before = {"structure":"hash_table","buckets":[{"index":0,"entries":[]},{"index":1,"entries":[{"key":1,"value":10}],"size":1},{"index":2,"entries":[]}],"metadata":{"capacity":3,"size":1,"capacity_policy":"fixed"}}
    after = {"structure":"hash_table","buckets":[{"index":0,"entries":[]},{"index":1,"entries":[{"key":-2,"value":20},{"key":1,"value":10}],"size":2},{"index":2,"entries":[]}],"metadata":{"capacity":3,"size":2,"capacity_policy":"fixed"}}
    line = "int indice = th_indice(tabla, clave);"
    frame = build_hash_frame(operation_name="insert", payload={"key":-2,"value":20}, step={"line_index":0,"line_text":line,"state_snapshot":before,"state_after":after}, source_lines=[line], success=True)
    validate_hash_frame(frame, source_code=line)
    assert frame["hash"]["raw_remainder"] == -2
    assert frame["hash"]["normalized_index"] == 1
    assert frame["hash"]["normalization_applied"] is True
    assert frame["memory"]["allocated"][0]["address"] == "0xHASH--2"
    assert frame["invariant"]["holds"] is True


def test_hash_golden_concepts_are_stable():
    fixtures=json.loads(Path("tests/golden/hash_pedagogical_frames_v1.json").read_text(encoding="utf-8"))["fixtures"]
    state={"structure":"hash_table","buckets":[{"index":0,"entries":[]},{"index":1,"entries":[{"key":1,"value":10}]},{"index":2,"entries":[]}],"metadata":{"capacity":3,"size":1,"capacity_policy":"fixed"}}
    for fixture in fixtures.values():
        frame=build_hash_frame(operation_name="insert",payload={"key":1,"value":10},step={"line_index":0,"line_text":fixture["line"],"state_snapshot":state,"state_after":state},source_lines=[fixture["line"]],success=True)
        validate_hash_frame(frame,source_code=fixture["line"]);assert frame["concept"]==fixture["concept"]


def test_real_trace_has_schema_levels_helpers_and_frames(client):
    client.post("/hash/hash_table/operate", json={"operation":"create_table","payload":{"capacity":3}})
    response = client.post("/hash/hash_table/operate", json={"operation":"insert","payload":{"key":1,"value":10}})
    assert response.status_code == 200
    trace = response.get_json()["execution_trace"]
    assert trace["pedagogy_schema_version"] == HASH_FRAME_SCHEMA_VERSION
    assert trace["pedagogy_schema"] == hash_frame_schema()
    assert trace["learning_profile"]["capacity_policy"] == "fixed"
    assert "int th_indice" in trace["source_code"] and "bool th_insertar" in trace["source_code"]
    assert all("pedagogy" in step for step in trace["steps"])


def test_catalog_examples_and_page_regions(client):
    assert HASH_LEARNING_CATALOG["value_type"] == "int"
    assert {item["id"] for item in HASH_GUIDED_EXAMPLES} >= {"empty","collision","update","negative"}
    html = client.get("/hash/hash_table").get_data(as_text=True)
    for label in ("Preparar","Predecir","Ejecutar","Comprender","Relacionar con C","Comparar","Reflexionar"):
        assert label in html
    for element_id in ("hash-learning-level","hash-guided-example","hash-load-example","hash-visual-region","hash-code-region","hash-function-list","hash-hide-comments","hash-reset-execution","hash-formula-view","hash-chain-view","hash-pointers-view","hash-memory-view","hash-invariant-view"):
        assert f'id="{element_id}"' in html


def test_help_and_frontend_remove_false_rehash_claim_and_generate_c17_main():
    help_text = Path("app/services/hash_help_service.py").read_text(encoding="utf-8")
    assert "redimensionamiento automatico" not in help_text.lower()
    source = Path("static/js/hash.js").read_text(encoding="utf-8")
    assert 'lines.push(\'#include "tad_tabla_hash.h"\')' in source
    assert 'lines.push("    th_destruir(&tabla);")' in source
    assert "renderHashPedagogy" in source and "initHashResponsiveWorkspace" in source
    c_data = CCodeService.get_structure_data("hash_table")
    assert "th_indice" in c_data["operations"]["insert"]
    assert "th_buscar" in c_data["operations"]["contains"]
