"""Only new required boundary witnesses and deterministic allocation failures."""
import json,hashlib,importlib
from copy import deepcopy
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
from test_controls40_real_flows import controls40_page
R=Path(__file__).resolve().parents[1];E=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/evidence/sequential-criteria-native'
CASES=[('singleton-initial',0),('child-middle-distinct',1)]
def meta(case):
 if case[1]==0:return {'seed':[(7,[3])],'operation':'eliminar_padre','payload':{'parent':7},'expected':[]}
 return {'seed':[(7,[3,4,5])],'operation':'eliminar_hijo','payload':{'parent':7,'child':4},'expected':[{'parent':7,'children':[3,5]}]}
from scripts.published_test_inputs import audit_input_path
def compare(data,case):
 binding=json.loads((audit_input_path(E/'source-bindings.json')).read_text(encoding='utf-8'));assert hashlib.sha256((audit_input_path(R/'docs/tads_C/tad_sublista.c')).read_bytes()).hexdigest()==binding['tad_sublista.c']
 events=[x for x in json.loads((audit_input_path(E/'sublist-two-events.json')).read_text(encoding='utf-8')) if x['case']==case[1]];fs=data['execution_trace']['steps'];mapping={0:'NULL',1:'P1',2:'H1.1',3:'H1.2',4:'H1.3'};cursor=0
 for event in events:
  if event['line']=='FINAL':continue
  indices=[i for i in range(cursor,len(fs)) if fs[i]['line_text'].strip()==event['line']];assert indices;index=indices[0];cursor=index+1;f=fs[index];m=f['pedagogy']['memory_state'];expected=[]
  for n in event['nodes']:
   item={'id':mapping[n['id']],'kind':'parent' if n['type']==1 else 'child','value':n['value'],'next':mapping[n['next']]}
   if n['type']==1:item['sub']=mapping[n['sub']]
   expected.append(item)
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in m['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id'])
  assert m['head']==mapping[event['root']];assert [n['id'] for n in f['pedagogy']['heap_transition']['freed']]==([mapping[event['freed']]] if event['freed'] else [])
 assert [{'parent':x['parent'],'children':x['children']} for x in data['visual_state']['items']]==meta(case)['expected'];assert all(f['console']==[] for f in fs)
 return {'case':case[0],'native_observations':len(events),'API_frames':len(fs),'native_new_runs':1,'native_scope':'post store/free witnesses only; not every frame/scoped local','indirect_events':[x['line'] for x in events if x['line'].startswith('*')]}

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_new_required_sublist_C_API(residual58_client,tmp_path,case):
 m=meta(case)
 for parent,children in m['seed']:
  assert residual58_client.post('/sequential/sublist/operate',json={'operation':'insertar_padre','payload':{'parent':parent}}).status_code==200
  for child in children:assert residual58_client.post('/sequential/sublist/operate',json={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).status_code==200
 data=residual58_client.post('/sequential/sublist/operate',json={'operation':m['operation'],'payload':m['payload']}).get_json()
 (tmp_path/'criteria-sublist-api-proof.json').write_text(json.dumps(compare(data,case),indent=2),encoding='utf-8')

FAULTS=[('linked-head','linked_list','insertar_inicio',{'value':99},'tad_lista','NodoLista','nro'),('linked-tail','linked_list','insertar_final',{'value':99},'tad_lista','NodoLista','nro'),('linked-position','linked_list','lista_insertar_elemento',{'value':99,'position':2},'tad_lista','NodoLista','nro'),('circular-head','circular_list','insertar_inicio',{'value':99},'tad_lista_circular','LCirNodo','valor'),('circular-tail','circular_list','insertar_final',{'value':99},'tad_lista_circular','LCirNodo','valor'),('sublist-parent','sublist','insertar_padre',{'parent':99},'tad_sublista','Nodo','nro'),('sublist-child','sublist','insertar_hijo',{'parent':7,'child':99},'tad_sublista','Sublista','nro')]
FAULTS += [('stack-new-api','stack','apilar',{'value':99},'tad_pila','NodoPila','nro'),('queue-new-api','queue','encolar',{'value':99},'tad_cola','NodoCola','nro'),('priority-new-api','priority_queue','encolar',{'value':99,'priority':1},'tad_cola_prioridad','CPNodo','valor')]
@pytest.mark.parametrize('fault',FAULTS,ids=lambda x:x[0])
def test_required_allocation_failure_C_API(residual58_client,residual58_app,monkeypatch,tmp_path,fault):
 name,family,op,payload,module,class_name,field=fault;url='/sequential/'+family+'/operate'
 seeds=[('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3})] if family=='sublist' else [('insertar_final',{'value':7}),('insertar_final',{'value':8})]
 if family=='stack':seeds=[('apilar',{'value':7})]
 elif family=='queue':seeds=[('encolar',{'value':7})]
 elif family=='priority_queue':seeds=[('encolar',{'value':7,'priority':2})]
 for operation,value in seeds:assert residual58_client.post(url,json={'operation':operation,'payload':value}).status_code==200
 with residual58_client.session_transaction() as session:before=deepcopy(dict(session))
 source=importlib.import_module('app.domain.sequential.'+module);constructor=getattr(source,class_name);denials=[]
 def denied(*args,**kwargs):
  value=kwargs.get(field,args[0] if args else None)
  if value==99:denials.append(value);raise MemoryError('Private deterministic allocation denial')
  return constructor(*args,**kwargs)
 monkeypatch.setattr(source,class_name,denied);monkeypatch.setitem(residual58_app.config,'PROPAGATE_EXCEPTIONS',False)
 response=residual58_client.post(url,json={'operation':op,'payload':payload});body=response.get_json(silent=True)
 with residual58_client.session_transaction() as session:after=deepcopy(dict(session))
 assert denials==[99] and before==after
 t=(body or {}).get('execution_trace');conforms=bool(response.status_code>=400 and (body or {}).get('success') is False and t and t.get('steps') and t.get('success') is False)
 proof={'case':name,'status':response.status_code,'body':body,'denied_allocations':len(denials),'session_unchanged':before==after,'C_error_contract':'no new object, roots unchanged; stack/queue/linked allocation diagnostic, priority/circular/sublist false/NULL silently','C_API_failure_equivalent':conforms,'no_actual_OOM':True}
 (tmp_path/'allocation-failure-proof.json').write_text(json.dumps(proof,indent=2),encoding='utf-8')
 assert conforms,proof

@pytest.mark.e2e
@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_new_required_sublist_C_API_animation(controls40_page,tmp_path,case):
 page,context,base=controls40_page;source=(audit_input_path(R/'tests/_audit_hash_query_medium_browser.py')).read_text(encoding='utf-8-sig');page.add_init_script(source.split('INJECT="""')[1].split('"""')[0].replace('__hash','__sub'))
 errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 m=meta(case)
 for parent,children in m['seed']:
  assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_padre','payload':{'parent':parent}}).status==200
  for child in children:assert context.request.post(base+'/sequential/sublist/operate',data={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).status==200
 page.goto(base+'/sequential/sublist');page.evaluate("""()=>{const original=renderVisualState;renderVisualState=function(...args){window.__subVisual=structuredClone(args[1]);return original(...args);};}""")
 page.select_option('#operation-select',m['operation']);payload={'parent':m['payload']['parent']}
 if m['operation'] in ['insertar_hijo','eliminar_hijo']:payload['child']=m['payload']['child']
 for k,v in payload.items():page.fill('#field-'+k,str(v))
 if not page.locator('#seq-step-toggle').is_checked():page.click('#seq-step-mode')
 with page.expect_response(lambda r:'/sequential/sublist/operate' in r.url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();report=compare(data,case);fs=data['execution_trace']['steps'];page.wait_for_function('(op)=>window.__subTrace?.operation_name===op',arg=m['operation']);count=len(posts);views=[]
 snapshot="""()=>({rendered:window.__subVisual,cursor:window.__subPlayer.getCursor(),active:[...document.querySelectorAll('#op-pseudocode .sim-active,#op-pseudocode .sim-done')].map(x=>Number(x.dataset.line)),head:document.querySelector('[data-sublist-head]')?.dataset.sublistHead,nodes:[...document.querySelectorAll('[data-sublist-node]')].map(n=>({id:n.dataset.sublistNode,kind:n.dataset.sublistKind,status:n.dataset.sublistStatus,next:n.dataset.sublistNext,sub:n.dataset.sublistSub,value:n.dataset.sublistValue})).sort((a,b)=>a.id.localeCompare(b.id)),frames:[...document.querySelectorAll('[data-sublist-frame]')].map(n=>n.dataset.sublistFrame),pointers:[...document.querySelectorAll('[data-sublist-pointer]')].map(n=>({name:n.dataset.sublistPointer,scope:n.dataset.sublistScope,target:n.querySelector('code').textContent})),freed:[...document.querySelectorAll('[data-sublist-freed]')].map(n=>n.dataset.sublistFreed),console:[...document.querySelectorAll('#seq-printf-console .console-line:not(.muted)')].map(n=>n.textContent),visual:document.querySelector('#visual-state').textContent,heap:document.querySelector('#seq-heap-view').textContent,pointerPanel:document.querySelector('#seq-pointer-view').textContent})"""
 for view in ['linked','current']:
  page.click('#stack-view-'+view);page.evaluate('window.__subPlayer.seek(-1)');shots=[]
  for i,f in enumerate(fs):
   page.click('#seq-sim-step');shot=page.evaluate(snapshot);memory=f['pedagogy']['memory_state'];assert shot['cursor']==i and shot['rendered']==memory and memory['items']==f['state_after']['items'];assert f['line_index'] in shot['active']
   expected=sorted([{'id':n['id'],'kind':n['kind'],'status':n['status'],'next':n['next'],'sub':n.get('sub',''),'value':str(n['value'])} for n in memory['heap_nodes']],key=lambda n:n['id']);assert shot['nodes']==expected,(i,f['line_text'],shot['nodes'],expected)
   assert shot['head']==memory['head'];assert shot['frames']==[x['function'] for x in memory['sublist_frames']]
   frame=memory['sublist_frames'][-1] if memory['sublist_frames'] else None
   expectedPointers=[{'name':k,'scope':frame['function'],'target':str(v)} for k,v in {**frame['parameters'],**frame['locals']}.items() if k in ['lista','padre','actual','anterior','next','lista_hijos','destino','nuevo']] if frame else []
   assert shot['pointers']==expectedPointers;assert shot['freed']==([memory['freed_actual']] if memory.get('freed_actual') else []);assert shot['console']==[];shots.append(shot)
  for i in range(len(shots)-2,-1,-1):page.click('#seq-sim-prev');assert page.evaluate(snapshot)==shots[i]
  views.append({'view':view,'frames':len(shots),'restorations':len(shots)-1})
 assert len(posts)==count and not errors;report.update(animation=views,extra_POSTs=0,JS_errors=errors)
 (tmp_path/'criteria-sublist-animation-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
