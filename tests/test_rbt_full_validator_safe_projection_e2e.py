"""Malformed live-object projections use flat identities in both RN representations."""
import json
from pathlib import Path
from copy import deepcopy
import pytest
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.rbt_query_instruction import build_rbt_query_trace
from _audit_rbt_full_validator_baseline_low import CASES
from test_rbt_full_validator_reload_e2e import INJECT
from test_audit_avl_main_e2e import avl_server
@pytest.mark.e2e
@pytest.mark.parametrize('name,desc',CASES[6:],ids=[x[0] for x in CASES[6:]])
def test_full_rn_safe_invalid_projection_browser(avl_server,tmp_path,name,desc):
 from playwright.sync_api import sync_playwright
 d=S.execute_operation('red_black','validar',{},[]);trace=deepcopy(d['execution_trace']);trace['source_code']=CCodeService.get_structure_data('red_black')['operations']['validar'];state=deepcopy(trace['steps'][0]['state_snapshot']);after=deepcopy(state);after['validation']=False
 ptr=lambda i:'NULL' if i is None else 'N'+str(i+1)
 projection={'head':'N1','heap_nodes':[dict(id=ptr(i),value=v,color={'r':'RED','n':'BLACK'}.get(c,'INVALID'),parent=ptr(p),left=ptr(l),right=ptr(r),status='linked') for i,(v,c,p,l,r) in enumerate(desc)]};trace=build_rbt_query_trace(trace,state,after,native_projection=projection)
 with sync_playwright() as pw:
  browser=pw.chromium.launch();ctx=browser.new_context();p=ctx.new_page();p.add_init_script(INJECT);errors=[];posts=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);p.goto(avl_server+'/hierarchical/red_black');p.click('#hier-understand-toggle')
  p.evaluate('()=>{const old=renderHierState;renderHierState=function(...args){window.rnActual=structuredClone(args[1]);return old(...args);};}');p.evaluate('t=>window.__rnPlayer.loadTrace(t)',trace)
  shots=[]
  for i,step in enumerate(trace['steps']):
   p.evaluate('i=>window.__rnPlayer.seek(i)',i);actual=p.evaluate('window.rnActual');assert actual==step['pedagogy']['memory_state'];assert p.locator('[data-abb-node]').count()==len(desc);assert p.locator('.viz-tree-node:not(.nil)').count()==len(desc)
   for node in projection['heap_nodes']:
    text=p.locator('[data-abb-node="'+node['id']+'"]').inner_text();assert 'padre: '+node['parent'] in text and 'color: '+node['color'] in text
   shots.append(actual)
  for i in range(len(shots)-2,-1,-1):p.evaluate('i=>window.__rnPlayer.seek(i)',i);assert p.evaluate('window.rnActual')==shots[i]
  assert not errors and not posts;p.screenshot(path=str(tmp_path/'invalid.png'));(tmp_path/'browser.json').write_text(json.dumps({'id':name,'frames':len(shots),'forward':len(shots),'back':len(shots)-1,'two_representations':True,'extra_posts':0,'JS_errors':errors}),encoding='utf-8');ctx.close();browser.close()
