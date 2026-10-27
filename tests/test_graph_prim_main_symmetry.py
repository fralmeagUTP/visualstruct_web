"""Generated caller preserves symmetric zero-weight updates/removals and failures."""
import re
import pytest
from playwright.sync_api import sync_playwright
from _canonical_graph_browser_contract import private_server, current_main, reload_main_twice, compile_downloaded_main


@pytest.mark.e2e
def test_non_directed_main_update_remove_zero_and_self_loop(tmp_path):
    with private_server(tmp_path) as base, sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        try:
            for directed,status in [(False,5),(True,6)]:
                context=browser.new_context();page=context.new_page();posts=[]
                page.on('request',lambda request:posts.append(request.url) if request.method=='POST' else None)
                history=[('create_graph',{'directed':directed}),
                    ('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),
                    ('insert_edge',{'origin':1,'target':2,'weight':4}),
                    ('insert_edge',{'origin':2,'target':1,'weight':0}),
                    ('remove_edge',{'origin':1,'target':2}),
                    ('insert_edge',{'origin':1,'target':1,'weight':0}),
                    ('run_prim',{'start':1})]
                for operation,payload in history:
                    response=context.request.post(base+'/graph/graph/operate',data={
                        'operation':operation,'payload':payload,'execution_mode':'normal'})
                    body=response.json()
                    if operation=='run_prim':
                        assert response.status==400 and body['c_status']==status
                        assert body['execution_started'] and body['history'][-1]['source_contract']=='graph-book/v1'
                    else:assert response.status==200 and body['success'],body
                page.goto(base+'/graph/graph/expansion-minima',wait_until='networkidle')
                main=reload_main_twice(page,context,base,posts)
                # Test exact calls independent of whitespace in the generated caller.
                calls=lambda name,args:len(re.findall(r'\b'+name+r'\s*\(\s*'+r'\s*,\s*'.join(r'&[A-Za-z_]\w*' if a=='&estado' else re.escape(a) for a in args)+r'\s*\)',main))
                assert calls('grafo_insertar_arco',['g','1','2','4','&estado'])==1
                assert calls('grafo_insertar_arco',['g','2','1','0','&estado'])==1
                assert calls('grafo_insertar_arco',['g','1','1','0','&estado'])==1
                assert calls('grafo_eliminar_arco',['g','1','2'])==1
                assert calls('grafo_insertar_arco',['g','2','1','4','&estado'])==(0 if directed else 1)
                assert calls('grafo_insertar_arco',['g','1','2','0','&estado'])==(0 if directed else 1)
                assert calls('grafo_eliminar_arco',['g','2','1'])==(0 if directed else 1)
                assert main.count('= grafo_prim(')==1
                assert main.count('grafo_liberar_arcos(&lista_')==1
                out=tmp_path/('directed' if directed else 'undirected');out.mkdir()
                native=compile_downloaded_main(context,base,main,out)
                assert f'Prim: estado={status}' in native['stdout']
                # Reload proves the failed native query remains in the real session.
                page.reload(wait_until='networkidle');assert current_main(page,context,base)==main
                context.close()
        finally:browser.close()
