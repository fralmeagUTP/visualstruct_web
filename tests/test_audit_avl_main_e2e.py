"""Compile actual AVL history, query values, repeated requests and reload."""
import json,threading,subprocess,re,shutil,hashlib
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from werkzeug.serving import make_server
pytestmark=pytest.mark.e2e

@pytest.fixture
def avl_server():
 server=make_server('127.0.0.1',0,create_app());thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 yield f'http://127.0.0.1:{server.server_port}'
 server.shutdown();thread.join(timeout=5)

def compile_main(main,context,base,target):
 target.mkdir();(target/'main.c').write_text(main,encoding='utf-8');hashes={}
 for kind,suffix in [('source','c'),('header','h')]:
  response=context.request.get(base+'/help/source/avl/'+kind);assert response.status==200;raw=response.body()
  assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes()
  assert b'avl_maximo(' not in raw and b'avl_inorden(' not in raw and b'avl_validar_fes(' not in raw
  (target/('tad_avl.'+suffix)).write_bytes(raw);hashes[suffix]=hashlib.sha256(raw).hexdigest()
 gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'tad_avl.c'),str(target/'main.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
 doxygen=Path(r'C:\Users\fralm\Documents\Codex\2026-09-30\task-2\doxygen-tool\doxygen.exe');assert doxygen.exists();warn=target/'warnings.log';cfg=target/'Doxyfile'
 cfg.write_text('\n'.join(['PROJECT_NAME = "Actual AVL history main"','INPUT = "'+(target/'main.c').as_posix()+'"','OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([str(doxygen),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',(docs.stderr,warn.read_text(encoding='utf-8'))
 return {'stdout':run.stdout,'download_hashes':hashes,'strict_compile':True,'doxygen_warnings':0}

def test_avl_generator_preflight_decimal_helpers_errors_and_c_compile(avl_server,tmp_path):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();page.goto(avl_server+'/hierarchical/avl',wait_until='networkidle')
  entries=[{'operation':'insertar','payloadRaw':{'value':v},'success':True} for v in ['010','0005','015','08']]
  entries += [{'operation':op,'payloadRaw':{'value':'0005'} if op=='buscar' else {},'success':True} for op in ['buscar','minimo','maximo','altura','inorden','validar']]
  entries += [{'operation':'minimo','payloadRaw':{},'success':False},{'operation':'buscar','payloadRaw':{'value':'bad'},'success':False}]
  main=page.evaluate('h=>buildHierMainCode("avl",h,window.HIER_VIEW_MODEL.didactic)',entries)
  body=main.split('int main(void)',1)[1];assert 'avl_insertar(&arbol, 10);' in body and 'avl_insertar(&arbol, 8);' in body and 'avl_buscar(arbol, 5)' in body
  review=compile_main(main,context,avl_server,tmp_path/'preflight')
  assert 'INORDEN: 5 8 10 15 \n' in review['stdout'] and 'MINIMO: 5\n' in review['stdout'] and 'MAXIMO: 15\n' in review['stdout'] and 'ALTURA: 3\n' in review['stdout']
  assert 'BUSCAR 5: encontrado\n' in review['stdout'] and 'EQUILIBRIO POR ALTURAS: correcto\n' in review['stdout']
  context.close();browser.close()

@pytest.mark.parametrize('seed',[[],[10,5,15],[-5,-10,0]])
def test_actual_avl_queries_repeat_failures_reload_and_generated_results(avl_server,tmp_path,seed):
 records=[];reviews=[];errors=[]
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  for v in seed:assert context.request.post(avl_server+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/avl',wait_until='networkidle')
  def operate(op,payload=None):
   page.select_option('#operation-select',op)
   for name,value in (payload or {}).items():page.locator('[name="'+name+'"]').fill(str(value))
   with page.expect_response(lambda resp:resp.url.endswith('/avl/operate') and resp.request.method=='POST') as pending:page.click('#hier-sim-play')
   data=pending.value.json();page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");return data
  def queries(values,height,repeats=2):
   search='0005' if not seed or seed[0]>0 else '-010'
   expected={'buscar':int(search) in values,'minimo':min(values) if values else None,'maximo':max(values) if values else None,'altura':height,'inorden':sorted(values),'validar':True}
   for op in expected:
    for _ in range(repeats):
     data=operate(op,{'value':search} if op=='buscar' else None)
     if op in ['minimo','maximo'] and not values:assert not data['success'];continue
     assert data['success'] and data['result']==expected[op]
     records.append({'operation':op,'value':int(search) if op=='buscar' else None,'result':expected[op]})
  queries(seed,2 if seed else 0)
  assert operate('insertar',{'value':'08'})['success'];queries([*seed,8],3 if seed else 1,1)
  assert not operate('insertar',{'value':'08'})['success'] and not operate('eliminar',{'value':'99'})['success']
  assert operate('limpiar')['success'] and operate('limpiar')['success'];queries([],0)
  def check(label):
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');body=main.split('int main(void)',1)[1]
   for op in ['maximo','inorden','validar']:
    canonical=CCodeService.get_structure_data('avl')['operations'][op];assert main.count(canonical)==1
   assert 'avl_verArbol(' not in body and 'avl_eliminar(&arbol, 99);' not in body and body.count('avl_insertar(&arbol, 8);')==1
   clean=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
   for op,call in [('buscar','avl_buscar'),('minimo','avl_minimo'),('maximo','avl_maximo'),('altura','avl_altura'),('inorden','avl_inorden'),('validar','avl_validar_fes')]:assert clean.count(call+'(')==sum(x['operation']==op for x in records)
   review=compile_main(main,context,avl_server,tmp_path/label);stdout=review['stdout']
   calculated={
    'buscar':[(int(v),status=='encontrado') for v,status in re.findall(r'^BUSCAR (-?\d+): (encontrado|ausente)$',stdout,re.M)],
    'minimo':[int(v) for v in re.findall(r'^MINIMO: (-?\d+)$',stdout,re.M)],
    'maximo':[int(v) for v in re.findall(r'^MAXIMO: (-?\d+)$',stdout,re.M)],
    'altura':[int(v) for v in re.findall(r'^ALTURA: (\d+)$',stdout,re.M)],
    'inorden':[[int(v) for v in text.split()] for text in re.findall(r'^INORDEN: (.*)$',stdout,re.M)],
    'validar':[status=='correcto' for status in re.findall(r'^EQUILIBRIO POR ALTURAS: (correcto|incorrecto)$',stdout,re.M)]}
   for op,result in calculated.items():assert result==[(x['value'],x['result']) if op=='buscar' else x['result'] for x in records if x['operation']==op],(op,result,records,stdout)
   reviews.append({'label':label,**review,'queries':len(records)})
  check('before-reload');count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count;check('after-reload')
  data=operate('buscar',{'value':'08'});assert data['success'] and data['result'] is False;records.append({'operation':'buscar','value':8,'result':False});check('after-repeat')
  assert not errors;context.close();browser.close()
 (tmp_path/'avl-main-history-review.json').write_text(json.dumps({'seed':seed,'programs':reviews,'queries':records,'errors':errors,'extra_reload_posts':0,'limits':['Small nonrotating histories isolate reproduction fixes; known native FE/rotation discrepancies remain open.','Queries are computed by exact displayed helper; equilibrium-by-height does not certify stored FE.','Program cleanup remains the existing explicit history/footer convention.']},ensure_ascii=False,indent=2),encoding='utf-8')
 print('AVL actual main/history verified',seed,len(reviews),len(records),flush=True)
