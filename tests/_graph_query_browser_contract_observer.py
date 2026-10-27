"""One new private Graph query player case; no canonical preview/cache/cookies."""
from pathlib import Path
import sys,json,threading,ast,time,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from _graph_trace_contract import decode_graph_http_trace
from app import create_app
from app.config import Config
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server
OUT=Path(os.environ.get('FOCAL_QUERY_BROWSER_OUT',str(Path(__file__).resolve().parent/'graph-query-browser')));OUT.mkdir(parents=True,exist_ok=True)
FIXED=os.environ.get('FOCAL_EXPECT_FIXED')=='1'
VERTEX=int(os.environ.get('FOCAL_QUERY_VERTEX','3'))
EXPECTED=[] if VERTEX==3 else [2,3]
class PrivateConfig(Config):
 APP_ENV='testing';TESTING=True;SECRET_KEY='private-new-query-baseline';SESSION_TYPE='cachelib';SESSION_CACHE_DIR=str(OUT/'cache');SESSION_COOKIE_NAME='focal_private_query';ENABLE_CHECKPOINTS=False
collect=None
for node in ast.parse((ROOT/'tests/test_graph_four_instruction_e2e.py').read_text(encoding='utf-8')).body:
 if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id=='COLLECT':collect=ast.literal_eval(node.value)
assert collect
app=create_app(PrivateConfig);server=make_server('127.0.0.1',0,app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';t0=time.monotonic()
try:
 with sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':900});page=context.new_page();posts=[];errors=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  history=[('create_graph',{'directed':True})]+[('insert_edge',{'origin':o,'target':t,'weight':w}) for o,t,w in [(1,2,3),(1,3,5),(2,3,7)]]
  for op,payload in history:
   reply=context.request.post(base+'/graph/graph/operate',data={'operation':op,'payload':payload});assert reply.status==200 and reply.json()['success']
  page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.auditGraphPlayer=player;return player;};});")
  page.goto(base+'/graph/graph/construccion',wait_until='networkidle');page.select_option('#graph-operation-select','neighbors');page.locator('#g-op-field-vertex').fill(str(VERTEX));page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
  with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as pending:page.click('#graph-sim-play')
  data=pending.value.json();assert data['success'] and data['result']==EXPECTED
  assert data['source_contract']=='graph-book/v1'
  trace=decode_graph_http_trace(data['execution_trace']);assert trace['book_instruction_model']
  steps=trace['steps'];page.wait_for_function('(n)=>window.auditGraphPlayer.getTotalSteps()===n',arg=len(steps));page.evaluate('()=>window.auditGraphPlayer.pause()');before=len(posts);rows=page.evaluate(collect,len(steps));assert len(posts)==before
  wrong=[]
  for row in rows:
   idx=row['index']
   if idx>=0:
    step=steps[idx]
    if step['pedagogy']['instruction_event']['C_executed']:assert step['line_index'] in row['highlighted']
    else:assert row['highlighted']==[]
    if 'malloc' in step['line_text'] or 'nuevo->' in step['line_text'] or 'ver = nuevo' in step['line_text']:wrong.append({'index':idx,'direction':row['direction'],'line_text':step['line_text'],'DOM_highlighted_lines':row['highlighted']})
  if FIXED:
   if VERTEX==3:assert not wrong,wrong
   else:
    assert sum(s['phase']=='allocate' for s in steps)==2
    assert sum(s['phase']=='free' for s in steps)==2
   compact=lambda v:json.dumps(v,ensure_ascii=False,separators=(',',':'))
   for row in rows:
    idx=row['index'];ped=steps[idx]['pedagogy'] if idx>=0 else steps[0]['pedagogy']['initial_frame'];mem=ped.get('memory_display',ped['memory_state'])
    assert row['heap']==[{'id':n['id'],'kind':n['kind'],'contents':compact(n['fields'])} for n in mem['heap_nodes']],(idx,row['direction'])
    assert row['stack']==[{'id':f['frame_id'],'text':f['function']+': '+f['scope_status']} for f in ped['call_stack']],(idx,row['direction'],row['stack'],mem['frames'])
    assert row['heads']=='Grafo prestado: '+compact(mem['graph'])
    assert row['retired']=='Retiradas (sólo registro histórico): '+compact(mem['retired_objects'])
    assert len(row['variables'])==len(ped['variables'])
    for got,v in zip(row['variables'],ped['variables']):
     assert got['name']==v['name'] and got['scope']==v['scope']
     assert compact(v['previous']) in got['text'] and compact(v['value']) in got['text']
    assert row['message']==(data['message'] if idx==len(steps)-1 else 'Operación preparada: resultado pendiente hasta completar las llamadas C.')
  else:assert wrong,'Native-proven body defect not observed in browser; re-read baseline'
  main=lambda:page.locator('#action-history').get_attribute('data-raw-code')
  prior=main();page.reload(wait_until='networkidle');assert len(posts)==before and main()==prior
  assert context.request.get(base+'/help/source/graph/main').body()==prior.encode('utf-8');assert not errors
  (OUT/'response.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'DOM.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'main.c').write_text(prior,encoding='utf-8');page.screenshot(path=str(OUT/'UI.png'),full_page=True)
  report={'case_id':'GRAPH-QUERY-EXISTING-NO-SUCCESSORS-DOM-20261004','elapsed_seconds':time.monotonic()-t0,'private_host':base,'cache':str(OUT/'cache'),'success':True,'vertex':VERTEX,'result':EXPECTED,'steps':len(steps),'DOM_boundaries':len(rows),'incorrect_body_highlights':wrong if VERTEX==3 else [],'body_highlight_observations':wrong,'replay_POSTs':0,'reload_POSTs':0,'reloads':1,'DOM_HTTP_main_identical':True,'query_recorded_in_main':('grafo_sucesores(' in prior),'source_contract':'graph-book/v1','errors':errors,'fixed_verified':FIXED,'finding':('Actual player: canonical query path; memory/frames/variables bound in both directions.' if FIXED else 'Historical comparison mode.')+' Caller records the real query and owned-result cleanup under graph-book/v1. Finite two-query browser validation.','source_inputs':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'static/js/graph.js',ROOT/'static/js/interpreter_runtime.js',ROOT/'templates/graph/structure.html']}}
  (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['incorrect_body_highlights','source_inputs']},ensure_ascii=False,indent=2));context.close();browser.close()
finally:server.shutdown();thread.join(timeout=5)
