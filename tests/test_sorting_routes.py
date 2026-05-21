"""Integration tests for sorting routes."""

from __future__ import annotations


def test_sorting_module_page_loads(client) -> None:
    """Sorting index should be reachable."""
    response = client.get("/sorting/")
    assert response.status_code == 200
    assert "Modulo de Metodos de Ordenamiento".encode("utf-8") in response.data


def test_sorting_visualizer_page_loads(client) -> None:
    """Sorting visualizer page should load with controls."""
    response = client.get("/sorting/visualizador")
    assert response.status_code == 200
    assert b"didactic-mode-switch" in response.data
    assert "Mostrar codigo y detalles tecnicos".encode("utf-8") in response.data
    assert b"sorting-sim-play" in response.data
    assert b"sorting-step-toggle" in response.data
    assert "Codigo C:".encode("utf-8") in response.data


def test_sorting_create_random_select_run_flow(client) -> None:
    """Sorting API should support full flow."""
    create = client.post("/api/ordenamiento/create-array", json={"values": "8,3,1,5"})
    assert create.status_code == 200
    assert create.get_json()["visual_state"]["items"] == [8, 3, 1, 5]

    select = client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "quicksort"})
    assert select.status_code == 200

    run_step = client.post("/api/ordenamiento/run", json={"mode": "step_by_step", "algorithm_id": "quicksort"})
    assert run_step.status_code == 200
    step_data = run_step.get_json()
    assert step_data["success"] is True
    assert len(step_data["execution_trace"]["steps"]) > 0
    step_final = step_data["visual_state"]["items"]

    client.post("/api/ordenamiento/reset", json={})
    client.post("/api/ordenamiento/create-array", json={"values": "8,3,1,5"})
    client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "quicksort"})
    run_fast = client.post("/api/ordenamiento/run", json={"mode": "fast", "algorithm_id": "quicksort"})
    assert run_fast.status_code == 200
    fast_final = run_fast.get_json()["visual_state"]["items"]
    assert fast_final == step_final
    assert fast_final == [1, 3, 5, 8]


def test_sorting_invalid_algorithm_is_blocked(client) -> None:
    """Unknown algorithm should be rejected."""
    response = client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "algo_inexistente"})
    assert response.status_code == 400
    assert "algoritmo" in response.get_json()["message"].lower()


def test_sorting_help_pages_available(client) -> None:
    """Sorting module help and structure help should be reachable."""
    module_help = client.get("/help/sorting")
    structure_help = client.get("/help/sorting/sorting_array")
    assert module_help.status_code == 200
    assert "Ayuda del modulo de metodos de ordenamiento".encode("utf-8") in module_help.data
    assert structure_help.status_code == 200
    assert b"ordenar_burbuja" in structure_help.data
