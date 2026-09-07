"""Unit tests for hash-table adapter operations and visualization contract."""

from __future__ import annotations

from app.adapters.hash_table_adapter import HashTableAdapter


def test_create_table_with_valid_capacity() -> None:
    """Adapter should create hash table with requested positive capacity."""
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": "11"})
    state = adapter.to_visual_state()
    assert state["metadata"]["capacity"] == 11


def test_create_table_invalid_capacity_blocked() -> None:
    """Adapter should block zero or negative capacity."""
    adapter = HashTableAdapter()
    try:
        adapter.execute("create_table", {"capacity": "0"})
        assert False, "Capacidad 0 debio fallar"
    except ValueError as error:
        assert "positiva" in str(error).lower()


def test_insert_update_get_and_contains() -> None:
    """Insert/update/get/contains should behave consistently."""
    adapter = HashTableAdapter()
    adapter.execute("insert", {"key": 1, "value": "1"})
    adapter.execute("insert", {"key": 1, "value": "2"})

    get_result = adapter.execute("get", {"key": 1})["result"]
    contains_result = adapter.execute("contains", {"key": 1})["result"]
    missing_result = adapter.execute("get", {"key": 99})["result"]

    assert get_result == 2
    assert contains_result is True
    assert missing_result is None


def test_remove_existing_and_missing_key() -> None:
    """Remove should return True for existing key and False otherwise."""
    adapter = HashTableAdapter()
    adapter.execute("insert", {"key": 1, "value": "1"})

    removed = adapter.execute("remove", {"key": 1})["result"]
    missing = adapter.execute("remove", {"key": 1})["result"]

    assert removed is True
    assert missing is False


def test_keys_values_items_stats_and_clear() -> None:
    """Adapter should expose query operations and clear state."""
    adapter = HashTableAdapter()
    adapter.execute("insert", {"key": 1, "value": "1"})
    adapter.execute("insert", {"key": 2, "value": "2"})

    keys = adapter.execute("keys", {})["result"]
    values = adapter.execute("values", {})["result"]
    items = adapter.execute("items", {})["result"]
    stats = adapter.execute("stats", {})["result"]

    assert set(keys) == {1, 2}
    assert set(values) == {1, 2}
    assert set(tuple(item) for item in items) == {(1, 1), (2, 2)}
    assert stats["size"] == 2
    assert stats["capacity"] >= 2

    adapter.execute("clear", {})
    cleared = adapter.to_visual_state()
    assert cleared["metadata"]["size"] == 0


def test_to_visual_state_has_fixed_capacity_and_deterministic_collisions() -> None:
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": "3"})
    adapter.execute("insert", {"key": 1, "value": 10})
    adapter.execute("insert", {"key": 4, "value": 40})
    adapter.execute("insert", {"key": 7, "value": 70})

    state = adapter.to_visual_state()
    assert state["structure"] == "hash_table"
    assert "buckets" in state
    assert "metadata" in state
    assert state["metadata"]["capacity"] == 3
    assert state["metadata"]["capacity_policy"] == "fixed"
    assert state["metadata"]["collisions"] == 2
