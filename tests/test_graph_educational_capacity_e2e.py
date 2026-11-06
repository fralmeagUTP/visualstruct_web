"""UI15/16 admission and lossless suspension of a historical16-vertex session."""
import json,threading
from pathlib import Path
import pytest
from app import create_app
from app.config import Config
from app.services.session_service import SessionService
from flask import request,jsonify
from werkzeug.serving import make_server
from test_residual97_navigation import reveal_with_public_control
pytestmark=pytest.mark.e2e

def test_capacity_inputs_reject_without_POST_and_legacy_keeps_all_nodes(tmp_path):
    class PrivateConfig(Config):
        TESTING=True;SECRET_KEY='capacity-ui-private';SESSION_CACHE_DIR=str(tmp_path/'sessions')
    app=create_app(PrivateConfig)
    @app.post('/qa/seed')
    def seed():
        count=request.get_json()['count']
        h=[{'operation':'create_graph','payload':{'directed':False}},*[{'operation':'insert_vertex','payload':{'vertex':v}} for v in range(1,count+1)]]
        if count <= 15: h=[dict(record,source_contract='graph-book/v1') for record in h]
        SessionService.save_history('graph::graph',h);return jsonify(success=True)
    @app.get('/qa/history')
    def stored():return jsonify(SessionService.get_history('graph::graph'))
    server=make_server('127.0.0.1',0,app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    try:
        with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
            browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[]
            page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
            page.on('pageerror',lambda e:errors.append(str(e)))
            context.request.post(base+'/qa/seed',data={'count':15});page.goto(base+'/graph/graph/construccion',wait_until='networkidle')
            original=page.evaluate('JSON.stringify(window.GRAPH_VIEW_MODEL.visual_state)');history=context.request.get(base+'/qa/history').json()
            for operation,field in [('generate_random_graph','vertices_count'),('insert_vertex','vertex')]:
                page.select_option('#graph-operation-select',operation);input=page.locator('#g-op-field-'+field)
                if field=='vertices_count':assert input.get_attribute('max')=='15' and input.get_attribute('step')=='1'
                input.fill('16');before=len(posts)
                if field=='vertices_count':
                    assert input.evaluate('(el)=>el.validity.rangeOverflow')
                    assert page.locator('#graph-sim-play').is_disabled()
                else:
                    page.click('#graph-sim-play')
                    page.wait_for_function("document.querySelector('#graph-message-box').textContent.includes('15')")
                assert len(posts)==before and page.evaluate('JSON.stringify(window.GRAPH_VIEW_MODEL.visual_state)')==original
                assert context.request.get(base+'/qa/history').json()==history
            context.request.post(base+'/qa/seed',data={'count':16});page.reload(wait_until='networkidle')
            original_history=context.request.get(base+'/qa/history').json()
            assert len(original_history)==17 and all('source_contract' not in r for r in original_history)
            assert page.evaluate('window.GRAPH_VIEW_MODEL.suspended') is True
            assert page.locator('#graph-visual-state circle.viz-graph-node').count()==0
            assert 'suspendido' in page.locator('#graph-message-box').text_content()
            assert page.locator('#graph-sim-play').is_disabled()
            assert page.locator('#graph-download-main').get_attribute('aria-disabled')=='true'
            assert context.request.get(base+'/help/source/graph/main').status==409
            before=len(posts)
            export_button=page.locator('#graph-export-summary')
            reveal_with_public_control(page,export_button)
            with page.expect_download() as exported:export_button.click()
            exported.value.save_as(tmp_path/'legacy-history.json')
            export=json.loads((tmp_path/'legacy-history.json').read_text())
            assert export['history']==original_history
            assert context.request.get(base+'/qa/history').json()==original_history and len(posts)==before and not errors
            report={'UI_generator_max':15,'UI_rejections_no_POST':2,'legacy_history_records_preserved':17,'legacy_state_suspended':True,'legacy_export_exact':True,'errors':errors}
            (tmp_path/'capacity-browser-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
            page.screenshot(path=str(tmp_path/'capacity-browser.png'),full_page=True);context.close();browser.close()
    finally:server.shutdown();thread.join(timeout=5)
