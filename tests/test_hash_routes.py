"""Integration tests for hash routes."""

from __future__ import annotations


def test_hash_module_page_loads(client) -> None:
    """Hash module index should be reachable."""
    response = client.get("/hash/")
    assert response.status_code == 200
    assert b"Modulo de Tablas Hash" in response.data


def test_hash_structure_page_loads(client) -> None:
    """Hash structure page should load."""
    response = client.get("/hash/hash_table")
    assert response.status_code == 200
    assert b"Estado visual" in response.data


def test_create_table_valid_and_invalid_capacity_via_route(client) -> None:
    """Route should accept valid capacity and block invalid ones."""
    valid = client.post(
        "/hash/hash_table/operate",
        json={"operation": "create_table", "payload": {"capacity": "13"}},
    )
    assert valid.status_code == 200
    assert valid.get_json()["visual_state"]["metadata"]["capacity"] == 13

    invalid = client.post(
        "/hash/hash_table/operate",
        json={"operation": "create_table", "payload": {"capacity": "0"}},
    )
    assert invalid.status_code == 400
    assert "positiva" in invalid.get_json()["message"].lower()


def test_insert_update_search_contains_remove_via_route(client) -> None:
    """Core hash operations should work through routes."""
    insert = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "A", "value": "1"}},
    )
    assert insert.status_code == 200

    update = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "A", "value": "2"}},
    )
    assert update.status_code == 200
    assert update.get_json()["result"]["updated"] is True

    get_existing = client.post(
        "/hash/hash_table/operate",
        json={"operation": "get", "payload": {"key": "A"}},
    )
    assert get_existing.status_code == 200
    assert get_existing.get_json()["result"] == "2"

    get_missing = client.post(
        "/hash/hash_table/operate",
        json={"operation": "get", "payload": {"key": "Z"}},
    )
    assert get_missing.status_code == 200
    assert get_missing.get_json()["result"] is None

    contains = client.post(
        "/hash/hash_table/operate",
        json={"operation": "contains", "payload": {"key": "A"}},
    )
    assert contains.status_code == 200
    assert contains.get_json()["result"] is True

    removed = client.post(
        "/hash/hash_table/operate",
        json={"operation": "remove", "payload": {"key": "A"}},
    )
    assert removed.status_code == 200
    assert removed.get_json()["result"] is True

    missing_remove = client.post(
        "/hash/hash_table/operate",
        json={"operation": "remove", "payload": {"key": "A"}},
    )
    assert missing_remove.status_code == 200
    assert missing_remove.get_json()["result"] is False


def test_queries_stats_visual_collisions_resize_and_clear_via_route(client) -> None:
    """Route should expose queries, stats, collisions, resize and clear."""
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "create_table", "payload": {"capacity": "3"}},
    )
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "k1", "value": "v1"}},
    )
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "k2", "value": "v2"}},
    )
    third = client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "k3", "value": "v3"}},
    )
    assert third.status_code == 200
    state_after_resize = third.get_json()["visual_state"]
    assert state_after_resize["metadata"]["resized"] is True
    assert state_after_resize["metadata"]["resize_event"]["old_capacity"] == 3
    assert state_after_resize["metadata"]["resize_event"]["new_capacity"] == 7

    keys = client.post("/hash/hash_table/operate", json={"operation": "keys", "payload": {}})
    values = client.post("/hash/hash_table/operate", json={"operation": "values", "payload": {}})
    items = client.post("/hash/hash_table/operate", json={"operation": "items", "payload": {}})
    stats = client.post("/hash/hash_table/operate", json={"operation": "stats", "payload": {}})

    assert keys.status_code == 200
    assert values.status_code == 200
    assert items.status_code == 200
    assert stats.status_code == 200
    assert stats.get_json()["result"]["size"] == 3

    clear = client.post("/hash/hash_table/operate", json={"operation": "clear", "payload": {}})
    assert clear.status_code == 200
    assert clear.get_json()["visual_state"]["metadata"]["size"] == 0


def test_hash_session_persistence_and_reset(client) -> None:
    """Hash history should persist in session and reset correctly."""
    client.post(
        "/hash/hash_table/operate",
        json={"operation": "insert", "payload": {"key": "Persistida", "value": "ok"}},
    )
    get_result = client.post(
        "/hash/hash_table/operate",
        json={"operation": "get", "payload": {"key": "Persistida"}},
    )
    assert get_result.status_code == 200
    assert get_result.get_json()["result"] == "ok"

    reset = client.post("/hash/hash_table/reset")
    assert reset.status_code == 200
    assert reset.get_json()["visual_state"]["metadata"]["size"] == 0


def test_hash_help_pages_available(client) -> None:
    """Hash module and structure help pages should be reachable."""
    module_help = client.get("/help/hash")
    structure_help = client.get("/help/hash/hash_table")

    assert module_help.status_code == 200
    assert b"Ayuda del modulo de tablas hash" in module_help.data
    assert structure_help.status_code == 200
    assert b"Operaciones soportadas" in structure_help.data
