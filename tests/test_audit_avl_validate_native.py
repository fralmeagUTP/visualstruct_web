"""Independent canonical validator and actual downloaded-height instruction oracle."""
from pathlib import Path
import json,re,subprocess,shutil
import pytest
from app import create_app
from app.adapters.avl_adapter import AVLAdapter
from app.domain.hierarchical.tad_avl import nodoAVL
from app.services.c_code_service import CCodeService
CASES=[{'seed':s} for s in [[],[7],[30,20,10],[10,20,30],[30,10,20],[10,30,20],[50,30,70,20,40,60,80,35,37],[0,-2147483648,2147483647]]]+[{'tree':t} for t in [(3,(2,(1,None,None),None),None),(3,(4,None,None),None),(10,(5,(3,(1,None,None),None),None),(20,None,None)),(10,(5,None,None),(20,None,(30,None,(40,None,None))))]]
CASES += [{'tree':(10,(5,(3,(1,None,None),None),None),(20,(15,None,None),None))},{'tree':(10,(5,(3,None,None),None),(20,None,(30,None,(40,None,None))))}]
def fixture(case):
 a=AVLAdapter();meta=CASES[case]
 if 'seed' in meta:
  for v in meta['seed']:a.execute('insertar',{'value':v})
 else:
  def load(t,parent=None):
   if t is None:return None
   n=nodoAVL(t[0],padre=parent);n.izq=load(t[1],n);n.der=load(t[2],n)
   def h(q):return 0 if q is None else 1+max(h(q.izq),h(q.der))
   n.FE=h(n.der)-h(n.izq);return n
  a._structure._raiz=load(meta['tree']);a._structure._tamano=len(values(a.to_visual_state()['root']))
 return a
def values(n):return [] if n is None else [n['value'],*values(n['left']),*values(n['right'])]
def trace_for(case):
 from app.domain.hierarchical.avl_validate_instruction import build_avl_validate_trace
 a=fixture(case);state=a.to_visual_state();helper=CCodeService.get_structure_data('avl')['operations']['validar'];trace=build_avl_validate_trace({'source_code':helper,'payload':{},'success':True},state,state);return trace,state,a.execute('validar',{})['result']
PRE=r'''
#include <stdio.h>
#include "tad_avl.h"
typedef struct {int id,kind,node,flags[2],v[2];} Frame;
static Frame frames[256];static int depth,serial,case_id,count,caller_live,caller_result=-2;static AVL nodes[256];
static int ident(AVL p){if(!p)return 0;for(int i=0;i<count;i++)if(nodes[i]==p)return i+1;return -1;}
static void enter(int kind,AVL node){frames[depth++]=(Frame){.id=++serial,.kind=kind,.node=ident(node)};}
static void event(int line,const char*phase,int value){
 printf("AUDIT {\"case\":%d,\"source_index\":%d,\"phase\":\"%s\",\"value\":%d,\"caller_live\":%d,\"caller_result\":%d,\"frames\":[",case_id,line,phase,value,caller_live,caller_result);
 for(int i=0;i<depth;i++){Frame f=frames[i];printf("%s{\"id\":\"F%d\",\"function\":\"%s\",\"depth\":%d,\"parameters\":{\"%s\":\"",i?",":"",f.id,f.kind?"avl_altura":"avl_validar_fes",i,f.kind?"arbol":"nodo");if(f.node)printf("N%d",f.node);else printf("NULL");printf("\"},\"locals\":{");int printed=0;for(int k=0;k<(f.kind?2:1);k++)if(f.flags[k]){printf("%s\"%s\":",printed++?",":"",f.kind?(k?"altDer":"altIzq"):"fe");if(f.flags[k]==1)printf("\"sin inicializar\"");else printf("%d",f.v[k]);}printf("}}");}printf("],\"nodes\":[");for(int i=0;i<count;i++){AVL n=nodes[i];printf("%s{\"id\":\"N%d\",\"value\":%d,\"balance_factor\":%d,\"left\":%d,\"right\":%d,\"parent\":%d}",i?",":"",i+1,n->nro,n->FE,ident(n->izq),ident(n->der),ident(n->padre));}printf("]}\n");
}
static int condition(int line,int value){event(line,"condition",value);return value;}
'''
@pytest.fixture(scope='module')
def avl_validate_native(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-validate-native');client=create_app().test_client()
 for kind,suffix in [('source','c'),('header','h')]:
  raw=client.get('/help/source/avl/'+kind).data;assert raw==(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix)).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(raw)
 helper=CCodeService.get_structure_data('avl')['operations']['validar'];height=CCodeService.get_structure_data('avl')['operations']['altura'];source=trace_for(0)[0]['source_code'];lines=source.splitlines()
 def index(text,function,k=0):
  start=next(i for i,l in enumerate(lines) if l.strip().startswith('int '+function+'('));return [i for i in range(start,len(lines)) if lines[i].strip()==text][k]
 def log(text,phase,value='-2',function='avl_validar_fes',k=0):return f'event({index(text,function,k)},"{phase}",{value});'
 code=helper;sig='int avl_validar_fes(AVL nodo) {';code=code.replace(sig,sig+'enter(0,nodo);'+log(sig,'enter'))
 for t,expr in [('if (nodo == NULL) {','nodo==NULL'),('if (fe < -1 || fe > 1) {','fe < -1 || fe > 1')]:code=code.replace(t,f'if(condition({index(t,"avl_validar_fes")},{expr})){{')
 t='int fe = avl_altura(nodo->der) - avl_altura(nodo->izq);';code=code.replace(t,'frames[depth-1].flags[0]=1;'+log(t,'call')+'int audit_right=avl_altura(nodo->der);event('+str(index(t,'avl_validar_fes'))+',"call",-2);int audit_left=avl_altura(nodo->izq);int fe=audit_right-audit_left;frames[depth-1].flags[0]=2;frames[depth-1].v[0]=fe;'+log(t,'assignment','fe'))
 for side in ['izq','der']:
  t=f'if (!avl_validar_fes(nodo->{side})) {{';code=code.replace(t,log(t,'call')+f'if(condition({index(t,"avl_validar_fes")},!avl_validar_fes(nodo->{side}))){{')
 for v in [0,1]:
  t=f'return {v};';ks=iter(range(sum(l.strip()==t for l in helper.splitlines())));code=re.sub(re.escape(t),lambda m:'depth--;'+log(t,'return',str(v),k=next(ks))+t,code)
 sig='int avl_altura(AVL arbol) {';hcode=height.replace(sig,sig+'enter(1,arbol);'+log(sig,'enter',function='avl_altura'))
 t='if (arbol == NULL)';hcode=hcode.replace(t,f'if(condition({index(t,"avl_altura")},arbol==NULL))');hcode=hcode.replace('return 0;','{depth--;'+log('return 0;','return','0',function='avl_altura')+'return 0;}')
 for name,side,k in [('altIzq','izq',0),('altDer','der',1)]:
  t=f'int {name} = avl_altura(arbol->{side});';hcode=hcode.replace(t,f'frames[depth-1].flags[{k}]=1;'+log(t,'call',function='avl_altura')+t+f'frames[depth-1].flags[{k}]=2;frames[depth-1].v[{k}]={name};'+log(t,'assignment',function='avl_altura'))
 t='return (altIzq > altDer ? altIzq : altDer) + 1;';hcode=hcode.replace(t,f'int got=(condition({index(t,"avl_altura")},altIzq>altDer)?altIzq:altDer)+1;depth--;'+log(t,'return','got',function='avl_altura')+'return got;')
 caller='int ejecutar_equilibrio(AVL raiz) {\n    return avl_validar_fes(raiz);\n}'
 ccode=caller.replace('{','{caller_live=1;'+log(caller.splitlines()[0],'caller_enter',function='ejecutar_equilibrio'),1);t='return avl_validar_fes(raiz);';ccode=ccode.replace(t,log(t,'call',function='ejecutar_equilibrio')+'int got=avl_validar_fes(raiz);caller_live=0;caller_result=got;'+log(t,'caller_result','got',function='ejecutar_equilibrio')+'return got;')
 main='\nint main(void){nodoAVL store[128];';expected=[]
 for case in range(len(CASES)):
  state=fixture(case).to_visual_state();items=[]
  def load(n,parent=None):
   if n is None:return None
   i=len(items);items.append({'value':n['value'],'fe':n['balance_factor'],'parent':parent});items[i]['left']=load(n['left'],i);items[i]['right']=load(n['right'],i);return i
  root=load(state['root']);main+=f'case_id={case};count={len(items)};depth=serial=caller_live=0;caller_result=-2;'
  def ptr(i):return 'NULL' if i is None else f'&store[{i}]'
  for i,n in enumerate(items):main+=f'store[{i}]=(nodoAVL){{.nro={n["value"]},.FE={n["fe"]},.izq={ptr(n["left"])},.der={ptr(n["right"])},.padre={ptr(n["parent"])}}};nodes[{i}]=&store[{i}];'
  main+=f'(void)ejecutar_equilibrio({ptr(root)});';expected.append(state)
 main+='return 0;}'
 (out/'instrumented.c').write_text(PRE+code+'\n'+hcode+'\n'+ccode+main,encoding='utf-8');gcc=shutil.which('gcc');assert gcc
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'instrumented.c'),'-o',str(out/'oracle.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(out/'oracle.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')];(out/'stdout.txt').write_text(run.stdout,encoding='utf-8')
 # An untouched canonical-helper executable confirms that selecting a legal pure-operand order does not change results.
 rawmain=re.sub(r'case_id=\d+;count=\d+;depth=serial=caller_live=0;caller_result=-2;','',main)
 rawmain=re.sub(r'nodes\[\d+\]=&store\[\d+\];','',rawmain)
 rawmain=re.sub(r'\(void\)ejecutar_equilibrio\(([^;]+)\);',lambda m:'printf("%d\\n",avl_validar_fes('+m.group(1)+'));',rawmain)
 (out/'canonical-result.c').write_text('#include <stdio.h>\n#include "tad_avl.h"\n'+helper+rawmain,encoding='utf-8')
 build=subprocess.run([gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'canonical-result.c'),str(out/'tad_avl.c'),'-o',str(out/'canonical-result.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 rawrun=subprocess.run([str(out/'canonical-result.exe')],capture_output=True,text=True,timeout=10);assert rawrun.returncode==0
 assert [int(v) for v in rawrun.stdout.splitlines()]==[e['value'] for e in events if e['phase']=='caller_result'];(out/'canonical-stdout.txt').write_text(rawrun.stdout,encoding='utf-8')
 report={'cases':CASES,'events':events,'states':expected,'canonical_helper':helper,'canonical_height':height,'caller':caller,'limits':['Selected legal right-then-left subtraction evaluation for this pure height operation, not language-mandated ordering.','Automatic fixture storage, no allocation/free during operation; no malformed-pointer/cycle guarantee.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report
@pytest.mark.parametrize('case',range(len(CASES)))
def test_avl_validation_each_native_instruction(avl_validate_native,case):
 trace,state,backend=trace_for(case);events=[e for e in avl_validate_native['events'] if e['case']==case];assert len(trace['steps'])==len(events)
 for s,e in zip(trace['steps'],events):
  p=s['pedagogy'];st=p['memory_state'];assert s['line_index']==e['source_index'] and p['instruction_event']['phase']==e['phase'];assert st['tree_frames']==e['frames'];assert [{**{k:v for k,v in n.items() if k not in ['left','right','parent','status']},**{k:(0 if n[k]=='NULL' else int(n[k][1:])) for k in ['left','right','parent']}} for n in st['heap_nodes']]==e['nodes'];assert bool(st['caller_frame'])==bool(e['caller_live']);assert st['wrapper_result']==(None if e['caller_result']==-2 else e['caller_result']);assert st['root']==state['root'] and st['console_stdout']=='';assert st['validation'] is None and st['backend_validation']==backend
  assert p['memory']['objects_before']==p['memory']['objects_after'] and not p['memory']['allocated_objects'] and not p['memory']['freed_objects']
  if e['phase']=='condition':assert s['condition_result']==bool(e['value'])
  if e['phase'] in ['return','caller_result']:assert p['instruction_event']['return']==e['value']
 assert trace['steps'][-1]['state_after']==state
 assert events[-1]['value']==(1 if case<8 or case==9 else 0)
 if case==9:assert not backend and events[-1]['value']==1

@pytest.mark.parametrize('case,occurrence',[(12,1),(13,2)])
def test_avl_validator_propagates_false_child_and_shortcircuits(avl_validate_native,case,occurrence):
 trace,state,backend=trace_for(case);assert backend is False
 indices=[i for i,l in enumerate(trace['source_code'].splitlines()) if l.strip()=='return 0;']
 # Three validator return0 sites precede the public-height return0 site.
 events=[e for e in avl_validate_native['events'] if e['case']==case]
 assert any(e['phase']=='return' and e['source_index']==indices[occurrence] and e['value']==0 for e in events)
 root_return=next(e for e in reversed(events) if e['phase']=='return');assert root_return['source_index']==indices[occurrence]
 if case==12:
  rightcall=next(i for i,l in enumerate(trace['source_code'].splitlines()) if l.strip()=='if (!avl_validar_fes(nodo->der)) {')
  assert not any(e['phase']=='call' and e['source_index']==rightcall and len(e['frames'])==1 for e in events)
