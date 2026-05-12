"""Regression tests for interpreter coherence in hierarchical module."""

from __future__ import annotations

from pathlib import Path

from app.services.hierarchical_structure_service import HierarchicalStructureService



def _operate_hier(
    structure_id: str,
    operation: str,
    payload: dict[str, str] | None,
    history: list[dict],
) -> dict:
    return HierarchicalStructureService.execute_operation(
        structure_id=structure_id,
        operation_name=operation,
        payload=payload or {},
        history=history,
    )



def test_red_black_null_render_contract_css_js_and_state() -> None:
    """NULL leaves in red-black rendering must keep the black/nil contract."""
    css_text = Path("static/css/styles.css").read_text(encoding="utf-8", errors="replace")
    js_text = Path("static/js/hierarchical.js").read_text(encoding="utf-8", errors="replace")

    assert ".viz-tree-node.nil" in css_text
    assert "fill: #12161b;" in css_text
    assert 'class="viz-tree-node black nil"' in js_text
    assert 'class="viz-tree-text nil">NULL</text>' in js_text

    history: list[dict] = []
    for value in [10, 5, 15]:
        result = _operate_hier("red_black", "insertar", {"value": str(value)}, history)
        assert result["success"] is True
        history = result["history"]

    state = result["visual_state"]
    assert state["validation"] is True
    root = state["root"]
    assert root is not None
    assert root["color"] == "BLACK"
    # En un arbol con al menos 1 nodo, debe haber ramas ausentes para dibujar NULL.
    def _count_missing(node: dict | None) -> int:
        if node is None:
            return 0
        missing = 0
        left = node.get("left")
        right = node.get("right")
        if left is None:
            missing += 1
        if right is None:
            missing += 1
        return missing + _count_missing(left) + _count_missing(right)

    assert _count_missing(root) >= 2



def test_avl_and_red_black_successive_deletions_keep_validation() -> None:
    """Successive deletions should preserve invariants after each step."""
    avl_history: list[dict] = []
    for value in [40, 20, 10, 30, 60, 50, 70, 65]:
        res = _operate_hier("avl", "insertar", {"value": str(value)}, avl_history)
        assert res["success"] is True
        assert res["visual_state"]["validation"] is True
        avl_history = res["history"]

    for value in [10, 65, 40, 30]:
        res = _operate_hier("avl", "eliminar", {"value": str(value)}, avl_history)
        assert res["success"] is True
        assert res["visual_state"]["validation"] is True
        avl_history = res["history"]

    rn_history: list[dict] = []
    for value in [40, 20, 10, 30, 60, 50, 70, 65]:
        res = _operate_hier("red_black", "insertar", {"value": str(value)}, rn_history)
        assert res["success"] is True
        assert res["visual_state"]["validation"] is True
        rn_history = res["history"]

    for value in [10, 65, 40, 30]:
        res = _operate_hier("red_black", "eliminar", {"value": str(value)}, rn_history)
        assert res["success"] is True
        assert res["visual_state"]["validation"] is True
        rn_history = res["history"]



def test_hierarchical_history_replay_matches_visual_state_main_coherence() -> None:
    """Replaying operation history must reproduce the exact final visual state."""
    history: list[dict] = []
    final_response: dict | None = None

    steps = [
        ("insertar", {"value": "50"}),
        ("insertar", {"value": "10"}),
        ("insertar", {"value": "70"}),
        ("insertar", {"value": "60"}),
        ("eliminar", {"value": "10"}),
        ("buscar", {"value": "60"}),
        ("validar", {}),
    ]

    for operation, payload in steps:
        response = _operate_hier("abb", operation, payload, history)
        assert response["success"] is True
        history = response["history"]
        final_response = response

    assert final_response is not None

    rebuilt_model = HierarchicalStructureService.get_view_model("abb", history)
    assert rebuilt_model["visual_state"] == final_response["visual_state"]
    assert rebuilt_model["visual_state"]["traversals"]["inorden"] == [50, 60, 70]
    assert rebuilt_model["visual_state"]["validation"] is True
    assert len(history) == 5

