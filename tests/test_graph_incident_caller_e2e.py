"""Focused private actual player checks for incident caller frames and downloaded main."""
from pathlib import Path
import json, os, threading
import pytest
from werkzeug.serving import make_server
from app import create_app
from app.config import Config
from app.domain.graph.incident_caller import incident_caller_lines
from test_graph_four_instruction_e2e import COLLECT, compact

pytestmark=pytest.mark.e2e
COLLECT=COLLECT.replace("condition:document.querySelector", "returned:document.querySelector('[data-graph-return]')?.textContent,condition:document.querySelector")

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
            data=response.value.json();assert data["success"];trace=data["execution_trace"];steps=trace["steps"];assert trace["incident_caller_model"]
            page.wait_for_function("(n)=>window.auditGraphPlayer.getTotalSteps()===n",arg=len(steps));page.evaluate("()=>window.auditGraphPlayer.pause()")
            before=len(posts);rows=page.evaluate(COLLECT,len(steps))
            for row in rows:
                i=row["index"];ped=steps[i]["pedagogy"] if i>=0 else steps[0]["pedagogy"]["initial_frame"];st=ped["memory_state"]
                assert row["heap"]==[{"id":n["id"],"kind":n["kind"],"contents":compact(n["fields"])} for n in st["heap_nodes"]],(i,row["direction"])
                heading="Cabezas del caller C (retira incidentes tras el retorno): " if ped["instruction_event"].get("origin")=="caller" else "Cabezas C (arcos conservados por esta función): "
                assert row["heads"]==heading+compact(st["graph"])
                assert row["retired"]=="Retiradas (sólo registro histórico): "+compact(st["retired_objects"])
                return_heading="Retorno C registrado (identidades retiradas no utilizables): " if ped["instruction_event"].get("origin")=="caller" else "Retorno al caller: "
                assert row["returned"]==return_heading+compact(st["returned"])
                assert row["stack"]==[{"id":f["frame_id"],"text":f["function"]+": "+f["scope_status"]} for f in ped["call_stack"]]
                assert len(row["variables"])==len(ped["variables"])
                for got,v in zip(row["variables"],ped["variables"]):
                    assert got["name"]==v["name"] and got["scope"]==v["scope"]
                    assert compact(v["previous"]) in got["text"] and compact(v["value"]) in got["text"]
                if ped["condition"]:assert ped["condition"]["substituted"] in row["condition"]
                assert row["stdout"]=="(sin salida printf en esta ruta)"
                assert row["message"]==(data["message"] if i==len(steps)-1 else "Operación preparada: resultado pendiente hasta completar la traza.")
                expected=steps[i]["state_after"] if i>=0 else steps[0]["state_snapshot"]
                assert row["svgNodes"]==len(expected["nodes"]),(i,row["direction"])
                if i>=0:assert steps[i]["line_index"] in row["highlighted"]
            assert len(posts)==before and not errors
            raw_return=next(s for s in reversed(steps) if s["phase"]=="return" and s["pedagogy"]["instruction_event"].get("origin")=="callee")
            receipt=next(s for s in steps if s["phase"]=="caller_receipt")
            assert raw_return["pedagogy"]["memory_state"]["graph"]==receipt["pedagogy"]["memory_state"]["graph"]
            assert len([n for n in raw_return["pedagogy"]["memory_state"]["heap_nodes"] if n["kind"]=="struct NodoA"])==(4 if directed else 7)
            assert all(s["pedagogy"]["instruction_event"]["function"]=="main" for s in steps if s["phase"]=="free" and s["pedagogy"]["memory_state"]["frames"][0]["function"]=="main")
            main=lambda:"\n".join(page.locator(".didactic-history-main .code-line").all_text_contents()).replace("\u00a0","")
            prior=main();assert "\n".join(incident_caller_lines(1)) in prior
            for _ in range(2):
                page.reload(wait_until="networkidle");assert main()==prior and len(posts)==before
            downloaded=context.request.get(base+"/help/source/graph/main");assert downloaded.body()==prior.encode("utf-8") and len(posts)==before
            (out/"main.c").write_bytes(downloaded.body());(out/"response.json").write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
            (out/"DOM.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding="utf-8")
            (out/"report.json").write_text(json.dumps(dict(directed=directed,boundaries=len(rows),steps=len(steps),caller_C_events=len([e for e in trace["C_instruction_events"] if e["origin"]=="caller"]),replay_POSTs=0,reload_POSTs=0,reloads=2,DOM_HTTP_main_identical=True,callee_arcs_preserved=True,caller_only_arc_cleanup=True,errors=errors),indent=2),encoding="utf-8")
            page.screenshot(path=str(out/"UI.png"),full_page=True);context.close();browser.close()
    finally:server.shutdown();thread.join(timeout=5)
