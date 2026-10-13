"""Independent actual AVL minimum, displayed maximum and guarded value caller."""
import json,subprocess,shutil
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService

SEEDS=[[],[7],[10,5,15,3,7,12,18],[-5,-10,0],[10,5,15,3]]
CASES=[(op,seed) for op in ['minimo','maximo'] for seed in SEEDS]
@pytest.fixture(scope='module')
def avl_extreme_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-extreme-native');client=create_app().test_client();raw=client.get('/help/source/avl/source').data;header=client.get('/help/source/avl/header').data
 for suffix,data in [('c',raw),('h',header)]:
  assert data==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(data)
 source=raw.decode('utf-8-sig');maximum=CCodeService._build_avl_data()['operations']['maximo'];assert b'avl_maximo' not in raw and b'avl_maximo' not in header
 snippets={'minimo':CCodeService._build_avl_data()['operations']['minimo'],'maximo':maximum}
 helper=r'''
static AVL audit_nodes[128];static int audit_count,audit_case,audit_active,audit_callee,audit_function,audit_arg,audit_aux_present,audit_aux;
static int audit_caller,audit_root,audit_found_state,audit_found,audit_output_initialized,audit_output;
static int audit_id(AVL n){if(!n)return 0;for(int i=0;i<audit_count;i++)if(audit_nodes[i]==n)return i+1;return -1;}
static void audit_register(AVL n){if(!n)return;audit_nodes[audit_count++]=n;audit_register(n->izq);audit_register(n->der);}
static int audit_valid(AVL n,AVL parent){if(!n)return 0;int l=audit_valid(n->izq,n),r=audit_valid(n->der,n);if(l<0||r<0||n->padre!=parent||n->FE!=r-l||r-l>1||r-l< -1)return -100;return 1+(l>r?l:r);}
static void audit_emit(int line,const char*scope,const char*phase,int result){if(!audit_active)return;printf("AUDIT {\"case\":%d,\"line\":%d,\"scope\":\"%s\",\"phase\":\"%s\",\"result\":%d,\"callee\":%d,\"function\":%d,\"arg\":%d,\"aux_present\":%d,\"aux\":%d,\"caller\":%d,\"root\":%d,\"found_state\":%d,\"found\":%d,\"output_initialized\":%d,\"output\":%d,\"nodes\":[",audit_case,line,scope,phase,result,audit_callee,audit_function,audit_arg,audit_aux_present,audit_aux,audit_caller,audit_root,audit_found_state,audit_found_state==2?audit_found:0,audit_output_initialized,audit_output_initialized?audit_output:0);for(int i=0;i<audit_count;i++){AVL n=audit_nodes[i];if(i)printf(",");printf("{\"id\":%d,\"value\":%d,\"left\":%d,\"right\":%d,\"parent\":%d,\"balance_factor\":%d}",i+1,n->nro,audit_id(n->izq),audit_id(n->der),audit_id(n->padre),n->FE);}printf("]}\n");}
static int audit_condition(int line,const char*scope,const char*phase,int result){audit_emit(line,scope,phase,result);return result;}
'''
 callers={};instrumented={}
 for operation in ['minimo','maximo']:
  fn='avl_'+operation;parameter='nodo' if operation=='minimo' else 'raiz';snippet=snippets[operation];lines=snippet.splitlines()
  def line(text):return next(i+1 for i,l in enumerate(lines) if l.strip()==text)
  body=snippet[snippet.index('AVL '+fn+'(AVL '+parameter+') {'):]
  body=body.replace('{',f'{{audit_callee=1;audit_function={1 if operation=="minimo" else 2};audit_arg=audit_id({parameter});audit_aux_present=0;audit_emit({line("AVL "+fn+"(AVL "+parameter+") {")},"callee","enter",-2);',1)
  if operation=='maximo':
   text='AVL aux = raiz;';body=body.replace(text,text+f'audit_aux_present=1;audit_aux=audit_id(aux);audit_emit({line(text)},"callee","assignment",-2);')
  text='while (nodo->izq)' if operation=='minimo' else 'while (aux != NULL && aux->der != NULL) {';expression='nodo->izq != NULL' if operation=='minimo' else 'aux != NULL && aux->der != NULL'
  body=body.replace(text,f'while (audit_condition({line(text)},"callee","condition",{expression}))'+(' {' if operation=='maximo' else ''))
  text='nodo = nodo->izq;' if operation=='minimo' else 'aux = aux->der;'
  replacement='{'+text+('audit_arg=audit_id(nodo);' if operation=='minimo' else 'audit_aux=audit_id(aux);')+f'audit_emit({line(text)},"callee","assignment",-2);'+'}'
  body=body.replace(text,replacement)
  text='return nodo;' if operation=='minimo' else 'return aux;';value='nodo' if operation=='minimo' else 'aux'
  body=body.replace(text,f'audit_emit({line(text)},"callee","return",audit_id({value}));audit_callee=0;'+text)
  instrumented[operation]=body
  caller='int ejecutar_'+operation+'(AVL raiz, int *resultado) {\n    if (raiz == NULL)\n        return 0;\n    AVL encontrado = '+fn+'(raiz);\n    *resultado = encontrado->nro;\n    return 1;\n}'
  callers[operation]=caller;clines=caller.splitlines()
  def cline(text):return next(i+1 for i,l in enumerate(clines) if l.strip()==text)
  caller=caller.replace('{','{audit_caller=1;audit_root=audit_id(raiz);audit_found_state=0;audit_output_initialized=0;audit_emit(1,"caller","caller_enter",-2);',1)
  caller=caller.replace('if (raiz == NULL)',f'if (audit_condition({cline("if (raiz == NULL)")},"caller","caller_condition",raiz==NULL))')
  caller=caller.replace('return 0;','{audit_emit(3,"caller","caller_result",0);audit_caller=0;return 0;}')
  text='AVL encontrado = '+fn+'(raiz);';number=cline(text)
  caller=caller.replace(text,f'audit_found_state=1;audit_emit({number},"caller","call",-2);'+text+f'audit_found_state=2;audit_found=audit_id(encontrado);audit_emit({number},"caller","caller_assignment",-2);')
  text='*resultado = encontrado->nro;';caller=caller.replace(text,text+f'audit_output_initialized=1;audit_output=*resultado;audit_emit({cline(text)},"caller","caller_store",-2);')
  caller=caller.replace('return 1;','audit_emit(6,"caller","caller_result",1);audit_caller=0;return 1;')
  instrumented['caller_'+operation]=caller
 start=source.index('AVL avl_minimo(AVL nodo) {');end=source.index('\n}',start)+2
 # Remove instrumentation outside the chosen function from the actual source.
 instrumented_source=source[:start]+helper+instrumented['minimo']+source[end:]
 main='\nint main(void){AVL root=NULL;int value,status;\nif(avl_maximo(NULL)!=NULL){return 8;}\n'
 for case,(op,seed) in enumerate(CASES):
  main+='audit_active=0;audit_count=0;audit_callee=0;root=NULL;\n'+''.join(f'avl_insertar(&root,{v});' for v in seed)
  main+=f'if(audit_valid(root,NULL)<0){{return 9;}}\naudit_register(root);audit_case={case};audit_active=1;status=ejecutar_{op}(root,&value);audit_active=0;'
  main+=f'if(status!=1||value!={(min(seed) if op=="minimo" else max(seed))}){{return 10;}}' if seed else 'if(status!=0||audit_callee){return 11;}'
  main+='avl_liberarAVL(root);root=NULL;\n'
 main+='return 0;}'
 # This C download defines its own type; a separate caller translation unit uses H.
 translation=instrumented_source+'\n'+instrumented['maximo']+'\n'+instrumented['caller_minimo']+'\n'+instrumented['caller_maximo']+main
 (out/'instrumented.c').write_text(translation,encoding='utf-8')
 gcc=shutil.which('gcc');assert gcc;build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0,'Invalid native fixture/caller/observer: '+run.stderr
 (out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 for e in events:
  op=CASES[e['case']][0];text=callers[op] if e['scope']=='caller' else snippets[op];e['source_line']=text.splitlines()[e['line']-1].strip()
 report={'events':events,'cases':[{'operation':op,'seed':seed} for op,seed in CASES],'callers':callers,'snippets':snippets,'native_fixture_invariants_verified':True,'raw_maximum_NULL_verified':True,'minimum_NULL_not_called':True,'limits':['Actual minimum precondition: nonNULL. Empty interface maps to guarded equivalent caller0.','Maximum is existing main-local helper, not public C/H.','No sanitizer or all-path certificate.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

def identity(value):return 'N'+str(value) if value else 'NULL'
def extreme_matches(trace,events):
 used=set();pairs=[]
 for e in events:
  candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==e['phase']];assert candidates,e;step=candidates[0];used.add(step['step_index']);pairs.append((e,step))
 return pairs

@pytest.mark.parametrize('case',range(10))
def test_avl_extreme_native_aliases_guarded_caller_and_output(avl_extreme_native,case):
 client=create_app().test_client();op,seed=CASES[case]
 for v in seed:assert client.post('/hierarchical/avl/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 response=client.post('/hierarchical/avl/operate',json={'operation':op,'payload':{}});data=response.json;assert response.status_code==(200 if seed else 400) and data['success']==bool(seed)
 if seed:assert data['result']==(min(seed) if op=='minimo' else max(seed))
 else:assert 'result' not in data
 trace=data['execution_trace'];events=[e for e in avl_extreme_native['events'] if e['case']==case];assert len(trace['steps'])==len(events)
 if not seed:assert not any(e['scope']=='callee' for e in events) and data['message']=='El arbol esta vacio.'
 initial=trace['steps'][0]['state_snapshot']
 for e,step in extreme_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase'] in {'return','caller_result'} else ped['memory_state']
  assert state['root']==initial['root'] and state['head']==identity(e['root'])
  assert state['heap_nodes']==[{'id':identity(n['id']),'value':n['value'],'left':identity(n['left']),'right':identity(n['right']),'parent':identity(n['parent']),'balance_factor':n['balance_factor'],'status':'linked'} for n in e['nodes']]
  assert len(state['tree_frames'])==e['callee']<=1 and bool(state['caller_frame'])==bool(e['caller'])
  if e['callee']:
   f=state['tree_frames'][0];assert f['id']=='F1' and f['function']=='avl_'+op and f['parameters']=={('nodo' if op=='minimo' else 'raiz'):identity(e['arg'])} and f['locals']==({'aux':identity(e['aux'])} if e['aux_present'] else {})
  if e['caller']:
   assert state['caller_frame']['parameters']=={'raiz':identity(e['root']),'resultado':'&salida'}
   assert state['caller_frame']['locals']==({'encontrado':'sin inicializar' if e['found_state']==1 else identity(e['found'])} if e['found_state'] else {})
  assert state['caller_output']['initialized']==bool(e['output_initialized']) and state['caller_output']['value']==(e['output'] if e['output_initialized'] else None)
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['return_propagation']['reconnects_subtree'] and state['console_stdout']==''
  if e['phase'] in {'condition','caller_condition'}:assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='return':assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['call_stack'][-1]['return']==identity(e['result']) and ped['memory_state']['returned']==identity(e['result']) and not ped['memory_state']['tree_frames']
  if e['phase']=='caller_result':assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['memory_state']['wrapper_result']==e['result'] and not ped['memory_state']['caller_frame']
 assert not initial['tree_frames'] and not initial['caller_frame'] and initial['wrapper_result'] is None and initial['caller_output']['value'] is None
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_avl_extreme_native_coverage(avl_extreme_native):
 assert avl_extreme_native['raw_maximum_NULL_verified'] and avl_extreme_native['minimum_NULL_not_called']
 for operation in ['minimo','maximo']:
  cases=[i for i,(op,seed) in enumerate(CASES) if op==operation];events=[e for e in avl_extreme_native['events'] if e['case'] in cases]
  assert {e['result'] for e in events if e['phase']=='caller_condition'}=={0,1}
  assert {e['result'] for e in events if e['phase']=='condition'}=={0,1}
