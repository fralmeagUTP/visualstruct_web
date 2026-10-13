"""Compile the actual displayed history against HTTP-downloaded Linked C/H."""
import json,shutil,subprocess,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_linked_form_main_compiles_and_replays_typed_values(tmp_path):
    sync=pytest.importorskip('playwright.sync_api').sync_playwright
    gcc=shutil.which('gcc')
    if not gcc:pytest.skip('Native GCC unavailable')
    app=create_app();app.config.update(TESTING=False,SECRET_KEY='main-audit');server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[]
    try:
      with sync() as p:
        browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'/sequential/linked_list',wait_until='networkidle')
        for kind,name in [('source','tad_lista.c'),('header','tad_lista.h')]:
          response=context.request.get(base+'/help/source/linked_list/'+kind);assert response.status==200;(tmp_path/name).write_bytes(response.body())
        operations=[('insertar_inicio',{'value':'008'}),('insertar_final',{'value':'010'}),('insertar_final',{'value':'-012'}),('lista_insertar_elemento',{'value':'2147483647','position':'0002'}),('insertar_inicio',{'value':'008'}),('buscar_elemento',{'value':'008'}),('eliminar_elemento',{'value':'010'}),('eliminar_repetidos',{'value':'008'}),('limpiar',{})]
        for index,(operation,payload) in enumerate(operations):
          page.select_option('#operation-select',operation)
          for name,value in payload.items():page.fill('#field-'+name,value)
          with page.expect_response(lambda r:r.url.endswith('/sequential/linked_list/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
          data=response.value.json();assert data['success'];expected=[x['value'] for x in data['visual_state']['items']]
          for reload in [False,True]:
            if reload:page.reload(wait_until='networkidle')
            main=page.locator('.didactic-history-main').inner_text();assert '\u00a0' not in main
            if operation=='buscar_elemento':
              # Approved action-history contract retains successful search on reload.
              assert main.count('lista_buscar_elemento(lista, 8);')==1
            # Only append a native observation before return; displayed calls stay byte-for-byte.
            observed=main.replace('    return 0;','    printf("AUDIT:");\n    for(Tlista p=lista;p!=NULL;p=p->sgte) printf(" %d",p->nro);\n    printf("\\n");\n    lista_limpiar(&lista);\n    return 0;')
            source=tmp_path/f'main-{index}-{reload}.c';source.write_text('#include <stdio.h>\n#include "tad_lista.h"\n'+observed,encoding='utf-8');exe=tmp_path/'main.exe'
            build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_lista.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
            run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
            audit=next(line for line in run.stdout.splitlines() if line.startswith('AUDIT:'));actual=[int(x) for x in audit[6:].split()];assert actual==expected
            rows.append({'operation':operation,'payload':payload,'reload':reload,'expected':expected,'actual':actual,'main':main,'native_stdout':run.stdout})
        browser.close()
    finally:server.shutdown();thread.join(timeout=5)
    assert not errors
    (tmp_path/'generated-main-review.json').write_text(json.dumps({'rows':rows,'page_errors':errors,'limits':['Main is displayed for copy; HTTP downloads are canonical TAD C/H, not a downloadable generated main.','Successful search is retained before and after reload; reconstruction replays only mutating actions.', 'State/typed arguments checked; UI summary printf is additional narration, not asserted identical to native TAD stdout.']},indent=2),encoding='utf-8')
