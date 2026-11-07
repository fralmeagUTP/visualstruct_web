"""Focused private actual player checks for incident caller frames and downloaded main."""
from pathlib import Path
import json, os, threading
import pytest
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
from _book_graph_browser_contract import main_text, COLLECT, decoded_body, assert_browser_row

pytestmark=pytest.mark.e2e


@pytest.mark.parametrize("directed",[True,False])
def test_incident_caller_actual_player_reverse_main_DOM_HTTP_reload(tmp_path,directed):
    out=Path(os.environ.get("GRAPH_INCIDENT_QA_OUT",str(tmp_path)))/("browser-directed" if directed else "browser-undirected")
    out.mkdir(parents=True,exist_ok=True)
    class PrivateConfig(Config):
        APP_ENV="testing"
        TESTING=True
        SECRET_KEY="incident-caller-private-browser"
        SESSION_CACHE_DIR=str(out/"cache")
    app=create_app(PrivateConfig);server=make_server("127.0.0.1",0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.importorskip("playwright.sync_api").sync_playwright() as p:
            browser=p.chromium.launch();context=browser.new_context(viewport={"width":1366,"height":1000});page=context.new_page();posts=[];errors=[]
            page.on("request",lambda r:posts.append(r.url) if r.method=="POST" else None)
            page.on("pageerror",lambda e:errors.append(str(e)))
            history=[("create_graph",{"directed":directed})]+[("insert_vertex",{"vertex":v}) for v in [1,2,3,4]]
            history += [("insert_edge",{"origin":o,"target":d,"weight":w}) for o,d,w in [(2,1,3),(3,4,6),(1,3,4),(1,1,5)]]
            for operation,payload in history:
                r=context.request.post(base+"/graph/graph/operate",data={"operation":operation,"payload":payload});assert r.json()["success"]
            page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.auditGraphPlayer=player;return player;};});")
            page.goto(base+"/graph/graph/construccion",wait_until="networkidle")
            page.select_option("#graph-operation-select","remove_vertex");page.locator("#g-op-field-vertex").fill("1")
            page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
            with page.expect_response(lambda r:r.url.endswith("/graph/graph/operate") and r.request.method=="POST") as response:page.click("#graph-sim-play")
            data=decoded_body(response.value.json());assert data["success"];trace=data["execution_trace"];steps=trace["steps"];assert trace["book_instruction_model"]
            page.wait_for_function("(n)=>window.auditGraphPlayer.getTotalSteps()===n",arg=len(steps));page.evaluate("()=>window.auditGraphPlayer.pause()")
            before=len(posts);rows=page.evaluate(COLLECT,len(steps))
            assert len(rows)==2*len(steps)+2
            for row in rows:
                assert_browser_row(row,data)
            assert len(posts)==before and not errors
            frees=[s for s in steps if s['phase']=='free']
            assert len(frees)==(4 if directed else 6)
            assert all(s['pedagogy']['instruction_event']['function']=='grafo_eliminar_vertice' for s in frees)
            receipt=next(s for s in steps if s['phase']=='caller_receipt')
            assert receipt['pedagogy']['instruction_event']['returned']==receipt['pedagogy']['memory_state']['graph']
            assert len([n for n in steps[-1]['pedagogy']['memory_state']['heap_nodes'] if n['kind']=='struct NodoA'])==(1 if directed else 2)
            assert data['visual_state']['edges']==[{'source':'3','target':'4','weight':6}]
            main=lambda:main_text(page)
            prior=main();assert 'g = grafo_eliminar_vertice(g, 1);' in prior
            assert 'while (g.a' not in prior
            for _ in range(2):
                page.reload(wait_until="networkidle");assert main()==prior and len(posts)==before
            downloaded=context.request.get(base+"/help/source/graph/main");assert downloaded.body()==prior.encode("utf-8") and len(posts)==before
            (out/"main.c").write_bytes(downloaded.body());(out/"response.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            (out/"DOM.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
            (out/"report.json").write_text(json.dumps(dict(directed=directed,boundaries=len(rows),steps=len(steps),canonical_C_events=len(trace["C_instruction_events"]),replay_POSTs=0,reload_POSTs=0,reloads=2,DOM_HTTP_main_identical=True,callee_incident_cleanup=True,errors=errors),indent=2),encoding="utf-8")
            page.screenshot(path=str(out/"UI.png"),full_page=True);context.close();browser.close()
    finally:server.shutdown();thread.join(timeout=5)
