"""Private actual browser traversal of the two vertex traces and reload history."""
from pathlib import Path
import json, os, threading
import pytest
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
from _book_graph_browser_contract import main_text, COLLECT, decoded_body, assert_browser_row

pytestmark=pytest.mark.e2e

@pytest.mark.parametrize("operation,seed,x,incident",[
    ("insert_vertex",[],7,False),
    ("remove_vertex",[7],7,False),
    ("remove_vertex",[1,2,3],2,False),
    ("insert_vertex",[1,2,3],2,False),
    ("remove_vertex",[1,2],9,False),
    ("remove_vertex",[1,2,3],1,True),
])
def test_vertex_actual_player_reverse_and_reload_no_redispatch(tmp_path,operation,seed,x,incident):
    out=Path(os.environ.get("GRAPH_VERTEX_QA_OUT",str(tmp_path)))/("browser-"+operation+"-"+str(len(seed))+"-"+str(int(incident)))
    out.mkdir(parents=True,exist_ok=True)
    class PrivateConfig(Config):
        APP_ENV="testing"
        TESTING=True
        SECRET_KEY="vertex-private-finite-qa"
        SESSION_CACHE_DIR=str(out/"session-cache")
    app=create_app(PrivateConfig)
    server=make_server("127.0.0.1",0,app,threaded=True)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f"http://127.0.0.1:{server.server_port}"
    try:
        with pytest.importorskip("playwright.sync_api").sync_playwright() as p:
            browser=p.chromium.launch();context=browser.new_context(viewport={"width":1366,"height":1000});page=context.new_page()
            posts=[];errors=[]
            page.on("request",lambda r:posts.append(r.url) if r.method=="POST" else None)
            page.on("pageerror",lambda e:errors.append(str(e)))
            for v in seed:
                response=context.request.post(base+"/graph/graph/operate",data={"operation":"insert_vertex","payload":{"vertex":v}})
                assert response.json()["success"]
            if incident:
                response=context.request.post(base+"/graph/graph/operate",data={"operation":"insert_edge","payload":{"origin":1,"target":2,"weight":5}})
                assert response.json()["success"]
            page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.auditGraphPlayer=player;return player;};});")
            page.goto(base+"/graph/graph/construccion",wait_until="networkidle")
            page.select_option("#graph-operation-select",operation);page.locator("#g-op-field-vertex").fill(str(x))
            page.evaluate("()=>{const b=document.querySelector('#graph-step-toggle');b.checked=true;b.dispatchEvent(new Event('change'));}")
            with page.expect_response(lambda r:r.url.endswith("/graph/graph/operate") and r.request.method=="POST") as response:
                page.click("#graph-sim-play")
            data=decoded_body(response.value.json());trace=data["execution_trace"];steps=trace["steps"]
            assert trace["book_instruction_model"]
            if incident:
                frees=[s for s in steps if s['phase']=='free']
                assert len(frees)==3
                assert all(s['pedagogy']['instruction_event']['function']=='grafo_eliminar_vertice' for s in frees)
                assert steps[-1]['state_after']['edges']==[]

            page.wait_for_function("(n)=>window.auditGraphPlayer.getTotalSteps()===n",arg=len(steps))
            page.evaluate("()=>window.auditGraphPlayer.pause()")
            before=len(posts);rows=page.evaluate(COLLECT,len(steps))
            assert len(rows)==2*len(steps)+2
            for row in rows:
                assert_browser_row(row,data)
            assert len(posts)==before and not errors
            main=lambda:main_text(page)
            before_main=main();assert before_main
            for _ in range(2):
                page.reload(wait_until="networkidle");assert main()==before_main and len(posts)==before
            download=context.request.get(base+"/help/source/graph/main")
            assert download.body()==before_main.encode("utf-8") and len(posts)==before
            (out/"trace.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            (out/"DOM.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
            (out/"report.json").write_text(json.dumps(dict(operation=operation,seed=seed,x=x,boundaries=len(rows),C_events=len(trace["C_instruction_events"]),
                exact_DOM=True,replay_POSTs=0,reload_POSTs=0,reloads=2,history_main_download_exact=True,errors=errors),indent=2),encoding="utf-8")
            page.screenshot(path=str(out/"page.png"),full_page=True)
            context.close();browser.close()
    finally:
        server.shutdown();thread.join(timeout=5)
