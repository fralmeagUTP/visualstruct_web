"""The educational C API works without caller status; diagnostics remain private."""
from pathlib import Path
import shutil
import subprocess
import pytest
from app.domain.graph.book_c_subset import BookSession, NULL
from app.services.graph_main_service import build_graph_main
from app.adapters.graph_adapter import GraphAdapter

ROOT = Path(__file__).resolve().parents[1]


def compile_run(tmp_path, source):
    gcc = shutil.which('gcc')
    if gcc is None:
        pytest.skip('gcc is required for native public API verification')
    main = tmp_path / 'main.c'
    main.write_text(source)
    binary = tmp_path / 'main'
    result = subprocess.run([gcc, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                             '-I', str(ROOT / 'docs/tads_C'), str(main),
                             str(ROOT / 'docs/tads_C/tad_grafo.c'), '-o', str(binary)],
                            capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, result.stderr
    result = subprocess.run([str(binary)], capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    return result.stdout


def test_all_public_functions_compile_without_status(tmp_path):
    header = (ROOT / 'docs/tads_C/tad_grafo.h').read_text()
    assert 'GrafoEstado' not in header
    assert 'estado' not in header
    source = r'''
#include "tad_grafo.h"
#include <assert.h>
int main(void) {
    Grafo g = grafo_crear();
    g = grafo_insertar_vertice(g, 1);
    g = grafo_insertar_vertice(g, 2);
    g = grafo_insertar_arco(g, 1, 2, 7);
    g = grafo_insertar_arco(g, 2, 1, 7);
    assert(grafo_orden(g) == 2 && grafo_tamano(g) == 2);
    assert(grafo_existe_vertice(g, 1) && grafo_existe_arco(g, 1, 2));
    int costo = 0;
    assert(grafo_costo_arco(g, 1, 2, &costo) && costo == 7);
    assert(grafo_grado_vertice(g, 1) > 0);
    g = grafo_marcar_vertice(g, 1);
    assert(grafo_marcado_vertice(g, 1));
    g = grafo_desmarcar_vertice(g, 1);
    g = grafo_desmarcar(g);
    ListaVertice v = grafo_sucesores(g, 1); assert(v && v->dato == 2); grafo_liberar_vertices(&v);
    v = grafo_predecesores(g, 1); assert(v && v->dato == 2); grafo_liberar_vertices(&v);
    v = grafo_bfs(g, 1); assert(v && v->sig); grafo_liberar_vertices(&v);
    v = grafo_dfs(g, 1); assert(v && v->sig); grafo_liberar_vertices(&v);
    ListaArco a = grafo_dijkstra(g, 1, 2); assert(a && a->costo == 7); grafo_liberar_arcos(&a);
    a = grafo_bellman_ford(g, 1, 2); assert(a && a->costo == 7); grafo_liberar_arcos(&a);
    a = grafo_prim(g, 1); assert(a && a->costo == 7); grafo_liberar_arcos(&a);
    a = grafo_kruskal(g); assert(a && a->costo == 7); grafo_liberar_arcos(&a);
    assert(grafo_vertices(g) && grafo_arcos(g));
    grafo_imprimir_vertices(g); grafo_imprimir_arcos(g);
    g = grafo_eliminar_arco(g, 1, 2);
    g = grafo_eliminar_vertice(g, 2);
    assert(grafo_orden(g) == 1 && grafo_tamano(g) == 0);
    grafo_destruir(&g);
    assert(g.v == NULL && g.a == NULL);
    return 0;
}
'''
    assert 'GrafoEstado' not in source
    compile_run(tmp_path, source)


@pytest.mark.parametrize('function,args,status', [
    ('grafo_insertar_vertice', [3], 0), ('grafo_insertar_arco', [1, 2, 4], 0),
    ('grafo_sucesores', [1], 0), ('grafo_predecesores', [2], 0),
    ('grafo_bfs', [1], 0), ('grafo_dfs', [1], 0),
    ('grafo_dijkstra', [1, 2], 0), ('grafo_bellman_ford', [1, 2], 0),
    ('grafo_prim', [1], 0), ('grafo_kruskal', [], 0),
])
def test_public_interpreter_arity_and_private_diagnostics(function, args, status):
    session = BookSession([1, 2], [(1, 2, 4), (2, 1, 4)], trace=True)
    assert all(name != 'estado' for name, _ in session.program.functions[function]['parameters'])
    result = session.call(function, args)
    assert result['status'] == status
    assert 'estado' not in result['memory']['external']
    assert result['memory']['diagnostic_status'] == status
    assert result['transitions']


@pytest.mark.parametrize('function,args,arcs,status', [
    ('grafo_bfs', [99], [], 2), ('grafo_dfs', [99], [], 2),
    ('grafo_dijkstra', [1, 2], [(1, 2, -1)], 3),
    ('grafo_bellman_ford', [1, 2], [(1, 2, -1), (2, 1, -1)], 4),
    ('grafo_prim', [1], [], 5), ('grafo_kruskal', [], [], 5),
])
def test_private_errors_still_report_real_failure(function, args, arcs, status):
    result = BookSession([1, 2], arcs).call(function, args)
    assert result['status'] == status
    assert result['returned'] == NULL


@pytest.mark.parametrize('function,args', [
    ('grafo_insertar_vertice', [3]), ('grafo_insertar_arco', [1, 2, 4]),
    ('grafo_bfs', [1]), ('grafo_dfs', [1]), ('grafo_dijkstra', [1, 2]),
    ('grafo_bellman_ford', [1, 2]), ('grafo_prim', [1]), ('grafo_kruskal', []),
])
def test_private_allocation_failure_survives_simplified_api(function, args):
    result = BookSession([1, 2], fail_allocation=1).call(function, args)
    assert result['status'] == 1
    assert result['graph_after']['vertices'] == [2, 1]
    assert result['graph_after']['arcs'] == []


def test_generated_program_and_interpreted_stdout_match(tmp_path):
    operations = [('create_graph', {'directed': False}),
                  ('insert_vertex', {'vertex': 1}), ('insert_vertex', {'vertex': 2}),
                  ('insert_edge', {'origin': 1, 'target': 2, 'weight': 7}),
                  ('neighbors', {'vertex': 1}), ('run_bfs', {'start': 1}),
                  ('run_dfs', {'start': 1}),
                  ('run_dijkstra', {'start': 1, 'end': 2}),
                  ('run_bellman_ford', {'start': 1, 'end': 2}),
                  ('run_prim', {'start': 1}), ('run_kruskal', {}),
                  ('run_bfs', {'start': 99})]
    history = [{'operation': op, 'payload': payload} for op, payload in operations]
    main = build_graph_main(history)
    assert 'GrafoEstado' not in main and '&estado' not in main
    assert 'grafo_insertar_vertice(g, 1);' in main
    assert 'grafo_insertar_arco(g, 1, 2, 7);' in main
    native = compile_run(tmp_path, main)
    adapter = GraphAdapter(); adapter.create()
    interpreted = ''
    for op, payload in operations:
        adapter.execute(op, payload)
        interpreted += adapter._last_book_execution['stdout']
    assert interpreted == native

@pytest.mark.parametrize('function,args', [
    ('grafo_bfs', [1]), ('grafo_dfs', [1]), ('grafo_dijkstra', [1, 2]),
    ('grafo_bellman_ford', [1, 2]), ('grafo_prim', [1]), ('grafo_kruskal', []),
])
def test_unobserved_fast_path_preserves_state_status_and_event_count(function, args):
    fixture = ([1, 2], [(1, 2, 4), (2, 1, 4)])
    normal = BookSession(*fixture).call(function, args)
    observed_events = []
    observed = BookSession(*fixture, event_observer=observed_events.append).call(function, args)
    for key in ('returned', 'status', 'graph_after', 'result_items', 'event_count', 'ownership'):
        assert normal[key] == observed[key], key
    assert normal['events'] == [] and observed_events
