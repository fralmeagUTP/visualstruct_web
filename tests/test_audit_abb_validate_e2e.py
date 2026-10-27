"""Actual validator API, forged internal fixtures, all executed frames and replay."""
from pathlib import Path
import json,shutil,subprocess,threading
import pytest
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.c_code_service import CCodeService
from werkzeug.serving import make_server
from test_audit_abb_validate_native import abb_validate_native,CASES,fixture
pytestmark=pytest.mark.e2e

from scripts.test_tool_paths import resolve_doxygen
def compile_main(main,context,base,target):
 target.mkdir();(target/'main.c').write_text(main,encoding='utf-8')
 for kind,suffix in [('source','c'),('header','h')]:
  raw=context.request.get(base+'/help/source/abb/'+kind).body();assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_abb.'+suffix)).read_bytes();assert b'abb_validar_rango' not in raw;(target/('tad_abb.'+suffix)).write_bytes(raw)
 gcc=shutil.which('gcc');assert gcc;run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'tad_abb.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 warning=target/'warnings.log';cfg=target/'Doxyfile';cfg.write_text('\n'.join(['INPUT = "'+target.as_posix()+'"','FILE_PATTERNS = *.c *.h','OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warning.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([resolve_doxygen(),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warning.read_text(encoding='utf-8')=='',(docs.stderr,warning.read_text(encoding='utf-8'));return run.stdout

@pytest.mark.parametrize('case',range(16))
def test_abb_validar_native_views_frames_replay_and_calculated_main(tmp_path,abb_validate_native,monkeypatch,case):
 meta=CASES[case];forged='tree' in meta;rows=[];errors=[];programs=[]
 if forged:
  original=HierarchicalStructureService._new_adapter
  monkeypatch.setattr(HierarchicalStructureService,'_new_adapter',staticmethod(lambda sid:fixture(case) if sid=='abb' else original(sid)))
 app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
 try:
  with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
   browser=p.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1100});page=context.new_page();posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for value in meta.get('seed',[]):assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
   page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#operation-select option').count()==12
   page.evaluate('()=>{const old=renderHierState;renderHierState=function(...args){window.auditState=structuredClone(args[1]);return old(...args);};}')
   page.locator('#hier-understand-toggle').click();page.select_option('#operation-select','validar');page.click('#hier-step-mode')
   with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST') as resp:page.click('#hier-sim-play')
   d=resp.value.json();assert d['success'] and d['result']==abb_validate_native['expected'][case];steps=d['execution_trace']['steps'];native=[e for e in abb_validate_native['events'] if e['case']==case];assert len(steps)==len(native);count=len(posts)
   pending='Validacion preparada: resultado pendiente hasta completar la traza.';assert page.locator('#message-box').inner_text()==pending
   def values(root):return [] if root is None else [str(root['value']),*values(root['left']),*values(root['right'])]
   for direction,selector,indices in [('forward','#hier-sim-step',range(len(steps))),('backward','#hier-sim-prev',range(len(steps)-2,-2,-1))]:
    for index in indices:
     assert page.locator(selector).is_enabled();page.locator(selector).evaluate('b=>b.click()');page.wait_for_function("n=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: '+n+'/')",arg=index+1)
     st=page.evaluate('window.auditState');expected=steps[index]['pedagogy']['memory_state'] if index>=0 else steps[0]['state_snapshot'];assert st==expected
     assert st['root']==d['visual_state']['root'];assert sorted(page.locator('.viz-tree-text').all_text_contents())==sorted(values(st['root']))
     assert page.locator('[data-abb-node]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbNode,value:Number(x.dataset.abbValue),left:x.dataset.abbLeft,right:x.dataset.abbRight,status:x.dataset.abbStatus}))')==st['heap_nodes']
     assert page.locator('[data-abb-head]').get_attribute('data-abb-head')==st['head'];assert page.locator('[data-abb-frame]').evaluate_all('xs=>xs.map(x=>({id:x.dataset.abbFrame,depth:Number(x.dataset.abbDepth)}))')==[{'id':f['id'],'depth':f['depth']} for f in st['tree_frames']]
     aliases=page.locator('[data-abb-alias]').evaluate_all('xs=>xs.map(x=>({frame:x.dataset.abbAliasFrame,name:x.dataset.abbAlias,type:x.dataset.abbAliasType,target:x.dataset.abbAliasTarget}))');assert aliases==[{'frame':f['id'],'name':name,'type':'ABBNodo *' if name=='nodo' else 'int','target':str(value)} for f in st['tree_frames'] for name,value in f['parameters'].items()]
     ped=steps[index]['pedagogy'] if index>=0 else steps[0]['pedagogy']['initial_frame']
     actual=page.locator('#hier-variables-view tbody tr').evaluate_all('xs=>xs.map(x=>({scope:x.querySelector("small").textContent,previous:x.children[1].textContent,value:x.children[2].textContent,type:x.children[0].querySelector("code").textContent}))');assert actual==[{'scope':v['scope'],'previous':str(v['previous']),'value':str(v['value']),'type':v['type']+' '+v['name']} for v in ped['variables']]
     assert page.locator('#hier-stack-view .hier-stack-frame').count()==len(ped['call_stack']);assert page.locator('#hier-printf-console').text_content()==st['console_stdout']==''
     assert page.locator('#message-box').inner_text()==(d['message'] if index==len(steps)-1 else pending)
     assert page.locator('[data-abb-validation-pending]').count()==int(st['wrapper_result'] is None)
     if st['wrapper_result'] is None:assert 'Resultado:' not in page.locator('#visual-state').inner_text()
     if index>=0:
      e=native[index];assert st['heap_nodes']==e['nodes'] and [{'id':f['id'],'depth':f['depth'],'parameters':f['parameters'],'locals':f['locals']} for f in st['tree_frames']]==e['frames']
      assert steps[index]['line_text'].strip()==e['text'];assert steps[index]['line_index'] in page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').evaluate_all('xs=>xs.map(x=>Number(x.dataset.line))')
      if e['source_index']>=0:assert steps[index]['line_index']==e['source_index']
      if ped['condition']:assert str(ped['condition']['result']) in page.locator('#hier-path-view').text_content() or str(ped['condition']['result']).lower() in page.locator('#hier-path-view').text_content()
      if direction=='forward' and case in [2,10,14] and e['phase']=='return' and e['result']==0:page.screenshot(path=str(tmp_path/f'validate-{case}-{index}.png'),full_page=True)
     rows.append({'case':case,'direction':direction,'index':index,'frames':len(st['tree_frames']),'root':st['head'],'result':st['wrapper_result']})
   assert len(posts)==count and not errors and page.locator('#hier-sim-prev').is_disabled()
   if not forged:
    # Repeated validation is computed by the actual generated main, not a cached UI answer.
    page.click('#hier-step-mode')
    for _ in range(2):
     page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
     with page.expect_response(lambda r:r.url.endswith('/abb/operate') and r.request.method=='POST'):page.click('#hier-sim-play')
     page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
    mains=[];canonical=CCodeService.get_structure_data('abb')['operations']['validar']
    for label in ['before','after']:
     main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count(canonical)==1 and main.count('= abb_validar_rango(arbol, 0, 0, 0, 0);')==3
     assert compile_main(main,context,base,tmp_path/f'history-{case}-{label}').splitlines().count('VALIDAR ABB: correcto')==3;mains.append(main)
     if label=='before':count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
    assert mains[0]==mains[1];programs.append({'case':case,'actual_mains':2,'computed_repeated_validations':6,'doxygen_warnings':0})
   else:programs.append({'case':case,'actual_mains':0,'internal_fixture_only':True,'native_expected':d['result']})
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 (tmp_path/'abb-validate-browser-review.json').write_text(json.dumps({'case':case,'rows':rows,'programs':programs,'errors':errors,'extra_replay_posts':0,'forged_internal_fixture':forged},indent=2),encoding='utf-8')
