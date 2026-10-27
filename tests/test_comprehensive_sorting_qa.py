"""Complete HTTP-level QA matrix for every sorting option and algorithm."""

from __future__ import annotations

from collections import Counter
from typing import Any

import pytest

from app.domain.sorting import SORTING_ALGORITHMS


ALGORITHMS = [item["id"] for item in SORTING_ALGORITHMS]


def _post(client: Any, path: str, payload: dict[str, Any]) -> Any:
    return client.post(f"/api/ordenamiento/{path}", json=payload)


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("values", ["7", "3,1,3,0,-2", "5,4,3,2,1"])
def test_all_sorting_algorithms_finish_with_the_api_equivalent_of_python_sort(client: Any, algorithm: str, values: str) -> None:
    created = _post(client, "create-array", {"values": values})
    assert created.status_code == 200, created.get_json()
    source = [int(value) for value in values.split(",") if value.strip()]
    selected = _post(client, "algorithm", {"algorithm_id": algorithm})
    assert selected.status_code == 200
    run = _post(client, "run", {"mode": "step_by_step", "algorithm_id": algorithm})
    assert run.status_code == 200, run.get_json()
    body = run.get_json()
    assert body["visual_state"]["items"] == sorted(source)
    assert Counter(body["visual_state"]["items"]) == Counter(source)
    assert body["execution_trace"]["steps"][-1]["state_after"] == body["visual_state"]


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_empty_array_is_rejected_consistently_before_selecting_any_sorting_algorithm(client: Any, algorithm: str) -> None:
    """The empty boundary is an intentional input-validation case, not a silent execution."""
    created = _post(client, "create-array", {"values": ""})
    assert created.status_code == 400
    assert created.get_json()["success"] is False
    assert _post(client, "algorithm", {"algorithm_id": algorithm}).status_code == 200


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_sorting_fast_and_step_api_results_are_equivalent_for_each_algorithm(client: Any, algorithm: str) -> None:
    values = "8,-3,8,0,2,-9,4"
    assert _post(client, "create-array", {"values": values}).status_code == 200
    fast = _post(client, "run", {"mode": "fast", "algorithm_id": algorithm})
    assert fast.status_code == 200, fast.get_json()
    assert _post(client, "create-array", {"values": values}).status_code == 200
    stepped = _post(client, "run", {"mode": "step_by_step", "algorithm_id": algorithm})
    assert stepped.status_code == 200, stepped.get_json()
    assert fast.get_json()["visual_state"]["items"] == stepped.get_json()["visual_state"]["items"] == sorted([8, -3, 8, 0, 2, -9, 4])


def test_every_sorting_endpoint_option_manual_random_step_state_compare_and_reset(client: Any) -> None:
    manual = _post(client, "create-array", {"values": "4,1,3,2"})
    assert manual.status_code == 200
    random = _post(client, "random-array", {"size": 6, "min_value": -2, "max_value": 2, "seed": 20260823})
    assert random.status_code == 200
    assert random.get_json()["result"]["array"] == _post(client, "random-array", {"size": 6, "min_value": -2, "max_value": 2, "seed": 20260823}).get_json()["result"]["array"]
    assert _post(client, "algorithm", {"algorithm_id": "quicksort"}).status_code == 200
    first = _post(client, "step", {"direction": "next", "cursor": -1, "algorithm_id": "quicksort"})
    assert first.status_code == 200 and first.get_json()["cursor"] == 0
    previous = _post(client, "step", {"direction": "prev", "cursor": 1, "algorithm_id": "quicksort"})
    assert previous.status_code == 200 and previous.get_json()["cursor"] == 0
    state = client.get("/api/ordenamiento/state")
    assert state.status_code == 200 and state.get_json()["algorithms"]
    comparison = _post(client, "compare", {"values": "4,1,3,2", "left_algorithm": "burbuja", "right_algorithm": "insercion"})
    assert comparison.status_code == 200 and comparison.get_json()["success"] is True
    reset = _post(client, "reset", {})
    assert reset.status_code == 200 and reset.get_json()["visual_state"]["items"] == []


@pytest.mark.parametrize(
    ("path", "payload"),
    [
        ("create-array", {"values": "1,,2"}),
        ("random-array", {"size": 0, "min_value": 1, "max_value": 2}),
        ("algorithm", {"algorithm_id": "does-not-exist"}),
        ("run", {"mode": "unknown", "algorithm_id": "burbuja"}),
        ("step", {"direction": "sideways", "cursor": 0, "algorithm_id": "burbuja"}),
        ("compare", {"values": "1,2", "left_algorithm": "burbuja", "right_algorithm": "unknown"}),
    ],
)
def test_sorting_invalid_options_are_controlled_client_errors(client: Any, path: str, payload: dict[str, Any]) -> None:
    response = _post(client, path, payload)
    assert response.status_code == 400
    assert response.get_json()["success"] is False
