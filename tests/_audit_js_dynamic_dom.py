"""Observe source-linked interactive node creation in isolated initial page DOM."""
import json,re,tempfile,threading,sys,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--report',required=True);args=parser.parse_args()
 candidates=json.loads(Path('openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals/evidence/js-dynamic-control-candidates.json').read_text(encoding='utf-8'))['candidates'];observed=[]
 routes=['/sequential/'+name for name in ['stack','queue','priority_queue','linked_list','circular_list','sublist']]+['/hierarchical/'+name for name in ['abb','avl','red_black','binary_heap']]+['/graph/graph','/hash/hash_table','/sorting/visualizador']
 with tempfile.TemporaryDirectory(prefix='vs-js-dom-') as folder:
  class Private(Config):
   APP_ENV='testing';TESTING=True;SECRET_KEY='private-js-dom';SESSION_CACHE_DIR=folder;SESSION_FILE_DIR=folder
  server=make_server('127.0.0.1',0,create_app(Private));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  try:
   with sync_playwright() as pw:
    browser=pw.chromium.launch(headless=True);context=browser.new_context()
    context.add_init_script("""(() => {const original=document.createElement;window.__createdInteractive=[];document.createElement=function(...args){const node=original.apply(this,args);if(['button','input','select','textarea','a'].includes(String(args[0]).toLowerCase()))window.__createdInteractive.push({node,stack:new Error().stack});return node;};})();""")
    for route in routes:
     page=context.new_page();page.set_default_timeout(10000);page.goto(f'http://127.0.0.1:{server.server_port}'+route,wait_until='networkidle')
     rows=page.evaluate("""() => window.__createdInteractive.map(x=>({id:x.node.id,tag:x.node.tagName.toLowerCase(),name:x.node.getAttribute('name'),connected:x.node.isConnected,visible:!!x.node.getClientRects().length,stack:x.stack,text:x.node.textContent.slice(0,60)}))""")
     for row in rows:
      match=re.search(r'/static/js/([A-Za-z_]+\.js)(?:\?[^:]*)?:(\d+):\d+',row.pop('stack') or '')
      if match:observed.append({'route':route,'source':'static/js/'+match[1],'line':int(match[2]),**row})
     page.close()
    context.close();browser.close()
  finally:server.shutdown();thread.join(timeout=5)
 results=[]
 for candidate in candidates:
  witnesses=[x for x in observed if x['source']==candidate['source'] and x['line']==candidate['line'] and x['tag']==candidate['tag']]
  results.append({**candidate,'dom_witnesses':witnesses,'dom_status':'OBSERVED_CONNECTED' if any(x['connected'] for x in witnesses) else 'NOT_TRIGGERED_IN_INITIAL_PAGES','published_visibility_verified':any(x['connected'] and x['visible'] for x in witnesses)})
 report={'scope':'13initial pages only; no algorithms, export/download or all conditional states tested','private_sessions':True,'candidates':len(results),'observed_candidate_factories':sum(bool(x['dom_witnesses']) for x in results),'visible_candidate_factories':sum(x['published_visibility_verified'] for x in results),'untriggered_candidate_factories':sum(not x['dom_witnesses'] for x in results),'results':results}
 Path(args.report).write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:report[k] for k in ['candidates','observed_candidate_factories','visible_candidate_factories','untriggered_candidate_factories']}))
if __name__=='__main__':main()
