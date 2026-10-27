"""Independent typed native insertion snapshots versus product instruction model."""
from pathlib import Path
import os,json,hashlib,re,copy
import pytest
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.rbt_delete_instruction import build_rbt_delete_trace
from _audit_rbt_delete_instruction_observer import observe,CASES

def pointer(value):return 'NULL' if value==0 else '&raiz' if value==-2 else 'N'+str(value)
def var(v,retired=()):
 if not v['initialized']:return 'sin inicializar'
 if v['kind']==3:return chr(v['value'])
 if v['kind']==0:return v['value']
 value=pointer(v['value']);return value+' [valor indeterminado; identidad historica]' if v['kind']==1 and v['value'] in retired else value
def source_line(report,event):return report['_source_lines'][event['line']-1].strip() if event['line'] else None
def pairs(trace,events,report):
 assert len(trace['steps'])==len(events),(len(trace['steps']),len(events))
 for step,event in zip(trace['steps'],events):
  phase={'before':'caller_enter','after':'caller'}.get(event['phase'],event['phase']);assert step['pedagogy']['instruction_event']['phase']==phase,(step['line_text'],phase,step['pedagogy']['instruction_event'])
  if event['line']:assert step['line_text'].strip()==source_line(report,event),(step['line_text'],source_line(report,event))
  yield step,event

def check(step,event):
 ped=step['pedagogy'];state=step['state_snapshot'] if event['phase']=='return' else ped['memory_state']
 expected=[{'id':pointer(n['id']),'value':n['value'],'left':pointer(n['left']),'right':pointer(n['right']),'parent':pointer(n['parent']),'color':n['color'],'initialized':31} for n in event['heap']]
 assert [{k:n[k] for k in expected[0]} for n in state['heap_nodes']]==expected if expected else not state['heap_nodes']
 assert state['head']==pointer(event['root']) and state['heap_count']==len(event['heap']) and state['validation'] is None
 actual=[{'function':f['function'],'invocation':int(f['id'][1:]),'parameters':f['parameters'],'locals':f['locals']} for f in state['tree_frames']]
 expected_frames=[{**{k:f[k] for k in ['function','invocation']},'parameters':{k:var(v,event['retired_ids']) for k,v in f['parameters'].items()},'locals':{k:var(v,event['retired_ids']) for k,v in f['locals'].items()}} for f in event['frames']];assert actual==expected_frames,(step['line_text'],actual,expected_frames)
 assert state['console_stdout']=='' and not step['console']
 if event['phase'] in ['condition','operand','selection']:
  assert ped['condition']['result']==bool(event['result']) and step['condition_result']==bool(event['result'])
  assert re.sub(r'[\s()]','',ped['instruction_event']['expression'])==re.sub(r'[\s()]','',event['expression'])
  if event['phase']=='condition' and 'colorOf' in event['expression']:assert 'colorOf(' not in ped['condition']['substituted'].split('(omitido')[0]
  if event['expression']=='y_color_original == NEGRO':assert ped['condition']['substituted'] in ["'n' == 'n'","'r' == 'n'"]
 if event['phase']=='return':
  result=pointer(event['result']) if event['function']=='minimo' else chr(event['result']) if event['function']=='colorOf' else 'void';assert ped['return_propagation']['value']==result and ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and len(ped['memory_state']['tree_frames'])==len(event['frames'])-1
 assert not ped['return_propagation']['reconnects_subtree'] and not ped['memory']['allocated_objects']
 before={n['id'] for n in step['state_snapshot']['heap_nodes']};remaining={pointer(n['id']) for n in event['heap']};freed=before-remaining
 assert {n['id'] for n in ped['memory']['freed_objects']}==freed and ped['memory']['event']==('free' if freed else 'none')
 assert {n['id'] for n in state['freed_nodes']}=={pointer(i) for i in event['retired_ids']}
 assert ped['invariant']['holds'] is None
 previous={(f['id'],name):v for f in step['state_snapshot']['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()}
 current={(f['id'],name):v for f in ped['memory_state']['tree_frames'] for name,v in {**f['parameters'],**f['locals']}.items()}
 shown={(v['frame_id'],v['name']):v for v in ped['variables'] if v['frame_id']!='caller'}
 assert set(shown)==set(previous)|set(current)
 for key,v in shown.items():assert v['previous']==previous.get(key,'fuera de ambito') and v['value']==current.get(key,'fuera de ambito')


@pytest.fixture(scope='session')
def rbt_delete_instruction_native(tmp_path_factory):
 root=Path(__file__).resolve().parents[1];cache=os.environ.get('AUDIT_RBT_DELETE_INSTRUCTION_CACHE')
 if cache:
  folder=Path(cache);report=json.loads((folder/'review.json').read_text(encoding='utf-8'))
  for suffix,key in [('c','source_sha256'),('h','header_sha256')]:assert hashlib.sha256((root/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes()).hexdigest()==report[key]
  assert report['observer_sha256']==hashlib.sha256(Path(__file__).with_name('_audit_rbt_delete_instruction_observer.py').read_bytes()).hexdigest()
 else:folder=tmp_path_factory.mktemp('rbt-delete-observer-parent')/'native';report=observe(folder)
 report['_source_lines']=(root/'docs/tads_C/tad_rojo_negro.c').read_text(encoding='utf-8-sig').splitlines()
 return report
def prepare_case(report,case):
 meta=report['cases'][case]
 if 'instruction_trace' in meta:return meta
 history=[{'operation':'insertar','payload':{'value':v}} for v in meta['seed']];adapter,_=S._rebuild_adapter('red_black',history);before=adapter.to_visual_state()
 result=S.execute_operation('red_black','eliminar',{'value':meta['value']},history);meta['data']=result
 if meta['present']:meta['instruction_trace']=result['execution_trace']
 else:
  trace=copy.deepcopy(result['execution_trace']);trace['source_code']=CCodeService.get_structure_data('red_black')['operations']['eliminar'];trace['final_state']=before
  meta['instruction_trace']=build_rbt_delete_trace(trace,before,before)
 return meta
@pytest.mark.parametrize('case',range(len(CASES)))
def test_delete_every_native_instruction_scope_alias_heap_and_lifetime(rbt_delete_instruction_native,case):
 report=rbt_delete_instruction_native;meta=prepare_case(report,case);trace=meta['instruction_trace'];events=[e for e in report['events'] if e['case']==case]
 for step,event in pairs(trace,events,report):check(step,event)
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']
 assert trace['steps'][-1]['state_after']==trace['final_state']
 assert trace['steps'][-1]['pedagogy']['memory_state']['root']==meta['native_root']
 assert sum(len(s['pedagogy']['memory']['freed_objects']) for s in trace['steps'])==int(meta['present'])
@pytest.mark.parametrize('value',[99,'abc'])
def test_delete_application_rejection_does_not_fabricate_C(value):
 result=S.execute_operation('red_black','eliminar',{'value':value},[{'operation':'insertar','payload':{'value':10}}]);assert not result['success'];trace=result['execution_trace'];assert trace['application_precondition_rejected'];ped=trace['steps'][0]['pedagogy'];assert not ped['instruction_event']['C_invoked'] and not ped['call_stack'] and not ped['variables'] and not ped['memory']['freed_objects']

from scripts.test_tool_paths import resolve_doxygen
@pytest.mark.parametrize('case',[70,24,49,32,1,25,0,3,4,9,13,21,6,79,80,81,73])
def test_delete_shown_caller_native_endpoint_and_stdout(tmp_path,rbt_delete_instruction_native,case):
 import subprocess,shutil
 report=rbt_delete_instruction_native;meta=prepare_case(report,case);trace=meta['instruction_trace'];root=Path(__file__).resolve().parents[1]
 source=trace['source_code'];caller='/**\n * @brief Invoca el TAD'+source.split('/**\n * @brief Invoca el TAD',1)[1]
 assertions=[]
 def expect(n,path,parent='NULL'):
  if n is None:assertions.append('assert('+path+'==NULL);');return
  assertions.append('assert('+path+'!=NULL && '+path+'->nro=='+str(n['value'])+' && '+path+'->rbt_color=='+('NEGRO' if n['color']=='BLACK' else 'ROJO')+' && '+path+'->padre=='+parent+');')
  expect(n['left'],path+'->izq',path);expect(n['right'],path+'->der',path)
 expect(meta['native_root'],'raiz')
 main='#include "tad_rojo_negro.h"\n#include <assert.h>\n#include <stddef.h>\n'+caller+'\n/** @brief Verifica el caller observado y libera fuera de su traza. @return 0. */\nint main(void){RBT raiz=NULL;'+''.join('rbt_insertar(&raiz,'+str(v)+');' for v in meta['seed'])+'ejecutar_eliminacion(&raiz);'+''.join(assertions)+'rbt_liberar(raiz);raiz=NULL;return 0;}\n'
 (tmp_path/'main.c').write_text(main,encoding='utf-8')
 for suffix in ['c','h']:(tmp_path/('tad_rojo_negro.'+suffix)).write_bytes((root/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes())
 build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_rojo_negro.c'),'-o',str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0 and not run.stderr,run.stderr
 assert run.stdout=='\tEl numero ha sido insertado\n'*len(meta['seed'])
 doxygen=Path(resolve_doxygen());warn=tmp_path/'warnings.log';cfg=tmp_path/'Doxyfile'
 cfg.write_text('\n'.join(['INPUT = "'+(tmp_path/'main.c').as_posix()+'"','OUTPUT_DIRECTORY = "'+(tmp_path/'doxygen').as_posix()+'"','EXTRACT_ALL = NO','WARN_IF_UNDOCUMENTED = YES','WARN_IF_DOC_ERROR = YES','WARN_NO_PARAMDOC = YES','WARN_LOGFILE = "'+warn.as_posix()+'"','GENERATE_XML = YES','GENERATE_HTML = NO','GENERATE_LATEX = NO','QUIET = YES','HAVE_DOT = NO']),encoding='utf-8')
 docs=subprocess.run([str(doxygen),str(cfg)],capture_output=True,text=True,timeout=30);assert docs.returncode==0 and warn.read_text(encoding='utf-8')=='',(docs.stderr,warn.read_text(encoding='utf-8'))
 (tmp_path/'caller-review.json').write_text(json.dumps({'case':case,'strict_c17':True,'exact_shown_wrapper':True,'stdout':run.stdout,'all_final_fields_checked':True,'doxygen_warnings':0,'cleanup':'test fixture outside shown operation; actual main ownership reviewed separately; cleanup outside operation'}),encoding='utf-8')
