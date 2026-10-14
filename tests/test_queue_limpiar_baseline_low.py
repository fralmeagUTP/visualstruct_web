"""Finite Cola limpiar baseline: explicit lifetime regressions, no xfail."""
from pathlib import Path
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-limpiar-baseline-low'
from scripts.published_test_inputs import audit_input_path
def rows():
 current=E.parent/'visible-queue-limpiar-instructions-medium/report.json'
 return [r for r in json.loads((audit_input_path(current if current.exists() else E/'report.json')).read_text(encoding='utf-8')) if 'data' in r]
def multi(): return next(r for r in rows() if r['case']=='multi' and r['repeat']==1)
def frame(line): return next(f for f in multi()['data']['execution_trace']['steps'] if f['line_text'].strip()==line)
def pointer(f,name): return next(p for p in f['pedagogy']['pointers'] if p['name']==name)
@pytest.mark.parametrize('case',['empty','single','multi','reinsert'])
def test_finite_final_empty_repeat_reinsert_match_original_C(case):
 rr=[r for r in rows() if r['case']==case];assert len(rr)==2
 for r in rr:
  assert r['C_API_final_match'] and r['data']['success'] and r['data']['visual_state']['items']==[]
  assert all(x['match'] for x in r['instruction_comparison'])
def test_native_NULL_guard_and_rear_shadow_never_read_retired_storage():
 ns=json.loads((audit_input_path(E/'native-report.json')).read_text());assert len(ns)==92 and len({n['sample'] for n in ns})==9
 null=[n for n in ns if n['root_argument_NULL']];assert [n['event'] for n in null]==['entry','aux_declared','root_guard','return']
 retired=[n for n in ns if not n['rear_valid'] and not n['root_argument_NULL']];assert len(retired)==12 and all(n['rear_id']==-1 for n in retired)
 assert 'OWNERSHIP 8 8 0' in (audit_input_path(E/'native/stderr.log')).read_text()
def test_aux_declared_is_function_scoped_uninitialized_not_NULL():
 p=pointer(frame('struct NodoCola *aux;'),'aux');assert p['type']=='struct NodoCola *' and p.get('initialized') is False and p.get('valid') is False and p.get('scope')=='cola_vaciar'
def test_aux_assignment_borrows_existing_head_identity():
 f=frame('aux = q->delante;');p=pointer(f,'aux');ids={h['id'] for h in f['pedagogy']['heap_objects']};assert p['target'] in ids and p.get('valid') is True
 assert p['target']==pointer(f,'delante')['target']
def test_unlinked_head_remains_live_until_free():
 f=frame('q->delante = aux->sgte;');n=next(n for n in multi()['native_events'] if n['event']=='root_assigned');assert len(f['pedagogy']['heap_objects'])==len(n['live'])
 assert any(h.get('status')=='detached' for h in f['pedagogy']['heap_objects'])
def test_aux_after_free_is_indeterminate_and_history_is_separate():
 f=frame('free(aux);');p=pointer(f,'aux');assert p.get('initialized') is False and p.get('valid') is False and p['target'] is None
 retired=f['pedagogy']['heap_transition']['freed'];assert retired and all(h.get('initialized_mask')==0 and h.get('fields_valid') is False for h in retired)
def test_rear_invalid_between_last_free_and_NULL_store():
 frees=[f for f in multi()['data']['execution_trace']['steps'] if f['line_text'].strip()=='free(aux);'];p=pointer(frees[-1],'atras');assert p.get('valid') is False and p['target'] is None and p.get('historical_identity')
def test_pointer_variables_use_actual_NodoCola_type():
 f=frame('aux = q->delante;');variables={v['name']:v for v in f['pedagogy']['variables']};assert all(variables[n]['type']=='struct NodoCola *' for n in ['aux','delante','atras'])
def test_final_void_return_retires_function_call_and_scope():
 final=multi()['data']['execution_trace']['steps'][-1];assert final['event_type']=='return' and final['pedagogy']['call_stack']==[]
 assert not any(p.get('scope')=='cola_vaciar' for p in final['pedagogy']['pointers'])
