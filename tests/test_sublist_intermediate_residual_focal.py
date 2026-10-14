"""Eleven finite sublist integrations using final immutable C observations."""
import json
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
from test_controls40_real_flows import controls40_page
from test_queue_intermediate_residual_focal import C_tokens
R=Path(__file__).resolve().parents[1]
F=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sublist-insertions-review/final/sublist-native0/audit-evidence/native-sublist-visible'
REVIEW=json.loads((F/'review.json').read_text(encoding='utf-8'))
CASES=[('parent-empty',17),('parent-tail',0),('child-first',2),('child-tail',1),('delete-empty',19),('parent-head-delete',4),('parent-interior-delete',5),('parent-tail-delete',6),('child-head-delete',8),('child-tail-delete',9),('parent-leaves-unit',23)]

def meta(case):return REVIEW['cases'][case[1]]
def identities(rows):
 first=rows[0]['native'];nodes={n['id']:n for n in first['nodes']};mapping={0:'NULL'};parent=first['root'];i=0
 while parent>0:
  i+=1;mapping[parent]=f'P{i}';child=nodes[parent]['sub'];j=0
  while child>0:j+=1;mapping[child]=f'H{i}.{j}';child=nodes[child]['next']
  parent=nodes[parent]['next']
 for row in rows:
  e=row['native']
  for n in e['nodes']:
   if n['id'] in mapping:continue
   if n['type']==1:mapping[n['id']]='P'+str(1+sum(x.startswith('P') for x in mapping.values()))
   else:
    owners=[f['aliases'][4] for f in e['frames'] if f['aliases'][4]>0];assert owners;prefix='H'+mapping[owners[-1]][1:]+'.';mapping[n['id']]=prefix+str(1+sum(x.startswith(prefix) for x in mapping.values()))
 return mapping

def compare(data,case):
 assert C_tokens((F/'downloaded.c').read_bytes())==C_tokens((R/'docs/tads_C/tad_sublista.c').read_bytes())
 rows=[r for r in REVIEW['rows'] if r['native']['case']==case[1]];mapping=identities(rows);fs=data['execution_trace']['steps'];cursor=0
 for row in rows:
  e=row['native'];matches=[i for i in range(cursor,len(fs)) if fs[i]['line_text'].strip()==e['line']];assert matches,(case,e['line']);i=matches[0];cursor=i+1;f=fs[i];state=f['state_snapshot'] if e['line'].startswith(('if ','while ','return ')) or e['condition'] in {-3,-6} else f['state_after'];expected=[]
  for n in e['nodes']:
   mask=n['mask'];node={'id':mapping[n['id']],'kind':'parent' if n['type']==1 else 'child','value':n['value'] if mask&1 else 'sin inicializar','next':mapping[n['next']] if mask&2 else 'sin inicializar'}
   if n['type']==1:node['sub']=mapping[n['sub']] if mask&4 else 'sin inicializar'
   expected.append(node)
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id']),(case,e,state)
  assert state['head']==mapping[e['root']] and len(state['sublist_frames'])==len(e['frames'])==e['depth']+1
  for observed,frame in zip(e['frames'],state['sublist_frames']):
   assert frame['function']==observed['function'];values={**frame['parameters'],**frame['locals']}
   for name,slot in {'nuevo':0,'actual':1,'anterior':2,'next':3,'padre':4}.items():
    alias=observed['aliases'][slot]
    if alias!=-2:assert values[name]==('indeterminado (liberado)' if alias<=-100 else mapping[alias]),(e,name,frame)
  if e['condition'] in [0,1]:assert f['pedagogy']['condition']['result']==bool(e['condition'])
  assert f['console']==[];assert [n['id'] for n in f['pedagogy']['heap_transition']['freed']]==([mapping[e['freed']]] if e['line']=='free(actual);' else [])
 assert data['success']==meta(case)['success'];assert data['visual_state']==meta(case)['state'];assert all(f['console']==[] for f in fs)
 return {'case':case[0],'native_case':case[1],'native_observations':len(rows),'API_frames':len(fs),'native_new_runs':0,'C_tokens_equal':True,'indirect_events':[r['native']['line'] for r in rows if r['native']['line'].startswith('*')],'native_source':F.relative_to(R).as_posix()}

def seed(client,case):
 for parent,children in meta(case)['seed']:
  assert client.post('/sequential/sublist/operate',json={'operation':'insertar_padre','payload':{'parent':parent}}).status_code==200
  for child in children:assert client.post('/sequential/sublist/operate',json={'operation':'insertar_hijo','payload':{'parent':parent,'child':child}}).status_code==200

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_sublist_C_current_API(residual58_client,tmp_path,case):
 seed(residual58_client,case);m=meta(case);response=residual58_client.post('/sequential/sublist/operate',json={'operation':m['operation'],'payload':m['payload']});assert response.status_code==200
 (tmp_path/'sublist-api-proof.json').write_text(json.dumps(compare(response.get_json(),case),indent=2),encoding='utf-8')

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_sublist_C_API_animation(controls40_page,tmp_path,case):
 page,context,base=controls40_page;source=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');page.add_init_script(source.split('INJECT="""')[1].split('"""')[0].replace('__hash','__sub'))
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
 (tmp_path/'sublist-animation-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
