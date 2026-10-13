"""Actual heap generator, downloaded C/H, capacity boundaries and query reload."""
import ast, json, shutil, subprocess, threading
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.domain.hierarchical.tad_wrappers import MonticuloBinario
from werkzeug.serving import make_server

@pytest.fixture
def heap_server():
 server=make_server('127.0.0.1',0,create_app()); thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 yield f'http://127.0.0.1:{server.server_port}'
 server.shutdown();thread.join(timeout=5)

def compile_download(main,context,base,target):
 target.mkdir(); (target/'main.c').write_text(main,encoding='utf-8')
 for kind,suffix in [('source','c'),('header','h')]:
  r=context.request.get(base+'/help/source/binary_heap/'+kind); assert r.status==200
  raw=r.body(); assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_monticulo_binario.'+suffix)).read_bytes()
  (target/('tad_monticulo_binario.'+suffix)).write_bytes(raw)
 gcc=shutil.which('gcc'); assert gcc
 run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'tad_monticulo_binario.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30); assert run.returncode==0,run.stderr
 run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
 cfg=target/'Doxyfile';warn=target/'warnings.log'
 cfg.write_text('\n'.join(['PROJECT_NAME = "Heap actual main and downloads"','INPUT = "'+target.as_posix()+'"','FILE_PATTERNS = *.c *.h','OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([r'C:\Users\fralm\Documents\Codex\2026-09-30\task-2\doxygen-tool\doxygen.exe',str(cfg)],capture_output=True,text=True,timeout=30)
 assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',(docs.stderr,warn.read_text(encoding='utf-8'))
 return run.stdout

@pytest.mark.e2e
@pytest.mark.parametrize('count',[0,1,255,256,257,513])
def test_heap_actual_generator_untruncated_copy(heap_server,tmp_path,count):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(heap_server+'/hierarchical/binary_heap',wait_until='networkidle')
  seed=list(range(count-1,-1,-1)); expected=MonticuloBinario(seed).a_lista()
  # Boundary histories use the real generator; server-driven reload is tested separately.
  history=[{'operation':'insertar','payloadRaw':{'value':v},'success':True} for v in seed]
  history += [{'operation':'a_lista','payloadRaw':{},'success':True} for _ in range(2)]
  main=page.evaluate('h=>buildHierMainCode("binary_heap",h,window.HIER_VIEW_MODEL.didactic)',history)
  assert '[256]' not in main and 'free(buffer_' in main
  stdout=compile_download(main,context,heap_server,tmp_path/'actual-generator')
  lists=[ast.literal_eval(line.removeprefix('A LISTA: ')) for line in stdout.splitlines() if line.startswith('A LISTA: ')]
  assert lists==[expected,expected]
  snippet=CCodeService.get_structure_data('binary_heap')['operations']['a_lista']
  probe='#include <assert.h>\n#include <stdlib.h>\n#include "tad_monticulo_binario.h"\nint main(void){MonticuloBinario monticulo;monticulo_inicializar(&monticulo,MONTICULO_MIN,16);'+''.join(f'monticulo_insertar(&monticulo,{v});' for v in seed)+snippet.replace('free(buffer);','assert(usados == '+str(count)+');'+''.join(f'assert(buffer[{i}] == {v});' for i,v in enumerate(expected))+'free(buffer);')+'\nmonticulo_destruir(&monticulo);return 0;}'
  # The displayed C snippet also compiles; no fixed-size array is retained.
  assert '[256]' not in snippet
  compile_download(probe.replace('int main(void)', '/** @brief Compile the displayed heap-copy snippet. @return 0 on completion. */\nint main(void)'),context,heap_server,tmp_path/'displayed-snippet')
  (tmp_path/'capacity-review.json').write_text(json.dumps({'count':count,'copies':2,'complete':lists==[expected,expected],'doxygen_warnings':0,'scope':'Actual generator with constructed successful history; actual server/UI reload covered separately.'}),encoding='utf-8')
  browser.close()

@pytest.mark.e2e
def test_heap_success_queries_repeat_reload_and_download(heap_server,tmp_path):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(heap_server+'/hierarchical/binary_heap',wait_until='networkidle')
  def operate(op,value=None):
   page.select_option('#operation-select',op)
   if value is not None:page.locator('[name="value"]').fill(str(value))
   with page.expect_response(lambda r:r.url.endswith('/binary_heap/operate') and r.request.method=='POST') as pending:page.click('#hier-sim-play')
   data=pending.value.json();page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");return data
  assert not operate('raiz')['success']
  failed_main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents())
  assert 'monticulo_raiz(&monticulo,' not in failed_main
  # Failed UI entries are local annotations, not executable persisted history.
  n=len(posts);page.reload(wait_until='networkidle');assert len(posts)==n
  assert operate('a_lista')['result']==[]
  for v in [7,-1,7,'00']:assert operate('insertar',v)['success']
  expected=MonticuloBinario([7,-1,7,0]).a_lista()
  for op in ['a_lista','a_lista','raiz','raiz']:
   assert operate(op)['result']==(expected if op=='a_lista' else -1)
  mains=[]
  for label in ['before-reload','after-reload']:
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')
   stdout=compile_download(main,context,heap_server,tmp_path/label)
   lists=[ast.literal_eval(x.removeprefix('A LISTA: ')) for x in stdout.splitlines() if x.startswith('A LISTA: ')]
   assert lists==[[],expected,expected];assert stdout.count('RAIZ: -1\n')==2
   assert [x for x in stdout.splitlines() if x.startswith(('A LISTA:','RAIZ:'))]==['A LISTA: []',f'A LISTA: {expected}',f'A LISTA: {expected}','RAIZ: -1','RAIZ: -1']
   assert main.count('monticulo_raiz(&monticulo,')==2 # Failed empty root is not replayed.
   mains.append(main)
   if label=='before-reload':n=len(posts);page.reload(wait_until='networkidle');assert len(posts)==n
  assert mains[0]==mains[1] and not errors
  (tmp_path/'reload-review.json').write_text(json.dumps({'successful_queries':5,'failed_queries':1,'reload_post_count':0,'main_identical':True,'doxygen_warnings':0}),encoding='utf-8');browser.close()

def test_heap_restoring_queries_never_executes_them(monkeypatch):
 from app.adapters.binary_heap_adapter import BinaryHeapAdapter
 actual=BinaryHeapAdapter.execute; calls=[]
 def spy(self,op,payload):calls.append(op);return actual(self,op,payload)
 monkeypatch.setattr(BinaryHeapAdapter,'execute',spy)
 history=[{'operation':'insertar','payload':{'value':7}},{'operation':'raiz','payload':{}},{'operation':'a_lista','payload':{}},{'operation':'a_lista','payload':{}}]
 adapter,restored=HierarchicalStructureService._rebuild_adapter('binary_heap',history)
 assert restored==history and calls==['insertar'] and adapter.to_visual_state()['array']==[7]

@pytest.mark.e2e
def test_generated_heap_copy_allocation_failure_exits_without_partial_result(heap_server,tmp_path):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(heap_server+'/hierarchical/binary_heap',wait_until='networkidle')
  history=[{'operation':'insertar','payloadRaw':{'value':'0008'},'success':True},{'operation':'a_lista','payloadRaw':{},'success':True}]
  main=page.evaluate('h=>buildHierMainCode("binary_heap",h,window.HIER_VIEW_MODEL.didactic)',history)
  artifact=tmp_path/'actual-main';stdout=compile_download(main,context,heap_server,artifact)
  assert stdout=='INSERTAR: 8\nA LISTA: [8]\n'
  main=main.replace('malloc(', 'audit_copy_malloc(')
  shim='\n/** @brief Inject caller-copy failure. @param n Requested bytes. @return NULL. */\nstatic void *audit_copy_malloc(size_t n){(void)n;return NULL;}\n'
  main=main.replace('int main(void)',shim+'int main(void)',1);(artifact/'failure.c').write_text(main,encoding='utf-8')
  gcc=shutil.which('gcc');assert gcc
  run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(artifact),str(artifact/'failure.c'),str(artifact/'tad_monticulo_binario.c'),'-o',str(artifact/'failure.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
  run=subprocess.run([str(artifact/'failure.exe')],capture_output=True,text=True,timeout=5)
  assert run.returncode==1 and run.stdout=='INSERTAR: 8\n' and 'A LISTA' not in run.stdout
  (tmp_path/'failure-review.json').write_text(json.dumps({'exit_status':run.returncode,'stdout':run.stdout,'copy_partial_output':False,'failure_injected_only_into_caller':True}),encoding='utf-8');browser.close()
