"""Complete authentic-baseline gates reject unreviewed changes and weakened C checks."""
import ast
import json
import shutil
from pathlib import Path
import pytest
from scripts.published_test_inputs import audit_input_path
from tests._sorting_published_test_contract import (
    assert_archived_shell_test_portability, assert_archived_burbuja_test_portability,
    assert_published_test_successor,
)

ROOT=Path(__file__).resolve().parents[1]
GATES={'shell':assert_archived_shell_test_portability,'burbuja':assert_archived_burbuja_test_portability}


def paths(algorithm):
    current=Path(f'tests/test_sorting_{algorithm}_baseline_low.py')
    snapshot=Path('openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence')/f'visible-sorting-{algorithm}-instructions'/'before'/current
    return current,snapshot


def published_burbuja(root):
    receipt=json.loads((root/'tests/fixtures/sorting-history/burbuja-test-migration.json').read_text())
    assert_published_test_successor(root,{'sha256':receipt['original_declared_sha256'],
                                         'path':receipt['source']['path']},'burbuja')


@pytest.mark.parametrize('algorithm',GATES)
def test_complete_archived_and_published_gates_accept_only_reviewed_successor(algorithm):
    GATES[algorithm](ROOT)
    if algorithm=='burbuja':published_burbuja(ROOT)


@pytest.mark.parametrize('algorithm',GATES)
@pytest.mark.parametrize('fault',['assertion','number','delete_case','snapshot','normalize_current',
    'different_position','change_condition','ignore_c_h_content'])
def test_complete_public_gates_reject_unreviewed_changes(tmp_path,algorithm,fault):
    current,snapshot=paths(algorithm);old=audit_input_path(ROOT/snapshot).read_bytes()
    tree=ast.parse((ROOT/current).read_text(encoding='utf-8-sig'))
    if fault=='assertion':next(n for n in ast.walk(tree) if isinstance(n,ast.Assert)).test=ast.Constant(True)
    elif fault=='number':next(n for n in ast.walk(tree) if isinstance(n,ast.Constant) and type(n.value) is int).value+=1
    elif fault=='delete_case':tree.body.remove(next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')))
    elif fault=='snapshot':old+=b'\n'
    elif fault=='normalize_current':
        if algorithm=='burbuja':
            node=next(n for n in ast.walk(tree) if isinstance(n,ast.Compare) and isinstance(n.left,ast.Call) and isinstance(n.left.func,ast.Name) and n.left.func.id=='current_swap_display')
            node.comparators[0]=ast.Call(func=ast.Name(id='current_swap_display',ctx=ast.Load()),args=[node.comparators[0]],keywords=[])
        else:
            node=next(n for n in ast.walk(tree) if isinstance(n,ast.Compare))
            node.left=ast.Call(func=ast.Name(id='current_swap_display',ctx=ast.Load()),args=[node.left],keywords=[])
    elif fault=='different_position':
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.Compare))
        node.comparators[0]=ast.Call(func=ast.Name(id='current_swap_display',ctx=ast.Load()),args=[node.comparators[0]],keywords=[])
    elif fault=='change_condition':
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.If));node.test=ast.Constant(True)
    else:
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_c_h'))
        # A syntactically plausible C/H check must not hide any source contents.
        loop=next(n for n in node.body if isinstance(n,ast.For));loop.body=[ast.Assert(test=ast.Constant(True),msg=None)]
    (tmp_path/snapshot).parent.mkdir(parents=True);(tmp_path/snapshot).write_bytes(old)
    (tmp_path/current).parent.mkdir(parents=True);(tmp_path/current).write_text(ast.unparse(tree))
    with pytest.raises(AssertionError):GATES[algorithm](tmp_path)
    if algorithm=='burbuja' and fault!='snapshot':
        shutil.copytree(ROOT/'tests/fixtures/sorting-history',tmp_path/'tests/fixtures/sorting-history')
        with pytest.raises(AssertionError):published_burbuja(tmp_path)


def test_burbuja_old_only_display_adapter_detects_current_text_regression():
    from tests._sorting_trace_text_contract import current_swap_display
    from app.domain.sorting.tad_ordenamiento import SortingInterpreter
    current=SortingInterpreter([2,1],'shell');current._swap(0,1)
    import copy
    historical=copy.deepcopy(current._steps)
    for step in historical:
        for field in ('action','console_output'):
            if isinstance(step.get(field),str):step[field]=step[field].replace('posición','posicion')
    assert historical!=current._steps
    assert current_swap_display(historical)==current._steps
    assert current_swap_display(historical)!=historical
