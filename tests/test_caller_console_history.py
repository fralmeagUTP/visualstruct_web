"""Finite oracle: generated C17 caller stdout equals interpreted caller output."""
from pathlib import Path
import shutil
import subprocess
import pytest

from app.domain.graph.book_source import ROOT, canonical_source
from app.services.graph_structure_service import GraphStructureService as Service
from app.services.graph_main_service import build_graph_main


def history(edges=()):
    entries = [('create_graph', {'directed': True})]
    entries += [('insert_vertex', {'vertex': v}) for v in [1, 2, 3]]
    entries += [('insert_edge', {'origin': a, 'target': b, 'weight': w}) for a, b, w in edges]
    return [{'operation': op, 'payload': p, 'source_contract': 'graph-book/v1'} for op, p in entries]


@pytest.mark.parametrize('operation,payload,edges', [
    ('run_dijkstra', {'start': 1, 'end': 3}, [(1, 3, 9), (1, 2, 2), (2, 3, 3)]),
    ('run_dijkstra', {'start': 1, 'end': 3}, [(1, 2, 2)]),
    ('run_dijkstra', {'start': 1, 'end': 1}, []),
    ('run_dijkstra', {'start': 1, 'end': 3}, [(1, 2, -1)]),
    ('run_bfs', {'start': 1}, [(1, 2, 2)]),
    ('run_dfs', {'start': 1}, [(1, 2, 2)]),
    ('run_bellman_ford', {'start': 1, 'end': 3}, [(1, 2, 2), (2, 3, -1)]),
    ('run_prim', {'start': 1}, []),
    ('run_kruskal', {}, []),
    ('neighbors', {'vertex': 1}, [(1, 2, 2)]),
    ('list_vertices', {}, []),
    ('list_edges', {}, [(1, 2, 2)]),
    ('exists_vertex', {'vertex': 1}, []),
    ('exists_edge', {'origin': 1, 'target': 2}, []),
    ('edge_weight', {'origin': 1, 'target': 2}, [(1, 2, 2)]),
    ('edge_weight', {'origin': 1, 'target': 2}, []),
])
def test_native_caller_stdout_and_cursor_prefix(tmp_path, operation, payload, edges):
    before = history(edges)
    data = Service.execute_operation('graph', operation, payload, before, execution_mode='step')
    assert 'console_stdout' in data, data
    caller = tmp_path / 'main.c'
    caller.write_text(data['main_c'], encoding='utf8')
    for name in ['tad_grafo.c', 'tad_grafo.h']:
        shutil.copyfile(ROOT / 'docs/tads_C' / name, tmp_path / name)
    compiler = shutil.which('gcc')
    assert compiler, 'Native C17 compiler is required for this oracle'
    executable = tmp_path / 'caller.exe'
    built = subprocess.run([compiler, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                            str(caller), str(tmp_path / 'tad_grafo.c'), '-o', str(executable)],
                           capture_output=True, text=True, timeout=30)
    assert built.returncode == 0, built.stderr
    native = subprocess.run([str(executable)], capture_output=True, text=True, timeout=15)
    assert native.returncode == 0, native.stderr
    assert native.stdout == data['console_prefix'] + data['console_stdout']
    trace = data['execution_trace']
    # Logical trace before transport contains the exact per-instruction snapshots.
    snapshots = [step['pedagogy']['memory_state']['console_stdout'] for step in trace['steps']]
    emitted = ''.join(fragment for step in trace['steps'] for fragment in step['console'])
    assert emitted == data['console_stdout'] == snapshots[-1]
    assert snapshots[0] == ''
    assert all(emitted.startswith(value) for value in snapshots)
    caller_events = [step for step in trace['steps'] if step['console']]
    assert caller_events and all(step['pedagogy']['instruction_event']['caller_C_executed'] for step in caller_events)
    # Back and replay read snapshots; they never append an already printed fragment.
    for cursor in [len(snapshots)-1, 0, len(snapshots)-1, len(snapshots)//2, len(snapshots)-1]:
        visible = data['console_prefix'] + snapshots[cursor]
        assert native.stdout.startswith(visible)
    reloaded = Service.get_view_model('graph', data['history'])
    assert reloaded['console_stdout'] == native.stdout
    normal = Service.execute_operation('graph', operation, payload, before, execution_mode='normal')
    assert normal['console_prefix'] + normal['console_stdout'] == native.stdout
    assert data['main_c'] == build_graph_main(data['history'])
    canonical_source()  # Byte-locked C/H remain unchanged.


def test_void_mutations_do_not_gain_invented_messages():
    for operation, payload in [('remove_vertex', {'vertex': 1}),
                               ('remove_edge', {'origin': 1, 'target': 2}),
                               ('clear_graph', {})]:
        data = Service.execute_operation('graph', operation, payload, history())
        assert data['console_stdout'] == ''
