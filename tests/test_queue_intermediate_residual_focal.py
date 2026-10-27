"""Finite Queue C-observer/API projection comparison; no native rerun."""
import json,hashlib,importlib.util,re
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
R=Path(__file__).resolve().parents[1];B=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence'
CASES=[('enqueue','encolar',[],{'value':9},0),('dequeue','desencolar',[-1],{},4),('empty-console','desencolar',[],{},2),('cleanup','limpiar',[7,-2,7],{},4)]
def C_tokens(data):
 text=data.decode('utf-8-sig')
 pattern=r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*|[A-Za-z_]\w*|[0-9]+|->|\+\+|--|==|!=|<=|>=|&&|\|\||<<|>>|\+=|-=|\*=|/=|[^\s]'
 return [m.group(0) for m in re.finditer(pattern,text,re.S) if not m.group(0).startswith(('/*','//'))]

from scripts.published_test_inputs import audit_input_path
def source_proof(folder):
 for ext in ['c','h']:
  current=(audit_input_path(R/'docs/tads_C'/('tad_cola.'+ext))).read_bytes();old=(audit_input_path(folder/'native'/('tad_cola.'+ext))).read_bytes();assert C_tokens(current)==C_tokens(old),'Executable tokens or literal differs; native reuse forbidden'

def compare_enqueue(trace,folder,sample):
 native=[x for x in json.loads((audit_input_path(folder/'native-report.json')).read_text(encoding='utf-8')) if x['sample']==sample];assert len(native)==len(trace['steps']);mapping={}
 for n,f in zip(native,trace['steps']):
  d=f['debug'];assert n['event']==f['event_type'];assert (None if n['condition']==-1 else bool(n['condition']))==f['condition_result'];assert len(n['live'])==len(d['heap'])
  for obj,h in zip(n['live'],d['heap']):
   if obj['id'] in mapping:assert mapping[obj['id']]==h['id']
   mapping[obj['id']]=h['id']
  symbol=lambda value:None if value==-1 else mapping[value]
  for obj,h in zip(n['live'],d['heap']):
   assert obj['mask']==h['initialized_mask'] and obj['value']==h['fields']['nro'];assert h['fields']['sgte']==(symbol(obj['next_id']) if obj['mask']&2 else None)
  assert d['root']['front']==symbol(n['front_id']) and d['root']['rear']==symbol(n['rear_id']);assert [x['value'] for x in f['state_after']['items']]==n['root_values'];assert ''.join(line+'\n' for line in f['console'])==n['console']
 return native

def compare_dequeue(trace,folder,sample):
 native=[json.loads(x) for x in (audit_input_path(folder/'native/events.jsonl')).read_text(encoding='utf-8').splitlines()];native=[x for x in native if x['sample']==sample];assert len(native)==len(trace['steps']);symbols={h['id']:'N'+str(i+1) for i,h in enumerate(native[0]['heap'])};symbol=lambda value:None if value==-1 else symbols[value]
 for n,f in zip(native,trace['steps']):
  d=f['debug'];aux=d['aux'];num=d['num'];actual={'token':d['token'],'condition':f['condition_result'],'root_NULL':not d['root']['alive'],'front':d['root']['front'],'rear':d['root']['rear'],'aux_initialized':aux is not None,'aux_id':aux['value'] if aux else None,'aux_alive':bool(aux and aux['valid']),'num_initialized':num['initialized'],'num':num['value'] if num['initialized'] else None,'result_initialized':d['result'] is not None,'result':d['result'],'values':[x['value'] for x in f['state_after']['items']],'heap':[{'id':x['id'],'value':x['fields']['nro'],'next':x['fields']['sgte']} for x in d['heap']],'console':f['console']}
  expected={'token':n['event'],'condition':None if n['condition']==-1 else bool(n['condition']),'root_NULL':bool(n['root_NULL']),'front':symbol(n['front']),'rear':symbol(n['rear']),'aux_initialized':bool(n['aux_initialized']),'aux_id':symbol(n['aux_id']) if n['aux_initialized'] else None,'aux_alive':bool(n['aux_alive']),'num_initialized':bool(n['num_initialized']),'num':n['num'] if n['num_initialized'] else None,'result_initialized':bool(n['result_initialized']),'result':n['result'] if n['result_initialized'] else None,'values':n['values'],'heap':[{'id':symbol(h['id']),'value':h['value'],'next':symbol(h['next'])} for h in n['heap']],'console':n['console'].splitlines()};assert actual==expected,(n['event'],actual,expected)
 return native

def compare_case(data,case):
 name,operation,seeds,payload,sample=case;folder=B/('visible-queue-'+{'encolar':'encolar','desencolar':'desencolar','limpiar':'limpiar'}[operation]+'-baseline-low');source_proof(folder);trace=data['execution_trace']
 if operation=='encolar':native=compare_enqueue(trace,folder,sample)
 elif operation=='desencolar':native=compare_dequeue(trace,folder,sample)
 else:
  spec=importlib.util.spec_from_file_location('retained_cleanup_oracle',audit_input_path(R/'tests/_audit_queue_limpiar_compare_medium.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.compare(trace,sample);native=[x for x in json.loads((audit_input_path(folder/'native-report.json')).read_text(encoding='utf-8')) if x['sample']==sample]
 return {'case':name,'events':len(native),'native_rerun':False,'native_source':folder.relative_to(R).as_posix(),'C_executable_tokens_equal':True,'documentation_changes_not_execution_changes':True,'console_frames':sum(bool(x.get('console')) for x in native)}

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_queue_real_C_events_match_current_API(residual58_client,tmp_path,case):
 name,operation,seeds,payload,sample=case
 for value in seeds:assert residual58_client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':value}}).status_code==200
 response=residual58_client.post('/sequential/queue/operate',json={'operation':operation,'payload':payload});data=response.get_json();assert response.status_code in [200,400];report=compare_case(data,case)
 (tmp_path/'queue-event-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')

from test_controls40_real_flows import controls40_page

@pytest.mark.e2e
@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_queue_C_API_animation_frames(controls40_page,tmp_path,case):
 page,context,base=controls40_page
 source=(audit_input_path(R/'tests/_audit_hash_query_medium_browser.py')).read_text(encoding='utf-8-sig')
 inject=source.split('INJECT="""')[1].split('"""')[0].replace('__hash','__queue')
 page.add_init_script(inject);errors=[];posts=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 page.goto(base+'/sequential/queue')
 name,operation,seeds,payload,sample=case
 for value in seeds:assert context.request.post(base+'/sequential/queue/operate',data={'operation':'encolar','payload':{'value':value}}).status==200
 page.reload();page.select_option('#operation-select',operation)
 if payload:page.fill('#field-value',str(payload['value']))
 if not page.locator('#seq-step-toggle').is_checked():page.click('#seq-step-mode')
 with page.expect_response(lambda r:'/sequential/queue/operate' in r.url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();proof=compare_case(data,case);trace=data['execution_trace']
 page.wait_for_function('(op)=>window.__queueTrace?.operation_name===op',arg=operation)
 count=len(posts);snapshots=[]
 snap="""()=>({state:window.__queueRendered,cursor:window.__queuePlayer.getCursor(),active:[...document.querySelectorAll('#op-pseudocode .sim-active')].map(x=>Number(x.dataset.line)),done:[...document.querySelectorAll('#op-pseudocode .sim-done')].map(x=>Number(x.dataset.line)),heap:document.querySelector('#seq-heap-view')?.textContent,pointers:document.querySelector('#seq-pointer-view')?.textContent,console:document.querySelector('#seq-printf-console')?.textContent,visual:document.querySelector('#visual-state')?.textContent})"""
 for view in ['linked','current']:
  page.click('#stack-view-'+view);page.evaluate('window.__queuePlayer.seek(-1)');shots=[]
  for i,f in enumerate(trace['steps']):
   page.click('#seq-sim-step');page.wait_for_function('(i)=>window.__queuePlayer.getCursor()===i',arg=i)
   shot=page.evaluate(snap);assert shot['state']==f['state_after']
   assert f['line_index'] in shot['active'] or (i==len(trace['steps'])-1 and f['line_index'] in shot['done'])
   for line in f['console']:assert line in shot['console']
   if operation in ['encolar','desencolar']:
    prefix='queue-'+('enqueue' if operation=='encolar' else 'dequeue')
    for field in ['front','rear']:assert page.locator('[data-'+prefix+'-'+field+']').get_attribute('data-'+prefix+'-'+field)==(f['debug']['root'][field] or 'NULL')
    nodes=page.locator('[data-'+prefix+'-node]').evaluate_all("(els,p)=>els.map(n=>({id:n.getAttribute('data-'+p+'-node'),status:n.getAttribute('data-'+p+'-status')}))",prefix)
    assert nodes==[{'id':h['id'],'status':h['status']} for h in f['debug']['heap']]
   if operation=='limpiar':
    assert page.locator('[data-queue-cleanup-front]').get_attribute('data-queue-cleanup-front')==(f['debug']['root']['front'] or 'NULL')
    assert page.locator('[data-queue-cleanup-rear-valid]').get_attribute('data-queue-cleanup-rear-valid')==str(f['debug']['root']['rear_valid']).lower()
    nodes=page.locator('[data-queue-cleanup-node]').evaluate_all("els=>els.map(n=>({id:n.dataset.queueCleanupNode,status:n.dataset.queueCleanupStatus,mask:Number(n.dataset.queueCleanupMask)}))")
    assert nodes==[{'id':h['id'],'status':h['status'],'mask':h['initialized_mask']} for h in f['debug']['heap'] if h['alive']]+[{'id':h['id'],'status':h['status'],'mask':0} for h in f['debug']['heap'] if not h['alive']]
   shots.append(shot)
  for i in range(len(shots)-2,-1,-1):page.click('#seq-sim-prev');assert page.evaluate(snap)==shots[i]
  snapshots.append({'view':view,'frames':len(shots),'restorations':len(shots)-1})
 assert len(posts)==count and not errors
 proof.update(animation=snapshots,navigation_extra_POSTs=0,page_errors=errors)
 (tmp_path/'queue-animation-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
