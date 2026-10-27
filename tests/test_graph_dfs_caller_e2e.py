"""Actual DFS UI history reload and downloaded computed/freed C caller."""
import json,threading,subprocess,shutil
import pytest
from app import create_app
from werkzeug.serving import make_server
from _audit_graph_bfs_native_observer import CASES
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('case',[1,6,7])
def test_dfs_actual_history_caller(tmp_path,case):
    c=CASES[case];app=create_app();app.config['TESTING']=True
    server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    try:
        with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
            browser=p.chromium.launch();context=browser.new_context();page=context.new_page();errors=[];posts=[]
            page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
            for op,payload in [('create_graph',{'directed':True}),*[('insert_vertex',{'vertex':v}) for v in c['vertices']],*[('insert_edge',{'origin':a,'target':b,'weight':1}) for a,b in c['edges']]]:
                assert context.request.post(base+'/graph/graph/operate',data={'operation':op,'payload':payload}).json()['success']
            page.goto(base+'/graph/graph/recorridos',wait_until='networkidle');page.select_option('#graph-algorithm-select','run_dfs');page.locator('#g-alg-field-start').fill(str(c['start']))
            results=[]
            for _ in range(2):
                with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
                data=response.value.json();assert data['success'];results.append(data['result'])
                page.wait_for_timeout(100)
            assert results[0]==results[1];before=len(posts)
            page.locator('#g-alg-field-start').fill('999')
            with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as rejected:page.click('#graph-sim-play')
            fail=rejected.value.json();assert not fail['success'] and fail['history']==data['history'];before=len(posts)
            programs=[]
            for _ in range(2):
                page.reload(wait_until='networkidle')
                main='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
                assert main.count('= grafo_dfs(')==2;programs.append(main)
            assert programs[0]==programs[1] and len(posts)==before and not errors
            for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
                for kind,ext in [('source','c'),('header','h')]:
                    resp=context.request.get(base+'/help/source/'+tad+'/'+kind);assert resp.status==200;(tmp_path/(stem+'.'+ext)).write_bytes(resp.body())
            (tmp_path/'main.c').write_text(programs[0],encoding='utf-8');exe=tmp_path/'main.exe'
            build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_grafo.c'),str(tmp_path/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30)
            assert build.returncode==0 and not build.stderr,build.stderr
            run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0
            expected='DFS:'+''.join(' '+str(v) for v in results[0]);assert [line for line in run.stdout.splitlines() if line.startswith('DFS:')]==[expected,expected]
            assert main.count('free(rec_')==2
            (tmp_path/'browser-report.json').write_text(json.dumps({'case':case,'result':results[0],'calls_retained':2,'reload_posts':0,'main_strict_c17':True,'computed_stdout':run.stdout,'errors':errors},indent=2))
            context.close();browser.close()
    finally:server.shutdown();thread.join(timeout=5)
