import json
import os
from pathlib import Path
import subprocess
import sys
from collections import Counter

import pytest

from app.domain.hash.tad_wrappers import TablaHash
from app.services.trace.strategies import TreeTraceStrategy
from app.services.c_code_service import CCodeService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.graph_structure_service import GraphStructureService
from app.services.trace import TraceEngine
from app.adapters.priority_queue_adapter import PriorityQueueAdapter
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph import Grafo
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting.tad_ordenamiento import SORTING_ALGORITHMS, SortingInterpreter
from app.adapters.sublist_adapter import SublistAdapter


ROOT = Path(__file__).resolve().parents[1]


def test_hash_001_backend_keeps_c_fixed_capacity() -> None:
    table = TablaHash[int, str](capacidad=3)
    for key in (1, 4, 7):
        table.insertar(key, str(key))
    assert table.capacidad() == 3

    c_source = (ROOT / "docs/tads_C/tad_tabla_hash.c").read_text(encoding="utf-8")
    assert "realloc(" not in c_source
    assert "rehash" not in c_source.lower()

    finding = json.loads((ROOT / "docs/qa/findings/HASH-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_hash_002_integer_bucket_mapping_matches_c_modulo() -> None:
    table = TablaHash[int, str](17)
    assert [table._indice(key) for key in (-18, -1, 0, 1, 18)] == [16, 16, 0, 1, 1]
    with pytest.raises(ValueError, match="entero"):
        table._indice("A")

    finding = json.loads((ROOT / "docs/qa/findings/HASH-002.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_heap_001_reproduces_omitted_sift_up_states() -> None:
    before = {"kind": "heap", "array": [2, 5, 3], "root": {}, "size": 3, "empty": False}
    after = {"kind": "heap", "array": [1, 2, 3, 5], "root": {}, "size": 4, "empty": False}
    boundaries = TreeTraceStrategy().build_heap_boundaries(before, after, 6, ["if"] * 6)
    arrays = [state["array"] for state in boundaries]
    assert [2, 5, 3, 1] in arrays
    assert [2, 1, 3, 5] in arrays

    finding = json.loads((ROOT / "docs/qa/findings/HEAP-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_stack_001_top_snippet_is_real_c_function() -> None:
    snippet = CCodeService.get_structure_data("stack")["operations"]["cima"]
    header = (ROOT / "docs/tads_C/tad_pila.h").read_text(encoding="utf-8")
    source = (ROOT / "docs/tads_C/tad_pila.c").read_text(encoding="utf-8")
    assert "int pila_cima(ptrPila p)" in snippet
    assert "int pila_cima(ptrPila p);" in header
    assert "int pila_cima(ptrPila p)" in source

    finding = json.loads((ROOT / "docs/qa/findings/STACK-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_stack_002_reproduces_missing_temporary_node(client) -> None:
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "9"}},
    )
    steps = response.get_json()["execution_trace"]["steps"]
    temporary_lines = [
        step for step in steps
        if any(token in str(step.get("line_text", "")) for token in ("malloc", "aux->nro", "aux->sgte"))
    ]
    assert temporary_lines
    assert all("temporaries" in step["state_after"] for step in temporary_lines)

    finding = json.loads((ROOT / "docs/qa/findings/STACK-002.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"


def test_queue_001_query_snippets_are_real_c_functions() -> None:
    operations = CCodeService.get_structure_data("queue")["operations"]
    c_source = (ROOT / "docs/tads_C/tad_cola.c").read_text(encoding="utf-8")
    assert "int cola_frente(" in c_source
    assert "int cola_frente(struct Cola q)" in operations["frente"]
    assert "int cola_final(struct Cola q)" in operations["final"]

    finding = json.loads((ROOT / "docs/qa/findings/QUEUE-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_priority_001_visual_and_internal_keep_arrival_order() -> None:
    adapter = PriorityQueueAdapter()
    for value, priority in ((100, 5), (200, 1), (300, 3)):
        adapter.execute("encolar", {"value": value, "priority": priority})
    visual = [(item["value"], item["priority"]) for item in adapter.to_visual_state()["items"]]
    internal = adapter._structure.a_lista()  # noqa: SLF001
    assert visual == [(100, 5), (200, 1), (300, 3)]
    assert internal == visual

    c_source = (ROOT / "docs/tads_C/tad_cola_prioridad.c").read_text(encoding="utf-8")
    enqueue_body = c_source[c_source.index("bool cp_encolar"):c_source.index("bool cp_desencolar")]
    assert "cola->atras->sgte = nuevo" in enqueue_body
    assert "prioridad <" not in enqueue_body
    assert "actual->prioridad < objetivo->prioridad" in c_source

    finding = json.loads((ROOT / "docs/qa/findings/PRIORITY-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_priority_002_front_uses_same_stable_selection_as_dequeue() -> None:
    adapter = PriorityQueueAdapter()
    adapter.execute("encolar", {"value": 100, "priority": 5})
    adapter.execute("encolar", {"value": 200, "priority": 1})
    assert adapter.execute("frente", {})["result"] == 200
    assert adapter.to_visual_state()["items"][0]["value"] == 100
    snippet = CCodeService.get_structure_data("priority_queue")["operations"]["frente"]
    assert "bool cp_frente(" in snippet

    finding = json.loads((ROOT / "docs/qa/findings/PRIORITY-002.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"


def test_linked_001_operations_have_c_implementations_and_mappings() -> None:
    header = (ROOT / "docs/tads_C/tad_lista.h").read_text(encoding="utf-8")
    operations = CCodeService.get_structure_data("linked_list")["operations"]
    for name in ("invertir", "primero", "ultimo", "eliminar_posicion"):
        assert f"lista_{name}" in header
        assert name in operations

    finding = json.loads((ROOT / "docs/qa/findings/LINKED-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_circular_001_detects_missing_single_node_self_loop() -> None:
    javascript = (ROOT / "static/js/sequential.js").read_text(encoding="utf-8")
    assert "if (nodes.length < 1)" in javascript
    assert "if (circular && items.length > 0)" in javascript

    finding = json.loads((ROOT / "docs/qa/findings/CIRCULAR-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_sublist_001_reproduces_duplicate_parent_collapse() -> None:
    adapter = SublistAdapter()
    adapter.execute("insertar_padre", {"parent": 1})
    adapter.execute("insertar_padre", {"parent": 1})
    assert adapter._structure._lista_ref[0].sgte is not None  # noqa: SLF001
    state = adapter.to_visual_state()
    assert state["size"] == 2
    assert len({item["id"] for item in state["items"]}) == 2
    finding = json.loads((ROOT / "docs/qa/findings/SUBLIST-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"


def test_sublist_002_detects_clear_without_c_destroy() -> None:
    source = (ROOT / "app/domain/sequential/tad_wrappers.py").read_text(encoding="utf-8")
    body = source[source.index("class Sublista"):]
    clear_body = body[body.index("def limpiar"):body.index("def __repr__")]
    assert "sublista_destruir" in clear_body
    finding = json.loads((ROOT / "docs/qa/findings/SUBLIST-002.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_abb_001_reproduces_missing_successor_copy_state() -> None:
    before = {"kind": "binary_tree", "title": "ABB", "root": {"value": 2, "left": {"value": 1, "left": None, "right": None}, "right": {"value": 3, "left": None, "right": None}}, "size": 3}
    after = {"kind": "binary_tree", "title": "ABB", "root": {"value": 3, "left": {"value": 1, "left": None, "right": None}, "right": None}, "size": 2}
    lines = ["ABBNodo* temp = abb_encontrarMinimo(nodo->derecho);", "nodo->valor = temp->valor;", "nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);"]
    states = TreeTraceStrategy().build_boundaries(before, after, 3, "eliminar", {"value": 2}, lines)
    roots = [state["root"] for state in states]
    assert any(root.get("value") == 3 and isinstance(root.get("right"), dict) and root["right"].get("value") == 3 for root in roots)
    finding = json.loads((ROOT / "docs/qa/findings/ABB-001.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_avl_001_reproduces_missing_first_half_of_double_rotation() -> None:
    before = {"kind": "binary_tree", "title": "AVL", "root": {"value": 30, "left": {"value": 10, "left": None, "right": None}, "right": None}, "size": 2}
    after = {"kind": "binary_tree", "title": "AVL", "root": {"value": 20, "left": {"value": 10, "left": None, "right": None}, "right": {"value": 30, "left": None, "right": None}}, "size": 3}
    lines = ["void avl_insertar(AVL *raiz, int x) {", "padre->der = nuevo;", "avl_RDD(raiz, padre);", "return;"]
    states = TreeTraceStrategy().build_boundaries(before, after, 4, "insertar", {"value": 20}, lines)
    roots = [state["root"] for state in states]

    def is_after_first_rotation(root: dict) -> bool:
        left = root.get("left")
        return (
            root.get("value") == 30
            and isinstance(left, dict)
            and left.get("value") == 20
            and isinstance(left.get("left"), dict)
            and left["left"].get("value") == 10
        )

    assert any(is_after_first_rotation(root) for root in roots)
    finding = json.loads((ROOT / "docs/qa/findings/AVL-001.json").read_text(encoding="utf-8"))
    assert finding["result"] == "failed"
    assert finding["severity"] == "high"


def test_rbt_001_reproduces_fixup_recolors_at_call_site() -> None:
    history: list[dict] = []
    for value in (10, 5, 15):
        result = HierarchicalStructureService.execute_operation(
            structure_id="red_black", operation_name="insertar",
            payload={"value": str(value)}, history=history,
        )
        history = result["history"]
    result = HierarchicalStructureService.execute_operation(
        structure_id="red_black", operation_name="insertar",
        payload={"value": "1"}, history=history,
    )
    changed_lines = [
        str(step.get("line_text", "")).strip()
        for step in result["execution_trace"]["steps"]
        if (step.get("state_snapshot") or {}) != (step.get("state_after") or {})
    ]
    assert "n->padre->rbt_color = NEGRO;" in changed_lines
    assert "t->rbt_color = NEGRO;" in changed_lines
    assert "a->rbt_color = ROJO;" in changed_lines
    finding = json.loads((ROOT / "docs/qa/findings/RBT-001.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_rbt_002_delete_trace_follows_real_branch_and_delays_final_state() -> None:
    history: list[dict] = []
    for value in (7, 3, 18, 10, 22, 8, 11, 26):
        result = HierarchicalStructureService.execute_operation(
            structure_id="red_black", operation_name="insertar",
            payload={"value": str(value)}, history=history,
        )
        history = result["history"]
    result = HierarchicalStructureService.execute_operation(
        structure_id="red_black", operation_name="eliminar",
        payload={"value": "3"}, history=history,
    )
    lines = [str(step.get("line_text", "")).strip() for step in result["execution_trace"]["steps"]]
    assert lines.count("while (z != NULL && z->nro != key) {") == 2
    assert "x = z->der;" in lines
    assert "x = z->izq;" not in lines
    steps = result["execution_trace"]["steps"]
    free_step = next(step for step in steps if str(step.get("line_text", "")).strip() == "free(z);")
    assert free_step["state_after"]["size"] == 8
    assert steps[-1]["state_after"]["size"] == 7
    fix_step = next(step for step in steps if "arreglarEliminacion" in str(step.get("line_text", "")))
    assert set(fix_step["debug"]["logical_nodes"]) == {"z", "y", "x", "x_parent", "w"}
    finding = json.loads((ROOT / "docs/qa/findings/RBT-002.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_graph_001_c_and_python_share_auto_create_and_update_contract() -> None:
    graph = Grafo(dirigido=True)
    graph.insertar_arista(1, 2, 5)
    graph.insertar_arista(1, 2, 7)
    assert graph.vertices() == [1, 2]
    assert graph.aristas() == [(1, 2, 7.0)]

    source = (ROOT / "docs/tads_C/tad_grafo.c").read_text(encoding="utf-8")
    body = source[source.index("Grafo grafo_insertar_arco"):source.index("void grafo_imprimir_vertices")]
    assert "grafo_insertar_vertice" in body
    assert "existente->costo = z" in body
    assert "malloc" in body
    finding = json.loads((ROOT / "docs/qa/findings/GRAPH-001.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_graph_002_rejects_fractional_weight_without_mutation() -> None:
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": False})
    try:
        adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 2.75})
        assert False, "El contrato C debe rechazar pesos fraccionarios."
    except ValueError as error:
        assert "entero" in str(error)
    state = adapter.to_visual_state()
    assert state["directed"] is False
    assert state["edges"] == []
    header = (ROOT / "docs/tads_C/tad_grafo.h").read_text(encoding="utf-8")
    assert "grafo dirigido ponderado" in header.lower()
    assert "int costo" in header
    finding = json.loads((ROOT / "docs/qa/findings/GRAPH-002.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_graph_003_c_and_backend_return_direct_visit_order() -> None:
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": True})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 1})
    adapter.execute("insert_edge", {"origin": 2, "target": 3, "weight": 1})
    assert adapter.execute("run_bfs", {"start": 1})["result"] == [1, 2, 3]
    assert adapter.execute("run_dfs", {"start": 1})["result"] == [1, 2, 3]
    source = (ROOT / "docs/tads_C/tad_grafo.c").read_text(encoding="utf-8")
    assert "else ultimo->sig = tmp;" in source
    assert "grafo_agregar_recorrido(recorrido, tmp);" in source
    finding = json.loads((ROOT / "docs/qa/findings/GRAPH-003.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_graph_004_c_and_backend_reject_negative_dijkstra_graph() -> None:
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": True})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 1})
    adapter.execute("insert_edge", {"origin": 2, "target": 3, "weight": 2})
    adapter.execute("insert_edge", {"origin": 1, "target": 3, "weight": -5})
    try:
        adapter.execute("run_dijkstra", {"start": 1, "end": 3})
        assert False, "El backend debe bloquear cualquier peso negativo."
    except Exception as error:  # noqa: BLE001
        assert "negativo" in str(error).lower()
    source = (ROOT / "docs/tads_C/tad_grafo.c").read_text(encoding="utf-8")
    assert "if (grafo_tiene_peso_negativo(g)) {" in source
    finding = json.loads((ROOT / "docs/qa/findings/GRAPH-004.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_graph_005_reproduces_missing_shortest_path_temporary_tables() -> None:
    history: list[dict] = []
    for operation, payload in (
        ("create_graph", {"directed": "true"}),
        ("insert_edge", {"origin": "1", "target": "2", "weight": "4"}),
        ("insert_edge", {"origin": "2", "target": "3", "weight": "1"}),
    ):
        result = GraphStructureService.execute_operation("graph", operation, payload, history)
        history = result["history"]
    result = GraphStructureService.execute_operation(
        "graph", "run_dijkstra", {"start": "1", "end": "3"}, history
    )
    progress = [
        step.get("debug", {}).get("graph_progress", {})
        for step in result["execution_trace"]["steps"]
        if isinstance(step.get("debug"), dict)
    ]
    assert progress
    assert all(all(key in item for key in ("distances", "previous", "visited", "candidates")) for item in progress)
    finding = json.loads((ROOT / "docs/qa/findings/GRAPH-005.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_graph_006_reports_minimum_spanning_forest_and_connectivity() -> None:
    adapter = GraphAdapter()
    for vertex in (1, 2, 3, 4):
        adapter.execute("insert_vertex", {"vertex": vertex})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 1})
    adapter.execute("insert_edge", {"origin": 2, "target": 3, "weight": 2})
    prim = adapter.execute("run_prim", {"start": 1})["result"]
    kruskal = adapter.execute("run_kruskal", {})["result"]
    assert len(prim["mst_edges"]) == 2 and prim["connected"] is False
    assert len(kruskal["mst_edges"]) == 2 and kruskal["connected"] is False
    assert prim["kind"] == kruskal["kind"] == "minimum_spanning_forest"
    assert prim["components_count"] == kruskal["components_count"] == 2
    adapter.execute("create_graph", {"directed": True})
    try:
        adapter.execute("run_prim", {"start": 1})
        assert False, "El frontend debe bloquear Prim dirigido."
    except ValueError:
        pass
    source = (ROOT / "docs/tads_C/tad_grafo.c").read_text(encoding="utf-8")
    assert "ListaArco grafo_prim(Grafo g, int inicio)" in source
    assert "dirigido" not in source[source.index("ListaArco grafo_prim"):source.index("typedef struct Conjunto")].lower()
    finding = json.loads((ROOT / "docs/qa/findings/GRAPH-006.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_sort_001_reproduces_unshown_quicksort_failed_comparisons() -> None:
    result = SortingInterpreter([1, 2, 3], "quicksort").run()
    pivot_steps = [step for step in result["steps"] if step.get("pivot_index") == 1]
    assert pivot_steps
    assert any(step.get("comparing_indices") == [1, 1] for step in pivot_steps)
    source = (ROOT / "docs/tads_C/tad_ordenamiento.c").read_text(encoding="utf-8")
    assert "while (arreglo[i] < pivote)" in source
    assert "while (arreglo[j] > pivote)" in source
    finding = json.loads((ROOT / "docs/qa/findings/SORT-001.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_sort_002_reproduces_missing_source_mapping_for_merge_and_binsort() -> None:
    operations = CCodeService.get_structure_data("sorting_array")["operations"]
    missing_by_algorithm: dict[str, int] = {}
    for algorithm in ("mergesort", "binsort"):
        adapter = SortingAdapter()
        adapter.execute("create_array", {"values": "5,-1,4,2,2,0"})
        adapter.execute("select_algorithm", {"algorithm_id": algorithm})
        result = adapter.execute("run", {"mode": "step_by_step", "source_code": operations[algorithm]})
        missing_by_algorithm[algorithm] = sum(
            step.get("line_index") is None for step in result["execution_trace"]["steps"]
        )
    assert missing_by_algorithm["mergesort"] == 0
    assert missing_by_algorithm["binsort"] == 0
    finding = json.loads((ROOT / "docs/qa/findings/SORT-002.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_sort_003_radix_int_min_uses_defined_unsigned_magnitude() -> None:
    int_min = -(2**31)
    result = SortingInterpreter([0, int_min, -1, 7], "radixsort").run()
    assert result["final_state"]["items"] == [int_min, -1, 0, 7]
    source = (ROOT / "docs/tads_C/tad_ordenamiento.c").read_text(encoding="utf-8")
    assert "negativos[cant_negativos++] = 0U - (uint32_t)arreglo[i];" in source
    assert "magnitud == (uint32_t)INT_MAX + 1U ? INT_MIN" in source
    assert "negativos[cant_negativos++] = -arreglo[i];" not in source
    finding = json.loads((ROOT / "docs/qa/findings/SORT-003.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "critical"


def test_sort_004_rejects_unbounded_counting_range_before_allocation() -> None:
    source = (ROOT / "docs/tads_C/tad_ordenamiento.c").read_text(encoding="utf-8")
    counting = source[source.index("int ordenar_counting_sort"):source.index("int ordenar_binsort")]
    assert "maximo - (long long)minimo + 1LL" in counting
    assert "calloc(rango" in counting
    assert "rango > ORDENAMIENTO_RANGO_MAX" in counting
    adapter_source = (ROOT / "app/domain/sorting/tad_ordenamiento.py").read_text(encoding="utf-8")
    assert "if rng > ORDENAMIENTO_RANGO_MAX" in adapter_source
    finding = json.loads((ROOT / "docs/qa/findings/SORT-004.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_all_sorting_algorithms_preserve_multiset_and_match_both_modes() -> None:
    values = [5, -1, 4, 2, 2, 0]
    for algorithm in (item["id"] for item in SORTING_ALGORITHMS):
        outputs = []
        for mode in ("fast", "step_by_step"):
            adapter = SortingAdapter()
            adapter.execute("create_array", {"values": values})
            adapter.execute("select_algorithm", {"algorithm_id": algorithm})
            result = adapter.execute("run", {"mode": mode, "source_code": ""})
            output = result["visual_state"]["items"]
            assert output == sorted(values)
            assert Counter(output) == Counter(values)
            assert result["execution_trace"]["final_state"] == result["visual_state"]
            outputs.append(output)
        assert outputs[0] == outputs[1]


def test_trace_001_detects_printf_reconstruction_from_source_and_message() -> None:
    for script_name in ("sequential.js", "hierarchical.js", "graph.js", "hash.js"):
        source = (ROOT / "static/js" / script_name).read_text(encoding="utf-8")
        assert "Array.isArray(step.console)" in source
        assert "[printf] ${finalMessage}" not in source
    finding = json.loads((ROOT / "docs/qa/findings/TRACE-001.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_trace_002_validator_accepts_discontinuous_frames() -> None:
    trace = {
        "structure_id": "stack",
        "steps": [
            {"line_index": 0, "line_text": "a", "event_type": "line", "phase": "start", "state_snapshot": {"size": 0}, "state_after": {"size": 1}},
            {"line_index": 1, "line_text": "b", "event_type": "line", "phase": "end", "state_snapshot": {"size": 99}, "state_after": {"size": 2}},
        ],
        "final_state": {"size": 2},
    }
    with pytest.raises(ValueError, match="Discontinuidad"):
        TraceEngine.validate_legacy_trace(trace)
    finding = json.loads((ROOT / "docs/qa/findings/TRACE-002.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_trace_003_validator_accepts_source_line_mismatch() -> None:
    trace = {
        "structure_id": "queue",
        "source_code": "linea real",
        "steps": [{"line_index": 50, "line_text": "linea inventada", "event_type": "line", "phase": "single", "state_snapshot": {}, "state_after": {}}],
        "final_state": {},
    }
    with pytest.raises(ValueError, match="fuera de rango"):
        TraceEngine.validate_legacy_trace(trace)
    finding = json.loads((ROOT / "docs/qa/findings/TRACE-003.json").read_text(encoding="utf-8"))
    assert finding["severity"] == "high"


def test_trace_player_exposes_reversible_control_contract() -> None:
    source = (ROOT / "static/js/interpreter_runtime.js").read_text(encoding="utf-8")
    for token in ("playFromStart", "pause", "step", "prev", "reset", "applyStateSnapshot", "applyStateAfter"):
        assert token in source
    assert "applyStateAfter(previousStep);" in source
    assert "applyStateSnapshot(firstStep);" in source
