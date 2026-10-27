"""Eight current circular C/API/UI integrations; no native rerun."""
import json,re
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app,residual58_client
from test_controls40_real_flows import controls40_page
from test_queue_intermediate_residual_focal import C_tokens
R=Path(__file__).resolve().parents[1];B=R/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence'
CASES=[('insert-empty','insertar_inicio',[],11,0),('insert-unit','insertar_inicio',[7],11,1),('insert-tail','insertar_final',[7,8,9],11,6),('delete-empty','eliminar_primero',[],7,0),('delete-unit','eliminar_primero',[7],7,1),('delete-head','eliminar_primero',[7,8,9],7,3),('delete-interior','eliminar_primero',[7,8,9],8,4),('delete-tail','eliminar_primero',[7,8,9],9,5)]

from scripts.published_test_inputs import audit_input_path
def compare(data,case):
 name,op,seeds,value,number=case;insert=op.startswith('insertar');folder=B/('visible-circular-two-insertions-review/after-fix' if insert else 'visible-circular-delete-first-review/after-fix/native_delete_first0/native-delete-first')
 assert C_tokens((audit_input_path(folder/'downloaded.c')).read_bytes())==C_tokens((audit_input_path(R/'docs/tads_C/tad_lista_circular.c')).read_bytes())
 rows=json.loads((audit_input_path(folder/(f'comparison-{number}.json' if insert else f'case-{number}.json'))).read_text(encoding='utf-8'));fs=data['execution_trace']['steps'];cursor=0;ptr=lambda n:'sin inicializar' if n==-2 else 'NULL' if n==0 else 'N'+str(n)
 for row in rows:
  e=row['native'];indices=[i for i in range(cursor,len(fs)) if fs[i]['line_text'].strip()==e['line']];assert indices,e['line'];i=indices[0];cursor=i+1;f=fs[i];state=f['state_snapshot'] if e['line'].startswith(('if ','return ')) else f['state_after'];ids=[ptr(n) for n in e['reachable']]
  assert state['cabeza']==ptr(e['head']) and state['cola']==ptr(e['tail']) and state['cantidad']==e['cantidad'] and state['node_ids']==ids
  expected=[{'id':ptr(n['id']),'value':n['value'],'next':ptr(n['next']),'status':'linked' if ptr(n['id']) in ids else 'temporary' if insert else 'detached'} for n in e['nodes']];assert state['heap_nodes']==expected
  assert state['items']==[{'value':next(n['value'] for n in expected if n['id']==id)} for id in ids]
  for var,n in ({k:e[k] for k in ['nuevo','nodo']} if insert else dict(zip(['actual','anterior'],e['aliases'][:2]))).items():
   if n==-2:assert var not in state
   else:assert state[var]==('indeterminado (liberado)' if n<=-100 else ptr(n))
  if e['condition']!=-1:assert f['pedagogy']['condition']['result']==bool(e['condition'])
  assert f['console']==[];assert [x['id'] for x in f['pedagogy']['heap_transition']['freed']]==([ptr(e['freed'])] if not insert and e['line']=='free(actual);' else [])
 expected=list(seeds)
 if insert:expected.insert(0,value) if op=='insertar_inicio' else expected.append(value)
 elif value in expected:expected.remove(value)
 assert [x['value'] for x in data['visual_state']['items']]==expected
 return {'case':name,'native_observations':len(rows),'API_frames':len(fs),'native_new_runs':0,'C_tokens_equal':True,'source':folder.relative_to(R).as_posix(),'indirect_assignments_observed':[x['native']['line'] for x in rows if x['native']['line'].startswith('*')]}

@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_circular_C_current_API(residual58_client,tmp_path,case):
 name,op,seeds,value,num=case
 for v in seeds:assert residual58_client.post('/sequential/circular_list/operate',json={'operation':'insertar_final','payload':{'value':v}}).status_code==200
 response=residual58_client.post('/sequential/circular_list/operate',json={'operation':op,'payload':{'value':value}});assert response.status_code==200
 (tmp_path/'circular-api-proof.json').write_text(json.dumps(compare(response.get_json(),case),indent=2),encoding='utf-8')

@pytest.mark.e2e
@pytest.mark.parametrize('case',CASES,ids=lambda x:x[0])
def test_circular_C_API_animation(controls40_page,tmp_path,case):
 page,context,base=controls40_page;source=(audit_input_path(R/'tests/_audit_hash_query_medium_browser.py')).read_text(encoding='utf-8-sig');page.add_init_script(source.split('INJECT="""')[1].split('"""')[0].replace('__hash','__circ'))
 errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 page.goto(base+'/sequential/circular_list');name,op,seeds,value,num=case;payload={'value':value}
 for v in seeds:assert context.request.post(base+'/sequential/circular_list/operate',data={'operation':'insertar_final','payload':{'value':v}}).status==200
 page.reload();page.evaluate("""()=>{const original=renderVisualState;renderVisualState=function(...args){window.__circVisual=structuredClone(args[1]);return original(...args);};}""")
 page.select_option('#operation-select',op)
 for key,value in payload.items():page.fill('#field-'+key,str(value))
 if not page.locator('#seq-step-toggle').is_checked():page.click('#seq-step-mode')
 with page.expect_response(lambda r:'/sequential/circular_list/operate' in r.url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();report=compare(data,case);fs=data['execution_trace']['steps'];page.wait_for_function('(op)=>window.__circTrace?.operation_name===op',arg=op);count=len(posts);views=[]
 snapshot="""()=>({rendered:window.__circVisual,cursor:window.__circPlayer.getCursor(),active:[...document.querySelectorAll('#op-pseudocode .sim-active,#op-pseudocode .sim-done')].map(x=>Number(x.dataset.line)),roots:Object.fromEntries([...document.querySelectorAll('[data-clear-pointer]')].map(n=>[n.dataset.clearPointer,n.querySelector('code').textContent])),nodes:[...document.querySelectorAll('[data-clear-node]')].map(n=>({id:n.dataset.clearNode,next:n.dataset.clearNext,status:n.dataset.clearStatus,value:(()=>{const t=n.querySelector('.stack-linked-field strong').textContent;return t==='sin inicializar'?t:Number(t)})()})).sort((a,b)=>a.id.localeCompare(b.id)),reachable:[...document.querySelectorAll('[data-clear-node][data-clear-status=linked]')].map(n=>n.dataset.clearNode),freed:[...document.querySelectorAll('[data-clear-freed]')].map(n=>n.dataset.clearFreed),console:[...document.querySelectorAll('#seq-printf-console .console-line:not(.muted)')].map(n=>n.textContent),visual:document.querySelector('#visual-state').textContent,heap:document.querySelector('#seq-heap-view').textContent,pointers:document.querySelector('#seq-pointer-view').textContent})"""
 for view in ['linked','current']:
  page.click('#stack-view-'+view);page.evaluate('window.__circPlayer.seek(-1)');shots=[]
  for i,f in enumerate(fs):
   page.click('#seq-sim-step');shot=page.evaluate(snapshot);assert shot['cursor']==i;memory=f['pedagogy'].get('memory_state') or f['state_after'];assert shot['rendered']==memory and memory['items']==f['state_after']['items'];assert f['line_index'] in shot['active']
   assert shot['nodes']==sorted([{k:n[k] for k in ['id','next','status','value']} for n in memory['heap_nodes']],key=lambda n:n['id']);assert shot['reachable']==memory['node_ids']
   expected_roots={k:memory[k] for k in ['lista','cabeza','cola']};locals=[] if memory.get('scope_ended') else ['actual','anterior'] if op=='eliminar_primero' else ['nodo'] if memory.get('active_function')=='lcir_crear_nodo' else ['nuevo'];expected_roots.update({k:memory[k] for k in locals if k in memory});assert shot['roots']==expected_roots,(i,f['line_text'],shot['roots'],expected_roots)
   freed=[memory[k] for k in ['freed_actual'] if memory.get(k)];assert shot['freed']==freed;assert page.locator('[data-circular-count]').get_attribute('data-circular-count')==str(memory['cantidad'])
   expected_console=[]
   for frame in fs[:i+1]:
    for chunk in frame['console']:
     line=chunk.strip()
     if line and (not expected_console or expected_console[-1]!=line):expected_console.append(line)
   assert [x.strip() for x in shot['console']]==expected_console;shots.append(shot)
  for i in range(len(shots)-2,-1,-1):page.click('#seq-sim-prev');assert page.evaluate(snapshot)==shots[i]
  views.append({'view':view,'frames':len(shots),'restorations':len(shots)-1})
 assert len(posts)==count and not errors;report.update(animation=views,extra_POSTs=0,JS_errors=errors)
 (tmp_path/'circular-animation-proof.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
