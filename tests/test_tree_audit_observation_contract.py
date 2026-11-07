"""C/API and real-renderer regressions; these do not certify browser execution."""
import json
from pathlib import Path
import shutil
import subprocess

import pytest
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from e2e_contract_helpers import observe_before_cleanup
from e2e_hierarchical_contract import same_nodes
from test_audit_abb_delete_native import delete_baselines, delete_case
from test_audit_abb_validate_native import CASES, fixture
from test_audit_avl_validate_e2e import COLLECT

ROOT = Path(__file__).resolve().parents[1]


def render_rows(tmp_path, family, trace, memory=False):
    collect = COLLECT
    if memory:
        collect = collect.replace(" const records=[];", " const panel=document.createElement('div');panel.id='hier-memory-view';document.querySelector('#root').append(panel);\n const records=[];")
        collect = collect.replace("direction:dir,index,state:", "memory:document.querySelector('#hier-memory-view').textContent,direction:dir,index,state:")
    path = tmp_path / 'trace.json'
    path.write_text(json.dumps(dict(family=family, trace=trace, collect=collect)))
    run = subprocess.run(['node', 'qa/emit_e2e_hierarchical_records.js', str(path)], cwd=ROOT, capture_output=True, text=True, timeout=90)
    assert run.returncode == 0, run.stderr
    return json.loads(run.stdout)


@pytest.mark.parametrize('case', [6, 7, 10, 13, 14])
def test_abb_validation_focus_changes_card_order_not_identity(tmp_path, case):
    meta = CASES[case]
    history = []
    if 'tree' in meta:
        adapter = fixture(case)
        # Use the same supported forged fixture route as the native oracle.
        from unittest.mock import patch
        original = S._new_adapter
        with patch.object(S, '_new_adapter', staticmethod(lambda sid: adapter if sid == 'abb' else original(sid))):
            data = S.execute_operation('abb', 'validar', {}, history)
    else:
        for value in meta.get('seed', []):
            data = S.execute_operation('abb', 'insertar', {'value': value}, history)
            assert data['success']; history = data['history']
        data = S.execute_operation('abb', 'validar', {}, history)
    assert data['success']
    rows = render_rows(tmp_path, 'abb', data['execution_trace'])
    assert any(row['nodes'] != row['state']['heap_nodes'] for row in rows), 'Old ordered observer must reproduce failure'
    for row in rows:
        assert same_nodes(row['nodes'], row['state']['heap_nodes'])


def test_avl_free_memory_label_and_exact_identities(tmp_path):
    history = []
    for value in [7, 3, 9, 1, 5]:
        data = S.execute_operation('avl', 'insertar', {'value': value}, history)
        assert data['success']; history = data['history']
    data = S.execute_operation('avl', 'limpiar', {}, history)
    assert data['success']
    trace = data['execution_trace']; rows = render_rows(tmp_path, 'avl', trace, memory=True)
    frees = 0
    for row in rows:
        if row['index'] < 0: continue
        ped = trace['steps'][row['index']]['pedagogy']
        if ped['instruction_event']['phase'] == 'free':
            frees += 1
            expected = 'Liberados (identidades históricas): ' + ', '.join(x['address'] for x in ped['memory']['freed_objects'])
            assert expected in row['memory']
            assert 'Liberados (identidades historicas)' not in row['memory']
    assert frees == 10  # Five frees, forward and backward.


@pytest.mark.parametrize('family,case', [(0,i) for i in range(11)] + [(1,i) for i in range(2)])
def test_abb_delete_actual_and_equivalent_callers_observe_live_tree(tmp_path, delete_baselines, family, case):
    meta = delete_baselines[family]['cases'][case]
    if not meta['api_success']:
        assert not any(s.get('pedagogy', {}).get('memory_state', {}).get('abb_delete_model') for s in S.execute_operation('abb', 'eliminar', meta['payload'], [])['execution_trace']['steps'])
        return
    trace = delete_case(delete_baselines[family], case)
    operations = [{'name':'insertar','payload':{'value':v},'message':''} for v in meta['seed']]
    operations.append({'name':'eliminar','payload':meta['payload'],'message':''})
    config = [{'id':'abb','module':'hierarchical','model':S.get_view_model('abb', []),'operations':operations}]
    path = tmp_path / 'fixture.json'; path.write_text(json.dumps(config))
    subprocess.run(['node', 'qa/frontend_main_export.js', str(ROOT), str(path), str(tmp_path)], cwd=ROOT, check=True)
    actual = (tmp_path / 'abb.c').read_text()
    nodes = {n['id']:n for n in meta['native_endpoint']['nodes']}
    def assertions(identity, expression='arbol'):
        if not identity: return [f'assert({expression} == NULL);']
        n = nodes[identity]
        return [f'assert({expression} != NULL);', f'assert(({expression})->valor == {n["value"]});', *assertions(n['left'], f'({expression})->izquierdo'), *assertions(n['right'], f'({expression})->derecho')]
    observation = '\n'.join(assertions(meta['native_endpoint']['root']))
    observed = observe_before_cleanup(actual, 'abb_liberarArbol(arbol);', observation)
    assert observed.replace('    '+observation+'\n', '', 1) == actual
    equivalent = 'int main(void)' + trace['source_code'].split('int main(void)', 1)[1]
    parts = equivalent.rsplit('    return 0;', 1); assert len(parts) == 2
    equivalent = parts[0]+observation+'\nabb_liberarArbol(arbol);\n    return 0;'+parts[1]
    def run(source, label):
        c = tmp_path / (label+'.c'); exe = tmp_path / label
        c.write_text('#include "tad_abb.h"\n#include <stdio.h>\n#include <stddef.h>\n#include <assert.h>\n'+source)
        build = subprocess.run([shutil.which('gcc'), '-std=c17', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-I', str(ROOT/'docs/tads_C'), str(ROOT/'docs/tads_C/tad_abb.c'), str(c), '-o', str(exe)], capture_output=True, text=True, timeout=30)
        assert build.returncode == 0, build.stderr
        return subprocess.run([str(exe)], capture_output=True, text=True, timeout=5)
    assert run(actual, 'unaltered').returncode == 0
    assert run(observed, 'observed').returncode == 0
    eq = run(equivalent, 'equivalent'); assert eq.returncode == 0 and eq.stdout == ''
    if meta['native_endpoint']['root']:
        late = actual.replace('    return 0;', observation+'\n    return 0;')
        assert run(late, 'old-late-observer').returncode != 0
        wrong = observe_before_cleanup(actual, 'abb_liberarArbol(arbol);', 'assert(arbol == NULL);')
        assert run(wrong, 'wrong-tree-oracle').returncode != 0
