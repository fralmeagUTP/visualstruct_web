"""Compiled canonical helper observations; valid and independently forged invalid trees."""
from pathlib import Path
from copy import deepcopy
import json,re,shutil,subprocess
import pytest
from app import create_app
from app.adapters.abb_adapter import ABBAdapter
from app.domain.hierarchical.tad_abb import ABBNodo,abb_insertar
from app.services.c_code_service import CCodeService
MIN=-2147483648;MAX=2147483647
CASES=[{'seed':s} for s in [[],[0],[MIN],[MAX],[0,MIN,MAX],[10,5,15,MIN,7,12,MAX],[1,2,3,4],[4,3,2,1]]]+[{'tree':t} for t in [(10,(11,None,None),None),(10,None,(9,None,None)),(10,(5,None,(12,None,None)),(20,None,None)),(10,(5,None,None),(15,(8,None,None),None)),(10,(10,None,None),None),(10,None,(10,None,None)),(10,(12,None,None),(20,None,None)),(0,(MIN,None,(-1,None,None)),(MAX,(1,None,None),None))]]
def fixture(case):
 m=CASES[case];root=None
 if 'seed' in m:
  for v in m['seed']:root=abb_insertar(root,v)
 else:
  def load(t):return None if t is None else ABBNodo(t[0],load(t[1]),load(t[2]))
  root=load(m['tree'])
 a=ABBAdapter();a._structure._raiz=root
 def count(n):return 0 if n is None else 1+count(n.izquierdo)+count(n.derecho)
 a._structure._tamano=count(root);return a
def trace_for(case):
 from app.domain.hierarchical.abb_validate_instruction import build_abb_validate_trace
 a=fixture(case);state=a.to_visual_state();source=CCodeService.get_structure_data('abb')['operations']['validar']
 trace={'source_code':source,'payload':{},'success':True};return build_abb_validate_trace(trace,state,deepcopy(state)),state,a._structure.validar()
HELPER=r'''
typedef struct {ABBNodo*n;int lp,lo,hp,hi,id;} Frame;
static Frame frames[64];static int depth,serial,case_id,node_count,caller_live;
static ABBNodo *nodes[64];
static const char *identity(ABBNodo*n){static char names[64][12];if(!n)return "NULL";for(int i=0;i<node_count;i++)if(nodes[i]==n){snprintf(names[i],sizeof(names[i]),"N%d",i+1);return names[i];}return "INVALID";}
static void enter(ABBNodo*n,int lp,int lo,int hp,int hi){frames[depth++]=(Frame){n,lp,lo,hp,hi,++serial};}
static void log_event(const char*t,const char*p,int c,int result,int line){
 printf("AUDIT {\"case\":%d,\"text\":\"%s\",\"phase\":\"%s\",\"condition\":%d,\"result\":%d,\"source_index\":%d,\"caller_live\":%d,\"frames\":[",case_id,t,p,c,result,line,caller_live);
 for(int i=0;i<depth;i++){Frame f=frames[i];printf("%s{\"id\":\"F%d\",\"depth\":%d,\"parameters\":{\"nodo\":\"%s\",\"hay_minimo\":%d,\"minimo\":%d,\"hay_maximo\":%d,\"maximo\":%d},\"locals\":{}}",i?",":"",f.id,i,identity(f.n),f.lp,f.lo,f.hp,f.hi);}
 printf("],\"nodes\":[");for(int i=0;i<node_count;i++){ABBNodo*n=nodes[i];printf("%s{\"id\":\"%s\",\"value\":%d,\"left\":\"%s\",\"right\":\"%s\",\"status\":\"linked\"}",i?",":"",identity(n),n->valor,identity(n->izquierdo),identity(n->derecho));}printf("]}\n");
}
static int condition(const char*t,int c,int line){log_event(t,"condition",c,-2,line);return c;}
'''

@pytest.fixture(scope='module')
def abb_validate_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('abb-validate-native');client=create_app().test_client();helper=CCodeService.get_structure_data('abb')['operations']['validar'];assert 'hay_minimo' in helper
 for kind,suffix in [('source','c'),('header','h')]:
  raw=client.get('/help/source/abb/'+kind).data;assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_abb.'+suffix)).read_bytes();assert b'abb_validar_rango' not in raw;(out/('tad_abb.'+suffix)).write_bytes(raw)
 def replace(code,text,new,count=1):return re.sub(r'(?m)^([ \t]*)'+re.escape(text),lambda m:m.group(1)+new,code,count=count)
 def line_index(t,occurrence=0):
  rows=[i for i,l in enumerate(helper.splitlines()) if l.strip()==t];return rows[occurrence] if rows else -1
 def log(t,p,c='-2',result='-2',occurrence=0):return 'log_event('+','.join([json.dumps(t),json.dumps(p),c,result,str(line_index(t,occurrence))])+');'
 code=helper;sig=next(l for l in helper.splitlines() if l.startswith('int abb_validar_rango('));code=replace(code,sig,sig+'enter(nodo,hay_minimo,minimo,hay_maximo,maximo);'+log(sig,'enter'))
 for text,expr in [('if (nodo == NULL) {','nodo==NULL'),('if ((hay_minimo && nodo->valor <= minimo) || (hay_maximo && nodo->valor >= maximo)) {','(hay_minimo&&nodo->valor<=minimo)||(hay_maximo&&nodo->valor>=maximo)')]:code=replace(code,text,'if(condition('+json.dumps(text)+','+expr+','+str(line_index(text))+')){')
 for side,args in [('izquierdo','hay_minimo, minimo, 1, nodo->valor'),('derecho','1, nodo->valor, hay_maximo, maximo')]:
  text=f'if (!abb_validar_rango(nodo->{side}, {args})) {{';code=replace(code,text,log(text,'call')+'if(condition('+json.dumps(text)+',!abb_validar_rango(nodo->'+side+', '+args+'),'+str(line_index(text))+')){')
 for result in [0,1]:
  text=f'return {result};';occurrences=iter(range(sum(l.strip()==text for l in helper.splitlines())))
  code=re.sub(r'(?m)^([ \t]*)'+re.escape(text),lambda m:m.group(1)+'depth--;'+log(text,'return',result=str(result),occurrence=next(occurrences))+text,code)
 caller='int ejecutar_validacion(ABBNodo* raiz) {\n    return abb_validar_rango(raiz, 0, 0, 0, 0);\n}'
 impl=caller.replace('{','{caller_live=1;'+log(caller.splitlines()[0],'caller_enter'),1);call='return abb_validar_rango(raiz, 0, 0, 0, 0);';impl=replace(impl,call,log(call,'call')+'int result=abb_validar_rango(raiz,0,0,0,0);caller_live=0;'+log(call,'caller_result',result='result')+'return result;')
 main='\nint main(void){ABBNodo store[64];int got;'
 expected=[]
 for case in range(len(CASES)):
  state=fixture(case).to_visual_state();assert state['validation']==(case<8 or case==15);items=[]
  def load(n):
   if n is None:return None
   i=len(items);items.append({'value':n['value']});items[i]['left']=load(n['left']);items[i]['right']=load(n['right']);return i
  root=load(state['root']);n=len(items);expected.append(state['validation'])
  main+=f'case_id={case};node_count={n};depth=serial=caller_live=0;'
  for i,node in enumerate(items):
   left='NULL' if node['left'] is None else '&store['+str(node['left'])+']';right='NULL' if node['right'] is None else '&store['+str(node['right'])+']';main+=f'store[{i}]=(ABBNodo){{{node["value"]},{left},{right}}};nodes[{i}]=&store[{i}];'
  main+='got=ejecutar_validacion('+('NULL' if root is None else '&store[0]')+f');if(got!={int(state["validation"])})return 2;'
 main+='return 0;}'
 (out/'instrumented.c').write_text('#include <stdio.h>\n#include "tad_abb.h"\n'+HELPER+code+'\n'+impl+main,encoding='utf-8')
 gcc=shutil.which('gcc');assert gcc;build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),str(out/'tad_abb.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;(out/'stdout.txt').write_text(run.stdout,encoding='utf-8');events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')]
 report={'cases':CASES,'expected':expected,'events':events,'canonical_helper':helper,'caller':caller,'limits':['Native fixture storage is automatic; validator borrows nodes and never changes storage ownership.','Forged invalid fixtures test ordering without adding a UI insertion mode.','Finite acyclic trees and signed-int keys only; no cyclic/malformed ownership claims.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

@pytest.mark.parametrize('case',range(len(CASES)))
def test_abb_validation_each_native_instruction_and_unchanged_tree(abb_validate_native,case):
 trace,state,valid=trace_for(case);events=[e for e in abb_validate_native['events'] if e['case']==case];assert len(trace['steps'])==len(events)
 for step,e in zip(trace['steps'],events):
  p=step['pedagogy'];st=p['memory_state'];assert step['line_text'].strip()==e['text'] and p['instruction_event']['phase']==e['phase']
  if e['source_index']>=0:assert step['line_index']==e['source_index']
  assert [{'id':f['id'],'depth':f['depth'],'parameters':f['parameters'],'locals':f['locals']} for f in st['tree_frames']]==e['frames'];assert st['heap_nodes']==e['nodes'];assert st['root']==state['root'];assert bool(st['caller_frame'])==bool(e['caller_live']);assert st['console_stdout']==''
  assert st['wrapper_result']==(int(valid) if e['phase']=='caller_result' else None);assert st['validation']==(valid if e['phase']=='caller_result' else None)
  if e['condition']!=-2:assert step['condition_result']==bool(e['condition'])
  if e['result']!=-2:assert p['instruction_event']['return']==e['result']
  assert p['memory']['objects_before']==p['memory']['objects_after'] and not p['memory']['allocated_objects'] and not p['memory']['freed_objects']
 assert trace['steps'][-1]['state_after']==state

@pytest.mark.parametrize('seed',[[],[MIN],[MAX],[0,MIN,MAX]])
def test_abb_validations_persist_and_reload_does_not_reexecute(seed,monkeypatch):
 client=create_app().test_client()
 for value in seed:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 for i in range(3):
  d=client.post('/hierarchical/abb/operate',json={'operation':'validar','payload':{}}).json;assert d['success'] and d['result'] is True;assert len([h for h in d['history'] if h['operation']=='validar'])==i+1
 # to_visual_state also evaluates structure metadata; distinguish actual execute from metadata via replay path.
 from app.services.hierarchical_structure_service import HierarchicalStructureService
 from app.adapters.abb_adapter import ABBAdapter
 original_execute=ABBAdapter.execute;executed=[]
 def execute(self,name,payload):executed.append(name);return original_execute(self,name,payload)
 monkeypatch.setattr(ABBAdapter,'execute',execute);a,history=HierarchicalStructureService._rebuild_adapter('abb',d['history']);assert 'validar' not in executed;assert len(history)==len(seed)+3

def test_abb_optional_bounds_extreme_dummy_values_and_equality(tmp_path):
 client=create_app().test_client();helper=CCodeService.get_structure_data('abb')['operations']['validar']
 for kind,suffix in [('source','c'),('header','h')]:
  (tmp_path/('tad_abb.'+suffix)).write_bytes(client.get('/help/source/abb/'+kind).data)
 program='#include <assert.h>\n#include <stddef.h>\n#include <limits.h>\n#include "tad_abb.h"\n'+helper+'''\nint main(void){ABBNodo n={INT_MIN,NULL,NULL};
 assert(abb_validar_rango(&n,0,INT_MAX,0,INT_MIN)==1);
 assert(abb_validar_rango(&n,1,INT_MIN,0,0)==0);
 n.valor=INT_MAX;assert(abb_validar_rango(&n,0,INT_MAX,0,INT_MIN)==1);
 assert(abb_validar_rango(&n,0,0,1,INT_MAX)==0);
 assert(abb_validar_rango(NULL,1,INT_MAX,1,INT_MIN)==1);
 n.valor=0;assert(abb_validar_rango(&n,1,INT_MIN,1,INT_MAX)==1);
 assert(abb_validar_rango(&n,1,0,1,INT_MAX)==0);
 assert(abb_validar_rango(&n,1,INT_MIN,1,0)==0);
 assert(n.valor==0&&n.izquierdo==NULL&&n.derecho==NULL);return 0;}'''
 (tmp_path/'main.c').write_text(program,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 run=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'main.c'),str(tmp_path/'tad_abb.c'),'-o',str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(tmp_path/'main.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr
