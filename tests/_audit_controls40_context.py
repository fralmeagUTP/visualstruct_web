"""Discover real initial/prepared contexts for40assigned controls, not coverage."""
import json,threading
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from app import create_app
from app.config import Config
R=Path(__file__).resolve().parents[1];E=R/'openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/evidence'
def main():
 owned=E/'controls40-context-owned';owned.mkdir(exist_ok=False)
 class PrivateConfig(Config):
  TESTING=True;APP_ENV='testing';SECRET_KEY='controls40-private';SESSION_TYPE='cachelib';SESSION_CACHE_DIR=str(owned/'sessions');SESSION_COOKIE_NAME='controls40_private'
 app=create_app(PrivateConfig);server=make_server('127.0.0.1',0,app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 ids=json.loads((R/'tests/fixtures/residual40-controls-v1.json').read_text(encoding='utf-8'))['ids'];results=[]
 def save():
  (E/'controls40-context-report.json').write_text(json.dumps({'scope':'context discovery only, not behavioral proof','rows':results},indent=2)+'\n',encoding='utf-8')
 def snapshot(page,target):
  loc=page.locator('#'+target);return {'count':loc.count(),'visible':loc.is_visible() if loc.count()==1 else False,'enabled':loc.is_enabled() if loc.count()==1 else False,'markup':loc.evaluate('(e)=>e.outerHTML')[:350] if loc.count()==1 else None}
 try:
  with sync_playwright() as pw:
   browser=pw.chromium.launch()
   for module,path in [('graph','/graph/graph/construccion'),('hash','/hash/hash_table'),('hierarchical','/hierarchical/abb'),('sequential','/sequential/queue'),('sorting','/sorting/visualizador'),('sequential','/sequential/stack')]:
    context=browser.new_context();page=context.new_page();page.set_default_timeout(5000);page.goto(base+path,wait_until='networkidle')
    switch=page.locator('label[for="didactic-mode-switch"]')
    if switch.is_visible():switch.click()
    targets=[x for x in ids if '/'+module+'/' in x];rows=[{'id':ident,'page':path,'initial':snapshot(page,ident.split(':')[3])} for ident in targets]
    preparation={'performed':False}
    try:
     if path!='/sequential/stack' and module!='sorting':
      select='#graph-operation-select' if module=='graph' else ('#hash-operation-select' if module=='hash' else '#operation-select')
      operation='insert_vertex' if module=='graph' else ('insert' if module=='hash' else ('insertar' if module=='hierarchical' else 'encolar'))
      if page.locator(select).is_visible():
       page.select_option(select,operation)
       for key,value in ([('key','1'),('value','7')] if module=='hash' else ([('vertex','7')] if module=='graph' else [('value','7')])):
        loc=page.locator(f'[name="{key}"]');assert loc.is_visible();loc.fill(value)
       step='#'+{'graph':'graph','hash':'hash','hierarchical':'hier','sequential':'seq'}[module]+'-sim-step'
       if page.locator(step).is_visible() and page.locator(step).is_enabled():
        page.click(step);page.wait_for_timeout(700);preparation={'performed':True,'operation':operation}
     elif module=='sorting':
      response=context.request.post(base+'/api/ordenamiento/create-array',data={'values':[3,1]});assert response.status==200;page.reload(wait_until='networkidle');preparation={'performed':True,'operation':'create_array only'}
    except Exception as error:preparation={'performed':False,'error':str(error)[:500]}
    for row in rows:row['prepared']=snapshot(page,row['id'].split(':')[3]);row['preparation']=preparation
    results.extend(rows);save();context.close()
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 print(json.dumps({'rows':len(results),'initial_visible':sum(x['initial']['visible'] for x in results),'prepared_visible':sum(x['prepared']['visible'] for x in results)}))
if __name__=='__main__':main()
