"""Independent C-observed scopes, partial writes and lifetime/replay gates for six Merge cases."""
from pathlib import Path
from _audit_approved_source_supersessions import assert_historical_protected_hash
import json,hashlib
import pytest
from _audit_mergesort_baseline import audit,CASES
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';E=BASE/'evidence/visible-sorting-mergesort-instructions'
@pytest.fixture(scope='module')
def observed(tmp_path_factory):
 out=tmp_path_factory.mktemp('merge-instructions');return out,audit(out)
@pytest.mark.parametrize('case',list(CASES))
def test_C_typed_scopes_previous_calls_source_auxiliary_every_frame(case,observed):
 out,report=observed;d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));steps=d['response']['execution_trace']['steps'];native=d['native'];assert len(native)==len(steps);previous={}
 for index,(step,c) in enumerate(zip(steps,native)):
  event=c['event'];token=event['token'];p=step['pedagogy'];variables=p['variables'];by={(v['scope'],v['name']):v for v in variables};assert len(by)==len(variables)
  assert step['debug']['instruction_event']==event and step['state_after']['items']==c['array'] and step['state_snapshot']['items']==native[max(0,index-1)]['array']
  assert step['state_after']['auxiliary_array']==(c['auxiliary'] if event['aux_live'] else None)
  assert step['state_snapshot']['auxiliary_array']==(native[max(0,index-1)]['auxiliary'] if native[max(0,index-1)]['event']['aux_live'] else None)
  assert p['source']['function']==event['function'] and step['debug']['console_events']==[]
  assert (p['condition']['result'] if p['condition'] else None)==c['condition']
  assert p['invariant']['indices']==(list(range(len(CASES[case]))) if token=='sort_return' else [])
  assert step['state_after']['sorted_indices']==p['invariant']['indices']
  assert (step['state_after']['metrics']['comparisons'],step['state_after']['metrics']['moves'],step['state_after']['metrics']['swaps'])==(event['comparisons'],event['moves'],0)
  expected_names=set();calls=[]
  if token not in ['initial','sort_return']:
   expected_names.update({('ordenar_mergesort','arreglo'),('ordenar_mergesort','n')});assert by['ordenar_mergesort','n']['type']=='size_t' and by['ordenar_mergesort','n']['value']==len(CASES[case]);calls=['ordenar_mergesort']
   if token!='sort_entry':expected_names.add(('ordenar_mergesort','auxiliar'));aux=by['ordenar_mergesort','auxiliar'];assert aux['type']=='int *';assert aux['initialized']==(index>=next(i for i,x in enumerate(native) if x['event']['token']=='aux_reserve'))
  for depth,f in enumerate(event['frames'],1):
   scope=f"{f['function']}[{depth}]";calls.append(f['function']);expected_names.update({(scope,'arreglo'),(scope,'auxiliar')});assert by[scope,'arreglo']['type']==by[scope,'auxiliar']['type']=='int *'
   for name in ['izquierda','derecha','medio','i','j','k']:
    if f[name] is not None:
     expected_names.add((scope,name));v=by[scope,name];assert v['value']==f[name] and v['initialized'] and v['type']=='size_t'
    else:assert (scope,name) not in by
   call=p['call_stack'][depth];assert call['parameters']['izquierda']==f['izquierda'] and call['parameters']['derecha']==f['derecha'] and call['parameters']['auxiliar']=='reserva del wrapper'
   if f['function']=='mezclar':assert call['parameters']['medio']==f['medio']
  if token in ['valid_entry','valid_ptr','valid_n']:
   calls.append('arreglo_valido');expected_names.update({('arreglo_valido','arreglo'),('arreglo_valido','n')});assert by['arreglo_valido','arreglo']['type']=='const int *' and by['arreglo_valido','n']['value']==len(CASES[case])
  assert set(by)==expected_names and [c['function'] for c in p['call_stack']]==calls
  for key,v in by.items():
   old=previous.get(key);assert v['previous']==(old['value'] if old else None);assert v['changed']==(old is None or (old['value'],old['initialized'])!=(v['value'],v['initialized']))
  previous=by
  if p['loop']:assert p['loop']['iteration'] is None and p['loop']['bounds']==[event['frames'][-1]['izquierda'],event['frames'][-1]['derecha']]
  if token=='initial':assert step['line_index'] is None and not variables and not p['pointers']
  else:assert step['line_index'] is not None and step['line_text'].strip()
  if token=='split':assert 'size_t medio =' in step['line_text']
  if token=='copy_write':assert 'arreglo[i] = auxiliar[i]' in step['line_text']
  if token=='aux_free':assert 'free(auxiliar)' in step['line_text'] and 'liberada' in by['ordenar_mergesort','auxiliar']['value'] and all(q['name']!='auxiliar' for q in p['pointers'])
  if token=='rec_return':
   source='if (izquierda >= derecha)' if native[index-1]['event']['token']=='rec_guard' else '}'
   assert source in step['line_text']
 assert report['instruction_fidelity'] and all(row['auxiliary_mismatch_frames']==row['missing_local_frames']==0 for row in report['rows'])

def test_C_atomic_postincrements_ties_partial_copy_shortcircuit_suspend_retire(observed):
 out,_=observed;saw_partial=saw_tie=saw_short=False
 for case in CASES:
  d=json.loads((out/(case+'.json')).read_text(encoding='utf-8'));native=d['native'];steps=d['response']['execution_trace']['steps']
  for index,c in enumerate(native):
   e=c['event'];token=e['token'];prev=native[max(0,index-1)];f=e['frames'][-1] if e['frames'] else {};pf=prev['event']['frames'][-1] if prev['event']['frames'] else {}
   if token in ['aux_left_write','aux_right_write','left_tail_write','right_tail_write']:
    source='i' if token in ['aux_left_write','left_tail_write'] else 'j';expected=list(prev['auxiliary']);expected[pf['k']]=prev['array'][pf[source]];assert c['auxiliary']==expected and c['array']==prev['array'];assert f['k']==pf['k']+1 and f[source]==pf[source]+1 and f['j' if source=='i' else 'i']==pf['j' if source=='i' else 'i'];assert e['moves']==prev['event']['moves']+1
   if token=='merge_compare' and prev['array'][f['i']]==prev['array'][f['j']]:saw_tie=True;assert c['condition'] and native[index+1]['event']['token']=='aux_left_write'
   if token=='copy_write':
    expected=list(prev['array']);assert prev['auxiliary'][f['i']] is not None;expected[f['i']]=prev['auxiliary'][f['i']];assert c['array']==expected and c['auxiliary']==prev['auxiliary'] and e['moves']==prev['event']['moves']+1
    if c['array']!=sorted(CASES[case]) and c['array']!=prev['array']:saw_partial=True
   if token=='copy_increment':assert f['i']==pf['i']+1
   if token=='merge_left' and not c['condition']:saw_short=True;assert native[index+1]['event']['token']=='merge_while'
   if token in ['rec_entry','merge_entry'] and prev['event']['frames']:assert e['frames'][:-1]==prev['event']['frames']
   if token in ['rec_return','merge_return']:assert e['frames']==prev['event']['frames'][:-1]
   if token=='aux_reserve':assert c['auxiliary']==[None]*len(CASES[case]) and e['allocations']==1 and e['frees']==0
   if token=='aux_free':assert not e['aux_live'] and e['allocations']==e['frees']==1 and c['auxiliary']==[None]*len(CASES[case]) and steps[index]['state_after']['auxiliary_array'] is None
  if case=='single':assert len(native)==18 and not any(c['event']['token']=='merge_entry' for c in native)
 assert saw_partial and saw_tie and saw_short

@pytest.mark.parametrize('case',list(CASES))
def test_actual_UI_restores_C_aux_scopes_pointers_calls_without_redispatch(case):
 r=json.loads((E/'browser-final/report.json').read_text(encoding='utf-8'));row=next(x for x in r['rows'] if x['case']==case)
 assert row['forward_reverse_restorations']==2*row['instructions'] and row['replay_extra_POSTs']==0 and row['page_errors']==[] and row['fast_to_step_preserved'] and row['reload_main_preserved'] and row['recursive_scopes_auxiliary_lifetime_match_C'] and row['five_stages']
 c=row['caller'];assert c['strict_C17'] and c['doxygen_warnings']==0 and c['arrays']==[CASES[case],sorted(CASES[case])] and c['successful_native_runs']==1 and c['allocations']==c['frees']==1 and c['live']==0 and c['first_allocation_failure']['no_success_array_after_failure']
 assert r['empty_UI_rejected'] and r['empty_caller']['successful_native_runs']==r['empty_caller']['allocations']==r['empty_caller']['frees']==0

def test_original_regressions_C_H_closed_modules_and_observer_bytes_preserved():
 before=json.loads((E/'original-regressions.json').read_text(encoding='utf-8'));assert hashlib.sha256((ROOT/before['path']).read_bytes()).hexdigest()==before['sha256']
 prior=json.loads((BASE/'evidence/visible-sorting-quicksort-instructions/implementation-hashes.json').read_text(encoding='utf-8'))['files']
 for rel in ['docs/tads_C/tad_ordenamiento.c','docs/tads_C/tad_ordenamiento.h']+[f'app/domain/sorting/{m}_instructions.py' for m in ['intercambio','seleccion','insercion','burbuja','shell','quicksort']]:assert_historical_protected_hash(ROOT,rel,prior[rel])
 for name in ['observed.c','native.jsonl','tad_ordenamiento.c','tad_ordenamiento.h']:assert (E/'native-final'/name).read_bytes()==(BASE/'evidence/visible-sorting-mergesort-baseline-low/native'/name).read_bytes()
