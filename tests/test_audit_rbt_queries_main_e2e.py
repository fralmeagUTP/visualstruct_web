"""Actual Rojo-Negro displayed queries, downloaded mains and reload contracts."""
import json,subprocess,re,shutil,hashlib
from pathlib import Path
import pytest
from app.services.c_code_service import CCodeService
from test_audit_avl_main_e2e import avl_server
pytestmark=pytest.mark.e2e
def compile_main(main,context,base,target):
 target.mkdir();(target/'main.c').write_text(main,encoding='utf-8');hashes={}
 for kind,suffix in [('source','c'),('header','h')]:
  response=context.request.get(base+'/help/source/red_black/'+kind);assert response.status==200;raw=response.body()
  assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes()
  (target/('tad_rojo_negro.'+suffix)).write_bytes(raw);hashes[suffix]=hashlib.sha256(raw).hexdigest()
 gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'tad_rojo_negro.c'),str(target/'main.c'),'-o',str(target/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,run.stderr
 doxygen=Path(r'C:\Users\fralm\Documents\Codex\2026-09-30\task-2\doxygen-tool\doxygen.exe');assert doxygen.exists();warn=target/'warnings.log';cfg=target/'Doxyfile'
 cfg.write_text('\n'.join(['PROJECT_NAME = "Actual Rojo-Negro history main"','INPUT = "'+(target/'main.c').as_posix()+'"','OUTPUT_DIRECTORY = "'+(target/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([str(doxygen),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',(docs.stderr,warn.read_text(encoding='utf-8'))
 return {'stdout':run.stdout,'download_hashes':hashes,'strict_compile':True,'doxygen_warnings':0}
@pytest.mark.parametrize('seed',[[],[10],[10,5,15],[-2147483648,0,2147483647]])
def test_rbt_visible_queries_real_main_and_reload(avl_server,tmp_path,seed):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
  for v in seed:assert context.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/red_black',wait_until='networkidle');records=[]
  def op(name,value=None):
   page.select_option('#operation-select',name)
   if value is not None:page.locator('[name="value"]').fill(str(value))
   with page.expect_response(lambda resp:resp.url.endswith('/red_black/operate') and resp.request.method=='POST') as pending:page.click('#hier-sim-play')
   data=pending.value.json();page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");return data
  for phase in range(2):
   for name in ['inorden','altura','validar']:
    for _ in range(2):
     data=op(name);assert data['success'];records.append({'operation':name,'result':data['result']})
   if phase==0:assert op('limpiar')['success']
  bad=op('eliminar',99);assert not bad['success']
  mains=[];programs=[]
  for label in ['before','after']:
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');mains.append(main)
   for name in ['inorden','altura']:assert main.count(CCodeService.get_structure_data('red_black')['operations'][name])==1
   assert 'int rbt_validar(' not in main and 'rbt_validar_altura_negra' not in main
   body=main.split('int main(void)',1)[1];assert 'rbt_verArbol(' not in body and 'rbt_eliminar(&arbol, 99)' not in body
   assert 'rbt_izq' not in main and 'rbt_dato' not in main
   clean=re.sub(r'/\*.*?\*/|//[^\n]*','',body,flags=re.S)
   for name in ['inorden','altura','validar']:assert clean.count('rbt_'+name+'(')==sum(x['operation']==name for x in records)
   result=compile_main(main,context,avl_server,tmp_path/label);out=result['stdout'];calculated={'inorden':[[int(v) for v in line.split()] for line in re.findall(r'^INORDEN: (.*)$',out,re.M)],'altura':[int(v) for v in re.findall(r'^ALTURA: (\d+)$',out,re.M)],'validar':[v=='correcto' for v in re.findall(r'^VALIDAR RN COMPLETO: (correcto|incorrecto)$',out,re.M)]}
   for name,values in calculated.items():assert values==[x['result'] for x in records if x['operation']==name],(name,values,records,out)
   programs.append(result)
   if label=='before':n=len(posts);page.reload(wait_until='networkidle');assert len(posts)==n
  assert mains[0]==mains[1];assert not errors
  # Repeated read-only query after reload is a new operation, not deduplicated.
  data=op('inorden');assert data['success'] and data['result']==[]
  main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.split('int main(void)',1)[1].count('rbt_inorden(arbol);')==5
  programs.append(compile_main(main,context,avl_server,tmp_path/'repeat'));context.close();browser.close()
 (tmp_path/'rbt-main-review.json').write_text(json.dumps({'seed':seed,'programs':programs,'queries':records,'stable_reload':True,'extra_reload_posts':0,'errors':errors},indent=2))
