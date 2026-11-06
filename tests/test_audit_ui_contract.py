"""Regression of approved stages and exact causal state in both sequential views."""
from e2e_sequential_render_contract import OBSERVER, assert_causal_render
import re
import pytest
from test_ui_playwright_e2e import _live_server_url, _enable_manual_mode
from ui_stage_contract import assert_stage_contract

pytestmark = pytest.mark.e2e
PAGES = ["/sequential/"+x for x in ["stack","queue","priority_queue","linked_list","circular_list","sublist"]]+["/hierarchical/"+x for x in ["abb","avl","red_black","binary_heap"]]+["/hash/hash_table","/sorting/visualizador"]+["/graph/graph/"+x for x in ["construccion","recorridos","camino-minimo","expansion-minima"]]

@pytest.mark.parametrize("path",PAGES)
def test_five_stages_follow_the_same_exact_order(path):
    pw=pytest.importorskip("playwright.sync_api")
    with _live_server_url() as base, pw.sync_playwright() as p:
        browser=p.chromium.launch(); page=browser.new_page()
        page.goto(base+path,wait_until="networkidle")
        headings=page.locator("main h3, main summary").evaluate_all("els => els.map(el => {const copy=el.cloneNode(true); copy.querySelectorAll('small').forEach(n=>n.remove()); return copy.textContent;})")
        numbered=[re.sub(r"\s+"," ",h).strip().replace("Mostrar","").replace("Ocultar","").strip() for h in headings if re.match(r"\s*\d+\s",h)]
        assert_stage_contract(numbered, path)
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
        page.evaluate(OBSERVER)
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
                assert_causal_render(page.evaluate("window.auditRenderEvent"),result["execution_trace"],-1,tad)
                for selector,indices in [("#seq-sim-step",range(len(steps))),("#seq-sim-prev",range(len(steps)-2,-2,-1))]:
                    for idx in indices:
                        page.click(selector)
                        page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=idx+1)
                        expected=assert_causal_render(page.evaluate("window.auditRenderEvent"),result["execution_trace"],idx,tad)
                        if tad=="priority_queue" and view=="linked":
                            event=page.evaluate("window.auditRenderEvent")
                            prefix="priority-enqueue" if operation=="encolar" else "priority-dequeue"
                            for edge in ["front","rear"]:
                                node=page.locator(f"[data-{prefix}-{edge}]")
                                pointer=event["memory"]["root"][edge] or "NULL"
                                assert node.count()==1 and node.get_attribute(f"data-{prefix}-{edge}")==pointer
                                assert node.text_content().endswith(pointer), (operation,idx,edge)

                        if idx>=0 and steps[idx].get("line_index") is not None:
                            active=page.locator("#op-pseudocode .sim-active").evaluate_all("xs=>xs.map(x=>Number(x.dataset.line))")
                            done=page.locator("#op-pseudocode .sim-done").evaluate_all("xs=>xs.map(x=>Number(x.dataset.line))")
                            assert steps[idx]["line_index"] in active or (idx==len(steps)-1 and steps[idx]["line_index"] in done)
                assert len(posts)==post_count
        browser.close()
