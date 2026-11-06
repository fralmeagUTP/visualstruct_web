"""Fail-closed controls for the finite PR7 unit-test contract repairs."""
from copy import deepcopy
import json
from pathlib import Path
import shutil
import ast
import pytest
from _audit_sorting_c_source import assert_source_transport_identity
from tests._sorting_trace_text_contract import current_swap_display
from tests._sorting_text_source_contract import _SOURCE_PAIRS
from tests._sorting_published_test_contract import _CurrentSortingAssertionAdapter
from _audit_approved_source_supersessions import assert_historical_protected_hash

ROOT = Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('observed,canonical', [
    (b'int x;\n',b'int x;\r\n'),(b'int x;\r\n',b'int x;\n'),
    (b'int x;\r\n',b'int x;\r\n'),(b'int x;\n',b'int x;\n')])
def test_c_source_transport_preserves_all_bytes_except_crlf(observed,canonical):
    assert_source_transport_identity(observed,canonical)

@pytest.mark.parametrize('changed', [b'int y;\n',b'int  x;\n',b'/* added */int x;\n',b'int x;\r',b'int x;',b'int x;\n\n'])
def test_c_source_transport_rejects_content_or_nontransport_changes(changed):
    with pytest.raises(AssertionError):
        assert_source_transport_identity(changed,b'int x;\r\n')

@pytest.mark.parametrize('relative', _SOURCE_PAIRS)
def test_historical_hash_gate_dispatches_only_exact_sorting_successors(relative):
    assert_historical_protected_hash(ROOT,relative,_SOURCE_PAIRS[relative][0])

@pytest.mark.parametrize('mutation',['current','snapshot','receipt','expected'])
def test_historical_hash_gate_keeps_sorting_successor_closed(tmp_path,mutation):
    relative='app/domain/sorting/shell_instructions.py'
    path=tmp_path/relative;path.parent.mkdir(parents=True);path.write_bytes((ROOT/relative).read_bytes())
    folder=tmp_path/'tests/fixtures/sorting-source-history';shutil.copytree(ROOT/'tests/fixtures/sorting-source-history',folder)
    expected=_SOURCE_PAIRS[relative][0]
    if mutation=='expected':expected='0'*64
    else:
        changed=path if mutation=='current' else folder/('shell_instructions.py.snapshot' if mutation=='snapshot' else 'recovered-sources.json')
        changed.write_bytes(changed.read_bytes()+b' ')
    with pytest.raises(AssertionError):assert_historical_protected_hash(tmp_path,relative,expected)


def test_swap_spelling_only_updates_two_exact_display_fields():
    old={'action':'Asignar 1 a la primera posicion; temporal conserva 2.',
         'console_output':'Asignar temporal (2) a la segunda posicion.',
         'array_snapshot':[1,1],'metrics':{'moves':0},'temporaries':{'temporal':2},
         'line_text':'Asignar temporal (2) a la segunda posicion.'}
    original=deepcopy(old);current=current_swap_display(old)
    assert old==original
    assert current['action']=='Asignar 1 a la primera posición; temporal conserva 2.'
    assert current['console_output']=='Asignar temporal (2) a la segunda posición.'
    assert current['line_text']==old['line_text']
    for key in ['array_snapshot','metrics','temporaries']:assert current[key]==old[key]
    for key,bad in [('array_snapshot',[2,1]),('metrics',{'moves':1}),('temporaries',{})]:
        altered=deepcopy(old);altered[key]=bad
        assert current_swap_display(altered)!=current
    changed=deepcopy(old);changed['action']='Asignar 9 a la primera posicion; temporal conserva 2.'
    assert current_swap_display(changed)['action']==changed['action']


def normalize(source):
    return ast.dump(_CurrentSortingAssertionAdapter().visit(ast.parse(source)),include_attributes=False)

@pytest.mark.parametrize('old,new',[
    ('assert left.read_bytes() == right.read_bytes()', 'assert_source_transport_identity(left.read_bytes(), right.read_bytes())'),
    ('assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h[rel]', 'assert_sorting_text_source_continuity(ROOT, rel, h[rel])'),
    ('def test_shared_helper_default_unchanged_without_running_closed_methods():\n assert old._steps == now._steps and old.values == now.values and old.metrics.moves == now.metrics.moves == 0',
     'def test_shared_helper_default_unchanged_without_running_closed_methods():\n assert current_swap_display(old._steps) == now._steps and old.values == now.values and old.metrics.moves == now.metrics.moves == 0'),
    ("def test_shared_swap_default_preserved_and_heap_optin_no_fake_TAD_console():\n assert old == {'values': p.values, 'steps': p._steps, 'metrics': vars(p.metrics)}",
     "def test_shared_swap_default_preserved_and_heap_optin_no_fake_TAD_console():\n assert current_swap_display(old) == {'values': p.values, 'steps': p._steps, 'metrics': vars(p.metrics)}")])
def test_only_explicit_successor_assertion_shapes_map_to_old_contract(old,new):
    assert normalize(old)==normalize(new)

@pytest.mark.parametrize('changed',[
    'assert_sorting_text_source_continuity(ROOT, rel, "forged")',
    'assert_sorting_text_source_continuity(ROOT, rel, h[rel], ignore=True)',
    'assert_source_transport_identity(left.read_bytes(), b"forged")',
    'assert ignore_steps(old._steps) == now._steps',
    'assert current_swap_display(old._steps) == now._steps',
    'assert current_swap_display(old._steps) == now._steps[:-1]',
    'assert True'])
def test_assertion_projection_does_not_accept_changed_conditions(changed):
    old=['assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == h[rel]',
         'assert left.read_bytes() == right.read_bytes()',
         'assert old._steps == now._steps']
    assert all(normalize(changed)!=normalize(source) for source in old)


@pytest.mark.parametrize('mutation', ['current', 'both', 'reverse', 'other_function', 'changed_condition'])
def test_swap_projection_is_bound_to_exact_function_and_complete_assertion(mutation):
    name = 'test_shared_helper_default_unchanged_without_running_closed_methods'
    old = f'def {name}():\n assert old._steps == now._steps and old.values == now.values and old.metrics.moves == now.metrics.moves == 0'
    current = old.replace('old._steps ==', 'current_swap_display(old._steps) ==')
    if mutation == 'current':
        current = old.replace('== now._steps', '== current_swap_display(now._steps)')
    elif mutation == 'both':
        current = current.replace('== now._steps', '== current_swap_display(now._steps)')
    elif mutation == 'reverse':
        current = current.replace('current_swap_display(old._steps) == now._steps', 'now._steps == current_swap_display(old._steps)')
    elif mutation == 'other_function':
        current = current.replace(name, 'test_another_function')
        old = old.replace(name, 'test_another_function')
    else:
        current = current.replace('moves == 0', 'moves == 1')
    assert normalize(current) != normalize(old)
