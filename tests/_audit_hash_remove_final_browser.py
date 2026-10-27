from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-remove-instructions-medium';B=E/'browser-final-focused';B.mkdir(exist_ok=True)
sys.path.insert(0,str(R));q=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');INJECT=q.split('INJECT="""')[1].split('"""')[0];SNAP=q.split('SNAP="""')[1].split('"""')[0]
fixtures=json.loads((E/'report.json').read_text(encoding='utf-8'));pairs=[(1,10),(4,40),(7,70),(10,100)]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);reports=[]
 for case,entries in [('head',pairs)]:
  context=browser.new_context();page=context.new_page();page.add_init_script(INJECT);errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);page.goto('http://127.0.0.1:5051/hash/hash_table');page.wait_for_selector('#hash-operation-select')
  page.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'create_table','payload':{'capacity':3}})
  for k,v in entries:page.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'insert','payload':{'key':k,'value':v}})
  page.reload();page.wait_for_selector('#hash-operation-select');forward=back=0
  selected=[r for r in fixtures if r['case']==case]
  for item in selected:
   page.select_option('#hash-operation-select','remove');page.fill('#hash-field-key',str(item['key']))
   with page.expect_response(lambda r:'/hash/hash_table/operate' in r.url and r.request.method=='POST') as response:page.click('#hash-sim-play')
   data=response.value.json();assert data['success'] and data['result']==bool(item['native'][-1]['status']);assert response.value.status==200;trace=data['execution_trace'];assert [f['event_type'] for f in trace['steps']]==[n['token'] for n in item['native']];n=len(trace['steps']);post_count=len(posts);page.click('#hash-sim-step');snapshots=[]
   for i,f in enumerate(trace['steps']):
    page.evaluate('(i)=>window.__hashPlayer.seek(i)',i);snap=page.evaluate(SNAP);assert snap['state']==f['state_after'];assert snap['cursor']==i
    if f['line_index']>=0:assert snap['active']==[f['line_index']]
    assert 'Arreglo de punteros THNodo *' in snap['memory']
    assert 'Cantidad pendiente: '+('sí' if f['debug']['count_write_pending'] else 'no') in snap['memory']
    if f['event_type']=='node_free':assert not f['debug']['variables']['th_eliminar.actual']['initialized'];assert f['debug']['variables']['th_eliminar.actual']['value'] is None;assert f['pedagogy']['memory']['freed'][0]['historical'];assert f['pedagogy']['memory']['freed'][0]['address']==f['debug']['retired_actual'];assert 'retirado: no utilizable' in snap['pointers'];assert '\"fields_valid\": false' in snap['memory']
    if f['debug']['scopes']:assert 'TablaHash *' in snap['pointers']
    snapshots.append(snap);forward+=1
   for i in range(n-2,-1,-1):page.click('#hash-sim-prev');assert page.evaluate(SNAP)==snapshots[i];back+=1
   page.click('#hash-sim-step');page.click('#hash-sim-step');page.click('#hash-sim-next');assert page.evaluate(SNAP)==snapshots[0];assert len(posts)==post_count;page.evaluate('window.__hashPlayer.seek(window.__hashPlayer.getTotalSteps()-1)');page.click('#hash-sim-step')
  last=page.evaluate('window.__hashTrace');before_reload=len(posts);directory=B/case;directory.mkdir(exist_ok=True);main=page.request.get('http://127.0.0.1:5051/help/source/hash_table/main');assert main.status==200;(directory/'main.c').write_bytes(main.body());assert main.body().count(b'th_eliminar(')==len(selected);page.screenshot(path=str(directory/'final.png'),full_page=True);page.reload();page.wait_for_selector('#hash-operation-select');assert page.evaluate('window.__hashTrace')==last;assert len(posts)==before_reload;assert not errors
  reports.append({'case':case,'operations':len(selected),'forward_frames':forward,'backward_restorations':back,'extra_navigation_POSTs':0,'page_errors':errors,'reload_trace_equal':True,'sections':page.locator('.hash-stage').count(),'actual_main_calls':len(selected),'limit':'C statement sequence verified against independent native observer; finite sampled UI'});context.close()
 browser.close();(B/'report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps(reports))
