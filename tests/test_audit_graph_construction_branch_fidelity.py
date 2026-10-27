"""Graph construction branch fidelity: actual C branches, private fresh service objects."""
from app.services.graph_structure_service import GraphStructureService


def test_insert_first_vertex_does_not_highlight_unexecuted_duplicate_scan():
    # grafo_insertar_vertice: actual = g.v = NULL, so while body never runs.
    result = GraphStructureService.execute_operation("graph", "insert_vertex", {"vertex": 7}, [])
    assert result["success"] is True
    lines = [step["line_text"].strip() for step in result["execution_trace"]["steps"]]
    assert not any("actual->dato == x" in line or "actual = actual->sig" in line for line in lines), lines


def test_remove_single_vertex_does_not_highlight_else_branch():
    # The head contains x=7, so C unlinks/frees it in the true branch.
    history = [{"operation": "insert_vertex", "payload": {"vertex": 7}}]
    result = GraphStructureService.execute_operation("graph", "remove_vertex", {"vertex": 7}, history)
    assert result["success"] is True
    assert result["visual_state"]["nodes"] == []
    lines = [step["line_text"].strip() for step in result["execution_trace"]["steps"]]
    assert not any("k->sig" in line or "free(p)" in line for line in lines), lines
