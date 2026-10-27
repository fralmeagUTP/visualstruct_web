"""Focal before/after nominal bytes and semantic allocation-failure contracts."""
import json,os,hashlib
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
from test_controls40_real_flows import controls40_page
from test_sequential_acceptance_criteria_focal import FAULTS
R=Path(__file__).resolve().parents[1];E=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/evidence'
NOMINAL=[('stack','apilar',{'value':21},'apilar',{'value':23}),('queue','encolar',{'value':21},'encolar',{'value':23}),('priority_queue','encolar',{'value':21,'priority':2},'encolar',{'value':23,'priority':1}),('linked_list','insertar_final',{'value':21},'insertar_inicio',{'value':23}),('circular_list','insertar_final',{'value':21},'insertar_final',{'value':23}),('sublist','insertar_padre',{'parent':21},'insertar_hijo',{'parent':21,'child':23})]
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',NOMINAL,ids=lambda x:x[0])
def test_nominal_response_is_unchanged(residual58_client,tmp_path,case):
 family,seed,seed_payload,operation,payload=case;url='/sequential/'+family+'/operate';assert residual58_client.post(url,json={'operation':seed,'payload':seed_payload}).status_code==200
 response=residual58_client.post(url,json={'operation':operation,'payload':payload});assert response.status_code==200;data=response.get_json();assert data['success'] is True and len(data['history'])==2
 target=E/'allocation-nominal-before'/f'{family}.json'
 if os.environ.get('VS_CAPTURE_ALLOCATION_BASELINE')=='1':
  assert not audit_input_path(target).exists();target.parent.mkdir(exist_ok=True);target.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
 else:assert data==json.loads(audit_input_path(target).read_text(encoding='utf-8'))
 (tmp_path/'nominal-proof.json').write_text(json.dumps({'family':family,'complete_response_equal_to_before':os.environ.get('VS_CAPTURE_ALLOCATION_BASELINE')!='1','baseline_sha256':hashlib.sha256(audit_input_path(target).read_bytes()).hexdigest()}),encoding='utf-8')

@pytest.mark.parametrize('fault',FAULTS,ids=lambda x:x[0])
def test_delivered_failure_trace_is_C_NULL_not_success(tmp_path,fault):
 from app.services.trace.engine import TraceEngine
 from app.services.execution_trace_service import ExecutionTraceService
 name,family,op,payload,module,class_name,field=fault
 records=[json.loads(audit_input_path(p).read_text(encoding='utf-8')) for p in (audit_input_path(E/'allocation-transport-applied-fix-owned')).rglob('allocation-failure-proof.json')]
 record=next(x for x in records if x['case']==name);body=record['body'];trace=body['execution_trace'];assert record['status']==400 and body['success'] is False and trace['success'] is False and trace['mutates'] is False
 assert body['error']['code']==trace['error']['code']=='allocation_failed' and trace['error']['object_created'] is False
 assert trace['final_state']==body['visual_state'];TraceEngine.validate_legacy_trace_readonly(trace)
 first=trace['steps'][0]['pedagogy']['heap_objects'];expected={n['id']:n['fields'] for n in first}
 assert len(expected)==len(first)
 for step in trace['steps']:
  objects=step['pedagogy']['heap_objects'];assert len(objects)==len(expected) and {n['id']:n['fields'] for n in objects}==expected
  assert all(n['allocated'] and not n['freed'] and n['status']=='linked' for n in objects)
  assert not step['pedagogy']['heap_transition']['freed'] and not step['pedagogy']['heap_transition']['dangling_references']
  line=step['line_text'].strip();assert not __import__('re').search(r'->\w+\s*=(?!=)',line),line
  assert 'allocator_success_return'!=step['event_type']
  expected_console=ExecutionTraceService._printf_literal(step['line_text'],preserve_trailing_newlines=True) if line.startswith('printf(') else None
  assert step['console']==([expected_console] if expected_console is not None else [])
 raw=json.dumps(body,ensure_ascii=False);assert 'Private deterministic allocation denial' not in raw and 'Traceback' not in raw
 assert trace['c_return']==({'type':'void','value':None} if family in ['stack','queue','linked_list'] else {'type':'Nodo *','value':'NULL'} if family=='sublist' and op=='insertar_padre' else {'type':'bool','value':False})
 (tmp_path/'null-path-verification.json').write_text(json.dumps({'case':name,'frames':len(trace['steps']),'existing_objects':len(expected),'new_objects':0,'stdout_chunks':sum(len(f['console']) for f in trace['steps']),'C_return':trace['c_return'],'privacy':True}),encoding='utf-8')

def test_metadata_memory_error_is_not_relabelled_as_constructor_failure(monkeypatch):
 from app.services.structure_service import StructureService
 from app.domain.sequential.tad_wrappers import ListaEnlazada
 def metadata_error(self):raise MemoryError('Private metadata error after publication')
 monkeypatch.setattr(ListaEnlazada,'_recalcular_metadata',metadata_error)
 with pytest.raises(MemoryError,match='Private metadata error'):
  StructureService.execute_operation('linked_list','insertar_inicio',{'value':99},[])

import importlib
UI_FAULTS=[FAULTS[i] for i in [0,3,5,6,7,8,9]]
@pytest.mark.e2e
@pytest.mark.parametrize('fault',UI_FAULTS,ids=lambda x:x[0])
def test_failed_reservation_is_playable_without_new_objects(controls40_page,monkeypatch,tmp_path,fault):
 page,context,base=controls40_page;name,family,operation,payload,module,class_name,field=fault
 inject=(audit_input_path(R/'tests/_audit_hash_query_medium_browser.py')).read_text(encoding='utf-8-sig').split('INJECT="""')[1].split('"""')[0].replace('__hash','__allocation');page.add_init_script(inject)
 seeds=[('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3})] if family=='sublist' else [('insertar_final',{'value':7}),('insertar_final',{'value':8})]
 if family=='stack':seeds=[('apilar',{'value':7})]
 elif family=='queue':seeds=[('encolar',{'value':7})]
 elif family=='priority_queue':seeds=[('encolar',{'value':7,'priority':2})]
 url=base+'/sequential/'+family+'/operate'
 for op,values in seeds:assert context.request.post(url,data={'operation':op,'payload':values}).status==200
 page.goto(base+'/sequential/'+family);page.select_option('#operation-select',operation)
 for key,value in payload.items():page.fill('#field-'+key,str(value))
 source=importlib.import_module('app.domain.sequential.'+module);constructor=getattr(source,class_name);denied=[]
 def fail(*args,**kwargs):
  value=kwargs.get(field,args[0] if args else None)
  if value==99:denied.append(value);raise MemoryError('DO_NOT_EXPOSE_ALLOCATION_SECRET')
  return constructor(*args,**kwargs)
 monkeypatch.setattr(source,class_name,fail);errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 if not page.locator('#seq-step-toggle').is_checked():page.click('#seq-step-mode')
 with page.expect_response(lambda r:r.url==url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();assert response.value.status==400 and data['success'] is False;trace=data['execution_trace'];page.wait_for_function('()=>window.__allocationTrace?.allocation_failure===true');count=len(posts)
 assert page.locator('#seq-sim-step').is_enabled() and denied==[99];assert 'DO_NOT_EXPOSE' not in page.content();assert page.locator('#message-box').inner_text()==data['message']
 snap="""()=>({cursor:window.__allocationPlayer.getCursor(),rendered:window.__allocationRendered,active:[...document.querySelectorAll('#op-pseudocode .sim-active,#op-pseudocode .sim-done')].map(n=>Number(n.dataset.line)),visual:document.querySelector('#visual-state').textContent,heap:document.querySelector('#seq-heap-view').textContent,pointers:document.querySelector('#seq-pointer-view').textContent,console:[...document.querySelectorAll('#seq-printf-console .console-line:not(.muted)')].map(n=>n.textContent),ids:[...document.querySelectorAll('[data-clear-node],[data-sublist-node],[data-queue-enqueue-node],[data-priority-enqueue-node],[data-stack-push-node]')].map(n=>n.getAttribute('data-clear-node')||n.getAttribute('data-sublist-node')||n.getAttribute('data-queue-enqueue-node')||n.getAttribute('data-priority-enqueue-node')||n.getAttribute('data-stack-push-node'))})"""
 observations=[]
 for view in ['linked','current']:
  page.click('#stack-view-'+view);page.evaluate('window.__allocationPlayer.seek(-1)');shots=[];initial_ids=None
  for i,frame in enumerate(trace['steps']):
   page.click('#seq-sim-step');shot=page.evaluate(snap);assert shot['cursor']==i and shot['rendered']==frame['state_after'] and frame['line_index'] in shot['active']
   if initial_ids is None:initial_ids=sorted(shot['ids'])
   assert sorted(shot['ids'])==initial_ids and len(set(shot['ids']))==len(shot['ids']);expected=[]
   for f in trace['steps'][:i+1]:
    for chunk in f['console']:
     line=chunk.strip()
     if line and (not expected or expected[-1]!=line):expected.append(line)
   assert [x.strip() for x in shot['console']]==expected;shots.append(shot)
  for i in range(len(shots)-2,-1,-1):page.click('#seq-sim-prev');assert page.evaluate(snap)==shots[i]
  observations.append({'view':view,'frames':len(shots),'restorations':len(shots)-1,'object_ids':initial_ids})
 assert len(posts)==count and denied==[99] and not errors
 (tmp_path/'allocation-ui-proof.json').write_text(json.dumps({'case':name,'success':False,'status':400,'animation':observations,'extra_POSTs':0,'denied_allocations':1,'privacy':True,'JS_errors':errors}),encoding='utf-8')
