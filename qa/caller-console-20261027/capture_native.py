"""Reproduce the finite Dijkstra evidence with the actual generated main."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from app.services.graph_structure_service import GraphStructureService as Service
from app.domain.graph.book_source import HASHES, canonical_source

OUT = Path(__file__).resolve().parent
cases = [('route', [(1, 2, 2), (2, 3, 3)], 1, 3),
         ('unreachable', [(1, 2, 2)], 1, 3),
         ('same_vertex', [], 1, 1),
         ('negative_weight', [(1, 2, -1)], 1, 3)]
rows = []
for name, edges, start, end in cases:
    calls = [('create_graph', {'directed': True})]
    calls += [('insert_vertex', {'vertex': vertex}) for vertex in [1, 2, 3]]
    calls += [('insert_edge', {'origin': a, 'target': b, 'weight': cost}) for a, b, cost in edges]
    history = [{'operation': op, 'payload': payload, 'source_contract': 'graph-book/v1'} for op, payload in calls]
    data = Service.execute_operation('graph', 'run_dijkstra', {'start': start, 'end': end}, history)
    (OUT / f'{name}-main.c').write_text(data['main_c'], encoding='utf8')
    with tempfile.TemporaryDirectory(prefix='caller-native-') as temporary:
        tmp = Path(temporary)
        for filename in HASHES:
            shutil.copyfile(ROOT / 'docs/tads_C' / filename, tmp / filename)
        shutil.copyfile(OUT / f'{name}-main.c', tmp / 'main.c')
        compiler = shutil.which('gcc')
        built = subprocess.run([compiler, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
                                str(tmp / 'main.c'), str(tmp / 'tad_grafo.c'), '-o', str(tmp / 'caller.exe')],
                               capture_output=True, text=True, timeout=30)
        assert built.returncode == 0, built.stderr
        native = subprocess.run([str(tmp / 'caller.exe')], capture_output=True, text=True, timeout=15)
        expected = data['console_prefix'] + data['console_stdout']
        assert native.returncode == 0 and native.stdout == expected
        (OUT / f'{name}.stdout.txt').write_text(native.stdout, encoding='utf8')
        rows.append({'case': name, 'success': data['success'], 'c_status': data['c_status'],
                     'operation_stdout': data['console_stdout'], 'prefix_stdout': data['console_prefix'],
                     'native_stdout_equals_console': native.stdout == expected,
                     'caller_stdout_events': sum(bool(step['console']) for step in data['execution_trace']['steps'])})
canonical_source()
(OUT / 'native-report.json').write_text(json.dumps({'strict_c17': True, 'source_hashes_unchanged': HASHES,
                                                  'rows': rows}, indent=2), encoding='utf8')
print(json.dumps(rows, indent=2))
