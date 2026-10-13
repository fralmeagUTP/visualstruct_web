"""Private actual browser traversal of the two vertex traces and reload history."""
from pathlib import Path
import json, os, threading
import pytest
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
from test_graph_four_instruction_e2e import COLLECT, compact

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
            data=response.value.json();trace=data["execution_trace"];steps=trace["steps"]
            assert trace["vertex_instruction_model"]
            if incident:
                raw=steps[-2]
                assert raw["pedagogy"]["instruction_event"]["C_executed"] and raw["state_after"]["edges"]
                assert steps[-1]["pedagogy"]["instruction_event"]["C_executed"] is False and not steps[-1]["state_after"]["edges"]
                assert len([n for n in raw["pedagogy"]["memory_state"]["heap_nodes"] if n["kind"]=="struct NodoA"])==2

            page.wait_for_function("(n)=>window.auditGraphPlayer.getTotalSteps()===n",arg=len(steps))
            page.evaluate("()=>window.auditGraphPlayer.pause()")
            before=len(posts);rows=page.evaluate(COLLECT,len(steps))
            for row in rows:
                i=row["index"];ped=steps[i]["pedagogy"] if i>=0 else steps[0]["pedagogy"]["initial_frame"];st=ped["memory_state"]
                assert row["heap"]==[{"id":n["id"],"kind":n["kind"],"contents":compact(n["fields"])} for n in st["heap_nodes"]],(i,row["direction"])
                assert row["heads"]=="Cabezas C (arcos conservados por esta función): "+compact(st["graph"])
                assert row["retired"]=="Retiradas (sólo registro histórico): "+compact(st["retired_objects"])
                assert row["stack"]==[{"id":f["frame_id"],"text":f["function"]+": "+f["scope_status"]} for f in ped["call_stack"]]
                assert len(row["variables"])==len(ped["variables"])
                for got,v in zip(row["variables"],ped["variables"]):
                    assert got["name"]==v["name"] and got["scope"]==v["scope"]
                    assert compact(v["previous"]) in got["text"] and compact(v["value"]) in got["text"]
                if ped["condition"]:assert ped["condition"]["substituted"] in row["condition"]
                assert row["message"]==(data["message"] if i==len(steps)-1 else "Operación preparada: resultado pendiente hasta completar la traza.")
                assert row["stdout"]=="(sin salida printf en esta ruta)"
                expected_state=steps[i]["state_after"] if i>=0 else steps[0]["state_snapshot"]
                assert row["svgNodes"]==len(expected_state["nodes"]),(i,row["direction"])
                if i>=0:assert steps[i]["line_index"] in row["highlighted"]
            assert len(posts)==before and not errors
            main=lambda:"\n".join(page.locator(".didactic-history-main .code-line").all_text_contents()).replace("\u00a0","")
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
