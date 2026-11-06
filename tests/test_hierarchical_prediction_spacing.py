"""Regression coverage for the hierarchical prediction shortcut spacing."""

from __future__ import annotations

from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]


def test_prediction_shortcut_has_scoped_top_margin() -> None:
    """Keep a small gap without changing shared button or action-row spacing."""
    css = (ROOT / "static/css/contextual_help.css").read_text(encoding="utf-8")
    assert ".hier-classroom-controls > #hier-open-prediction { margin-top: .5rem; }" in css
    js = (ROOT / "static/js/hierarchical.js").read_text(encoding="utf-8")
    assert 'predictLink.id = "hier-open-prediction"' in js
    assert "classroomControls.append(actions, predictLink," in js


@pytest.mark.parametrize("structure", ["abb", "avl", "red_black", "binary_heap"])
def test_each_structure_loads_spacing_stylesheet(client, structure: str) -> None:
    """All four trees/heaps use the shared control view and patched stylesheet."""
    response = client.get(f"/hierarchical/{structure}")
    assert response.status_code == 200
    assert b"css/contextual_help.css" in response.data
    assert b'id="hier-sim-play"' in response.data
    assert b'id="hier-step-toggle"' in response.data
    assert b'id="hier-prediction"' in response.data
