"""Existing main-local Inorden helper observed independently against downloaded AVL C/H."""
import json,subprocess,shutil
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService

SEEDS=[[],[7],[10,5,15,3,7,12,18],[-5,-10,0],[10,5,15,3]]
@pytest.fixture(scope='module')
def avl_inorden_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-inorden-native');client=create_app().test_client();raw=client.get('/help/source/avl/source').data;header=client.get('/help/source/avl/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(data)
 snippet=CCodeService._build_avl_data()['operations']['inorden'];assert 'void avl_inorden(AVL nodo)' in snippet and b'avl_inorden' not in raw and b'avl_inorden' not in header
 (out/'displayed-helper.c').write_text(snippet,encoding='utf-8');lines=snippet.splitlines()
 def line(text):return next(i+1 for i,l in enumerate(lines) if l.strip()==text)
 closing=max(i+1 for i,l in enumerate(lines) if l.strip()=='}')
 helper=r'''
static AVL audit_nodes[128];static int audit_count,audit_depth=-1,audit_case,audit_active,audit_args[128];static char audit_stdout[1024];
static int audit_id(AVL n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(AVL n){if(!n)return;audit_nodes[audit_count++]=n;audit_register(n->izq);audit_register(n->der);}
static int audit_valid(AVL n,AVL parent){if(!n)return 0;int l=audit_valid(n->izq,n),r=audit_valid(n->der,n);if(l<0||r<0||n->padre!=parent||n->FE!=r-l||r-l>1||r-l< -1)return -100;return 1+(l>r?l:r);}
static void audit_emit(int line,const char*phase,int result){if(!audit_active)return;printf("\nAUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"frames\":[",audit_case,line,phase,result);for(int d=0;d<=audit_depth;d++){if(d)printf(",");printf("{\"nodo\":%d}",audit_args[d]);}printf("],\"console_hex\":\"");for(size_t i=0;i<strlen(audit_stdout);i++)printf("%02x",(unsigned char)audit_stdout[i]);printf("\",\"nodes\":[");for(int i=0;i<audit_count;i++){AVL n=audit_nodes[i];if(i)printf(",");printf("{\"id\":%d,\"value\":%d,\"left\":%d,\"right\":%d,\"parent\":%d,\"balance_factor\":%d}",i+1,n->nro,audit_id(n->izq),audit_id(n->der),audit_id(n->padre),n->FE);}printf("]}\n");}
static void audit_enter(AVL nodo){audit_depth++;audit_args[audit_depth]=audit_id(nodo);}
static int audit_condition(int line,int result){audit_emit(line,"condition",result);return result;}
'''
 body=snippet.replace('{','{audit_enter(nodo);audit_emit('+str(line('void avl_inorden(AVL nodo) {'))+',"enter",-2);',1)
 body=body.replace('if (nodo != NULL) {','if (audit_condition('+str(line('if (nodo != NULL) {'))+', nodo != NULL)) {')
 for field in ['izq','der']:
  text='avl_inorden(nodo->'+field+');';number=line(text);assert body.count(text)==1
  body=body.replace(text,'audit_emit('+str(number)+',"call",-2);'+text+'audit_emit('+str(number)+',"resume",-2);')
 text='printf("%d ", nodo->nro);';assert body.count(text)==1
 body=body.replace(text,text+'snprintf(audit_stdout+strlen(audit_stdout),sizeof(audit_stdout)-strlen(audit_stdout),"%d ",nodo->nro);audit_emit('+str(line(text))+',"printf",-2);')
 last=body.rfind('}');body=body[:last]+'audit_emit('+str(closing)+',"return",-2);audit_depth--;'+body[last:]
 main='\nint main(void){AVL root=NULL;\n'
 for case,seed in enumerate(SEEDS):
  main+='audit_active=0;audit_count=0;audit_depth=-1;audit_stdout[0]=0;root=NULL;\n'+''.join(f'avl_insertar(&root,{v});' for v in seed)
  main+=f'if(audit_valid(root,NULL)<0){{return 9;}}\naudit_register(root);audit_case={case};audit_active=1;avl_inorden(root);audit_emit(0,"caller",0);audit_active=0;avl_liberarAVL(root);root=NULL;\n'
 main+='return 0;}';(out/'instrumented-helper.c').write_text('#include "tad_avl.h"\n#include <stdio.h>\n#include <string.h>\n'+helper+body+main,encoding='utf-8')
 gcc=shutil.which('gcc');assert gcc;build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'tad_avl.c'),str(out/'instrumented-helper.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,'Invalid native fixture/observer: '+run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 for e in events:e['source_line']=lines[e['line']-1].strip() if e['line'] else None;e['console_stdout']=bytes.fromhex(e['console_hex']).decode('ascii')
 report={'events':events,'seeds':SEEDS,'native_fixture_invariants_verified':True,'helper':snippet,'helper_origin':'existing displayed main-local auxiliary; not a public downloadable C/H function','limits':['Inorden only; no mutation or rotation observed.','No sanitizer or all-path certificate.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def inorden_matches(trace,events):
 used=set();pairs=[]
 for e in events:
  if e['phase']=='caller':continue
  candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==e['phase']];assert candidates,e;step=candidates[0];used.add(step['step_index']);pairs.append((e,step))
 return pairs

def identity(value):return 'N'+str(value) if value else 'NULL'

@pytest.mark.parametrize('case',range(5))
def test_avl_inorden_native_scopes_heap_and_each_printf(avl_inorden_native,case):
 client=create_app().test_client()
 for v in SEEDS[case]:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 data=client.post('/hierarchical/avl/operate',json={'operation':'inorden','payload':{}}).json;assert data['success'];trace=data['execution_trace'];events=[e for e in avl_inorden_native['events'] if e['case']==case];initial=trace['steps'][0]['state_snapshot']
 assert trace['source_code'].strip()==avl_inorden_native['helper'].strip();assert len(trace['steps'])==len(events)-1
 assert data['result']==sorted(SEEDS[case]) and events[-1]['console_stdout']==''.join(str(v)+' ' for v in sorted(SEEDS[case]))
 for e,s in inorden_matches(trace,events):
  ped=s['pedagogy'];state=s['state_snapshot'] if e['phase']=='return' else ped['memory_state']
  assert state['root']==initial['root'] and state['head']==initial['head']
  assert state['heap_nodes']==[{'id':identity(n['id']),'value':n['value'],'left':identity(n['left']),'right':identity(n['right']),'status':'linked','parent':identity(n['parent']),'balance_factor':n['balance_factor']} for n in e['nodes']]
  assert len(state['tree_frames'])==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):assert f['function']=='avl_inorden' and f['depth']==depth and f['parameters']=={'nodo':identity(n['nodo'])} and f['locals']=={}
  assert state['console_stdout']==e['console_stdout'] and not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['return_propagation']['reconnects_subtree']
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='enter':assert ped['instruction_event']['frame_id']==state['tree_frames'][-1]['id']
  if e['phase']=='return':assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['call_stack'][-1]['return']=='void' and len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  assert s['console']==([str(e['nodes'][e['frames'][-1]['nodo']-1]['value'])+' '] if e['phase']=='printf' else [])
 assert trace['steps'][-1]['pedagogy']['memory_state']['console_stdout']==events[-1]['console_stdout'] and not initial['tree_frames'] and initial['console_stdout']==''
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_avl_inorden_native_guard_and_output_coverage(avl_inorden_native):
 assert {e['result'] for e in avl_inorden_native['events'] if e['phase']=='condition'}=={0,1}
 assert sum(e['phase']=='printf' for e in avl_inorden_native['events'])==sum(map(len,SEEDS))
