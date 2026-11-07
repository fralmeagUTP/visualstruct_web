from e2e_contract_helpers import main_source, observe_before_cleanup
"""Reload preserves successful searches in actual generated C main, without duplicate POST."""
import json,re,shutil,subprocess,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e
@pytest.mark.parametrize('structure,search',[('linked_list','buscar_elemento'),('circular_list','buscar_posiciones')])
def test_search_reload_main_native_results_and_failure_history(tmp_path,structure,search):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright;gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable; downloaded main unverified')
 app=create_app();app.config.update(TESTING=False,SECRET_KEY='search-history-audit');server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];posts=[];errors=[]
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.on('request',lambda x:posts.append(x.url) if x.method=='POST' and x.url.endswith('/operate') else None);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(base+'/sequential/'+structure,wait_until='networkidle')
   stem='tad_lista' if structure=='linked_list' else 'tad_lista_circular';fn='lista_buscar_elemento' if structure=='linked_list' else 'lcir_buscar_posiciones'
   for kind,suffix in [('source','.c'),('header','.h')]:
    response=context.request.get(base+'/help/source/'+structure+'/'+kind);assert response.status==200;(tmp_path/(stem+suffix)).write_bytes(response.body())
   for value in [7,7,9]:
    page.select_option('#operation-select','insertar_final');page.fill('#field-value',str(value))
    with page.expect_response(lambda x:x.url.endswith('/operate') and x.request.method=='POST') as response:page.click('#seq-sim-execute')
    assert response.value.json()['success'];page.wait_for_function("()=>!document.querySelector('#seq-sim-execute').disabled")
   for index,(value,expected) in enumerate([(7,[1,2]),(7,[1,2]),(99,[])]):
    page.select_option('#operation-select',search);page.fill('#field-value',str(value))
    with page.expect_response(lambda x:x.url.endswith('/operate') and x.request.method=='POST') as response:
     if index==0:page.evaluate("()=>{const b=document.querySelector('#seq-sim-execute');b.click();b.dispatchEvent(new MouseEvent('click',{bubbles:true}));}")
     else:page.click('#seq-sim-execute')
    data=response.value.json();assert data['success'] and data['result']==expected;page.wait_for_function("()=>!document.querySelector('#seq-sim-execute').disabled");assert len(data['history'])==4+index
    for reload in [False,True]:
     if reload:page.reload(wait_until='networkidle')
     main=main_source(page);calls=[line.strip() for line in main.splitlines() if re.search(r'\b'+fn+r'\(',line)];assert len(calls)==index+1
     if structure=='circular_list':assert all(re.search(r'int cantidad_\d+ = lcir_buscar_posiciones\(&lc, (?:7|99), posiciones_\d+, 3\);$',line) for line in calls)
     observe='printf("AUDIT:");for(Tlista p=lista;p!=NULL;p=p->sgte)printf(" %d",p->nro);printf("\\n");' if structure=='linked_list' else 'int values[32];int count=lcir_copiar_valores(&lc,values,32);printf("AUDIT:");for(int i=0;i<count;i++)printf(" %d",values[i]);printf("\\n");'
     source=tmp_path/f'main-{index}-{reload}.c';source.write_text(observe_before_cleanup(main,'lista_limpiar(&lista);' if structure=='linked_list' else 'lcir_destruir(&lc);',observe),encoding='utf-8');exe=tmp_path/'main.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/(stem+'.c')),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr;run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0;actual=[int(x) for x in next(line for line in run.stdout.splitlines() if line.startswith('AUDIT:'))[6:].split()];assert actual==[7,7,9]
     if structure=='linked_list':
      assert len(re.findall(r'Encontrado en la posicion 1\b',run.stdout))==min(index+1,2);assert len(re.findall(r'Encontrado en la posicion 2\b',run.stdout))==min(index+1,2);assert ('Numero no encontrado' in run.stdout)==(index==2)
     # The current caller stores the real C return count and prints every
     # returned position from its bounded output buffer, including no match.
     else:
      positions=[line for line in run.stdout.splitlines() if line.startswith('Posiciones:')]
      assert positions==['Posiciones: 1 2','Posiciones: 1 2','Posiciones:'][:index+1]
     rows.append({'search_index':index,'reload':reload,'main':main,'native_stdout':run.stdout,'state':actual,'search_calls':len(calls)})
   failed=context.request.post(base+'/sequential/'+structure+'/operate',data={'operation':search,'payload':{'value':'abc'}});assert failed.status==400;assert len(failed.json()['history'])==6;page.reload(wait_until='networkidle');assert len([line for line in main_source(page).splitlines() if re.search(r'\b'+fn+r'\(',line)])==3;assert len(posts)==6 and not errors
   other=browser.new_context();otherpage=other.new_page();otherpage.goto(base+'/sequential/'+structure);assert otherpage.locator('.didactic-history-main').count()==0;other.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'search-history-main-review.json').write_text(json.dumps({'structure':structure,'rows':rows,'browser_operation_posts':len(posts),'errors':errors,'failed_search_not_recorded':True,'isolated_session_empty':True},indent=2),encoding='utf-8')
