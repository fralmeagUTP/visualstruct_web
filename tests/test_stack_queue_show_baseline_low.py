"""Independent Mostrar regressions: preserve red IDs until scoped fixes."""
from pathlib import Path
from _audit_approved_source_supersessions import assert_historical_protected_hash
import json,io,contextlib,hashlib
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-stack-queue-show-baseline-low'
M=E.parent/'visible-stack-queue-show-instructions-medium'
CASES=['empty','single','multiple','duplicate','minus1','minus1-front','minus1-rear','bounds','bounds-reverse'];PAIRS=[(sid,name) for sid in ['stack','queue'] for name in CASES]+[('queue','front-only'),('queue','rear-only')];NORMAL=[(sid,name) for sid in ['stack','queue'] for name in CASES]
from scripts.published_test_inputs import audit_input_path
def read(name):return json.loads((audit_input_path((M if name in ['report.json','browser-report.json','caller-input-reuse.json','resources.json'] else E)/name)).read_text(encoding='utf-8'))
def row(sid,name):return next(d for d in read('report.json') if d['structure']==sid and d['case']==name)
def live(sid,name):
 from app.domain.sequential import tad_pila as S,tad_cola as Q
 d=row(sid,name);raw=S if sid=='stack' else Q;nodes=[(S.NodoPila if sid=='stack' else Q.NodoCola)(v) for v in d['values_order']]
 for i,n in enumerate(nodes):n.sgte=nodes[i+1] if i+1<len(nodes) else None
 q=(nodes[0] if nodes else None) if sid=='stack' else Q.Cola(nodes[0] if nodes and name!='rear-only' else None,nodes[-1] if nodes and name!='front-only' else None)
 return raw,q,nodes
@pytest.mark.parametrize('sid,name',PAIRS)
def test_raw_void_exact_native_printf_format_each_repeat(sid,name):
 raw,q,nodes=live(sid,name)
 for expected in row(sid,name)['native_outputs']:
  b=io.StringIO()
  with contextlib.redirect_stdout(b):result=getattr(raw,'pila_mostrar' if sid=='stack' else 'cola_mostrar')(q)
  assert result is None and b.getvalue()==expected
@pytest.mark.parametrize('sid,name',PAIRS)
def test_raw_repeat_readonly_root_both_queue_fields_nodes_links_values(sid,name):
 raw,q,nodes=live(sid,name)
 def snap():return (id(q),[(id(n),n.nro,id(n.sgte)) for n in nodes],None if sid=='stack' else (id(q.delante),id(q.atras)))
 before=snap()
 for _ in range(2):
  with contextlib.redirect_stdout(io.StringIO()):assert getattr(raw,'pila_mostrar' if sid=='stack' else 'cola_mostrar')(q) is None
  assert snap()==before
@pytest.mark.parametrize('sid,name',NORMAL)
def test_private_exact_source_initialized_parameter_copy_and_live_aliases(sid,name):
 d=row(sid,name);tr=d['private_trace'];assert ('void '+d['method']+'(') in tr['source_code'];m=tr['steps'][0]['pedagogy'];param='p' if sid=='stack' else 'q';v=next(v for v in m['variables'] if v['name']==param);assert v['type']==('ptrPila' if sid=='stack' else 'struct Cola') and v['initialized'] and v['scope']==d['method'];assert all(h['type']==('struct NodoPila' if sid=='stack' else 'struct NodoCola') and h['initialized_mask']==3 and h['alive'] for h in m['heap_objects'])
@pytest.mark.parametrize('sid,name',NORMAL)
def test_private_if_while_boundaries_outcomes_match_own_native(sid,name):
 d=row(sid,name);ns=[x for x in d['native'] if x['sample']==d['native'][0]['sample'] and x['phase'] in ['if','while']];actual=[s['pedagogy']['condition'] for s in d['private_trace']['steps'] if s['pedagogy'].get('condition') is not None];assert len(actual)==len(ns);assert [x['result'] for x in actual]==[bool(x['condition']) for x in ns]
@pytest.mark.parametrize('sid,name',NORMAL)
def test_private_incremental_console_exact_native_no_future_lines(sid,name):
 d=row(sid,name);ns=[x for x in d['native'] if x['sample']==d['native'][0]['sample']];steps=d['private_trace']['steps'];assert len(steps)==len(ns)
 for s,n in zip(steps,ns):assert ''.join(s['console'])==n['console']
@pytest.mark.parametrize('sid,name',NORMAL)
def test_private_aux_progress_void_exit_ended_scope_no_scalar_store(sid,name):
 d=row(sid,name);steps=d['private_trace']['steps'];ns=[x for x in d['native'] if x['sample']==d['native'][0]['sample']];assert len(steps)==len(ns)
 for step,n in zip(steps,ns):
  m=step['pedagogy'];assert step['state_after']==d['visual'];assert not any(v['name']=='return' and v['type']=='int' for v in m['variables'])
  if n['phase'] not in ['entry','end','return']:
   aux=next(v for v in m['variables'] if v['name']=='aux');assert aux['initialized'] and aux['value']==(None if n['aux_id']==-1 else 'N'+str(n['aux_id']+1))
 m=steps[-1]['pedagogy'];assert m['call_stack']==[] and any(s.get('state')=='ended' for s in m['scopes']);assert not any(v['scope']==d['method'] for v in m['variables'])
@pytest.mark.parametrize('sid,name',NORMAL)
def test_rejected_unsupported_validation_zero_Csteps_no_printf_scope(sid,name):
 for r in row(sid,name)['rejected']:
  tr=r['data']['execution_trace'];assert tr.get('execution_started') is False and tr['steps']==[]
@pytest.mark.parametrize('sid,name',NORMAL)
def test_existing_adapter_API_not_registered_400_POST_GET_no_target_or_records(sid,name):
 d=row(sid,name);assert d['adapter_error']=='ValueError' and d['not_registered'] and d['POST_GET_target']==d['journal_query']==0
 for r in d['rejected']:assert r['HTTP']==400 and not r['data']['success'] and r['data']['visual_state']==d['visual'] and not any(h['operation']=='mostrar' for h in r['data']['history'])
@pytest.mark.parametrize('sid,name',[(d['structure'],d['case']) for d in read('browser-report.json')])
def test_actual_browser_rejection_reload_existing_five_sections_views_no_new_controls(sid,name):
 d=next(d for d in read('browser-report.json') if (d['structure'],d['case'])==(sid,name));assert all(d[k] for k in ['not_registered','no_selector','readonly','views_equal','five_sections']);assert d['extra_UI_POSTs']==0 and not d['JS_errors'] and d['standalone_mostrar_calls']==d['query_records']==0;assert len(d['rejected'])==2

def test_shared_actual_callers_reused_only_eleven_byte_exact_inputs_no_mostrar_calls():
 d=read('caller-input-reuse.json');assert d['count']==len(d['inputs'])==11
 for x in d['inputs']:
  a=E.parents[4]/x['current'];b=E.parents[4]/x['baseline']
  assert hashlib.sha256(audit_input_path(b).read_bytes()).hexdigest()==x['SHA256']
  if x['current'].replace(chr(92),'/').startswith('docs/tads_C/'):
   assert_historical_protected_hash(E.parents[4],x['current'],x['SHA256'])
  else:assert audit_input_path(a).read_bytes()==audit_input_path(b).read_bytes() and hashlib.sha256(audit_input_path(a).read_bytes()).hexdigest()==x['SHA256']
  if a.name=='main.c':assert b'_mostrar(' not in audit_input_path(a).read_bytes()
def test_shared_native_observers_separate_safe_readonly_void_functions():
 for sid,calls,events,conditions in [('stack',18,192,68),('queue',22,240,58)]:
  d=read(sid+'-native-summary.json');assert (d['calls'],d['events'],d['conditions'])==(calls,events,conditions);ns=[json.loads(s) for s in (audit_input_path(E/('native-'+sid)/'events.jsonl')).read_text().splitlines()];assert len(ns)==events
  for x in ns:
   first=next(n for n in ns if n['sample']==x['sample']);assert (x['front_id'],x['rear_id'],x['nodes'])==(first['front_id'],first['rear_id'],first['nodes'])
def test_shared_Doxygen_target_symbols_from_exact_reused_source_sets():
 root=E.parent
 for sid,folder,symbol in [('stack','visible-stack-cima-baseline-low','pila_mostrar'),('queue','visible-queue-front-final-baseline-low','cola_mostrar')]:
  dox=root/folder/'caller-doxygen';assert not (audit_input_path(dox/'warnings.log')).read_text(encoding='utf-8').strip();assert any(('<name>'+symbol+'</name>') in audit_input_path(p).read_text(encoding='utf-8') for p in audit_input_path(dox).rglob('*.xml'))
def test_shared_finite_resources_separate_method_private_and_rejected_scopes():
 d=read('resources.json');assert len(d['samples'])==36
 for method in ['pila_mostrar','cola_mostrar']:
  rr=[x for x in d['samples'] if x['method']==method];assert len(rr)==18 and len({x['scope'] for x in rr})==2 and all(x['peak_bytes']>0 and x['JSON_bytes']>0 for x in rr)

@pytest.mark.parametrize('name',['front-only','rear-only'])
def test_private_queue_partial_roots_typed_printf_loop_alias_void_scope_readonly(name):
 from app.domain.sequential.show_instruction import build_show_trace
 from app.services.structure_service import StructureService
 d=row('queue',name);native=d['native'];n=native[0]
 fields={'delante':None if n['front_id']==-1 else 'N1','atras':None if n['rear_id']==-1 else 'N1'}
 heap=[{'id':'N1','address':'N1','type':'struct NodoCola','alive':True,'allocated':True,'freed':False,'initialized_mask':3,'fields':{'nro':19,'sgte':None}}]
 state={'items':[{'value':19}] if fields['delante'] else [],'size':int(bool(fields['delante'])),'empty':not bool(fields['delante'])}
 source=StructureService._didactic_content('queue')['operations']['mostrar']
 for sample in sorted({x['sample'] for x in native}):
  tr=build_show_trace(structure_id='queue',payload={},source_code=source,code_title='C',before_state=state,after_state=state,success=True,message='Private partial roots',borrowed_memory={'nodes':heap,'fields':fields});oracle=[x for x in native if x['sample']==sample];assert len(tr['steps'])==len(oracle)
  for step,n in zip(tr['steps'],oracle):
   m=step['pedagogy'];sm=m['show_memory'];assert step['event_type']==n['phase'] and ''.join(step['console'])==n['console'];assert sm['fields']==fields and sm['heap']==heap and step['state_after']==state and sm['allocations']==sm['frees']==0
   if n['phase'] not in ['return','end']:
    assert sm['parameter']['value']==fields and sm['parameter']['type']=='struct Cola' and sm['parameter']['address']!=sm['caller']['address']
    for field in fields:assert next(p for p in m['pointers'] if p['name']=='q.'+field)['target']==fields[field]
   else:assert m['call_stack']==[] and sm['parameter'] is None and sm['scope']=='ended' and not any(v['scope']=='cola_mostrar' for v in m['variables'])
   if n['phase']=='while':assert m['condition']['result']==bool(n['condition'])
   assert not any(v['name']=='return' and v['type']=='int' for v in m['variables'])
