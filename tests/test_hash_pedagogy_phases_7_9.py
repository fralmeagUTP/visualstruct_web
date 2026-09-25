"""Acceptance coverage for hash lifecycle, active learning and replay."""
from __future__ import annotations

from pathlib import Path

from app.domain.hash.pedagogy import HASH_GUIDED_EXAMPLES
from app.services.hash_structure_service import HashStructureService


def _run(history: list[dict], operation: str, payload: dict) -> dict:
    return HashStructureService.execute_operation("hash_table", operation, payload, history)


def _collision_history() -> list[dict]:
    history: list[dict] = []
    history = _run(history, "create_table", {"capacity": 3})["history"]
    for key in (1, 4, 7):
        history = _run(history, "insert", {"key": key, "value": key * 10})["history"]
    return history


def test_remove_trace_distinguishes_head_middle_and_absent_with_causal_pointers() -> None:
    for key, expected_link, expected_free in ((7, "tabla->buckets[indice] = actual->siguiente;", "0xHASH-7"), (4, "anterior->siguiente = actual->siguiente;", "0xHASH-4"), (10, "return false;", None)):
        response = _run(_collision_history(), "remove", {"key": key})
        steps = response["execution_trace"]["steps"]
        lines = [step["line_text"].strip() for step in steps]
        assert expected_link in lines
        free_steps = [step for step in steps if "free(actual)" in step["line_text"]]
        if expected_free is None:
            assert not free_steps
        else:
            assert len(free_steps) == 1
            assert free_steps[0]["pedagogy"]["pointers"]["actual"] == expected_free
            assert free_steps[0]["pedagogy"]["memory"]["freed"][0]["address"] == expected_free
        assert all(not step["pedagogy"]["memory"]["dangling_references"] for step in steps)


def test_clear_and_destroy_free_memory_with_distinct_postconditions() -> None:
    clear = _run(_collision_history(), "clear", {})
    clear_state = clear["visual_state"]
    assert clear_state["metadata"]["capacity"] == 3
    assert clear_state["metadata"]["size"] == 0
    clear_free = [step["pedagogy"]["memory"]["freed"][0]["address"] for step in clear["execution_trace"]["steps"] if "free(actual)" in step["line_text"]]
    assert clear_free == ["0xHASH-7", "0xHASH-4", "0xHASH-1"]

    destroyed = _run(_collision_history(), "destroy_table", {})
    state = destroyed["visual_state"]
    assert state["metadata"]["capacity"] == 0 and state["metadata"]["size"] == 0 and state["buckets"] == []
    frames = [step["pedagogy"] for step in destroyed["execution_trace"]["steps"]]
    assert any(frame["memory"]["bucket_array_freed"] for frame in frames)
    assert any(frame["memory"]["bucket_array_is_null"] for frame in frames)


def test_guided_examples_cover_hash_boundary_search_removal_and_memory_cases() -> None:
    ids = {item["id"] for item in HASH_GUIDED_EXAMPLES}
    assert {"empty", "capacity-one", "no-collision", "collision", "update", "search-head", "search-middle", "search-tail", "search-absent", "remove-head", "remove-middle", "remove-absent", "zero", "negative", "int-max", "low-load", "high-load", "malloc-failure"}.issubset(ids)


def test_trace_final_state_matches_fast_execution_and_every_frame_is_replay_safe() -> None:
    history = _collision_history()
    stepped = _run(history, "remove", {"key": 4})
    fast = _run(history, "remove", {"key": 4})
    trace = stepped["execution_trace"]
    assert trace["final_state"] == fast["visual_state"] == stepped["visual_state"]
    assert trace["steps"][-1]["state_after"] == trace["final_state"]
    assert all(frame["memory"]["dangling_references"] == [] for frame in (step["pedagogy"] for step in trace["steps"]))


def test_page_and_client_expose_practice_predictions_and_full_playback_controls(client) -> None:
    html = client.get("/hash/hash_table").get_data(as_text=True)
    for element_id in ("hash-sim-pause", "hash-sim-start", "hash-sim-end", "hash-sim-repeat", "hash-sim-progress", "hash-sim-detail", "hash-prediction-kind", "hash-prediction-answer", "hash-check-prediction", "hash-prediction-hint", "hash-skip-prediction", "hash-practice-mode", "hash-reset-progress"):
        assert f'id="{element_id}"' in html
    source = Path("static/js/hash.js").read_text(encoding="utf-8")
    for token in ("hashPredictionExpected", "hash-learning-progress", "tracePlayer?.seek", "tracePlayer?.pause", "playFromStart"):
        assert token in source


def test_capacity_comparison_uses_immutable_input_and_isolated_tables(client) -> None:
    response = client.post("/hash/compare-capacities", json={"entries": [[1, 10], [4, 40], [7, 70]], "success_key": 1, "absent_key": 10})
    assert response.status_code == 200
    data = response.get_json()
    assert data["input"]["entries"] == [[1, 10], [4, 40], [7, 70]]
    assert [item["capacity"] for item in data["variants"]] == [3, 7, 17]
    assert all(len(item["snapshots"]) == 4 for item in data["variants"])
    three = data["variants"][0]
    assert three["distribution"]["collisions"] == 2
    assert three["successful_lookup"]["comparisons"] == 3
    assert three["absent_lookup"]["comparisons"] == 3
    assert "no prueban" in data["conclusion"]


def test_hash_help_and_page_cover_comparison_accessibility_and_export(client) -> None:
    page = client.get("/hash/hash_table").get_data(as_text=True)
    for element_id in ("hash-compare-controls", "hash-compare-run", "hash-compare-progress", "hash-export-image", "hash-export-summary", "hash-accessible-announcer"):
        assert f'id="{element_id}"' in page
    help_page = client.get("/help/hash/hash_table").get_data(as_text=True)
    for label in ("Guía de aprendizaje", "Capacidad fija", "Glosario", "Guía docente", "Alt+→"):
        assert label in help_page
    source = Path("static/js/hash.js").read_text(encoding="utf-8")
    for token in ("compareControls?.dataset.compareUrl", "exportVisualStateAsJpg", "hash-learning-summary/v1"):
        assert token in source
    assert "prefers-reduced-motion" in Path("static/css/styles.css").read_text(encoding="utf-8")
