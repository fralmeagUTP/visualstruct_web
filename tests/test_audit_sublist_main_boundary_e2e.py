"""Boundary parity of the actual history renderer with the application's 1024-copy contract."""
import json,shutil,subprocess,threading
import pytest
from app import create_app
from app.adapters.sublist_adapter import SublistAdapter
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_sublist_main_query_1025_children_respects_actual_backend_copy_limit(tmp_path):
 gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable')
 sync=pytest.importorskip('playwright.sync_api').sync_playwright
 adapter=SublistAdapter();adapter.execute('insertar_padre',{'parent':7})
 history=[{'operation':'insertar_padre','subroutine':'sublista_insertar_padre_final','payloadMap':{'parent':7},'result':'OK'}]
 for value in range(1025):
  adapter.execute('insertar_hijo',{'parent':7,'child':value})
  history.append({'operation':'insertar_hijo','subroutine':'sublista_insertar_hijo','payloadMap':{'parent':7,'child':value},'result':'OK'})
 expected=adapter.execute('hijos_de',{'parent':7})['result'];assert expected==list(range(1024))
 history.append({'operation':'hijos_de','subroutine':'sublista_obtener_hijos','payloadMap':{'parent':7},'result':'OK'})
 app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(base+'/sequential/sublist',wait_until='networkidle')
   for kind,suffix in [('source','.c'),('header','.h')]:
    response=context.request.get(base+'/help/source/sublist/'+kind);assert response.status==200;(tmp_path/('tad_sublista'+suffix)).write_bytes(response.body())
   guide=context.request.get(base+'/help/sequential/sublist');assert guide.status==200 and '1024 hijos por consulta' in guide.text()
   page.evaluate('''history=>{const catalog=new Map([['insertar_padre',{inputs:[{name:'parent',type:'number'}]}],['insertar_hijo',{inputs:[{name:'parent',type:'number'},{name:'child',type:'number'}]}],['hijos_de',{inputs:[{name:'parent',type:'number'}]}]]);const out=document.createElement('ol');out.id='audit-boundary-main';document.body.append(out);renderActionHistory(history,out,'sublist',catalog);}''',history)
   main=page.locator('#audit-boundary-main .didactic-history-main').inner_text();assert 'hijos_1027[1024]' in main
   code='#include <stdio.h>\n#include "tad_sublista.h"\n'+main.replace('    return 0;','    printf("AUDIT_COUNT: %d\\n",sublista_contar_hijos(sublista));\n    sublista_destruir(&sublista);\n    return 0;')
   source=tmp_path/'main-boundary.c';source.write_text(code,encoding='utf-8');exe=tmp_path/'boundary.exe'
   build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_sublista.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
   run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
   line=next(x for x in run.stdout.splitlines() if x.startswith('Hijos:'));actual=[int(x) for x in line[6:].split()];assert actual==expected
   assert 'AUDIT_COUNT: 1025' in run.stdout;browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'sublist-main-boundary-review.json').write_text(json.dumps({'allocated_children':1025,'backend_copied':len(expected),'main_copied':len(actual),'capacity':1024,'compiler_exit':build.returncode,'native_exit':run.returncode,'limits':['Renderer given valid operation history directly to avoid 1025 HTTP mutations/rebuilds; 26 other tests compile main from actual forms/reloads.','Per-instruction destination/heap UI fidelity remains pending.']},indent=2),encoding='utf-8')
