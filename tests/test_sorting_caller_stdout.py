"""Real sorting caller stdout: C17 oracle, native AST and accepted-history cursors."""
from __future__ import annotations

from pathlib import Path
import shutil
import subprocess

import pytest

from app import create_app
from app.adapters.sorting_adapter import SortingAdapter
from app.domain.sorting import SORTING_ALGORITHMS
from app.services import sorting_caller_console as caller


@pytest.fixture
def client():
    app = create_app()
    app.config.update(TESTING=True)
    return app.test_client()


def _native(client, response, folder: Path) -> str:
    """Compile the exact API caller and downloaded canonical C/H, not a replica."""
    gcc = shutil.which('gcc')
    assert gcc, 'C17 oracle requires gcc'
    for kind, extension in [('source', 'c'), ('header', 'h')]:
        source = client.get('/help/source/sorting_array/' + kind)
        assert source.status_code == 200
        (folder / ('tad_ordenamiento.' + extension)).write_bytes(source.data)
    (folder / 'main.c').write_bytes(response['main_c'].encode('utf-8'))
    executable = folder / 'caller.exe'
    compiled = subprocess.run([gcc, '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror',
        str(folder/'main.c'), str(folder/'tad_ordenamiento.c'), '-o', str(executable)],
        capture_output=True, text=True, encoding='utf-8', timeout=30)
    assert compiled.returncode == 0 and compiled.stderr == '', compiled.stderr
    executed = subprocess.run([str(executable)], capture_output=True, timeout=10)
    assert executed.returncode == 0 and executed.stderr == b''
    return executed.stdout.decode('utf-8').replace('\r\n', '\n')


@pytest.mark.parametrize('algorithm', [a['id'] for a in SORTING_ALGORITHMS])
def test_actual_c17_caller_stdout_for_every_algorithm(client, tmp_path, algorithm):
    created = client.post('/api/ordenamiento/create-array', json={'values': [2, -1, 2]}).get_json()
    assert created['console_output'] == '[2, -1, 2]\n'
    response = client.post('/api/ordenamiento/run', json={'algorithm_id': algorithm, 'mode': 'fast'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['console_output'] == _native(client, data, tmp_path)
    trace = data['execution_trace']
    assert data['console_output'] == trace['console_prefix'] + trace['steps'][-1]['console_stdout']
    assert all(frame['console_stdout'] == '' for frame in trace['steps'][:-1])
    assert [f['step_index'] for f in trace['steps']] == list(range(len(trace['steps'])))
    assert trace['steps'][-1]['caller_console_events']
    assert all(e['source_role'] == 'caller' for e in trace['steps'][-1]['caller_console_events'])


def test_repeated_mixed_runs_random_seed_and_get_without_algorithm_replay(client, tmp_path, monkeypatch):
    generated = client.post('/api/ordenamiento/random-array',
        json={'size': 4, 'min_value': -4, 'max_value': 4, 'seed': 17})
    assert generated.status_code == 200
    first = client.post('/api/ordenamiento/run', json={'algorithm_id': 'burbuja', 'mode': 'fast'}).get_json()
    second = client.post('/api/ordenamiento/run', json={'algorithm_id': 'mergesort', 'mode': 'step_by_step'}).get_json()
    assert second['console_output'] == _native(client, second, tmp_path)
    trace = second['execution_trace']
    assert trace['console_prefix'].startswith(first['console_output'])
    assert 'Run 2: ordenar_mergesort\n' in trace['console_prefix']
    assert trace['steps'][-1]['console_stdout'].startswith('Estado: 1\n')
    # A cursor before the TAD sees its already executed caller header, never the
    # result printed after return. All intermediate native frames stay silent.
    assert trace['console_prefix'] + trace['steps'][0]['console_stdout'] == trace['console_prefix']
    monkeypatch.setattr(SortingAdapter, 'run', lambda *a, **k: pytest.fail('GET reran sorting'))
    restored = client.get('/api/ordenamiento/state').get_json()
    assert restored['history'] == second['history']
    assert restored['console_output'] == second['console_output']


def test_paged_final_cursor_and_reload_preserve_caller_stdout(client, monkeypatch):
    client.post('/api/ordenamiento/create-array', json={'values': [128, 0]})
    response = client.post('/api/ordenamiento/run', json={'algorithm_id': 'counting_sort', 'mode': 'step_by_step'})
    assert response.status_code == 200
    data = response.get_json()
    trace = data['execution_trace']
    assert trace['schema'] == 'counting-paged-trace/v1'
    assert all(f['console_stdout'] == '' for f in trace['initial_page']['steps'])
    monkeypatch.setattr(SortingAdapter, 'run', lambda *a, **k: pytest.fail('Page/GET reran sorting'))
    final_page = client.get(trace['page_url'], query_string={'start': trace['step_count']-1, 'limit': 1})
    assert final_page.status_code == 200
    page = final_page.get_json()
    assert page['console_prefix'] == trace['console_prefix']
    assert page['steps'][0]['console_stdout'] == 'Estado: 1\n[0, 128]\n'
    first_page = client.get(trace['page_url'], query_string={'start': 0, 'limit': 1}).get_json()
    assert first_page['steps'][0]['console_stdout'] == ''
    restored = client.get('/api/ordenamiento/state').get_json()
    assert restored['console_output'] == data['console_output']
    assert restored['execution_trace']['console_prefix'] == trace['console_prefix']
    assert restored['history'] == data['history']
    source_lines = (caller.CCodeService._DOCS_TADS_C / 'tad_ordenamiento.c').read_text(encoding='utf-8-sig').splitlines()
    for event in page['steps'][0]['caller_console_events']:
        if event['source_file'] == 'tad_ordenamiento.c':
            assert source_lines[event['line_index']] == event['line_text']


def test_rejected_run_does_not_append_caller_stdout_or_history(client):
    accepted = client.post('/api/ordenamiento/create-array', json={'values': [0, 1_000_001]}).get_json()
    rejected = client.post('/api/ordenamiento/run', json={'algorithm_id': 'counting_sort', 'mode': 'fast'})
    assert rejected.status_code == 400
    data = rejected.get_json()
    assert data['history'] == accepted['history']
    assert data['console_output'] == accepted['console_output']
    assert data['console_stdout'] == ''


def test_actual_main_printf_edits_are_interpreted_and_silent_main_is_silent(client, monkeypatch):
    client.post('/api/ordenamiento/create-array', json={'values': [2, 1]})
    data = client.post('/api/ordenamiento/run', json={'algorithm_id': 'burbuja', 'mode': 'fast'}).get_json()
    history = data['history']
    real_main = caller.build_sorting_main(history)
    monkeypatch.setattr(caller, 'build_sorting_main', lambda h: real_main.replace(
        '    imprimir_arreglo(arreglo, n);', '    printf("From actual main: ");\n    imprimir_arreglo(arreglo, n);'))
    changed = caller.execute_sorting_caller(history)
    assert changed['stdout'].count('From actual main: ') == 2
    silent = '\n'.join(line for line in real_main.splitlines()
                       if not line.strip().startswith(('printf(', 'imprimir_arreglo('))) + '\n'
    monkeypatch.setattr(caller, 'build_sorting_main', lambda h: silent)
    assert caller.execute_sorting_caller(history)['stdout'] == ''
    assert caller.execute_sorting_caller(history)['events'] == []
