from _rbt_legacy_consumer_oracle import assert_rbt_consumer
from _stack_push_memory_oracle import assert_empty_stack_push_memory
from _tree_intermediate_consumer_oracle import assert_tree_intermediate_consumer
from pathlib import Path

from app.adapters.sublist_adapter import SublistAdapter
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.trace.strategies import TreeTraceStrategy


ROOT = Path(__file__).resolve().parents[1]


def _tree_run(structure_id, values, operation, payload):
    history = []
    for value in values:
        result = HierarchicalStructureService.execute_operation(structure_id, "insertar", {"value": value}, history)
        history = result["history"]
    return HierarchicalStructureService.execute_operation(structure_id, operation, payload, history)


def test_abb_successor_copy_precedes_successor_unlink():
    result = _tree_run("abb", [2, 1, 3], "eliminar", {"value": 2})
    copied, unlinked = assert_tree_intermediate_consumer(result, "abb")
    assert copied["value"] == copied["right"]["value"] == 3
    assert unlinked["right"] is None


def test_avl_lr_exposes_first_rotation_with_recomputed_metadata():
    result = _tree_run("avl", [30, 10], "insertar", {"value": 20})
    middle = assert_tree_intermediate_consumer(result, "lr")
    assert middle["left"]["left"]["value"] == 10
    assert middle["height"] == 3
    assert middle["balance_factor"] == -2


def test_avl_rl_exposes_first_rotation_with_recomputed_metadata():
    result = _tree_run("avl", [10, 30], "insertar", {"value": 20})
    middle = assert_tree_intermediate_consumer(result, "rl")
    assert middle["right"]["right"]["value"] == 30
    assert middle["height"] == 3
    assert middle["balance_factor"] == 2


def test_rbt_recolors_only_on_the_corresponding_c_assignments():
    result = _tree_run("red_black", [10, 5, 15], "insertar", {"value": 1})
    changed = [step for step in result["execution_trace"]["steps"] if step["state_snapshot"] != step["state_after"]]
    lines = [step["line_text"].strip() for step in changed]
    for assignment in ("n->padre->rbt_color = NEGRO;", "t->rbt_color = NEGRO;", "a->rbt_color = ROJO;"):
        assert assignment in lines
    assert "rbt_insercion_caso1(actual, arbol);" not in lines


def test_rbt_rotation_is_applied_on_the_c_rotation_call():
    result = _tree_run("red_black", [10, 5], "insertar", {"value": 1})
    rotation = assert_rbt_consumer(result, "rotation")
    assert rotation["state_after"]["root"]["value"] == 5


def test_heap_insert_exposes_append_and_each_sift_up_swap():
    result = _tree_run("binary_heap", [2, 5, 3], "insertar", {"value": 1})
    arrays = [step["state_after"]["array"] for step in result["execution_trace"]["steps"]]
    assert [2, 5, 3, 1] in arrays
    assert [2, 1, 3, 5] in arrays
    assert arrays[-1] == [1, 2, 3, 5]


def test_heap_extract_exposes_replacement_and_sift_down_swap():
    result = _tree_run("binary_heap", [1, 2, 3, 5], "extraer_raiz", {})
    arrays = [step["state_after"]["array"] for step in result["execution_trace"]["steps"]]
    assert [5, 2, 3] in arrays
    assert arrays[-1] == [2, 5, 3]


def test_stack_trace_transports_temporary_allocation_value_and_link(client):
    response = client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": 9}})
    assert response.status_code == 200
    assert_empty_stack_push_memory(response.get_json(), 9)


def test_circular_single_node_renderer_keeps_self_link_contract():
    javascript = (ROOT / "static/js/sequential.js").read_text(encoding="utf-8")
    assert "if (nodes.length < 1)" in javascript
    assert "if (circular && items.length > 0)" in javascript


def test_sublist_duplicate_identity_and_child_before_parent_destruction():
    adapter = SublistAdapter()
    adapter.execute("insertar_padre", {"parent": 1})
    adapter.execute("insertar_padre", {"parent": 1})
    adapter.execute("insertar_hijo", {"parent": 1, "child": 8})
    state = adapter.to_visual_state()
    assert [item["parent"] for item in state["items"]] == [1, 1]
    assert len({item["id"] for item in state["items"]}) == 2
    adapter.execute("limpiar", {})
    events = adapter._structure.last_destroy_events  # noqa: SLF001
    assert [event["stage"] for event in events] == ["free_child", "free_parent", "free_parent"]
    assert events[0]["parent_logical_id"] == state["items"][0]["id"]


def test_sublist_clear_trace_removes_children_before_their_parent(client):
    client.post("/sequential/sublist/operate", json={"operation": "insertar_padre", "payload": {"parent": 4}})
    client.post("/sequential/sublist/operate", json={"operation": "insertar_hijo", "payload": {"parent": 4, "child": 8}})
    client.post("/sequential/sublist/operate", json={"operation": "insertar_hijo", "payload": {"parent": 4, "child": 9}})
    response = client.post("/sequential/sublist/operate", json={"operation": "limpiar", "payload": {}})
    states = [step["state_after"] for step in response.get_json()["execution_trace"]["steps"]]
    assert any(state["items"] and state["items"][0]["children"] == [9] for state in states)
    assert any(state["items"] and state["items"][0]["children"] == [] for state in states)
    assert states[-1]["items"] == []
