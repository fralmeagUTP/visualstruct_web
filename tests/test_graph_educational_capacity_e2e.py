"""UI30/31 guard and preserved incompatible legacy history use a private actual browser."""
import json,threading,os
from pathlib import Path
import pytest
from app import create_app
from app.config import Config
from app.services.session_service import SessionService
from flask import request,jsonify
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_capacity_inputs_reject_without_POST_and_legacy_keeps_all_nodes(tmp_path):
    class PrivateConfig(Config):
        TESTING=True;SECRET_KEY='capacity-ui-private';SESSION_CACHE_DIR=str(tmp_path/'sessions')
    app=create_app(PrivateConfig)
    @app.post('/qa/seed')
    def seed():
        count=request.get_json()['count']
        h=[{'operation':'create_graph','payload':{'directed':False}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in range(1,count+1)]]

        if count<=30:h=[dict(step,source_contract='graph-book/v1') for step in h]
        SessionService.save_history('graph::graph',h);return jsonify(success=True)
    @app.get('/qa/history')
    def stored():return jsonify(SessionService.get_history('graph::graph'))
    server=make_server('127.0.0.1',0,app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    try:
        with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
            browser=p.chromium.launch(**({'executable_path':os.environ['PLAYWRIGHT_CHROMIUM_EXECUTABLE']} if os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE') else {}));context=browser.new_context();page=context.new_page();posts=[];errors=[]
            page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
            page.on('pageerror',lambda e:errors.append(str(e)))
            context.request.post(base+'/qa/seed',data={'count':30});page.goto(base+'/graph/graph/construccion',wait_until='networkidle')
            original=page.evaluate('JSON.stringify(window.GRAPH_VIEW_MODEL.visual_state)');history=context.request.get(base+'/qa/history').json()
            for operation,field in [('generate_random_graph','vertices_count'),('insert_vertex','vertex')]:
                page.select_option('#graph-operation-select',operation);input=page.locator('#g-op-field-'+field)
                if field=='vertices_count':assert input.get_attribute('max')=='30' and input.get_attribute('step')=='1'
                input.fill('31');before=len(posts)
                if field=='vertices_count':
                    assert input.evaluate('(el)=>el.validity.rangeOverflow')
                    assert page.locator('#graph-sim-play').is_disabled()
                else:
                    page.click('#graph-sim-play')
                    page.wait_for_function("document.querySelector('#graph-message-box').textContent.includes('30')")
                assert len(posts)==before and page.evaluate('JSON.stringify(window.GRAPH_VIEW_MODEL.visual_state)')==original
                assert context.request.get(base+'/qa/history').json()==history
            context.request.post(base+'/qa/seed',data={'count':31});page.reload(wait_until='networkidle')
            assert page.evaluate('window.GRAPH_VIEW_MODEL.visual_state.suspended') is True
            assert page.locator('#graph-visual-state circle.viz-graph-node').count()==0
            assert page.locator('#graph-operation-select').is_disabled()
            assert len(context.request.get(base+'/qa/history').json())==32 and not errors
            report={'UI_generator_max':30,'UI_rejections_no_POST':2,'legacy_preserved_vertices':31,'errors':errors}
            (tmp_path/'capacity-browser-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            page.screenshot(path=str(tmp_path/'capacity-browser.png'),full_page=True);context.close();browser.close()
    finally:server.shutdown();thread.join(timeout=5)
