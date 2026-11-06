"""CI-only viewport diagnostics: isolated application and synthetic integers only."""
from pathlib import Path
import json
import sys
from urllib.parse import urlsplit
import pytest
from test_controls40_real_flows import controls40_page
from test_residual58_focal_cases import residual58_app
from e2e_trace_contracts import reveal_public
from e2e_hierarchical_contract import same_nodes

pytestmark=pytest.mark.e2e

def _local_target(base):
 """Only the isolated fixture's loopback origin may receive data or be captured."""
 parsed=urlsplit(base)
 assert parsed.scheme=='http' and parsed.hostname=='127.0.0.1' and parsed.port, 'Expected isolated loopback fixture'
 assert parsed.username is None and parsed.password is None and parsed.path in ('','/') and not parsed.query and not parsed.fragment, 'Unexpected fixture URL'
 return base.rstrip('/')+'/hierarchical/red_black'


def _capture_local_viewport(page,target,path):
 # Exact URL, including path: never capture an unexpected redirect destination.
 assert page.url==target, 'Refusing screenshot of unexpected destination'
 page.screenshot(path=str(path),full_page=False)

@pytest.mark.parametrize('label,seed,value',[
 ('small',[7,3,9],5),('medium',list(range(1,32)),32),
])
def test_rn_null_projection_and_safe_viewport_capture(controls40_page,label,seed,value):
 page,context,base=controls40_page
 target=_local_target(base)
 out=Path('visual-safe-diagnostics');out.mkdir(exist_ok=True)
 errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 failure=None
 try:
  for n in seed:
   response=context.request.post(base+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':n}})
   assert response.status==200 and response.json()['success']
  page.goto(target,wait_until='networkidle')
  _capture_local_viewport(page,target,out/f'rn-{label}-initial-1366x1000.png')
  page.select_option('#operation-select','insertar');page.locator('[name="value"]').fill(str(value));page.click('#hier-step-mode')
  with page.expect_response(lambda r:r.url.endswith('/red_black/operate') and r.request.method=='POST') as pending:
   page.click('#hier-sim-play')
  data=pending.value.json();assert data['success'];trace=data['execution_trace']
  for index in range(len(trace['steps'])):
   page.click('#hier-sim-step')
   page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
  state=trace['steps'][-1]['pedagogy']['memory_state'];nodes=state['heap_nodes'];live={n['id'] for n in nodes}
  # Memory remains publicly reachable and the illustration is not replaced by it.
  reveal_public(page,page.locator('[data-abb-node]').first)
  page.locator('#hier-visual-region').scroll_into_view_if_needed()
  actual=page.locator('[data-abb-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))")
  same_nodes(actual,[{k:n[k] for k in ['id','value','left','right','status']} for n in nodes])
  drawn=page.locator('[data-rbt-svg-node]').evaluate_all("xs=>xs.map(x=>({id:x.dataset.rbtSvgNode,parent:x.dataset.rbtSvgParent,color:x.dataset.rbtSvgColor}))")
  same_nodes(drawn,[{k:n[k] for k in ['id','parent','color']} for n in nodes])
  expected=sorted((n['id'],side,n[side]) for n in nodes for side in ['left','right'] if n[side] in live or n[side]=='NULL')
  edges=page.locator('[data-rbt-svg-from]').evaluate_all("xs=>xs.map(x=>[x.dataset.rbtSvgFrom,x.dataset.rbtSvgSide,x.dataset.rbtSvgTo])")
  assert sorted(map(tuple,edges))==expected
  assert page.locator('.viz-tree-node.nil').count()==sum(target=='NULL' for _,_,target in expected)
  assert page.locator('[data-abb-node="NULL"]').count()==0
  assert not errors
  (out/f'rn-{label}-null-memory.json').write_text(json.dumps({'synthetic_data_only':True,'seed':seed,'inserted':value,'live_reservations':len(nodes),'NULL_markers':sum(target=='NULL' for _,_,target in expected),'edges':expected,'viewport':page.viewport_size,'scope':'Viewport screenshot; overflow may require manual pan. DOM asserts cover all reservations/links.','JS_errors':errors},ensure_ascii=False,indent=2))
 except BaseException as exc:
  failure=exc
  raise
 finally:
  try:
   _capture_local_viewport(page,target,out/f'rn-{label}-null-memory-1366x1000.png')
  except BaseException as diagnostic_error:
   if failure is None:
    raise
   note=f'Viewport diagnostic unavailable: {type(diagnostic_error).__name__}: {diagnostic_error}'
   try:
    add_note=getattr(failure,'add_note',None)
    if callable(add_note):add_note(note)
    else:print(note,file=sys.stderr)  # Python 3.10 has no BaseException.add_note.
   except Exception:
    pass  # Diagnostic reporting must never replace the original UI failure.
