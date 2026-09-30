"""Integration tests for sequential operate/reset routes."""

from __future__ import annotations


def test_linked_list_methods_via_route(client) -> None:
    """Linked-list route should execute core methods and keep visual state in sync."""
    assert client.post(
        "/sequential/linked_list/operate",
        json={"operation": "insertar_final", "payload": {"value": "10"}},
    ).status_code == 200

    assert client.post(
        "/sequential/linked_list/operate",
        json={"operation": "insertar_inicio", "payload": {"value": "5"}},
    ).status_code == 200

    insert_pos = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "lista_insertar_elemento", "payload": {"value": "7", "position": "2"}},
    )
    assert insert_pos.status_code == 200
    assert [item["value"] for item in insert_pos.get_json()["visual_state"]["items"]] == [5, 10, 7]

    search = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "buscar_posiciones", "payload": {"value": "7"}},
    )
    assert search.status_code == 200
    assert search.get_json()["result"] == [3]

    remove_pos = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "eliminar_posicion", "payload": {"position": "3"}},
    )
    assert remove_pos.status_code == 200
    assert remove_pos.get_json()["result"] == 7

    remove_first = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "eliminar_primero", "payload": {"value": "5"}},
    )
    assert remove_first.status_code == 200
    assert [item["value"] for item in remove_first.get_json()["visual_state"]["items"]] == [10]
    assert remove_first.get_json()["visual_state"]["size"] == 1


def test_stack_methods_via_route(client) -> None:
    """Stack route should preserve LIFO behavior through HTTP operations."""
    assert client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "10"}},
    ).status_code == 200
    assert client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "20"}},
    ).status_code == 200

    pop = client.post(
        "/sequential/stack/operate",
        json={"operation": "desapilar", "payload": {}},
    )
    assert pop.status_code == 200
    assert pop.get_json()["result"] == 20
    assert [item["value"] for item in pop.get_json()["visual_state"]["items"]] == [10]

    clear = client.post("/sequential/stack/operate", json={"operation": "limpiar", "payload": {}})
    assert clear.status_code == 200
    assert clear.get_json()["visual_state"]["size"] == 0
    assert clear.get_json()["visual_state"]["empty"] is True


def test_queue_methods_via_route(client) -> None:
    """Queue route should preserve FIFO behavior through HTTP operations."""
    assert client.post(
        "/sequential/queue/operate",
        json={"operation": "encolar", "payload": {"value": "10"}},
    ).status_code == 200
    assert client.post(
        "/sequential/queue/operate",
        json={"operation": "encolar", "payload": {"value": "20"}},
    ).status_code == 200
    assert client.post(
        "/sequential/queue/operate",
        json={"operation": "encolar", "payload": {"value": "30"}},
    ).status_code == 200

    first_out = client.post(
        "/sequential/queue/operate",
        json={"operation": "desencolar", "payload": {}},
    )
    assert first_out.status_code == 200
    assert first_out.get_json()["result"] == 10

    second_out = client.post(
        "/sequential/queue/operate",
        json={"operation": "desencolar", "payload": {}},
    )
    assert second_out.status_code == 200
    assert second_out.get_json()["result"] == 20
    assert [item["value"] for item in second_out.get_json()["visual_state"]["items"]] == [30]


def test_priority_queue_methods_via_route(client) -> None:
    """Priority-queue route should respect priority and tie stability."""
    assert client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "encolar", "payload": {"value": "100", "priority": "3"}},
    ).status_code == 200
    assert client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "encolar", "payload": {"value": "200", "priority": "1"}},
    ).status_code == 200
    assert client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "encolar", "payload": {"value": "300", "priority": "1"}},
    ).status_code == 200
    last_in = client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "encolar", "payload": {"value": "400", "priority": "2"}},
    )
    assert last_in.status_code == 200
    assert last_in.get_json()["visual_state"]["out_index"] == 1

    front = client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "frente", "payload": {}},
    )
    assert front.status_code == 200
    assert front.get_json()["result"] == 200

    first_out = client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "desencolar", "payload": {}},
    )
    second_out = client.post(
        "/sequential/priority_queue/operate",
        json={"operation": "desencolar", "payload": {}},
    )
    assert first_out.status_code == 200
    assert second_out.status_code == 200
    assert first_out.get_json()["result"] == 200
    assert second_out.get_json()["result"] == 300


def test_circular_list_methods_via_route(client) -> None:
    """Circular-list route should execute supported methods and keep state in sync."""
    assert client.post(
        "/sequential/circular_list/operate",
        json={"operation": "insertar_final", "payload": {"value": "10"}},
    ).status_code == 200
    assert client.post(
        "/sequential/circular_list/operate",
        json={"operation": "insertar_inicio", "payload": {"value": "5"}},
    ).status_code == 200
    assert client.post(
        "/sequential/circular_list/operate",
        json={"operation": "insertar_final", "payload": {"value": "10"}},
    ).status_code == 200

    search = client.post(
        "/sequential/circular_list/operate",
        json={"operation": "buscar_posiciones", "payload": {"value": "10"}},
    )
    assert search.status_code == 200
    assert search.get_json()["result"] == [2, 3]

    invert = client.post(
        "/sequential/circular_list/operate",
        json={"operation": "invertir", "payload": {}},
    )
    assert invert.status_code == 200
    assert [item["value"] for item in invert.get_json()["visual_state"]["items"]] == [10, 10, 5]

    remove = client.post(
        "/sequential/circular_list/operate",
        json={"operation": "eliminar_primero", "payload": {"value": "10"}},
    )
    assert remove.status_code == 200
    assert [item["value"] for item in remove.get_json()["visual_state"]["items"]] == [10, 5]

    clear = client.post(
        "/sequential/circular_list/operate",
        json={"operation": "limpiar", "payload": {}},
    )
    assert clear.status_code == 200
    assert clear.get_json()["visual_state"]["size"] == 0


def test_sublist_methods_via_route(client) -> None:
    """Sublist route should execute parent/child lifecycle operations."""
    assert client.post(
        "/sequential/sublist/operate",
        json={"operation": "insertar_padre", "payload": {"parent": "1"}},
    ).status_code == 200
    assert client.post(
        "/sequential/sublist/operate",
        json={"operation": "insertar_hijo", "payload": {"parent": "1", "child": "7"}},
    ).status_code == 200
    assert client.post(
        "/sequential/sublist/operate",
        json={"operation": "insertar_hijo", "payload": {"parent": "1", "child": "8"}},
    ).status_code == 200

    children = client.post(
        "/sequential/sublist/operate",
        json={"operation": "hijos_de", "payload": {"parent": "1"}},
    )
    assert children.status_code == 200
    assert children.get_json()["result"] == [7, 8]

    remove_child = client.post(
        "/sequential/sublist/operate",
        json={"operation": "eliminar_hijo", "payload": {"parent": "1", "child": "7"}},
    )
    assert remove_child.status_code == 200
    sublist_items = remove_child.get_json()["visual_state"]["items"]
    assert [{"parent": item["parent"], "children": item["children"]} for item in sublist_items] == [{"parent": 1, "children": [8]}]
    assert sublist_items[0]["id"].startswith("parent-")

    remove_parent = client.post(
        "/sequential/sublist/operate",
        json={"operation": "eliminar_padre", "payload": {"parent": "1"}},
    )
    assert remove_parent.status_code == 200
    assert remove_parent.get_json()["visual_state"]["size"] == 0


def test_sequential_routes_session_persistence_and_reset(client) -> None:
    """History replay should persist operations and reset should clear state."""
    client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "11"}},
    )
    client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "22"}},
    )

    pop = client.post(
        "/sequential/stack/operate",
        json={"operation": "desapilar", "payload": {}},
    )
    assert pop.status_code == 200
    assert pop.get_json()["result"] == 22

    reset = client.post("/sequential/stack/reset")
    assert reset.status_code == 200
    assert reset.get_json()["visual_state"]["size"] == 0
    assert reset.get_json()["history"] == []


def test_sequential_routes_validation_errors(client) -> None:
    """Route should validate missing operation, invalid payload and invalid position."""
    missing_operation = client.post(
        "/sequential/stack/operate",
        json={"payload": {"value": "1"}},
    )
    assert missing_operation.status_code == 400

    invalid_payload = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": "not-a-dict"},
    )
    assert invalid_payload.status_code == 400

    invalid_position = client.post(
        "/sequential/linked_list/operate",
        json={"operation": "lista_insertar_elemento", "payload": {"value": "9", "position": "0"}},
    )
    assert invalid_position.status_code == 400
    assert invalid_position.get_json()["success"] is False
