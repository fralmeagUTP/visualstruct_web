"""Six finite priority queue comparisons against preserved actual C observations."""
import json,re
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
from test_controls40_real_flows import controls40_page
from test_queue_intermediate_residual_focal import C_tokens
R=Path(__file__).resolve().parents[1]
B=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence'
CASES=[('empty-insert','encolar',[],{'value':9,'priority':3},0),('different-insert','encolar',[(7,2)],{'value':-1,'priority':-1},3),('equal-insert','encolar',[(7,1)],{'value':7,'priority':1},6),('interior-extract','desencolar',[(10,3),(20,1),(30,2)],{},1),('equal-extract','desencolar',[(10,3),(20,1),(30,1)],{},4),('empty-extract','desencolar',[],{},7)]

def proof_source(operation):
 folder=B/('visible-priority-queue-'+operation+'-baseline-low')
 for ext in ['c','h']:
  old=folder/('native/tad_cola_prioridad.'+ext if operation=='encolar' else 'current-tad_cola_prioridad.'+ext)
  assert C_tokens(old.read_bytes())==C_tokens((R/'docs/tads_C'/('tad_cola_prioridad.'+ext)).read_bytes())
 return folder

def compare_insert(data,sample,folder):
 native=[n for n in json.loads((folder/'native-report.json').read_text(encoding='utf-8')) if n['sample']==sample]
 fs=data['execution_trace']['steps'];assert len(native)==len(fs);mapping={}
 for n,f in zip(native,fs):
  d=f['debug'];assert n['event']==f['event_type'];assert f['condition_result']==(None if n['condition']==-1 else bool(n['condition']))
  assert len(n['live'])==len(d['heap']);assert f['state_after']['items']==n['root_items'] and f['state_after']['out_index']==n['out_index'] and d['root']['quantity']==n['quantity']
  for a,h in zip(n['live'],d['heap']):assert a['id'] not in mapping or mapping[a['id']]==h['id'];mapping[a['id']]=h['id']
  mapped=lambda x:None if x==-1 else mapping[x]
  for a,h in zip(n['live'],d['heap']):
   assert a['mask']==h['initialized_mask'];assert h['fields']['valor']==a['value'] and h['fields']['prioridad']==a['priority'];assert h['fields']['sgte']==(mapped(a['next_id']) if a['mask']&4 else None)
   assert h['field_validity']=={'valor':bool(a['mask']&1),'prioridad':bool(a['mask']&2),'sgte':bool(a['mask']&4)}
  assert d['root']['front']==mapped(n['front_id']) and d['root']['rear']==mapped(n['rear_id']) and d['root']['quantity']==n['quantity']
  assert f['console']==[] and f['pedagogy']['heap_transition']['freed']==[]
 return len(native),len(fs)

def compare_extract(data,case,folder):
 native=json.loads((folder/'reused-dequeue-native-events.json').read_text(encoding='utf-8'))
 events=[x for x in native if x['case']==case and (x['phase']=='after' or x['phase']=='before' and x['line'].startswith('return '))]
 fs=data['execution_trace']['steps'];cursor=0;norm=lambda s:re.sub(r'\s+',' ',s.strip())
 for event in events:
  candidates=[i for i in range(cursor,len(fs)) if norm(fs[i]['line_text'])==norm(event['line'])];assert candidates,event['line'];i=candidates[0];cursor=i+1;f=fs[i]
  state=f['state_snapshot'] if event['line'].startswith('return ') else f['state_after']
  expected={'items':[{'value':v,'priority':p} for v,p in event['items']],'delante':'NULL' if event['front']==0 else f'N{event["front"]}','atras':'NULL' if event['rear']==0 else f'N{event["rear"]}','cantidad':event['count']}
  for name,node in zip(['actual','prev','objetivo','objetivoPrev'],event['aliases']):
   if node is not None:expected[name]='NULL' if node==0 else f'N{node}'
  if event['output_value'] is not None:expected['valor']=event['output_value']
  if event['output_priority'] is not None:expected['prioridad']=event['output_priority']
  assert all(state.get(k)==v for k,v in expected.items()),(event,expected,state)
  if event['condition']!=-1:assert f['pedagogy']['condition']['result']==bool(event['condition'])
  assert f['console']==[]
 last=events[-1];assert data.get('result')==last['output_value'];assert data['visual_state']['items']==[{'value':v,'priority':p} for v,p in last['items']]
 if case!=7:
  unlink=next(f for f in fs if f['line_text'].strip()=='objetivoPrev->sgte = objetivo->sgte;');release=next(f for f in fs if f['line_text'].strip()=='free(objetivo);');m=unlink['pedagogy']['dequeue_memory'];ids={n['fields']['valor']:n['id'] for n in m['heap']};assert len(m['heap'])==3 and len(set(ids.values()))==3
  detached=next(n for n in m['heap'] if n['id']==ids[20]);assert detached['alive'] and detached['status']=='detached' and detached['fields']['sgte']==ids[30]
  assert next(n for n in m['heap'] if n['id']==ids[10])['fields']['sgte']==ids[30]
  released=release['pedagogy']['dequeue_memory'];assert len(released['heap'])==2 and len(released['retired'])==1 and released['retired'][0]['id']==ids[20] and not released['retired'][0]['alive'] and 'fields' not in released['retired'][0]
 return len(events),len(fs)

def compare(data,case):
 name,op,seeds,payload,sample=case;folder=proof_source(op)
 observed,frames=compare_insert(data,sample,folder) if op=='encolar' else compare_extract(data,sample,folder)
 return {'case':name,'native_observations_compared':observed,'API_frames':frames,'native_new_runs':0,'C_executable_tokens_equal':True,'console_C_output':[],'native_source':folder.relative_to(R).as_posix()}

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_priority_C_current_API(residual58_client,tmp_path,case):
 name,op,seeds,payload,sample=case
 for v,p in seeds:assert residual58_client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':v,'priority':p}}).status_code==200
 response=residual58_client.post('/sequential/priority_queue/operate',json={'operation':op,'payload':payload});assert response.status_code==(400 if name=='empty-extract' else 200)
 (tmp_path/'priority-api-proof.json').write_text(json.dumps(compare(response.get_json(),case),indent=2),encoding='utf-8')

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_priority_C_API_animation(controls40_page,tmp_path,case):
 page,context,base=controls40_page
 source=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');inject=source.split('INJECT="""')[1].split('"""')[0].replace('__hash','__priority')
 page.add_init_script(inject);errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 page.goto(base+'/sequential/priority_queue');name,op,seeds,payload,sample=case
 for v,p in seeds:assert context.request.post(base+'/sequential/priority_queue/operate',data={'operation':'encolar','payload':{'value':v,'priority':p}}).status==200
 page.reload();page.select_option('#operation-select',op)
 for k,v in payload.items():page.fill('#field-'+k,str(v))
 if not page.locator('#seq-step-toggle').is_checked():page.click('#seq-step-mode')
 with page.expect_response(lambda r:'/sequential/priority_queue/operate' in r.url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();report=compare(data,case);trace=data['execution_trace'];page.wait_for_function('(op)=>window.__priorityTrace?.operation_name===op',arg=op);count=len(posts);views=[]
 snap="""()=>({state:window.__priorityRendered,cursor:window.__priorityPlayer.getCursor(),active:[...document.querySelectorAll('#op-pseudocode .sim-active')].map(x=>Number(x.dataset.line)),done:[...document.querySelectorAll('#op-pseudocode .sim-done')].map(x=>Number(x.dataset.line)),visual:document.querySelector('#visual-state').textContent,heap:document.querySelector('#seq-heap-view').textContent,pointers:document.querySelector('#seq-pointer-view').textContent,variables:document.querySelector('#seq-variable-view').textContent,console:document.querySelector('#seq-printf-console').textContent})"""
 for view in ['linked','current']:
  page.click('#stack-view-'+view);page.evaluate('window.__priorityPlayer.seek(-1)');shots=[]
  for i,f in enumerate(trace['steps']):
   page.click('#seq-sim-step');page.wait_for_function('(i)=>window.__priorityPlayer.getCursor()===i',arg=i);shot=page.evaluate(snap);assert shot['state']==f['state_after'];assert f['line_index'] in shot['active'] or (i==len(trace['steps'])-1 and f['line_index'] in shot['done'])
   m=f['pedagogy']['enqueue_memory' if op=='encolar' else 'dequeue_memory'];prefix='priority-'+('enqueue' if op=='encolar' else 'dequeue')
   observed=page.evaluate("""p=>({front:document.querySelector('[data-'+p+'-front]').getAttribute('data-'+p+'-front'),rear:document.querySelector('[data-'+p+'-rear]').getAttribute('data-'+p+'-rear'),quantity:document.querySelector('[data-'+p+'-quantity]').getAttribute('data-'+p+'-quantity'),nodes:[...document.querySelectorAll('[data-'+p+'-node]')].map(n=>({id:n.getAttribute('data-'+p+'-node'),status:n.getAttribute('data-'+p+'-status'),mask:Number(n.getAttribute('data-'+p+'-mask')),fields:[...n.querySelectorAll('[data-'+p+'-field]')].map(f=>({field:f.getAttribute('data-'+p+'-field'),initialized:f.getAttribute('data-initialized'),text:f.querySelector('strong').textContent}))})),freed:[...document.querySelectorAll('[data-priority-dequeue-freed]')].map(n=>n.dataset.priorityDequeueFreed),printf:[...document.querySelectorAll('#seq-printf-console .console-line:not(.muted)')].map(n=>n.textContent)})""",prefix)
   expected={'front':m['root']['front'] or 'NULL','rear':m['root']['rear'] or 'NULL','quantity':str(m['root']['quantity']),'nodes':[],'freed':[n['id'] for n in m.get('retired',[])],'printf':[]}
   for n in m['heap']:
    fields=[]
    for field in (['valor','prioridad','sgte'] if view=='linked' else ['valor','prioridad']):
     text=(str(n['fields'][field]) if n['fields'][field] is not None else 'NULL') if n['field_validity'][field] else 'indeterminado; no leer'
     fields.append({'field':field,'initialized':str(n['field_validity'][field]).lower(),'text':text})
    expected['nodes'].append({'id':n['id'],'status':n['status'],'mask':n['initialized_mask'],'fields':fields})
   assert observed==expected,(i,f['line_text'],observed,expected)
   assert f['console']==[];shots.append(shot)
  for i in range(len(shots)-2,-1,-1):page.click('#seq-sim-prev');assert page.evaluate(snap)==shots[i]
  views.append({'view':view,'frames':len(shots),'restorations':len(shots)-1})
 assert len(posts)==count and not errors
 report.update(animation=views,extra_navigation_POSTs=0,JS_errors=errors)
 (tmp_path/'priority-animation-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
