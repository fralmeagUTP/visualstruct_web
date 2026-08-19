"""Compatibility tests for legacy session history migration."""

from __future__ import annotations

import pytest

from app.services.session_service import SESSION_KEY, SessionService


def test_legacy_history_is_migrated_without_losing_replay_events(app) -> None:
    legacy_history = [
        {"operation": "apilar", "payload": {"value": "10"}},
        {"operation": "apilar", "payload": {"value": "20"}},
    ]
    with app.test_request_context("/"):
        from flask import session

        session[SESSION_KEY] = {"stack": legacy_history}

        assert SessionService.get_history("stack") == legacy_history
        record = session[SESSION_KEY]["stack"]
        assert record == {
            "schema_version": 1,
            "history": legacy_history,
            "checkpoint": None,
        }
        assert session.modified is True


def test_legacy_route_replays_full_history_before_first_new_save(client) -> None:
    legacy_history = [
        {"operation": "apilar", "payload": {"value": "10"}},
        {"operation": "apilar", "payload": {"value": "20"}},
    ]
    with client.session_transaction() as sess:
        sess[SESSION_KEY] = {"stack": legacy_history}

    response = client.get("/sequential/stack")
    assert response.status_code == 200

    pop = client.post(
        "/sequential/stack/operate",
        json={"operation": "desapilar", "payload": {}},
    )
    assert pop.status_code == 200
    assert pop.get_json()["result"] == 20
    assert len(pop.get_json()["history"]) == 3


@pytest.mark.parametrize(
    "structure_id",
    ["stack", "binary_heap", "graph", "hash_table", "sorting"],
)
def test_legacy_history_migrates_for_every_structure_family(app, structure_id) -> None:
    """Pre-checkpoint list records remain readable for all five families."""
    legacy_history = [{"operation": "legacy-operation", "payload": {"value": "1"}}]
    with app.test_request_context("/"):
        from flask import session

        session[SESSION_KEY] = {structure_id: legacy_history}

        assert SessionService.get_history(structure_id) == legacy_history
        assert session[SESSION_KEY][structure_id]["checkpoint"] is None
        assert session[SESSION_KEY][structure_id]["schema_version"] == 1


def test_checkpoint_access_preserves_history_and_returns_defensive_copy(app) -> None:
    history = [{"operation": "apilar", "payload": {"value": "7"}}]
    checkpoint = {"schema_version": 1, "checksum": "a" * 64}
    with app.test_request_context("/"):
        SessionService.save_history("stack", history)
        SessionService.save_checkpoint("stack", checkpoint)

        loaded = SessionService.get_checkpoint("stack")
        assert loaded == checkpoint
        assert SessionService.get_history("stack") == history
        assert loaded is not None
        loaded["checksum"] = "changed"
        assert SessionService.get_checkpoint("stack") == checkpoint


def test_saving_new_history_invalidates_stale_checkpoint(app) -> None:
    with app.test_request_context("/"):
        SessionService.save_checkpoint("stack", {"checksum": "a" * 64})
        SessionService.save_history(
            "stack", [{"operation": "apilar", "payload": {"value": "1"}}]
        )
        assert SessionService.get_checkpoint("stack") is None
