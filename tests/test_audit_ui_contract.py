"""Regression of approved stages and exact causal state in both sequential views."""
import re
import pytest
from test_ui_playwright_e2e import _live_server_url, _enable_manual_mode

pytestmark = pytest.mark.e2e
PAGES = ["/sequential/"+x for x in ["stack","queue","priority_queue","linked_list","circular_list","sublist"]]+["/hierarchical/"+x for x in ["abb","avl","red_black","binary_heap"]]+["/hash/hash_table","/sorting/visualizador"]+["/graph/graph/"+x for x in ["construccion","recorridos","camino-minimo","expansion-minima"]]
STAGES=["1 Preparar y controlar ejecución","2 Visualizar y ejecutar","3 Relacionar con código","4 Comprender","5 Resultados de ejecución"]

@pytest.mark.parametrize("path",PAGES)
def test_five_stages_follow_the_same_exact_order(path):
    pw=pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base, pw.sync_playwright() as p:
        browser=p.chromium.launch(); page=browser.new_page()
        page.goto(base+path,wait_until="networkidle")
        headings=page.locator("main h3, main summary").evaluate_all("els => els.map(el => {const copy=el.cloneNode(true); copy.querySelectorAll('small').forEach(n=>n.remove()); return copy.textContent;})")
        numbered=[re.sub(r"\s+"," ",h).strip().replace("Mostrar","").replace("Ocultar","").strip() for h in headings if re.match(r"\s*[1-5]\s",h)]
        assert numbered==STAGES
        assert not page.evaluate("document.querySelector('.nav-links').scrollWidth > document.querySelector('.nav-links').clientWidth")
        for width in (390,1366):
            page.set_viewport_size({"width":width,"height":900})
            compact=page.evaluate("""() => {
                const nav=document.querySelector('.nav-links'),style=getComputedStyle(nav);
                const rows=new Set([...nav.querySelectorAll('a')].map(a=>Math.round(a.getBoundingClientRect().top)));
                const lineHeight=parseFloat(style.lineHeight)||parseFloat(style.fontSize)*1.5;
                const gap=parseFloat(style.rowGap)||0;
                return nav.getBoundingClientRect().height <= rows.size*(lineHeight+gap)+2;
            }""")
            assert compact, "Menu rows stretch into blank space instead of naturally wrapping"
        browser.close()

@pytest.mark.parametrize("tad,operations",[
    ("stack",["apilar","desapilar"]),("queue",["encolar","desencolar"]),
    ("priority_queue",["encolar","desencolar"]),("linked_list",["insertar_inicio","eliminar_elemento"]),
    ("circular_list",["insertar_final","eliminar_inicio"]),("sublist",["insertar_padre","eliminar_padre"]),
])
def test_both_views_use_each_exact_causal_state_and_replay_without_post(tad,operations):
    pw=pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base, pw.sync_playwright() as p:
        browser=p.chromium.launch();page=browser.new_page();posts=[]
        page.on("request",lambda request:posts.append(request.url) if request.method=="POST" else None)
        page.goto(base+"/sequential/"+tad,wait_until="networkidle")
        page.evaluate("""() => {const real=window.renderVisualState;window.auditRenderedState=null;
            window.renderVisualState=(id,state,container,hint)=>{window.auditRenderedState=structuredClone(state);return real(id,state,container,hint);};}""")
        _enable_manual_mode(page,"seq")
        for operation in operations:
            page.select_option("#operation-select",operation)
            for field in page.locator("#operation-form input").all():
                if field.is_visible() and field.get_attribute("type") not in {"checkbox","hidden"}:
                    field.fill("1" if "priority" in (field.get_attribute("id") or "") else "9")
            with page.expect_response(lambda r:"/operate" in r.url and r.request.method=="POST") as pending:
                page.click("#seq-sim-execute")
            result=pending.value.json();assert result["success"],result
            steps=result["execution_trace"]["steps"]; assert steps
            page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.includes('/'+n)",arg=len(steps))
            post_count=len(posts)
            for view in ["current","linked"]:
                page.click("#stack-view-"+view)
                page.click("#seq-step-mode");page.click("#seq-step-mode")
                assert page.evaluate("window.auditRenderedState")==steps[0]["state_snapshot"]
                for selector,indices in [("#seq-sim-step",range(len(steps))),("#seq-sim-prev",range(len(steps)-2,-2,-1))]:
                    for idx in indices:
                        page.click(selector)
                        page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=idx+1)
                        expected=steps[idx]["state_after"] if idx>=0 else steps[0]["state_snapshot"]
                        assert page.evaluate("window.auditRenderedState")==expected,(tad,operation,view,idx)
                        if tad=="priority_queue" and view=="linked":
                            roots=page.locator(".stack-linked-pointer").evaluate_all("els=>Object.fromEntries(els.map(el=>[(el.querySelector('strong')?.textContent||'').trim(),(el.querySelector('code')?.textContent||'').trim()]))")
                            for key,label in [("delante","delante"),("atras","atrás")]:
                                if key in expected:assert roots[label]==expected[key],(operation,idx,key)

                        if idx>=0 and steps[idx].get("line_index") is not None:
                            active=page.locator("#op-pseudocode .sim-active").evaluate_all("xs=>xs.map(x=>Number(x.dataset.line))")
                            done=page.locator("#op-pseudocode .sim-done").evaluate_all("xs=>xs.map(x=>Number(x.dataset.line))")
                            assert steps[idx]["line_index"] in active or (idx==len(steps)-1 and steps[idx]["line_index"] in done)
                assert len(posts)==post_count
        browser.close()
