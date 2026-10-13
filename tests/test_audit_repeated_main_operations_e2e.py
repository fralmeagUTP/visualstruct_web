"""Repeated actual operations remain in copied C main; pending UI duplicates coalesce."""
import json,shutil,subprocess,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e
@pytest.mark.parametrize('structure',['linked_list','circular_list'])
def test_consecutive_insertions_main_native_state_and_pending_click_guard(tmp_path,structure):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright;gcc=shutil.which('gcc')
 if not gcc:pytest.skip('Native GCC unavailable')
 app=create_app();app.config.update(TESTING=False,SECRET_KEY='repeat-audit');server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];posts=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and r.url.endswith('/operate') else None);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'/sequential/'+structure,wait_until='networkidle')
   stem='tad_lista' if structure=='linked_list' else 'tad_lista_circular'
   for kind,suffix in [('source','.c'),('header','.h')]:
    response=context.request.get(base+'/help/source/'+structure+'/'+kind);assert response.status==200;(tmp_path/(stem+suffix)).write_bytes(response.body())
   for index,value in enumerate([7,7,9]):
    page.select_option('#operation-select','insertar_final');page.fill('#field-value',str(value))
    if index==2:page.click('#seq-step-mode')
    with page.expect_response(lambda r:r.url.endswith('/'+structure+'/operate') and r.request.method=='POST') as response:
     if index==2:page.evaluate("()=>{const b=document.querySelector('#seq-sim-execute');b.click();b.dispatchEvent(new MouseEvent('click',{bubbles:true}));}")
     else:page.click('#seq-sim-execute')
    data=response.value.json();assert data['success'];page.wait_for_function("()=>!document.querySelector('#seq-sim-execute').disabled");expected=[x['value'] for x in data['visual_state']['items']];assert expected==[7,7,9][:index+1]
    if index==2:
     assert len(posts)==3
     if structure=='circular_list':
      for view in ['current','linked']:
       page.click('#stack-view-'+view);labels=page.locator('[data-clear-node] .stack-linked-field:not(.stack-linked-next) span').all_text_contents();assert labels and all(label=='valor' for label in labels)
    for reload in [False,True]:
     if reload:page.reload(wait_until='networkidle')
     main=page.locator('.didactic-history-main').inner_text();function='lista_insertar_final' if structure=='linked_list' else 'lcir_insertar_final';call_count=sum(line.strip().startswith(function+'(') for line in main.splitlines())
     observe='printf("AUDIT:"); for(Tlista p=lista;p!=NULL;p=p->sgte)printf(" %d",p->nro); printf("\\n"); lista_limpiar(&lista);' if structure=='linked_list' else 'int values[32];int count=lcir_copiar_valores(&lc,values,32);printf("AUDIT:");for(int i=0;i<count;i++)printf(" %d",values[i]);printf("\\n");lcir_destruir(&lc);'
     source=tmp_path/f'main-{index}-{reload}.c';source.write_text('#include <stdio.h>\n#include "'+stem+'.h"\n'+main.replace('    return 0;','    '+observe+'\n    return 0;'),encoding='utf-8');exe=tmp_path/'main.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/(stem+'.c')),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
     run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0;actual=[int(x) for x in next(line for line in run.stdout.splitlines() if line.startswith('AUDIT:'))[6:].split()]
     rows.append({'index':index,'reload':reload,'expected':expected,'actual':actual,'call_count':call_count,'main':main,'native_stdout':run.stdout});(tmp_path/'repeated-main-review.json').write_text(json.dumps({'structure':structure,'rows':rows,'posts':posts,'errors':errors},indent=2),encoding='utf-8')
     assert actual==expected and call_count==index+1
   assert len(posts)==3 and not errors;browser.close()
 finally:server.shutdown();thread.join(timeout=5)
