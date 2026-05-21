"""Security and robustness tests for routes and session history boundaries."""

from __future__ import annotations

from time import perf_counter


def test_healthz_contract(client) -> None:
    """Health endpoint should keep a stable liveness contract."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_assets_route_serves_known_file(client) -> None:
    """Assets endpoint should serve files from project assets directory."""
    response = client.get("/assets/logo_UTP.jpg")
    assert response.status_code == 200
    assert response.data


def test_assets_route_blocks_path_traversal(client) -> None:
    """Assets endpoint should not allow traversal outside assets directory."""
    response = client.get("/assets/../README.md")
    assert response.status_code in {400, 404}


def test_help_unknown_structure_falls_back_safely(client) -> None:
    """Unknown help structure should not crash and must render fallback text."""
    response = client.get("/help/sequential/no_existe")
    assert response.status_code == 200
    assert "Estructura no encontrada".encode("utf-8") in response.data
    assert "No hay estructura C documentada".encode("utf-8") in response.data


def test_session_history_is_trimmed_to_configured_max(client, app) -> None:
    """Session history should keep only the latest N mutating operations."""
    app.config["SESSION_MAX_HISTORY"] = 3

    for value in ("1", "2", "3", "4", "5"):
        response = client.post(
            "/sequential/stack/operate",
            json={"operation": "apilar", "payload": {"value": value}},
        )
        assert response.status_code == 200

    with client.session_transaction() as sess:
        histories = sess.get("sequential_histories", {})
        stack_history = histories.get("stack", [])

    assert len(stack_history) == 3
    payload_values = [step["payload"]["value"] for step in stack_history]
    assert payload_values == ["3", "4", "5"]


def test_session_histories_are_isolated_by_module_namespace(client) -> None:
    """Sequential and hierarchical states should be stored under independent keys."""
    seq = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "10"}},
    )
    hier = client.post(
        "/hierarchical/abb/operate",
        json={"operation": "insertar", "payload": {"value": "20"}},
    )
    assert seq.status_code == 200
    assert hier.status_code == 200

    with client.session_transaction() as sess:
        histories = sess.get("sequential_histories", {})

    assert "stack" in histories
    assert "hierarchical::abb" in histories


def test_graph_bfs_performance_smoke(client) -> None:
    """Smoke performance check: BFS on a moderate graph should finish quickly."""
    client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "false"}},
    )
    for value in range(1, 101):
        client.post(
            "/graph/graph/operate",
            json={"operation": "insert_vertex", "payload": {"vertex": str(value)}},
        )
    for value in range(1, 100):
        client.post(
            "/graph/graph/operate",
            json={
                "operation": "insert_edge",
                "payload": {"origin": str(value), "target": str(value + 1), "weight": "1"},
            },
        )

    start = perf_counter()
    response = client.post(
        "/graph/graph/operate",
        json={"operation": "run_bfs", "payload": {"start": "1"}},
    )
    elapsed = perf_counter() - start

    assert response.status_code == 200
    assert response.get_json()["success"] is True
    assert elapsed < 5.0
