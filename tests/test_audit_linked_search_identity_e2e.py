"""Visible first-occurrence deletion: aliases, live/detached heap, both views/replay."""

import json,threading

import pytest

from app import create_app

from werkzeug.serving import make_server

pytestmark=pytest.mark.e2e



def test_visible_search_both_views_replay_and_scope_endpoint(tmp_path):

    sync_playwright=pytest.importorskip('playwright.sync_api').sync_playwright

    W=tmp_path

    (W/'audit-evidence').mkdir()

    app=create_app();app.config.update(TESTING=False,SECRET_KEY='audit-clear-local');server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'

    rows=[];cases=[];errors=[]

    try:

     with sync_playwright() as p:

      browser=p.chromium.launch()

      for label,seed,value in [('empty',[],7),('single',[7],7),('interior',[7,8,9],8),('duplicates',[7,7,9],7),('missing',[7,8,9],99)]:

       context=browser.new_context(viewport={'width':1366,'height':1000});page=context.new_page();posts=[]

       page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)

       page.on('pageerror',lambda err:errors.append(str(err)))

       for seed_value in seed:

        assert context.request.post(base+'/sequential/linked_list/operate',data={'operation':'insertar_final','payload':{'value':seed_value}}).json()['success']

       page.goto(base+'/sequential/linked_list',wait_until='networkidle')

       page.evaluate('''()=>{window.auditRenderedState=null;const original=renderVisualState;renderVisualState=function(...args){window.auditRenderedState=structuredClone(args[1]);return original(...args);};}''')

       page.select_option('#operation-select','buscar_elemento');page.fill('#field-value',str(value));page.click('#seq-step-mode')

       with page.expect_response(lambda response:response.url.endswith('/sequential/linked_list/operate') and response.request.method=='POST') as response_info:

        page.click('#seq-sim-execute')

       data=response_info.value.json();assert data['success'];steps=data['execution_trace']['steps'];post_count=len(posts)

       page.wait_for_function('()=>document.querySelector("#seq-sim-counter").textContent.startsWith("Paso: 0/")')

       for view in ['current','linked']:

        page.click('#stack-view-'+view)

        for direction,selector,indices in [('forward','#seq-sim-step',range(len(steps))),('backward','#seq-sim-prev',range(len(steps)-2,-2,-1))]:

         for idx in indices:

          page.click(selector);page.wait_for_function("n=>document.querySelector('#seq-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=idx+1)

          actual=page.evaluate('window.auditRenderedState');canonical=steps[idx]['state_after'] if idx>=0 else steps[0]['state_snapshot'];expected=(steps[idx]['pedagogy']['memory_state'] or canonical) if idx>=0 else canonical

          active=page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))')

          console_lines=page.locator('#seq-printf-console .console-line:not(.muted)').all_text_contents()

          dom_roots=page.locator('[data-clear-pointer]').evaluate_all("els=>Object.fromEntries(els.map(el=>[el.dataset.clearPointer,el.querySelector('code').textContent]))")

          dom_nodes=page.locator('[data-clear-node]').evaluate_all("els=>els.map(el=>({id:el.dataset.clearNode,next:el.dataset.clearNext,status:el.dataset.clearStatus,value:Number(el.querySelector('.stack-linked-field strong').textContent)}))")

          expected_nodes=[{k:n[k] for k in ['id','next','status','value']} for n in actual.get('heap_nodes',[])]

          dom_nodes.sort(key=lambda node:node['id']);expected_nodes.sort(key=lambda node:node['id'])

          root_pass=dom_roots.get('lista')==actual['head'] and dom_roots.get('head')==actual['head'] and all(dom_roots.get(name)==actual.get(name) for name in ['q'])

          rows.append({'case':label,'view':view,'direction':direction,'step':idx,'backend_state_pass':actual==expected and actual['items']==canonical['items'],'highlight_pass':idx<0 or steps[idx]['line_index'] in active,'root_alias_pass':root_pass,'heap_dom_pass':dom_nodes==expected_nodes,'console_pass':[x.strip() for x in console_lines]==[x.strip() for step in steps[:idx+1] for x in step.get('console',[]) if x.strip()] if idx>=0 else len(console_lines)==0,'dom_roots':dom_roots,'dom_nodes':dom_nodes})

          if label=='interior' and direction=='forward' and idx>=0 and 'printf' in steps[idx]['line_text'] and 'Encontrado en la posicion' in steps[idx]['line_text'] and actual.get('head')=='N1':

           page.screenshot(path=str(W/'audit-evidence'/f'linked-search-{view}.png'),full_page=True)

        # Closing the mode seeks the same endpoint, preserving heap identities;

        # view switching and reopening are navigation and cannot POST again.

        page.click('#seq-step-mode')

        endpoint=page.evaluate('window.auditRenderedState')

        assert endpoint==steps[-1]['pedagogy']['memory_state']

        assert endpoint['items']==data['visual_state']['items']

        page.click('#stack-view-'+('linked' if view=='current' else 'current'))

        assert page.evaluate('window.auditRenderedState')==endpoint

        page.click('#stack-view-'+view)

        page.click('#seq-step-mode')

        assert page.evaluate('window.auditRenderedState')==steps[0]['state_snapshot']

       assert len(posts)==post_count

       cases.append({'case':label,'steps':len(steps),'operation_posts':post_count,'replay_extra_posts':len(posts)-post_count});context.close()

      browser.close()

    finally:

     server.shutdown();thread.join(timeout=5)

    report={'scope':'Actual visible menu Eliminar elemento + real execution buttons, both views forward/backward; 8 cases. Highlight means just executed. Browser compares exact backend snapshots, aliases and all live/detached node links.','cases':cases,'rows':rows,'page_errors':errors}

    (W/'audit-evidence/linked-search-browser-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');summary={'observations':len(rows),'page_errors':errors,'cases':cases,**{key:sum(not x[key] for x in rows) for key in ['backend_state_pass','highlight_pass','root_alias_pass','heap_dom_pass','console_pass']}}

    print(json.dumps(summary));assert not errors and all(all(row[key] for key in ['backend_state_pass','highlight_pass','root_alias_pass','heap_dom_pass','console_pass']) for row in rows)

