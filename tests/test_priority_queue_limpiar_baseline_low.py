"""Finite cp_vaciar baseline: root/count already faithful, pointer scopes still open."""
from pathlib import Path
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-limpiar-baseline-low'
M=E.parent/'visible-priority-queue-limpiar-instructions-medium'
if (M/'report.json').exists():E=M

def rows():return json.loads((E/'report.json').read_text(encoding='utf-8'))
def multi():return next(r for r in rows() if r['case']=='multi' and r['repeat']==1)
def frame(line):return next(f for f in multi()['data']['execution_trace']['steps'] if f['line_text'].strip()==line)
def pointer(f,name):return next(p for p in f['pedagogy']['pointers'] if p['name']==name)
@pytest.mark.parametrize('case',['empty','single','multi','reinsert'])
def test_finite_final_empty_repeat_reinsert_match_C(case):
 rs=[r for r in rows() if r['case']==case];assert len(rs)==2 and all(r['C_API_final_match'] and r['data']['success'] and r['data']['visual_state']['items']==[] for r in rs)
@pytest.mark.parametrize('case',['empty','single','multi','reinsert'])
def test_root_values_quantity_and_live_cardinality_match_current_C(case):
 for r in rows():
  if r['case']==case:assert all(x['root_values_match'] and x['quantity_match'] and x['C_live_count']==x['trace_heap_count'] for x in r['instruction_comparison'])
def test_native_NULL_guard_next_and_aux_shadow_avoid_uninitialized_and_retired_reads():
 ns=json.loads((E/'native-report.json').read_text(encoding='utf-8'));assert len(ns)==153 and sum(n['condition']!=-1 for n in ns)==41 and len({n['sample'] for n in ns})==9
 null=[n for n in ns if n['root_argument_NULL']];assert [n['event'] for n in null]==['entry','aux_declared','next_declared','root_guard','return']
 frees=[n for n in ns if n['event']=='node_free'];assert len(frees)==8 and all(not n['aux_valid'] and not n['aux_initialized'] and n['next_valid'] for n in frees)
 assert 'OWNERSHIP 8 8 0' in (E/'native/stderr.log').read_text(encoding='utf-8')
def test_aux_declaration_is_uninitialized_function_local():
 p=pointer(frame('CPNodo *aux;'),'aux');assert p['target'] is None and p.get('initialized') is False and p.get('valid') is False and p.get('scope')=='cp_vaciar'
def test_next_declaration_exists_uninitialized_with_CPNodo_type_and_scope():
 p=pointer(frame('CPNodo *next;'),'next');assert p['type']=='CPNodo *' and p.get('initialized') is False and p.get('scope')=='cp_vaciar'
def test_next_assignment_keeps_real_live_successor_identity():
 f=frame('next = aux->sgte;');p=pointer(f,'next');assert p.get('valid') is True and p['target'] in {h['id'] for h in f['pedagogy']['heap_objects']}
def test_detached_aux_keeps_original_node_identity_until_free():
 initial=frame('aux = cola->delante;')['pedagogy']['heap_objects'];f=frame('cola->delante = next;');nodes=f['pedagogy']['heap_objects'];assert {n['id'] for n in nodes}=={n['id'] for n in initial}
 p=pointer(f,'aux');assert p['target']==initial[0]['id'] and any(n['id']==p['target'] and n.get('status')=='detached' for n in nodes)
def test_aux_after_free_is_indeterminate_with_separate_history():
 f=frame('free(aux);');p=pointer(f,'aux');assert p['target'] is None and p.get('valid') is False and p.get('initialized') is False and p.get('historical_identity')
 assert all(h.get('initialized_mask')==0 and h.get('fields_valid') is False and h.get('historical_fields') for h in f['pedagogy']['heap_transition']['freed'])
def test_aux_and_next_variables_use_actual_CPNodo_pointer_type():
 f=frame('next = aux->sgte;');v={v['name']:v for v in f['pedagogy']['variables']};assert v['aux']['type']=='CPNodo *' and v['next']['type']=='CPNodo *'
def test_void_return_retires_callee_scope_but_preserves_caller():
 f=multi()['data']['execution_trace']['steps'][-1];assert f['event_type']=='return' and f['pedagogy']['call_stack']==[]
 assert not any(p.get('scope')=='cp_vaciar' for p in f['pedagogy']['pointers'])
