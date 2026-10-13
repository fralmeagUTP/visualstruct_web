"""Independent height observer on current downloaded C, validated AVL seeds."""
import json,subprocess,shutil,re
from pathlib import Path
import pytest
from app import create_app

SEEDS=[[],[7],[10,5,15,3,7,12,18],[10,5,15,3],[10,5,15,18]]
@pytest.fixture(scope='module')
def avl_height_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-height-native');client=create_app().test_client();raw=client.get('/help/source/avl/source').data;header=client.get('/help/source/avl/header').data
 for suffix,data in [('c',raw),('h',header)]:assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig');lines=source.splitlines();start=source.index('int avl_altura(AVL arbol) {');end=source.index('\n}',start)+2;body=source[start:end]
 function_line=source.count('\n',0,start)
 def line(text):return next(i+1 for i,l in enumerate(lines) if i>=function_line and l.strip()==text)
 helper=r'''
static AVL audit_nodes[128];static int audit_parent[128],audit_count,audit_depth=-1,audit_case,audit_active;
static int audit_args[128],audit_flags[128][2],audit_values[128][2];
static int audit_id(AVL n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(AVL n,int parent){if(!n)return;int id=++audit_count;audit_nodes[id-1]=n;audit_parent[id-1]=parent;audit_register(n->izq,id);audit_register(n->der,id);}
static int audit_valid(AVL n,AVL parent){if(!n)return 0;int l=audit_valid(n->izq,n),r=audit_valid(n->der,n);if(l<0||r<0||n->padre!=parent||n->FE!=r-l||r-l>1||r-l< -1)return -100;return 1+(l>r?l:r);}
static void audit_emit(int line,const char*phase,int result){if(!audit_active)return;printf("AUDIT {\"case\":%d,\"line\":%d,\"phase\":\"%s\",\"result\":%d,\"frames\":[",audit_case,line,phase,result);for(int d=0;d<=audit_depth;d++){if(d)printf(",");printf("{\"arbol\":%d,\"locals\":[[%d,%d],[%d,%d]]}",audit_args[d],audit_flags[d][0],audit_flags[d][0]==2?audit_values[d][0]:0,audit_flags[d][1],audit_flags[d][1]==2?audit_values[d][1]:0);}printf("]}\n");}
static void audit_enter(AVL arbol){audit_depth++;audit_args[audit_depth]=audit_id(arbol);audit_flags[audit_depth][0]=audit_flags[audit_depth][1]=0;}
static int audit_condition(int line,int result){audit_emit(line,"condition",result);return result;}
'''
 body=body.replace('{','{audit_enter(arbol);audit_emit('+str(line('int avl_altura(AVL arbol) {'))+',"enter",-2);',1)
 body=body.replace('if (arbol == NULL)','if (audit_condition('+str(line('if (arbol == NULL)'))+', arbol == NULL))')
 body=body.replace('return 0;','{audit_emit('+str(line('return 0;'))+',"return",0);audit_depth--;return 0;}')
 for name,field,slot in [('altIzq','izq',0),('altDer','der',1)]:
  text='int '+name+' = avl_altura(arbol->'+field+');';number=line(text)
  replacement=f'int {name}=(audit_flags[audit_depth][{slot}]=1,audit_emit({number},"call",-2),avl_altura(arbol->{field}));audit_flags[audit_depth][{slot}]=2;audit_values[audit_depth][{slot}]={name};audit_emit({number},"after",-2);'
  assert body.count(text)==1;body=body.replace(text,replacement)
 text='return (altIzq > altDer ? altIzq : altDer) + 1;';number=line(text)
 body=body.replace(text,f'int audit_result=(audit_condition({number},altIzq>altDer)?altIzq:altDer)+1;audit_emit({number},"return",audit_result);audit_depth--;return audit_result;')
 instrumented=source[:start]+helper+body+source[end:];main='\nint main(void){AVL root=NULL;int result;\n'
 for case,seed in enumerate(SEEDS):
  main+='audit_active=0;audit_count=0;root=NULL;audit_depth=-1;\n'+''.join(f'avl_insertar(&root,{v});' for v in seed)
  main+=f'if(audit_valid(root,NULL)<0){{return 9;}}\naudit_register(root,0);audit_case={case};audit_active=1;result=avl_altura(root);audit_emit(0,"caller",result);audit_active=0;avl_liberarAVL(root);root=NULL;\n'
 main+='return 0;}';(out/'instrumented.c').write_text(instrumented+main,encoding='utf-8')
 gcc=shutil.which('gcc');assert gcc;build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,'Invalid native AVL seed or observer failure: '+run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[{**json.loads(l[6:])} for l in run.stdout.splitlines() if l.startswith('AUDIT ')];assert len(events)==196
 for e in events:e['source_line']=lines[e['line']-1].strip() if e['line'] else None
 report={'events':events,'seeds':SEEDS,'native_fixture_invariants_verified':True,'limits':['Only height observed; no allocation/free/rotation during active operation.','Native seeds independently checked FE/parent/height balance before activation.','No sanitizer or all-path certificate.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def height_matches(trace,events):
 used=set();pairs=[]
 for e in events:
  if e['phase']=='caller':step=trace['steps'][-1]
  else:
   phase={'enter':'enter','condition':'condition','call':'call','after':'assignment','return':'return'}[e['phase']]
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==phase];assert candidates,e;step=candidates[0];used.add(step['step_index'])
  pairs.append((e,step))
 return pairs

@pytest.mark.parametrize('case',range(5))
def test_avl_height_native_scopes_locals_returns_and_immutable_fields(avl_height_native,case):
 client=create_app().test_client()
 for v in SEEDS[case]:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 data=client.post('/hierarchical/avl/operate',json={'operation':'altura','payload':{}}).json;assert data['success'];trace=data['execution_trace'];events=[e for e in avl_height_native['events'] if e['case']==case];initial=trace['steps'][0]['state_snapshot']
 assert len(trace['steps'])==len(events)+2 and data['result']==events[-1]['result']
 for e,s in height_matches(trace,events):
  ped=s['pedagogy'];state=s['state_snapshot'] if e['phase']=='return' else ped['memory_state']
  assert state['root']==initial['root'] and state['heap_nodes']==initial['heap_nodes'] and state['head']==initial['head']
  assert len(state['tree_frames'])==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):
   assert f['function']=='avl_altura' and f['depth']==depth and f['parameters']=={'arbol':'N'+str(n['arbol']) if n['arbol'] else 'NULL'}
   assert f['locals']=={name:('sin inicializar' if flag==1 else value) for name,(flag,value) in zip(['altIzq','altDer'],n['locals']) if flag}
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['return_propagation']['reconnects_subtree'] and state['console_stdout']==''
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='enter':assert ped['instruction_event']['frame_id']==state['tree_frames'][-1]['id']
  if e['phase']=='return':assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['call_stack'][-1]['return']==e['result'] and len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  if e['phase']=='caller':assert state['wrapper_result']==e['result'] and state['caller_frame'] is None
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_avl_height_native_true_false_ties(avl_height_native):
 rows=[e for e in avl_height_native['events'] if e['phase']=='condition' and 'altIzq > altDer' in e['source_line']]
 assert {e['result'] for e in rows}=={0,1} and any(e['frames'][-1]['locals'][0][1]==e['frames'][-1]['locals'][1][1] for e in rows)
