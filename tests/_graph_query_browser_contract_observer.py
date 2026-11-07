"""One new private Graph query player case; no canonical preview/cache/cookies."""
from pathlib import Path
import sys,json,threading,time,hashlib,os
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
from _book_graph_browser_contract import COLLECT, decoded_body, assert_browser_row, main_text
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
OUT=Path(os.environ.get('FOCAL_QUERY_BROWSER_OUT',str(Path(__file__).resolve().parent/'graph-query-browser')))
FIXED=os.environ.get('FOCAL_EXPECT_FIXED')=='1'
VERTEX=int(os.environ.get('FOCAL_QUERY_VERTEX','3'))
EXPECTED=[] if VERTEX==3 else [2,3]
class PrivateConfig(Config):
 APP_ENV='testing';TESTING=True;SECRET_KEY='private-new-query-baseline';SESSION_TYPE='cachelib';SESSION_CACHE_DIR=str(OUT/'cache');SESSION_COOKIE_NAME='focal_private_query';ENABLE_CHECKPOINTS=False
def main():
 from playwright.sync_api import sync_playwright
 OUT.mkdir(parents=True,exist_ok=True)
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
   data=decoded_body(pending.value.json());assert data['success'] and data['result']==EXPECTED
   assert data['source_contract']=='graph-book/v1'
   trace=data['execution_trace'];assert trace['book_instruction_model']
   steps=trace['steps'];page.wait_for_function('(n)=>window.auditGraphPlayer.getTotalSteps()===n',arg=len(steps));page.evaluate('()=>window.auditGraphPlayer.pause()');before=len(posts);rows=page.evaluate(COLLECT,len(steps));assert len(posts)==before
   assert len(rows)==2*len(steps)+2
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
    for row in rows:assert_browser_row(row,data)
   else:assert wrong,'Native-proven body defect not observed in browser; re-read baseline'
   main=lambda:main_text(page)
   prior=main();page.reload(wait_until='networkidle');assert len(posts)==before and main()==prior
   assert context.request.get(base+'/help/source/graph/main').body()==prior.encode('utf-8');assert not errors
   (OUT/'response.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'DOM.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(OUT/'main.c').write_text(prior,encoding='utf-8');page.screenshot(path=str(OUT/'UI.png'),full_page=True)
   report={'case_id':'GRAPH-QUERY-EXISTING-NO-SUCCESSORS-DOM-20261004','elapsed_seconds':time.monotonic()-t0,'private_host':base,'cache':str(OUT/'cache'),'success':True,'vertex':VERTEX,'result':EXPECTED,'steps':len(steps),'DOM_boundaries':len(rows),'incorrect_body_highlights':wrong if VERTEX==3 else [],'body_highlight_observations':wrong,'replay_POSTs':0,'reload_POSTs':0,'reloads':1,'DOM_HTTP_main_identical':True,'query_recorded_in_main':('grafo_sucesores(' in prior),'source_contract':'graph-book/v1','errors':errors,'fixed_verified':FIXED,'finding':('Actual player: canonical query path; memory/frames/variables bound in both directions.' if FIXED else 'Historical comparison mode.')+' Caller records the real query and owned-result cleanup under graph-book/v1. Finite two-query browser validation.','source_inputs':{str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in [ROOT/'static/js/graph.js',ROOT/'static/js/interpreter_runtime.js',ROOT/'templates/graph/structure.html']}}
   (OUT/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in report.items() if k not in ['incorrect_body_highlights','source_inputs']},ensure_ascii=False,indent=2));context.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)


if __name__ == '__main__':
 main()
