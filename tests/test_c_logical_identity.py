from scripts.didactic_qa_identity import logical_identity_frames


def test_sequence_identity_survives_insert_move_and_remove() -> None:
    frames = logical_identity_frames([
        {"state": {"values": [1]}},
        {"state": {"values": [2, 1]}},
        {"state": {"values": [1]}},
    ])
    original = frames[0]["entities"][0]["id"]
    assert frames[1]["entities"][1]["id"] == original
    assert frames[2]["entities"][0]["id"] == original


def test_tree_rotation_keeps_value_identity_without_addresses() -> None:
    frames = logical_identity_frames([
        {"state": {"inorder": [10, 20, 30]}},
        {"state": {"inorder": [10, 20, 30]}},
    ])
    assert [e["id"] for e in frames[0]["entities"]] == [e["id"] for e in frames[1]["entities"]]
    assert "0x" not in repr(frames)


def test_hash_entry_identity_is_key_based_when_value_changes() -> None:
    frames = logical_identity_frames([
        {"state": {"pairs": [{"key": 7, "value": 10}]}},
        {"state": {"pairs": [{"key": 7, "value": 99}]}},
    ])
    assert frames[0]["entities"][0]["id"] == frames[1]["entities"][0]["id"]
