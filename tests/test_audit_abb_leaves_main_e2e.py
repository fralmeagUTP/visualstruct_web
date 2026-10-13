"""Compile the actual history main and real downloads, including repeated leaves."""
import json,threading,subprocess,re,shutil,hashlib
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

def test_actual_leaf_main_canonical_helper_native_results_repeats_reload_and_failure(tmp_path):
 sync=pytest.importorskip('playwright.sync_api').sync_playwright;gcc=shutil.which('gcc')
 if not gcc:pytest.skip('GCC unavailable: actual main unverified')
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';reviews=[];errors=[]
 def compile_actual(page,context,case,label,expected):
  target=tmp_path/f'case-{case}-{label}';target.mkdir()
  main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
  helper=CCodeService.get_structure_data('abb')['operations']['contar_hojas'];assert main.count(helper)==1 and main.count('int abb_contarHojas(ABBNodo* nodo) {')==1
  assert main.count('= abb_contarHojas(arbol);')==len(expected) and 'abb_contarNiveles(arbol)' not in main
  assert main.count('printf("Hojas actuales: %d\\n", hojas_')==len(expected)
  assert main.index(helper)<main.index('int main(void)') and '#include "tad_abb.h"' in main
  assert 'abb_eliminar(arbol, 99)' not in main
  (target/'main.c').write_text(main,encoding='utf-8')
  hashes={}
  for kind,suffix in [('source','c'),('header','h')]:
   raw=context.request.get(base+'/help/source/abb/'+kind).body();assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_abb.'+suffix)).read_bytes();assert b'abb_contarHojas' not in raw;(target/('tad_abb.'+suffix)).write_bytes(raw);hashes[suffix]=hashlib.sha256(raw).hexdigest()
  build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'tad_abb.c'),str(target/'main.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
  run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
  calculated=[int(v) for v in re.findall(r'^Hojas actuales: (\d+)\s*$',run.stdout,re.M)];assert calculated==expected
  doxygen=Path(r'C:\Users\fralm\Documents\Codex\2026-09-30\task-2\doxygen-tool\doxygen.exe');assert doxygen.exists()
  warning_file=target/'doxygen-warnings.log';cfg=target/'Doxyfile'
  cfg.write_text('\n'.join(['PROJECT_NAME = "Actual generated ABB main"','INPUT = "'+(target/'main.c').as_posix()+'"','OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warning_file.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
  docs=subprocess.run([str(doxygen),str(cfg)],capture_output=True,text=True,timeout=60);assert docs.returncode==0,docs.stderr;assert warning_file.read_text(encoding='utf-8')==''
  row={'case':case,'phase':label,'calculated':calculated,'expected_api_results':expected,'stdout':run.stdout,'c_h_sha256':hashes,'canonical_helper_definitions':1,'actual_main_doxygen_warnings':0};(target/'review.json').write_text(json.dumps(row,indent=2),encoding='utf-8');reviews.append(row)
 try:
  with sync() as p:
   browser=p.chromium.launch()
   for case,seed in enumerate([[],[10,5,15,3,7,12,18],[10,5,15,3,7,12,18]]):
    context=browser.new_context();page=context.new_page();posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda q:posts.append(q.url) if q.method=='POST' else None)
    for value in seed:assert context.request.post(base+'/hierarchical/abb/operate',data={'operation':'insertar','payload':{'value':value}}).json()['success']
    page.goto(base+'/hierarchical/abb',wait_until='networkidle');assert page.locator('#hier-step-mode').get_attribute('aria-pressed')=='false';results=[]
    def operate(name,payload=None):
     page.select_option('#operation-select',name)
     if payload:page.locator('[name="value"]').fill(str(payload['value']))
     page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
     with page.expect_response(lambda z:z.url.endswith('/abb/operate') and z.request.method=='POST') as response:page.locator('#hier-sim-play').evaluate('b=>b.click()')
     data=response.value.json();page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");return data
    for index in range(3):
     data=operate('contar_hojas');assert data['success'];results.append(data['result'])
     if case==2 and index==0:assert operate('eliminar',{'value':3})['success']
    assert results==([0,0,0] if case==0 else [4,4,4] if case==1 else [4,3,3])
    assert not operate('eliminar',{'value':99})['success'];assert 'Operacion fallida' in page.locator('#action-history').text_content()
    compile_actual(page,context,case,'before-reload',results);count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
    compile_actual(page,context,case,'after-reload',results)
    data=operate('contar_hojas');assert data['success'];results.append(data['result']);compile_actual(page,context,case,'after-fourth',results)
    page.screenshot(path=str(tmp_path/f'leaf-history-case-{case}.png'),full_page=True);context.close();print('Actual Hojas main verified',case,results,flush=True)
   browser.close()
 finally:server.shutdown();thread.join(timeout=5)
 assert not errors and len(reviews)==9
 (tmp_path/'abb-leaves-actual-main-review.json').write_text(json.dumps({'programs':reviews,'errors':errors,'helper_duplicated':False,'reload_extra_posts':0,'limits':['Recorded histories, not all operations or histories.','Non-leaf historical print strings are outside this bounded repair.']},indent=2),encoding='utf-8')
