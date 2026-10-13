"""Compile real Sublista history main fragment with its HTTP-downloaded C/H.

The product downloads C/H; main is a displayed/copyable fragment, not a separate
main download. Includes provide the documented translation-unit context.
"""
import json,re,shutil,subprocess,threading
import pytest
from app import create_app
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_sublist_actual_main_all_visible_operations_typed_repeated_reload_and_native_state(tmp_path):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright;gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable: actual main cannot be certified')
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];errors=[];posts=[]
 operations=[('insertar_padre',{'parent':'0007'}),('insertar_padre',{'parent':'0007'}),('insertar_padre',{'parent':'008'}),('insertar_hijo',{'parent':'0007','child':'003'}),('insertar_hijo',{'parent':'0007','child':'003'}),('insertar_hijo',{'parent':'008','child':'-009'}),('hijos_de',{'parent':'0007'}),('hijos_de',{'parent':'0007'}),('eliminar_hijo',{'parent':'0007','child':'003'}),('eliminar_padre',{'parent':'008'}),('limpiar',{}),('insertar_padre',{'parent':'0007'}),('hijos_de',{'parent':'0007'})]
 try:
  with sync() as p:
   browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and r.url.endswith('/operate') else None);page.goto(base+'/sequential/sublist',wait_until='networkidle')
   for kind,suffix in [('source','.c'),('header','.h')]:
    response=context.request.get(base+'/help/source/sublist/'+kind);assert response.status==200;(tmp_path/('tad_sublista'+suffix)).write_bytes(response.body())
   query_results=[]
   for index,(operation,payload) in enumerate(operations):
    page.select_option('#operation-select',operation)
    for name,value in payload.items():page.fill('#field-'+name,value)
    with page.expect_response(lambda r:r.url.endswith('/sublist/operate') and r.request.method=='POST') as response:page.click('#seq-sim-execute')
    data=response.value.json();assert data['success'];assert len(data['history'])==index+1;expected=[{'parent':x['parent'],'children':x['children']} for x in data['visual_state']['items']]
    if operation=='hijos_de':query_results.append(data['result'])
    for reload in [False,True]:
     if reload:page.reload(wait_until='networkidle')
     main=page.locator('.didactic-history-main').inner_text();assert '\u00a0' not in main
     if operation=='hijos_de':assert main.count('sublista_obtener_hijos(')==len(query_results)
     observe='printf("AUDIT:");for(Nodo*p=sublista;p!=NULL;p=p->sgte){printf(" P%d",p->nro);for(Sublista*h=p->sub;h!=NULL;h=h->sgte)printf(" H%d",h->nro);}printf("\\n");sublista_destruir(&sublista);'
     source=tmp_path/f'main-{index}-{reload}.c';source.write_text('#include <stdio.h>\n#include "tad_sublista.h"\n'+main.replace('    return 0;','    '+observe+'\n    return 0;'),encoding='utf-8');exe=tmp_path/'main.exe';build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'tad_sublista.c'),str(source),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr;run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
     actual=[]
     for token in next(x for x in run.stdout.splitlines() if x.startswith('AUDIT:'))[6:].split():
      if token.startswith('P'):actual.append({'parent':int(token[1:]),'children':[]})
      else:actual[-1]['children'].append(int(token[1:]))
     assert actual==expected
     assert [[int(v) for v in line[6:].split()] for line in run.stdout.splitlines() if line.startswith('Hijos:')]==query_results
     rows.append({'index':index,'operation':operation,'payload':payload,'reload':reload,'main':main,'stdout':run.stdout,'state':actual,'queries':list(query_results)})
    if operation=='limpiar':
     failed=context.request.post(base+'/sequential/sublist/operate',data={'operation':'hijos_de','payload':{'parent':7}});assert failed.status==400;assert len(failed.json()['history'])==index+1;page.reload(wait_until='networkidle')
   assert len(posts)==len(operations);assert not errors
   other=browser.new_context();otherpage=other.new_page();otherpage.goto(base+'/sequential/sublist');assert otherpage.locator('.didactic-history-main').count()==0;other.close();browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'sublist-main-native-review.json').write_text(json.dumps({'rows':rows,'posts':len(posts),'errors':errors,'main_delivery':'Displayed/copyable main fragment; only C/H HTTP download exists','all_six_visible_methods':True},indent=2),encoding='utf-8')
