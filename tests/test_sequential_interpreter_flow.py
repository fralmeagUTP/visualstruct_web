"""End-to-end style sequential flows validating interpreter-like behavior."""

from __future__ import annotations


def _operate(client, structure_id: str, operation: str, payload: dict[str, str] | None = None):
    body = {"operation": operation, "payload": payload or {}}
    response = client.post(f"/sequential/{structure_id}/operate", json=body)
    return response, response.get_json()


def _values(data: dict) -> list[int]:
    return [item["value"] for item in data["visual_state"]["items"]]


def test_linked_list_interpreter_flow_history_and_visual_state(client) -> None:
    """Linked list should keep deterministic state and history across many operations."""
    mutating_steps = 0

    for op, payload in [
        ("insertar_final", {"value": "1"}),
        ("insertar_final", {"value": "2"}),
        ("insertar_inicio", {"value": "0"}),
        ("insertar_posicion", {"value": "9", "position": "2"}),
        ("eliminar_posicion", {"position": "3"}),
        ("eliminar_primero", {"value": "9"}),
    ]:
        response, data = _operate(client, "linked_list", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    assert _values(data) == [0, 2]

    response, search = _operate(client, "linked_list", "buscar_posiciones", {"value": "2"})
    assert response.status_code == 200
    assert search["result"] == [2]
    assert len(search["history"]) == mutating_steps

    for op, payload in [
        ("insertar_inicio", {"value": "-5"}),
        ("eliminar_final", {}),
        ("insertar_posicion", {"value": "7", "position": "2"}),
        ("eliminar_inicio", {}),
        ("limpiar", {}),
    ]:
        response, data = _operate(client, "linked_list", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    assert data["visual_state"]["size"] == 0
    assert data["visual_state"]["empty"] is True
    assert _values(data) == []


def test_stack_interpreter_flow_history_and_visual_state(client) -> None:
    """Stack should preserve LIFO semantics and replayable history in long flows."""
    mutating_steps = 0

    for op, payload in [
        ("apilar", {"value": "10"}),
        ("apilar", {"value": "20"}),
        ("apilar", {"value": "30"}),
        ("desapilar", {}),
        ("apilar", {"value": "40"}),
        ("desapilar", {}),
        ("desapilar", {}),
        ("apilar", {"value": "50"}),
        ("apilar", {"value": "60"}),
        ("desapilar", {}),
    ]:
        response, data = _operate(client, "stack", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    assert _values(data) == [50, 10]
    assert data["visual_state"]["size"] == 2

    response, cleared = _operate(client, "stack", "limpiar", {})
    assert response.status_code == 200
    assert len(cleared["history"]) == mutating_steps + 1
    assert cleared["visual_state"]["empty"] is True


def test_queue_interpreter_flow_history_and_visual_state(client) -> None:
    """Queue should preserve FIFO semantics and replayable history in long flows."""
    mutating_steps = 0

    for op, payload in [
        ("encolar", {"value": "10"}),
        ("encolar", {"value": "20"}),
        ("encolar", {"value": "30"}),
        ("desencolar", {}),
        ("encolar", {"value": "40"}),
        ("desencolar", {}),
        ("desencolar", {}),
        ("encolar", {"value": "50"}),
        ("encolar", {"value": "60"}),
        ("desencolar", {}),
    ]:
        response, data = _operate(client, "queue", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    assert _values(data) == [50, 60]
    assert data["visual_state"]["size"] == 2

    response, cleared = _operate(client, "queue", "limpiar", {})
    assert response.status_code == 200
    assert len(cleared["history"]) == mutating_steps + 1
    assert cleared["visual_state"]["empty"] is True


def test_priority_queue_interpreter_flow_history_and_visual_state(client) -> None:
    """Priority queue should keep priority ordering and stable ties under route replay."""
    mutating_steps = 0

    for op, payload in [
        ("encolar", {"value": "50", "priority": "5"}),
        ("encolar", {"value": "10", "priority": "1"}),
        ("encolar", {"value": "20", "priority": "1"}),
        ("encolar", {"value": "30", "priority": "3"}),
    ]:
        response, data = _operate(client, "priority_queue", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    response, front = _operate(client, "priority_queue", "frente", {})
    assert response.status_code == 200
    assert front["result"] == 10
    assert len(front["history"]) == mutating_steps

    for op, payload, expected in [
        ("desencolar", {}, 10),
        ("desencolar", {}, 20),
        ("encolar", {"value": "25", "priority": "2"}, None),
        ("encolar", {"value": "99", "priority": "9"}, None),
        ("desencolar", {}, 25),
        ("desencolar", {}, 30),
        ("desencolar", {}, 50),
        ("desencolar", {}, 99),
    ]:
        response, data = _operate(client, "priority_queue", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps
        if expected is not None:
            assert data["result"] == expected

    assert data["visual_state"]["empty"] is True
    assert data["visual_state"]["size"] == 0


def test_circular_list_interpreter_flow_history_and_visual_state(client) -> None:
    """Circular list should keep deterministic state and history in long flows."""
    mutating_steps = 0

    for op, payload in [
        ("insertar_final", {"value": "10"}),
        ("insertar_inicio", {"value": "5"}),
        ("insertar_final", {"value": "15"}),
        ("insertar_final", {"value": "10"}),
        ("eliminar_primero", {"value": "10"}),
        ("insertar_inicio", {"value": "1"}),
    ]:
        response, data = _operate(client, "circular_list", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    response, search = _operate(client, "circular_list", "buscar_posiciones", {"value": "10"})
    assert response.status_code == 200
    assert search["result"] == [4]
    assert len(search["history"]) == mutating_steps

    for op, payload in [
        ("invertir", {}),
        ("eliminar_inicio", {}),
        ("insertar_final", {"value": "99"}),
        ("eliminar_primero", {"value": "15"}),
        ("limpiar", {}),
    ]:
        response, data = _operate(client, "circular_list", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    assert data["visual_state"]["empty"] is True
    assert data["visual_state"]["size"] == 0


def test_sublist_interpreter_flow_history_and_visual_state(client) -> None:
    """Sublist should keep deterministic parent/child state and replayable history."""
    mutating_steps = 0

    for op, payload in [
        ("insertar_padre", {"parent": "1"}),
        ("insertar_padre", {"parent": "2"}),
        ("insertar_hijo", {"parent": "1", "child": "10"}),
        ("insertar_hijo", {"parent": "1", "child": "20"}),
        ("insertar_hijo", {"parent": "2", "child": "30"}),
        ("eliminar_hijo", {"parent": "1", "child": "10"}),
        ("insertar_hijo", {"parent": "2", "child": "31"}),
    ]:
        response, data = _operate(client, "sublist", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    response, children = _operate(client, "sublist", "hijos_de", {"parent": "2"})
    assert response.status_code == 200
    assert children["result"] == [30, 31]
    assert len(children["history"]) == mutating_steps

    for op, payload in [
        ("eliminar_padre", {"parent": "1"}),
        ("eliminar_hijo", {"parent": "2", "child": "30"}),
        ("limpiar", {}),
    ]:
        response, data = _operate(client, "sublist", op, payload)
        assert response.status_code == 200
        mutating_steps += 1
        assert len(data["history"]) == mutating_steps

    assert data["visual_state"]["empty"] is True
    assert data["visual_state"]["size"] == 0
