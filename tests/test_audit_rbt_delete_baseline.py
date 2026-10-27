"""Recorded actual-C deletion baseline, lifetime identity and exact source documentation."""
from pathlib import Path
import json,hashlib,os,subprocess,shutil,re
import pytest
from _application_rejection_contract import assert_unexecuted_input_rejection
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from _audit_rbt_delete_native_observer import observe,CASES,FUNCTIONS
from _audit_rbt_insert_native_observer import CHECK
@pytest.fixture(scope='module')
def rbt_delete_baseline(tmp_path_factory):
 root=Path(__file__).resolve().parents[1];cache=os.environ.get('AUDIT_RBT_DELETE_CACHE')
 if cache:
  r=json.loads((Path(cache)/'review.json').read_text());assert hashlib.sha256((root/'docs/tads_C/tad_rojo_negro.c').read_bytes()).hexdigest()==r['source_sha256'] and hashlib.sha256((root/'docs/tads_C/tad_rojo_negro.h').read_bytes()).hexdigest()==r['header_sha256'] and hashlib.sha256(Path(__file__).with_name('_audit_rbt_delete_native_observer.py').read_bytes()).hexdigest()==r['observer_sha256']
 else:r=observe(tmp_path_factory.mktemp('delete-native-parent')/'native')
 return r
@pytest.mark.parametrize('case',range(len(CASES)))
def test_delete_lifetime_identity_and_native_endpoint(rbt_delete_baseline,case):
 r=rbt_delete_baseline;m=r['cases'][case];ev=[e for e in r['events'] if e['case']==case];before,after=ev[0],ev[-1];target=next((n['id'] for n in before['heap'] if n['value']==m['value']),None)
 assert before['phase']=='before' and after['phase']=='after' and after['frames']==[] and m['present']==(target is not None) and after['frees']==int(target is not None) and not after['allocations'] and m['native_stdout']==''
 assert after['retired_ids']==([target] if target is not None else []);frees=[e for e in ev if e['phase']=='free'];assert [e['result'] for e in frees]==([target] if target is not None else [])
 values={n['id']:n['value'] for n in before['heap']};assert {n['id']:n['value'] for n in after['heap']}=={i:v for i,v in values.items() if i!=target}
 for e in ev:
  assert not e['allocations'] and all(n['id'] not in e['retired_ids'] for n in e['heap'])
  assert e['root'] in [0,*[n['id'] for n in e['heap']]]
  for n in e['heap']:assert n['value']==values[n['id']] and n['color'] in ['RED','BLACK']
 if target is None:assert before['heap']==after['heap'] and before['root']==after['root']
 assert r['strong_native_invariants']

@pytest.mark.parametrize('seed,value',[([],99),([10],99),([10,5,15],99),([10],'abc'),([],None),([-2147483648],2147483648)])
def test_application_rejection_is_not_a_native_delete_invocation(seed,value):
 history=[{'operation':'insertar','payload':{'value':v}} for v in seed];a,_=S._rebuild_adapter('red_black',history);before=a.to_visual_state();r=S.execute_operation('red_black','eliminar',{'value':value},history);assert not r['success'] and r['visual_state']==before and r['history']==history
 t=r['execution_trace']
 if t.get('execution_started') is False:
  assert_unexecuted_input_rejection(r)
 else:
  assert t['application_precondition_rejected'] and len(t['steps'])==1 and 'rbt_eliminar NO fue invocado' in t['source_code'];p=t['steps'][0]['pedagogy'];assert not p['instruction_event']['C_invoked'] and not p['variables'] and not p['call_stack'] and not p['memory']['allocated_objects'] and not p['memory']['freed_objects'] and p['return_propagation']['value'] is None and t['steps'][0]['console']==[]

from scripts.test_tool_paths import resolve_doxygen
def test_original_downloaded_helpers_contract_and_doxygen(tmp_path,rbt_delete_baseline):
 client=create_app().test_client();root=Path(__file__).resolve().parents[1]
 for kind,suffix in [('source','c'),('header','h')]:
  raw=client.get('/help/source/red_black/'+kind).data;assert raw==(root/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes();(tmp_path/('tad_rojo_negro.'+suffix)).write_bytes(raw)
 code='#include <assert.h>\n#include "tad_rojo_negro.c"\n'+CHECK+'\nint main(void){RBT root=NULL;'
 code+='assert(colorOf(NULL)==NEGRO&&minimo(NULL)==NULL);arreglarEliminacion(&root,NULL,NULL);struct nodoRBT p={.nro=10,.rbt_color=NEGRO},u={.nro=5,.rbt_color=ROJO,.padre=&p},v={.nro=3,.rbt_color=ROJO,.padre=&u};p.izq=&u;u.izq=&v;root=&p;assert(minimo(root)==&v);transplantar(&root,&u,&v);assert(root==&p&&p.izq==&v&&v.padre==&p&&u.padre==&p&&u.izq==&v);transplantar(&root,&p,&v);assert(root==&v&&v.padre==NULL&&v.nro==3&&v.rbt_color==ROJO);root=NULL;'
 for case,m in enumerate(rbt_delete_baseline['cases']):
  code+=''.join(f'rbt_insertar(&root,{v});' for v in m['seed'])+f'printf("RAW_BEGIN {case}\\n");rbt_eliminar(&root,{m["value"]});printf("RAW_END {case}\\nROOT {case} ");assert((!root||root->rbt_color==NEGRO)&&audit_valid(root,NULL,-2147483649LL,2147483648LL)>0);audit_tree(root);printf("\\n");rbt_liberar(root);root=NULL;'
 code+='return 0;}';(tmp_path/'raw.c').write_text(code,encoding='utf-8');gcc=shutil.which('gcc');build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'raw.c'),'-o',str(tmp_path/'raw.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(tmp_path/'raw.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stdout[-1000:]
 for case,m in enumerate(rbt_delete_baseline['cases']):
  assert run.stdout.split(f'RAW_BEGIN {case}\n')[1].split(f'RAW_END {case}\n')[0]=='';tree=re.search(r'^ROOT '+str(case)+r' (.*)$',run.stdout,re.M);assert json.loads(tree.group(1))==m['native_root']
 warn=tmp_path/'warnings.log';cfg=tmp_path/'Doxyfile';cfg.write_text('\n'.join(['INPUT = "'+(tmp_path/'tad_rojo_negro.c').as_posix()+'" "'+(tmp_path/'tad_rojo_negro.h').as_posix()+'"','OUTPUT_DIRECTORY = "'+(tmp_path/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','EXTRACT_STATIC = YES','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8');doxy=Path(resolve_doxygen());docs=subprocess.run([str(doxy),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',docs.stderr
 help=client.get('/help/hierarchical/red_black');assert help.status_code==200 and 'reserva original z' in help.text and 'sin copiar su valor' in help.text and 'altura negra uniforme' in help.text
 (tmp_path/'documentation-contract-review.json').write_text(json.dumps({'raw_original_cases':83,'C_H_Doxygen_warnings':0,'five_symbols_reviewed':['rbt_eliminar','colorOf','minimo','transplantar','arreglarEliminacion'],'helper_null_and_borrowed_transplant_contracts':True,'strong_endpoint_invariants':True,'manual_http_consistent':True,'instruction_UI_pending':True}),encoding='utf-8')
