"""LOW native insertion contracts and documentation, no instruction UI closure."""
from pathlib import Path
import os,json,hashlib,sys,subprocess,shutil
import pytest
from app import create_app
from _audit_rbt_insert_native_observer import observe,CASES,FUNCTIONS,CHECK
@pytest.fixture(scope='module')
def rbt_insert_baseline(tmp_path_factory):
 root=Path(__file__).resolve().parents[1];cached=os.environ.get('AUDIT_RBT_INSERT_CACHE')
 if cached:
  out=Path(cached);report=json.loads((out/'review.json').read_text(encoding='utf-8'))
  for suffix,key in [('c','downloaded_sha256'),('h','header_sha256')]:assert hashlib.sha256((root/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes()).hexdigest()==report[key]
  assert hashlib.sha256(Path(__file__).with_name('_audit_rbt_insert_native_observer.py').read_bytes()).hexdigest()==report['observer_sha256']
 else:report=observe(tmp_path_factory.mktemp('rbt-insert-parent')/'native')
 assert len(report['cases'])==24 and report['native_events']==1460 and all(report['function_counts'][f]>0 for f in FUNCTIONS);return report
@pytest.mark.parametrize('case',range(len(CASES)))
def test_insert_creation_publication_repair_baseline(rbt_insert_baseline,case):
 meta=rbt_insert_baseline['cases'][case];events=[e for e in rbt_insert_baseline['events'] if e['case']==case];before,after=events[0],events[-1];seed_count=len(meta['seed'])
 assert before['phase']=='before' and after['phase']=='after' and after['frames']==[]
 assert all(n['initialized']==31 for n in before['heap']) and len(after['heap'])==seed_count+int(meta['inserted'])
 for e in events:
  assert [n['id'] for n in e['heap']]==list(range(1,len(e['heap'])+1))
  for n in e['heap']:
   for key,bit in [('value',1),('left',2),('right',4),('parent',8),('color',16)]:
    if not n['initialized']&bit:assert n[key] is None
    elif key in ['left','right','parent']:assert 0<=n[key]<=len(e['heap'])
   if n['initialized']&16:assert n['color'] in ['RED','BLACK']
  assert not any(e['phase']=='free' for e in events)
 assert meta['allocation_attempts']==int(meta['mode']=='malloc_failure' or meta['inserted'])
 if meta['inserted']:
  created=[e['heap'][-1] for e in events if len(e['heap'])>seed_count and e['phase'] in ['allocate','initialize']];assert [n['initialized'] for n in created]==[0,1,7,15,31]
  assert created[-1]['value']==meta['value'] and created[-1]['left']==created[-1]['right']==0 and created[-1]['color']=='RED'
  assert meta['operation_stdout']=='\tEl numero ha sido insertado\n' and sum(e['phase']=='printf' for e in events)==1
  assert any(e['function']=='rbt_insercion_caso1' and e['phase']=='enter' for e in events)
 else:
  assert after['heap']==before['heap'] and after['root']==before['root'] and meta['operation_stdout']=='' and not any(e['phase'] in ['initialize','printf'] for e in events)
  # A failed malloc assignment is observed, but it creates no object.
  assert sum(e['phase']=='allocate' for e in events)==int(meta['mode']=='malloc_failure')
  for e in events:
   if e['phase']=='allocate':assert e['heap']==before['heap'] and e['allocation_attempts']==1
 # Rotations do not recolor, allocate or free; intermediate links can be partial/cyclic.
 for a,b in zip(events,events[1:]):
  if b['function'] in ['rbt_rotar_dcha','rbt_rotar_izda']:
   assert len(a['heap'])==len(b['heap']) and [n['color'] for n in a['heap']]==[n['color'] for n in b['heap']]
 assert meta['backend_endpoint_checked']==(meta['mode']=='normal')

from scripts.test_tool_paths import resolve_doxygen
def test_original_downloaded_contracts_helpers_and_manual(tmp_path,rbt_insert_baseline):
 client=create_app().test_client();root=Path(__file__).resolve().parents[1];raw=client.get('/help/source/red_black/source').data;header=client.get('/help/source/red_black/header').data
 for suffix,data in [('c',raw),('h',header)]:assert data==(root/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes();(tmp_path/('tad_rojo_negro.'+suffix)).write_bytes(data)
 code='#include <stdio.h>\n#include <stdlib.h>\n#include <assert.h>\n#include "tad_rojo_negro.h"\n'+CHECK+r'''
static int fail_next,attempts;void*audit_native_malloc(size_t n){attempts++;return fail_next?NULL:malloc(n);}
int main(void){RBT root=NULL;
'''
 for i,m in enumerate(CASES):
  code+='root=NULL;fail_next=0;'+''.join(f'rbt_insertar(&root,{v});' for v in m['seed'])+f'attempts=0;fail_next={int(m["mode"]=="malloc_failure")};rbt_insertar({"NULL" if m["mode"]=="NULL_reference" else "&root"},{m["value"]});'
  code+=f'assert((!root||root->rbt_color==NEGRO)&&audit_valid(root,NULL,-2147483649LL,2147483648LL)>0);printf("ORIGINAL {i} %d ",attempts);audit_tree(root);puts("");rbt_liberar(root);root=NULL;\n'
 code+=r'''
 nodoRBT a={.nro=10,.rbt_color=NEGRO},l={.nro=5,.rbt_color=ROJO},rr={.nro=15,.rbt_color=ROJO},c={.nro=7,.rbt_color=NEGRO};
 assert(rbt_abuelo(NULL)==NULL&&rbt_tio(NULL)==NULL);assert(rbt_abuelo(&a)==NULL&&rbt_tio(&a)==NULL);
 root=&a;rbt_rotar_dcha(NULL,&a);rbt_rotar_izda(NULL,&a);rbt_rotar_dcha(&root,NULL);rbt_rotar_izda(&root,NULL);rbt_rotar_dcha(&root,&a);rbt_rotar_izda(&root,&a);assert(root==&a&&a.izq==NULL&&a.der==NULL);
 a.izq=&l;l.padre=&a;l.der=&c;c.padre=&l;int old_attempts=attempts;
 rbt_rotar_dcha(&root,&a);assert(root==&l&&l.padre==NULL&&l.der==&a&&a.padre==&l&&a.izq==&c&&c.padre==&a);assert(l.rbt_color==ROJO&&a.rbt_color==NEGRO&&c.rbt_color==NEGRO);
 rbt_rotar_izda(&root,&l);assert(root==&a&&a.padre==NULL&&a.izq==&l&&l.padre==&a&&l.der==&c&&c.padre==&l&&attempts==old_attempts);
 a.der=&rr;rr.padre=&a;assert(rbt_abuelo(&c)==&a&&rbt_tio(&c)==&rr);
 puts("HELPER CONTRACTS PASS");return 0;}
'''
 (tmp_path/'contracts.c').write_text(code,encoding='utf-8');gcc=shutil.which('gcc');assert gcc;flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
 build=subprocess.run([gcc,*flags,'-Dmalloc=audit_native_malloc','-c',str(tmp_path/'tad_rojo_negro.c'),'-o',str(tmp_path/'raw.o')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 build=subprocess.run([gcc,*flags,str(tmp_path/'contracts.c'),str(tmp_path/'raw.o'),'-o',str(tmp_path/'contracts.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(tmp_path/'contracts.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0 and run.stdout.endswith('HELPER CONTRACTS PASS\n'),run.stdout
 records=[line.split(' ',3) for line in run.stdout.splitlines() if line.startswith('ORIGINAL ')];assert len(records)==24
 for row,meta in zip(records,rbt_insert_baseline['cases']):assert int(row[1])==meta['case'] and int(row[2])==meta['allocation_attempts'] and json.loads(row[3])==meta['native_root']
 (tmp_path/'stdout.log').write_text(run.stdout,encoding='utf-8')
 # Public-file content assertions and actual HTTP manual, separate from Doxygen warning count.
 for blob in [raw,header]:
  text=blob.decode('utf-8-sig');assert 'Retorna void. Duplicado, arbol NULL o fallo de malloc' in text and 'nuevo_n es otro local' in text and 'rotacion aislada no garantiza' in text and 'no comprueba globalmente orden' in text
 manual=client.get('/help/hierarchical/red_black');assert manual.status_code==200;body=manual.data.decode('utf-8');assert 'la aplicacion rechaza duplicados' in body and 'altura negra uniforme' in body and 'no certifica' in body
 doxygen=Path(resolve_doxygen());warn=tmp_path/'warnings.log';cfg=tmp_path/'Doxyfile'
 cfg.write_text('\n'.join(['PROJECT_NAME = "RBT insertion public C H documentation"','INPUT = "'+(tmp_path/'tad_rojo_negro.c').as_posix()+'" "'+(tmp_path/'tad_rojo_negro.h').as_posix()+'"','OUTPUT_DIRECTORY = "'+(tmp_path/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([str(doxygen),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',(docs.stderr,warn.read_text(encoding='utf-8'))
 (tmp_path/'contract-review.json').write_text(json.dumps({'raw_original_cases':24,'helper_contracts_verified':True,'strictC17':True,'C_H_Doxygen_warnings':0,'manual_consistency':True,'no_instruction_UI_claim':True},indent=2),encoding='utf-8')
