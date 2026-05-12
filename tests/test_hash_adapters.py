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
    adapter.execute("insert", {"key": "A", "value": "1"})
    adapter.execute("insert", {"key": "A", "value": "2"})

    get_result = adapter.execute("get", {"key": "A"})["result"]
    contains_result = adapter.execute("contains", {"key": "A"})["result"]
    missing_result = adapter.execute("get", {"key": "Z"})["result"]

    assert get_result == "2"
    assert contains_result is True
    assert missing_result is None


def test_remove_existing_and_missing_key() -> None:
    """Remove should return True for existing key and False otherwise."""
    adapter = HashTableAdapter()
    adapter.execute("insert", {"key": "A", "value": "1"})

    removed = adapter.execute("remove", {"key": "A"})["result"]
    missing = adapter.execute("remove", {"key": "A"})["result"]

    assert removed is True
    assert missing is False


def test_keys_values_items_stats_and_clear() -> None:
    """Adapter should expose query operations and clear state."""
    adapter = HashTableAdapter()
    adapter.execute("insert", {"key": "A", "value": "1"})
    adapter.execute("insert", {"key": "B", "value": "2"})

    keys = adapter.execute("keys", {})["result"]
    values = adapter.execute("values", {})["result"]
    items = adapter.execute("items", {})["result"]
    stats = adapter.execute("stats", {})["result"]

    assert set(keys) == {"A", "B"}
    assert set(values) == {"1", "2"}
    assert set(tuple(item) for item in items) == {("A", "1"), ("B", "2")}
    assert stats["size"] == 2
    assert stats["capacity"] >= 2

    adapter.execute("clear", {})
    cleared = adapter.to_visual_state()
    assert cleared["metadata"]["size"] == 0


def test_to_visual_state_has_buckets_collisions_and_resize() -> None:
    """Visual state should include buckets, collisions and resize info."""
    adapter = HashTableAdapter()
    adapter.execute("create_table", {"capacity": "3"})
    adapter.execute("insert", {"key": "k1", "value": "v1"})
    adapter.execute("insert", {"key": "k2", "value": "v2"})
    adapter.execute("insert", {"key": "k3", "value": "v3"})

    state = adapter.to_visual_state()
    assert state["structure"] == "hash_table"
    assert "buckets" in state
    assert "metadata" in state
    assert state["metadata"]["resized"] is True
    assert state["metadata"]["resize_event"]["old_capacity"] == 3
    assert state["metadata"]["resize_event"]["new_capacity"] == 7

    adapter.execute("create_table", {"capacity": "17"})
    index_map: dict[int, list[str]] = {}
    for i in range(200):
        key = f"key_{i}"
        bucket_index = adapter.table._indice(key)  # noqa: SLF001
        index_map.setdefault(bucket_index, []).append(key)
    colliding_pair = next(values for values in index_map.values() if len(values) >= 2)
    adapter.execute("insert", {"key": colliding_pair[0], "value": "a"})
    adapter.execute("insert", {"key": colliding_pair[1], "value": "b"})
    with_collisions = adapter.to_visual_state()
    assert with_collisions["metadata"]["collisions"] >= 1
