"""Finite real export/download activation for the twelve deferred JS factories."""
import argparse,json,re,tempfile,threading,sys,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app import create_app
from app.config import Config
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright

def run_flows(report_path):
    report_path=Path(report_path);report_path.parent.mkdir(parents=True,exist_ok=True)
    results=[];created=[]
    pages=[('graph','/graph/graph','graph'),('hash','/hash/hash_table','hash'),('hierarchical','/hierarchical/abb','hier'),('sequential','/sequential/stack','seq'),('sorting','/sorting/visualizador','sorting')]
    with tempfile.TemporaryDirectory(prefix='vs-js-export-private-') as folder:
        class Private(Config):
            APP_ENV='testing';TESTING=True;SECRET_KEY='private-export-test';SESSION_CACHE_DIR=folder;SESSION_FILE_DIR=folder
        server=make_server('127.0.0.1',0,create_app(Private));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        try:
            with sync_playwright() as pw:
                browser=pw.chromium.launch(headless=True);context=browser.new_context(accept_downloads=True,viewport={'width':1366,'height':900})
                context.add_init_script("""(() => {
                  const factory=document.createElement,click=HTMLAnchorElement.prototype.click;
                  window.__interactive=[];
                  document.createElement=function(...args){const e=factory.apply(this,args);if(['a','button'].includes(String(args[0]).toLowerCase()))window.__interactive.push({node:e,stack:new Error().stack,clicked:false});return e;};
                  HTMLAnchorElement.prototype.click=function(){const row=window.__interactive.find(x=>x.node===this);if(row)row.clicked=true;return click.apply(this,arguments);};
                })();""")
                for module,route,prefix in pages:
                    page=context.new_page();page.set_default_timeout(5000);page.goto(f'http://127.0.0.1:{server.server_port}'+route,wait_until='networkidle')
                    # Own small inputs; no algorithms and no shared user cookies.
                    seeds=[]
                    if module=='graph':seeds=[('/graph/graph/operate',{'operation':'insert_vertex','payload':{'vertex':7}})]
                    elif module=='hierarchical':seeds=[('/hierarchical/abb/operate',{'operation':'insertar','payload':{'value':7}})]
                    elif module=='sequential':seeds=[('/sequential/stack/operate',{'operation':'apilar','payload':{'value':7}})]
                    elif module=='sorting':seeds=[('/api/ordenamiento/create-array',{'values':[7]})]
                    elif module=='hash':seeds=[('/hash/hash_table/operate',{'operation':'create_table','payload':{'capacity':13}})]
                    for url,payload in seeds:
                        response=page.request.post(f'http://127.0.0.1:{server.server_port}'+url,data=payload);assert response.status==200,(module,response.status)
                    page.reload(wait_until='networkidle')
                    if module=='hierarchical':
                        toggle=page.locator('#hier-results-toggle')
                        if toggle.get_attribute('aria-expanded')=='false':toggle.click()
                    controls=[prefix+'-export-image',prefix+'-export-summary']
                    if module=='sequential':controls.append('export-visual-jpg-btn')
                    for identifier in controls:
                        button=page.locator('#'+identifier);record={'module':module,'route':route,'control_id':identifier,'own_seed':seeds,'control_present':button.count()==1}
                        if not record['control_present']:record['status']='NO_CONTROL_IN_PAGE';results.append(record);continue
                        # Open only real progressive-panel controls, never force hidden exports.
                        for _ in range(4):
                            if button.is_visible():break
                            opener=button.evaluate_handle("""e=>{for(let p=e.parentElement;p;p=p.parentElement){if(p.tagName==='DETAILS'&&!p.open)return p.querySelector(':scope > summary');const b=p.querySelector(':scope > h3 button[aria-expanded="false"],:scope > h2 button[aria-expanded="false"]');if(b&&b.getClientRects().length)return b;}return null;}""")
                            element=opener.as_element()
                            if not element:break
                            element.click()
                        record['control_visible']=button.is_visible()
                        if not record['control_visible']:record['status']='CONTEXT_REQUIRED_HIDDEN';results.append(record);continue
                        try:
                            with page.expect_download(timeout=7000) as download_event:button.click()
                            download=download_event.value;path=Path(download.path());data=path.read_bytes()
                            record.update(status='OPERABLE_DOWNLOAD',suggested_name=download.suggested_filename,bytes=len(data),sha256=hashlib.sha256(data).hexdigest())
                            if download.suggested_filename.endswith('.json'):
                                parsed=json.loads(data);record['json_keys']=sorted(parsed);record['content_valid']=bool(parsed)
                            else:record['jpeg_magic_valid']=data[:2]==b'\xff\xd8';record['content_valid']=record['jpeg_magic_valid']
                        except Exception as error:record.update(status='FLOW_NOT_COMPLETED',error_type=type(error).__name__,error=str(error)[:220])
                        results.append(record)
                    rows=page.evaluate("""() => window.__interactive.map(x=>({tag:x.node.tagName.toLowerCase(),id:x.node.id,connected:x.node.isConnected,visible:!!x.node.getClientRects().length,clicked:x.clicked,download:x.node.download||null,stack:x.stack}))""")
                    for row in rows:
                        match=re.search(r'/static/js/([A-Za-z_]+\.js)(?:\?[^:]*)?:(\d+):\d+',row.pop('stack') or '')
                        if match:created.append({'route':route,'source':'static/js/'+match[1],'line':int(match[2]),**row})
                    page.close()
                # Existing real sibling UI; classify the guarded duplicate factory without manufacturing it.
                page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/sequential/queue',wait_until='networkidle')
                sibling=page.evaluate("""()=>{const h=document.querySelector('#seq-reflect-title'),s=h?.closest('.seq-reflect'),b=h?.querySelector('.seq-pilot-toggle');return {heading:!!h,section:!!s,existing_toggle:!!b,guard_allows_new_factory:!!h&&!!s&&!b};}""")
                if sibling['existing_toggle']:
                    toggle=page.locator('#seq-reflect-title .seq-pilot-toggle');old=toggle.get_attribute('aria-expanded');toggle.click();sibling['existing_toggle_operable']=toggle.get_attribute('aria-expanded')!=old
                page.close();context.close();browser.close()
        finally:server.shutdown();thread.join(timeout=5)
    report={'scope':'12deferred factories only; own private inputs/downloads, no algorithms/containers','results':results,'created_nodes':created,'sibling_guard':sibling,'downloads_completed':sum(x['status']=='OPERABLE_DOWNLOAD' and x.get('content_valid') for x in results),'flows_requested':len(results)}
    report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');return report

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--report',required=True);args=parser.parse_args();report=run_flows(args.report);print(json.dumps({'downloads_completed':report['downloads_completed'],'flows_requested':report['flows_requested'],'statuses':[{'id':x['control_id'],'status':x['status']} for x in report['results']],'sibling_guard':report['sibling_guard']}))
if __name__=='__main__':main()
