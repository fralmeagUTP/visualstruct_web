"""Security and robustness tests for routes and session history boundaries."""

from __future__ import annotations

from time import perf_counter

import pytest


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


def test_help_unknown_structure_falls_back_safely(client, monkeypatch) -> None:
    """Unknown help returns 404; registered help without C retains its placeholder."""
    from app.services.c_code_service import CCodeService

    response = client.get("/help/sequential/no_existe")
    assert response.status_code == 404

    monkeypatch.setattr(CCodeService, "get_structure_data", staticmethod(lambda _structure: None))
    registered = client.get("/help/sequential/stack")
    assert registered.status_code == 200
    assert "No hay estructura C documentada".encode("utf-8") in registered.data
    assert "Estructura no encontrada".encode("utf-8") not in registered.data


def test_session_history_limit_rejects_growth_without_losing_state(client, app) -> None:
    """A replay history must never lose its initial mutations to a silent slice."""
    app.config["SESSION_MAX_HISTORY"] = 3
    for value in ("1", "2", "3"):
        response = client.post(
            "/sequential/stack/operate",
            json={"operation": "apilar", "payload": {"value": value}},
        )
        assert response.status_code == 200
    with client.session_transaction() as sess:
        from copy import deepcopy
        before = deepcopy(dict(sess))
    rejected = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "4"}},
    )
    assert rejected.status_code == 409
    assert rejected.get_json()["preserve_session"] is True
    assert rejected.get_json()["visual_state"] == response.get_json()["visual_state"]
    with client.session_transaction() as sess:
        assert dict(sess) == before
        history = sess["sequential_histories"]["stack"]["history"]
        assert [entry["payload"]["value"] for entry in history] == ["1", "2", "3"]
    assert client.get("/sequential/stack").status_code == 200
    assert client.post("/sequential/stack/reset").status_code == 200
    again = client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": "9"}})
    assert again.status_code == 200
    assert again.get_json()["visual_state"]["size"] == 1


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
    assert histories["stack"]["schema_version"] == 1
    assert histories["hierarchical::abb"]["schema_version"] == 1


@pytest.mark.performance
def test_graph_bfs_performance_smoke(client) -> None:
    """The public 15-vertex limit completes BFS in normal mode within 5s.

    A large trace must be rejected intact, never truncated to satisfy the budget.
    The historical 30-vertex fixture ignored capacity failures during setup.
    """
    from app.domain.graph.educational_capacity import MAX_VERTICES
    from app.domain.graph.trace_budget import MAX_TRACE_EVENTS
    assert MAX_VERTICES == 15

    def post(operation, payload, **options):
        response = client.post('/graph/graph/operate', json={
            'operation': operation, 'payload': payload, **options})
        return response, response.get_json()

    operations = [('create_graph', {'directed': 'false'})]
    operations += [('insert_vertex', {'vertex': str(v)}) for v in range(1, MAX_VERTICES + 1)]
    operations += [('insert_edge', {'origin': str(v), 'target': str(v + 1), 'weight': '1'})
                   for v in range(1, MAX_VERTICES)]
    for operation, payload in operations:
        prepared, before = post(operation, payload)
        assert prepared.status_code == 200 and before['success'], before.get('message')
    assert len(before['visual_state']['nodes']) == MAX_VERTICES

    rejected, boundary = post('insert_vertex', {'vertex': str(MAX_VERTICES + 1)})
    assert rejected.status_code == 400 and boundary['success'] is False
    assert boundary['history'] == before['history']
    assert boundary['visual_state'] == before['visual_state']

    rejected, over_budget = post('run_bfs', {'start': '1'}, execution_mode='step')
    assert rejected.status_code == 400 and over_budget['success'] is False
    assert over_budget['trace_event_limit'] == MAX_TRACE_EVENTS
    assert over_budget['trace_available'] is False and over_budget['execution_trace'] is None
    assert over_budget['history'] == before['history']
    assert over_budget['visual_state'] == before['visual_state']

    start = perf_counter()
    response, body = post('run_bfs', {'start': '1'}, execution_mode='normal')
    elapsed = perf_counter() - start
    assert response.status_code == 200 and body['success'] is True
    assert body['c_status'] == 0 and body['result'] == list(range(1, MAX_VERTICES + 1))
    assert body['console_stdout'] == 'BFS: estado=0 ' + ' '.join(map(str, range(1, MAX_VERTICES + 1))) + '\n'
    assert body['trace_available'] is False and body['execution_trace'] is None
    assert body['history'][:-1] == before['history']
    assert body['history'][-1] == {'operation': 'run_bfs', 'payload': {'start': '1'}, 'source_contract': 'graph-book/v1'}
    assert len(body['visual_state']['nodes']) == MAX_VERTICES
    assert all(node['marked'] == 1 for node in body['visual_state']['nodes'])
    assert elapsed < 5.0
