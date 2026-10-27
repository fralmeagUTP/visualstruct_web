"""Independent current-C search observer, borrowed identities and validated seeds."""
import json,subprocess,shutil
from pathlib import Path
import pytest
from app import create_app

BALANCED=[10,5,15,3,7,12,18]
CASES=[([],7),([7],7),([7],3),(BALANCED,10),(BALANCED,3),(BALANCED,18),(BALANCED,6),(BALANCED,99)]
@pytest.fixture(scope='module')
def avl_search_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-search-native');client=create_app().test_client();raw=client.get('/help/source/avl/source').data;header=client.get('/help/source/avl/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig');lines=source.splitlines();start=source.index('AVL avl_buscar(AVL raiz, int x) {');end=source.index('\n}',start)+2;body=source[start:end];function_line=source.count('\n',0,start)
 def line(text):return next(i+1 for i,l in enumerate(lines) if i>=function_line and l.strip()==text)
 helper=r'''
static AVL audit_nodes[128];static int audit_count,audit_depth=-1,audit_case,audit_active;
static int audit_args[128],audit_targets[128];
static int audit_id(AVL n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(AVL n){if(!n)return;audit_nodes[audit_count++]=n;audit_register(n->izq);audit_register(n->der);}
static int audit_valid(AVL n,AVL parent){if(!n)return 0;int l=audit_valid(n->izq,n),r=audit_valid(n->der,n);if(l<0||r<0||n->padre!=parent||n->FE!=r-l||r-l>1||r-l< -1)return -100;return 1+(l>r?l:r);}
static void audit_emit(int line,const char*phase,int result){if(!audit_active)return;printf("AUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"frames\":[",audit_case,line,phase,result);for(int d=0;d<=audit_depth;d++){if(d)printf(",");printf("{\"raiz\":%d,\"x\":%d}",audit_args[d],audit_targets[d]);}printf("],\"nodes\":[");for(int i=0;i<audit_count;i++){AVL n=audit_nodes[i];if(i)printf(",");printf("{\"id\":%d,\"value\":%d,\"left\":%d,\"right\":%d,\"parent\":%d,\"balance_factor\":%d}",i+1,n->nro,audit_id(n->izq),audit_id(n->der),audit_id(n->padre),n->FE);}printf("]}\n");}
static void audit_enter(AVL raiz,int x){audit_depth++;audit_args[audit_depth]=audit_id(raiz);audit_targets[audit_depth]=x;}
static int audit_condition(int line,int result){audit_emit(line,"condition",result);return result;}
'''
 body=body.replace('{','{audit_enter(raiz,x);audit_emit('+str(line('AVL avl_buscar(AVL raiz, int x) {'))+',"enter",-2);',1)
 for text,expression in [('if (!raiz)','!raiz'),('if (x < raiz->nro)','x < raiz->nro'),('if (x > raiz->nro)','x > raiz->nro')]:
  assert body.count(text)==1;body=body.replace(text,'if (audit_condition('+str(line(text))+', '+expression+'))')
 for text,value in [('return NULL;','NULL'),('return raiz;','raiz')]:
  assert body.count(text)==1;body=body.replace(text,'{audit_emit('+str(line(text))+',"return",audit_id('+value+'));audit_depth--;return '+value+';}')
 for field in ['izq','der']:
  text='return avl_buscar(raiz->'+field+', x);';number=line(text);assert body.count(text)==1
  body=body.replace(text,'{audit_emit('+str(number)+',"call",-2);AVL audit_result=avl_buscar(raiz->'+field+',x);audit_emit('+str(number)+',"return",audit_id(audit_result));audit_depth--;return audit_result;}')
 main='\nint main(void){AVL root=NULL,result;\n'
 for case,(seed,target) in enumerate(CASES):
  main+='audit_active=0;audit_count=0;root=NULL;audit_depth=-1;\n'+''.join(f'avl_insertar(&root,{v});' for v in seed)
  main+=f'if(audit_valid(root,NULL)<0){{return 9;}}\naudit_register(root);audit_case={case};audit_active=1;result=avl_buscar(root,{target});audit_emit(0,"caller",audit_id(result));audit_active=0;avl_liberarAVL(root);root=NULL;\n'
 main+='return 0;}';(out/'instrumented.c').write_text(source[:start]+helper+body+source[end:]+main,encoding='utf-8')
 gcc=shutil.which('gcc');assert gcc;build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,'Invalid native fixture/observer: '+run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 for e in events:e['source_line']=lines[e['line']-1].strip() if e['line'] else None
 report={'events':events,'cases':[{'seed':seed,'target':target} for seed,target in CASES],'native_fixture_invariants_verified':True,'limits':['Search only; no mutation or rotation observed.','No sanitizer or all-path certificate.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def search_matches(trace,events):
 used=set();pairs=[]
 for e in events:
  if e['phase']=='caller':step=trace['steps'][-1]
  else:
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==e['phase']];assert candidates,e;step=candidates[0];used.add(step['step_index'])
  pairs.append((e,step))
 return pairs

def identity(value):return 'N'+str(value) if value else 'NULL'

@pytest.mark.parametrize('case',range(8))
def test_avl_search_native_guard_comparisons_borrowed_alias_and_scopes(avl_search_native,case):
 client=create_app().test_client();seed,target=CASES[case]
 for v in seed:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 data=client.post('/hierarchical/avl/operate',json={'operation':'buscar','payload':{'value':target}}).json;assert data['success'];trace=data['execution_trace'];events=[e for e in avl_search_native['events'] if e['case']==case];initial=trace['steps'][0]['state_snapshot']
 assert len(trace['steps'])==len(events)+2 and data['result'] is (events[-1]['result']!=0)
 for e,s in search_matches(trace,events):
  ped=s['pedagogy'];state=s['state_snapshot'] if e['phase']=='return' else ped['memory_state']
  assert state['root']==initial['root'] and state['head']==initial['head']
  assert state['heap_nodes']==[{'id':identity(n['id']),'value':n['value'],'left':identity(n['left']),'right':identity(n['right']),'status':'linked','parent':identity(n['parent']),'balance_factor':n['balance_factor']} for n in e['nodes']]
  assert len(state['tree_frames'])==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):
   assert f['function']=='avl_buscar' and f['depth']==depth and f['parameters']=={'raiz':identity(n['raiz']),'x':n['x']} and f['locals']=={}
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['return_propagation']['reconnects_subtree'] and state['console_stdout']==''
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='enter':assert ped['instruction_event']['frame_id']==state['tree_frames'][-1]['id']
  if e['phase']=='return':assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['call_stack'][-1]['return']==identity(e['result']) and ped['memory_state']['returned']==identity(e['result']) and len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  if e['phase']=='caller':assert state['wrapper_result']==int(e['result']!=0) and state['returned']==identity(e['result']) and state['caller_frame'] is None
 assert initial['wrapper_result'] is None and not initial['tree_frames'] and not initial['caller_frame']
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_avl_search_native_condition_coverage(avl_search_native):
 for text in ['if (!raiz)','if (x < raiz->nro)','if (x > raiz->nro)']:
  assert {e['result'] for e in avl_search_native['events'] if e['phase']=='condition' and e['source_line']==text}=={0,1}
 for case in range(8):
  events=[e for e in avl_search_native['events'] if e['case']==case]
  for i,e in enumerate(events):
   if e['phase']=='condition' and e['source_line']=='if (!raiz)' and e['result']:
    assert events[i+1]['phase']=='return' and events[i+1]['source_line']=='return NULL;'
