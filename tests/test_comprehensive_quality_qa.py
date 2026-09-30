"""Non-functional quality gates used by the comprehensive QA OpenSpec."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter

import pytest


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    "path",
    [
        "/sequential/stack",
        "/hierarchical/avl",
        "/graph/graph/recorridos",
        "/hash/hash_table",
        "/sorting/visualizador",
    ],
)
def test_main_module_screens_publish_keyboard_and_reduced_motion_support(client, path: str) -> None:
    """Every learning screen exposes the common keyboard/a11y foundations."""
    response = client.get(path)
    assert response.status_code == 200
    assert b'aria-live="polite"' in response.data
    assert b"didactic-mode-switch" in response.data
    styles = (ROOT / "static" / "css" / "styles.css").read_text(encoding="utf-8")
    assert "prefers-reduced-motion: reduce" in styles


def test_security_boundaries_reject_traversal_and_untrusted_operation_payloads(client) -> None:
    """Public endpoints must not expose files or accept an unknown operation."""
    assert client.get("/assets/../../run.py").status_code in {400, 404}
    response = client.post("/hash/hash_table/operate", json={"operation": "__import__", "payload": {}})
    assert response.status_code == 400
    assert response.get_json()["success"] is False


@pytest.mark.performance
def test_common_views_and_small_trace_complete_within_local_quality_budget(client) -> None:
    """Keep page rendering and a representative trace comfortably interactive locally."""
    started = perf_counter()
    for path in ("/sequential/stack", "/hierarchical/avl", "/graph/graph", "/hash/hash_table", "/sorting/visualizador"):
        assert client.get(path).status_code == 200
    assert client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": "1"}}).status_code == 200
    assert perf_counter() - started < 5.0
