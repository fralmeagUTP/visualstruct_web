"""Fast allocation error preserves state and equals cached replay; private sessions."""
import importlib,json
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app
from test_controls40_real_flows import controls40_page
from test_allocation_transport_fix import UI_FAULTS
R=Path(__file__).resolve().parents[1]

@pytest.mark.parametrize('fault',UI_FAULTS,ids=lambda x:x[0])
def test_fast_error_equals_cached_replay_without_new_objects(controls40_page,monkeypatch,tmp_path,fault):
 page,context,base=controls40_page;name,family,operation,payload,module,class_name,field=fault
 inject=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig').split('INJECT="""')[1].split('"""')[0].replace('__hash','__fastError').replace("localStorage.setItem('didactic-mode','full');",'');page.add_init_script(inject)
 seeds=[('insertar_padre',{'parent':7}),('insertar_hijo',{'parent':7,'child':3})] if family=='sublist' else [('insertar_final',{'value':7}),('insertar_final',{'value':8})]
 if family=='stack':seeds=[('apilar',{'value':7})]
 elif family=='queue':seeds=[('encolar',{'value':7})]
 elif family=='priority_queue':seeds=[('encolar',{'value':7,'priority':2})]
 url=base+'/sequential/'+family+'/operate';seed_data=None
 for op,values in seeds:
  response=context.request.post(url,data={'operation':op,'payload':values});assert response.status==200;seed_data=response.json()
 page.goto(base+'/sequential/'+family);page.select_option('#operation-select',operation)
 for key,value in payload.items():page.fill('#field-'+key,str(value))
 assert not page.locator('#seq-step-toggle').is_checked()
 source=importlib.import_module('app.domain.sequential.'+module);original=getattr(source,class_name);denied=[]
 def fail(*args,**kwargs):
  value=kwargs.get(field,args[0] if args else None)
  if value==99:denied.append(value);raise MemoryError('FAST_ERROR_PRIVATE_SECRET')
  return original(*args,**kwargs)
 monkeypatch.setattr(source,class_name,fail);posts=[];errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None)
 with page.expect_response(lambda r:r.url==url and r.request.method=='POST') as response:page.click('#seq-sim-execute')
 data=response.value.json();assert response.value.status==400 and not data['success'];trace=data['execution_trace'];assert trace['allocation_failure']
 assert data['visual_state']==seed_data['visual_state'] and data['history']==seed_data['history']
 page.wait_for_function('()=>window.__fastErrorPlayer?.getCursor()===window.__fastErrorTrace?.steps.length-1')
 assert page.locator('#message-box').inner_text()==data['message'];assert 'FAST_ERROR_PRIVATE_SECRET' not in page.content();assert 'Reserva rechazada' in page.locator('#seq-sim-status').inner_text()
 assert not page.locator('#seq-sim-step').is_visible() and not page.locator('#seq-sim-prev').is_visible()
 snap="""()=>({rendered:window.__fastErrorRendered,visual:document.querySelector('#visual-state').textContent,heap:document.querySelector('#seq-heap-view').textContent,pointers:document.querySelector('#seq-pointer-view').textContent,console:[...document.querySelectorAll('#seq-printf-console .console-line:not(.muted)')].map(n=>n.textContent),ids:[...document.querySelectorAll('[data-clear-node],[data-sublist-node],[data-queue-enqueue-node],[data-priority-enqueue-node],[data-stack-push-node]')].map(n=>n.getAttribute('data-clear-node')||n.getAttribute('data-sublist-node')||n.getAttribute('data-queue-enqueue-node')||n.getAttribute('data-priority-enqueue-node')||n.getAttribute('data-stack-push-node'))})"""
 objects=trace['steps'][0]['pedagogy']['heap_objects'];object_ids={n['id'] for n in objects}
 assert all({n['id'] for n in f['pedagogy']['heap_objects']}==object_ids for f in trace['steps'])
 fast=page.evaluate(snap);assert fast['rendered']==data['visual_state'];assert len(fast['ids'])==len(set(fast['ids']))
 expected=[]
 for frame in trace['steps']:
  for chunk in frame['console']:
   line=chunk.strip()
   if line and(not expected or expected[-1]!=line):expected.append(line)
 assert [s.strip() for s in fast['console']]==expected
 count=len(posts);page.click('#seq-step-mode');assert page.locator('#seq-step-toggle').is_checked()
 for i in range(len(trace['steps'])):page.click('#seq-sim-step')
 replay=page.evaluate(snap);assert replay==fast
 page.click('#seq-step-mode');assert page.evaluate(snap)==fast
 assert len(posts)==count==1 and denied==[99] and not errors
 (tmp_path/'fast-error-proof.json').write_text(json.dumps({'case':name,'family':family,'HTTP':400,'fast_preserves_error':True,'state_history_unchanged':True,'heap_object_ids':sorted(object_ids),'objects_created':0,'fast_equals_replay_DOM':True,'toggle_fast_equals_replay_end':True,'console_reached_chunks':expected,'extra_POSTs':0,'private_denial_not_exposed':True,'JS_errors':errors},ensure_ascii=False,indent=2),encoding='utf-8')
