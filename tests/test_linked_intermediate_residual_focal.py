"""Nine finite singly linked list projections; native historical observers are reused."""
import json,re,hashlib
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
from test_controls40_real_flows import controls40_page
from test_queue_intermediate_residual_focal import C_tokens
R=Path(__file__).resolve().parents[1];B=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence'
CASES=[('insert-empty','insertar_inicio',[],{'value':7},0),('insert-unit','insertar_inicio',[7],{'value':7},1),('insert-tail','insertar_final',[7,8,9],{'value':7},6),('insert-interior','lista_insertar_elemento',[7,8,9],{'value':7,'position':2},12),('delete-empty','eliminar_elemento',[],{'value':7},0),('delete-unit','eliminar_elemento',[7],{'value':7},1),('delete-head','eliminar_elemento',[7,8,9],{'value':7},3),('delete-interior','eliminar_elemento',[7,8,9],{'value':8},4),('delete-tail','eliminar_elemento',[7,8,9],{'value':9},5)]

def function_tokens(source,name):
 ts=C_tokens(source);start=next(i-1 for i,t in enumerate(ts) if t==name and ts[i-1]=='void');brace=ts.index('{',start);depth=1;j=brace+1
 while depth:
  if ts[j]=='{':depth+=1
  if ts[j]=='}':depth-=1
  j+=1
 return ts[start:j]

from scripts.published_test_inputs import audit_input_path
def compare(data,case):
 name,op,seeds,payload,number=case;inserting=op!='eliminar_elemento';folder=B/('visible-linked-three-insertions-review/after-fix' if inserting else 'visible-linked-delete-one-review/after-fix')
 report=json.loads((audit_input_path(folder/('review.json' if inserting else 'native-review.json'))).read_text(encoding='utf-8'));old=json.loads((audit_input_path(folder/'backend-traces.json')).read_text(encoding='utf-8'))[number]
 fn='lista_'+op if not op.startswith('lista_') else op
 assert function_tokens(old['source_code'].encode(),fn)==function_tokens((audit_input_path(R/'docs/tads_C/tad_lista.c')).read_bytes(),fn)==function_tokens(data['execution_trace']['source_code'].encode(),fn)
 native=[row['native'] for row in report['rows'] if row['case']==number];fs=data['execution_trace']['steps'];cursor=0;norm=lambda s:re.sub(r'\s+',' ',s.strip())
 for n in native:
  indices=[i for i in range(cursor,len(fs)) if norm(fs[i]['line_text'])==norm(n['line'])];assert indices,n['line'];i=indices[0];cursor=i+1;f=fs[i];v=f['pedagogy'].get('memory_state') or f['state_after']
  assert [x['value'] for x in f['state_after']['items']]==n['reachable_values']
  assert [{k:x[k] for k in ['id','value','next']} for x in v['heap_nodes']]==[{'id':f'N{x["id"]}','value':x['value'],'next':f'N{x["next"]}' if x['next'] else 'NULL'} for x in n['nodes']]
  assert v['head']==(f'N{n["root"]}' if n['root'] else 'NULL') and v['lista']=='&cabeza'
  alias=f['state_snapshot'] if n['line']=='return;' else v;live={x['id'] for x in n['nodes']}
  for var,index in ([('q',0),('t',2)] if inserting else [('p',1),('ant',3)]):
   value=n['aliases'][index];expected=None if value==-2 else 'NULL' if value==0 else f'N{value}' if value in live else f'indeterminado (liberado N{value})';assert alias.get(var)==expected,(name,n['line'],var,alias.get(var),expected)
  if n['scalars'][0] is not None:assert alias.get('i')==n['scalars'][0]
  if n['condition']!=-1:assert f['pedagogy']['condition']['result']==bool(n['condition'])
  assert [line.strip() for chunk in f['console'] for line in chunk.splitlines() if line.strip()]==[x.strip() for x in n.get('console_since_previous',[]) if x.strip()]
  if n['line']=='return;':assert v['scope_ended'] and not any(var in v for var in (['q','t','i'] if inserting else ['p','ant']))
 # Contract checks for publication stores omitted by preserved native instrumentation.
 expected=list(seeds)
 if op=='insertar_inicio':expected.insert(0,payload['value'])
 elif op=='insertar_final':expected.append(payload['value'])
 elif op=='lista_insertar_elemento':expected.insert(payload['position'],payload['value'])
 elif seeds:expected.remove(payload['value'])
 assert [x['value'] for x in data['visual_state']['items']]==expected
 if name=='delete-empty':assert [chunk for f in fs for chunk in f['console']]==[' Valor no encontrado o lista vacia.\n']
 else:assert all(f['console']==[] for f in fs)
 return {'case':name,'native_observations':len(native),'API_frames':len(fs),'native_new_runs':0,'C_operation_tokens_equal':True,'native_source':folder.relative_to(R).as_posix(),'native_limit':'pointer-root assignments beginning *lista omitted; helper internal lines not recorded','final_contract_values':expected}

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_linked_C_current_API(residual58_client,tmp_path,case):
 name,op,seeds,payload,num=case
 for v in seeds:assert residual58_client.post('/sequential/linked_list/operate',json={'operation':'insertar_final','payload':{'value':v}}).status_code==200
 response=residual58_client.post('/sequential/linked_list/operate',json={'operation':op,'payload':payload});assert response.status_code==200
 (tmp_path/'linked-api-proof.json').write_text(json.dumps(compare(response.get_json(),case),indent=2),encoding='utf-8')

@pytest.mark.e2e
@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_linked_C_API_animation(controls40_page,tmp_path,case):
 page,context,base=controls40_page;source=(audit_input_path(R/'tests/_audit_hash_query_medium_browser.py')).read_text(encoding='utf-8-sig');page.add_init_script(source.split('INJECT="""')[1].split('"""')[0].replace('__hash','__linked'))
 errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 page.goto(base+'/sequential/linked_list');name,op,seeds,payload,num=case
 for v in seeds:assert context.request.post(base+'/sequential/linked_list/operate',data={'operation':'insertar_final','payload':{'value':v}}).status==200
 page.reload();page.evaluate("""()=>{const original=renderVisualState;renderVisualState=function(...args){window.__linkedVisual=structuredClone(args[1]);return original(...args);};}""")
 page.select_option('#operation-select',op)
 for key,value in payload.items():page.fill('#field-'+key,str(value))
 if not page.locator('#seq-step-toggle').is_checked():page.click('#seq-step-mode')
 with page.expect_response(lambda r:'/sequential/linked_list/operate' in r.url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();report=compare(data,case);fs=data['execution_trace']['steps'];page.wait_for_function('(op)=>window.__linkedTrace?.operation_name===op',arg=op);count=len(posts);views=[]
 snapshot="""()=>({rendered:window.__linkedVisual,cursor:window.__linkedPlayer.getCursor(),active:[...document.querySelectorAll('#op-pseudocode .sim-active,#op-pseudocode .sim-done')].map(x=>Number(x.dataset.line)),roots:Object.fromEntries([...document.querySelectorAll('[data-clear-pointer]')].map(n=>[n.dataset.clearPointer,n.querySelector('code').textContent])),nodes:[...document.querySelectorAll('[data-clear-node]')].map(n=>({id:n.dataset.clearNode,next:n.dataset.clearNext,status:n.dataset.clearStatus,value:Number(n.querySelector('.stack-linked-field strong').textContent)})).sort((a,b)=>a.id.localeCompare(b.id)),reachable:[...document.querySelectorAll('[data-clear-node][data-clear-status=linked]')].map(n=>n.dataset.clearNode),freed:[...document.querySelectorAll('[data-clear-freed]')].map(n=>n.dataset.clearFreed),console:[...document.querySelectorAll('#seq-printf-console .console-line:not(.muted)')].map(n=>n.textContent),visual:document.querySelector('#visual-state').textContent,heap:document.querySelector('#seq-heap-view').textContent,pointers:document.querySelector('#seq-pointer-view').textContent})"""
 for view in ['linked','current']:
  page.click('#stack-view-'+view);page.evaluate('window.__linkedPlayer.seek(-1)');shots=[]
  for i,f in enumerate(fs):
   page.click('#seq-sim-step');shot=page.evaluate(snapshot);assert shot['cursor']==i;memory=f['pedagogy'].get('memory_state') or f['state_after'];assert shot['rendered']==memory and memory['items']==f['state_after']['items'];assert f['line_index'] in shot['active']
   assert shot['nodes']==sorted([{k:n[k] for k in ['id','next','status','value']} for n in memory['heap_nodes']],key=lambda n:n['id']);assert shot['reachable']==memory['node_ids']
   expected_roots={k:memory[k] for k in ['lista','head','q','t','p','ant'] if k in memory};assert shot['roots']==expected_roots,(i,f['line_text'],shot['roots'],expected_roots)
   freed=[memory[k] for k in ['freed_temp','freed_p','freed_q'] if memory.get(k)];assert shot['freed']==freed
   expected_console=[]
   for frame in fs[:i+1]:
    for chunk in frame['console']:
     line=chunk.strip()
     if line and (not expected_console or expected_console[-1]!=line):expected_console.append(line)
   assert [x.strip() for x in shot['console']]==expected_console;shots.append(shot)
  for i in range(len(shots)-2,-1,-1):page.click('#seq-sim-prev');assert page.evaluate(snapshot)==shots[i]
  views.append({'view':view,'frames':len(shots),'restorations':len(shots)-1})
 assert len(posts)==count and not errors;report.update(animation=views,extra_POSTs=0,JS_errors=errors)
 (tmp_path/'linked-animation-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
