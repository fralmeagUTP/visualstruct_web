"""Independent downloaded-C AVL prefix invariants and allocation identities."""
from pathlib import Path
import json,subprocess,shutil
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from app.adapters.avl_adapter import AVLAdapter
SOURCE=r'''
#include "tad_avl.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
static AVL ids[1024];static int live[1024],count,case_id,prefix,fail_malloc;
static char console[8192];static int used;
void *audit_malloc(size_t n){if(fail_malloc){fail_malloc=0;return NULL;}void*p=malloc(n);if(p){ids[count]=p;live[count++]=1;}return p;}
static int identity(AVL p){if(!p)return 0;for(int i=0;i<count;i++)if(live[i]&&ids[i]==p)return i+1;return -1;}
void audit_free(void*p){int id=identity(p);if(id>0)live[id-1]=0;free(p);}
int audit_printf(const char*fmt,...){va_list a;va_start(a,fmt);int n=vsnprintf(console+used,sizeof(console)-(size_t)used,fmt,a);va_end(a);used+=n;return n;}
'''
TAIL=r'''
static void emit(AVL root,int result,int invoked){
 printf("AUDIT {\"case\":%d,\"prefix\":%d,\"root\":%d,\"result\":%d,\"invoked\":%d,\"created\":%d,\"nodes\":[",case_id,prefix,identity(root),result,invoked,count);
 int printed=0;for(int i=0;i<count;i++)if(live[i]){AVL n=ids[i];if(printed++)printf(",");printf("{\"id\":%d,\"value\":%d,\"fe\":%d,\"left\":%d,\"right\":%d,\"parent\":%d}",i+1,n->nro,n->FE,identity(n->izq),identity(n->der),identity(n->padre));}
 printf("],\"freed_ids\":[");printed=0;for(int i=0;i<count;i++)if(!live[i])printf("%s%d",printed++?",":"",i+1);
 printf("],\"console_hex\":\"");for(int i=0;i<used;i++)printf("%02x",(unsigned char)console[i]);printf("\"}\n");
}
int main(void){int total,n,v;char op;AVL root=NULL;if(scanf("%d",&total)!=1)return 2;
 for(case_id=0;case_id<total;case_id++){if(scanf("%d",&n)!=1)return 3;root=NULL;count=used=0;prefix=0;emit(root,0,1);
  for(prefix=1;prefix<=n;prefix++){if(scanf(" %c %d",&op,&v)!=2)return 4;used=0;int result=0,invoked=1;
   switch(op){case'I':avl_insertar(&root,v);break;case'D':avl_eliminar(&root,v);break;case'B':result=avl_buscar(root,v)!=NULL;break;case'N':if(root)result=avl_minimo(root)->nro;else invoked=0;break;case'X':if(root)result=avl_maximo(root)->nro;else invoked=0;break;case'H':result=avl_altura(root);break;case'O':avl_inorden(root);break;case'V':result=avl_validar_fes(root);break;case'C':avl_liberarAVL(root);root=NULL;break;case'F':fail_malloc=1;avl_insertar(&root,v);break;case'G':avl_insertar(NULL,v);avl_eliminar(NULL,v);avl_RSD(NULL,root);avl_RSI(NULL,root);avl_RDD(NULL,root);avl_RDI(NULL,root);avl_RSD(&root,NULL);avl_RSI(&root,NULL);avl_RDD(&root,NULL);avl_RDI(&root,NULL);if(!root||(!root->izq&&!root->der)){avl_RSD(&root,root);avl_RSI(&root,root);avl_RDD(&root,root);avl_RDI(&root,root);}break;default:return 5;}
   emit(root,result,invoked);
  }avl_liberarAVL(root);root=NULL;
 }return 0;
}
'''
OPS={'insertar':'I','eliminar':'D','buscar':'B','minimo':'N','maximo':'X','altura':'H','inorden':'O','validar':'V','limpiar':'C'}

def invariant(event):
 nodes={n['id']:n for n in event['nodes']};seen=set();errors=[]
 def rec(i,parent=0,lo=None,hi=None):
  if not i:return None,0
  if i not in nodes or i in seen:errors.append({'kind':'cycle_or_invalid_pointer','id':i});return None,0
  seen.add(i);n=nodes[i]
  if n['parent']!=parent:errors.append({'kind':'parent','id':i})
  if (lo is not None and n['value']<=lo) or (hi is not None and n['value']>=hi):errors.append({'kind':'order','id':i})
  left,lh=rec(n['left'],i,lo,n['value']);right,rh=rec(n['right'],i,n['value'],hi);fe=rh-lh
  if fe!=n['fe']:errors.append({'kind':'stored_fe','id':i,'value':n['value'],'stored':n['fe'],'calculated':fe})
  if abs(fe)>1:errors.append({'kind':'unbalanced','id':i,'value':n['value'],'calculated':fe})
  return {'value':n['value'],'left':left,'right':right,'height':1+max(lh,rh),'balance_factor':n['fe']},1+max(lh,rh)
 tree,_=rec(event['root'])
 if seen!=set(nodes):errors.append({'kind':'unreachable_live','ids':sorted(set(nodes)-seen)})
 return errors,tree

from scripts.published_test_inputs import audit_input_path
def build_probe(out):
 out.mkdir(exist_ok=True);client=create_app().test_client()
 for kind,suffix in [('source','c'),('header','h')]:
  raw=client.get('/help/source/avl/'+kind).data;assert raw==(audit_input_path(Path(__file__).resolve().parents[1]/'docs/tads_C'/('tad_avl.'+suffix))).read_bytes();(out/('tad_avl.'+suffix)).write_bytes(raw)
 ops=CCodeService.get_structure_data('avl')['operations'];helper=SOURCE+'\n#define printf audit_printf\n'+''.join(ops[op]+'\n' for op in ['maximo','inorden','validar'])+'\n#undef printf\n'+TAIL
 (out/'oracle.c').write_text(helper,encoding='utf-8');gcc=shutil.which('gcc');assert gcc;flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
 for cmd in [[gcc,*flags,'-Dmalloc=audit_malloc','-Dfree=audit_free','-Dprintf=audit_printf','-c',str(out/'tad_avl.c'),'-o',str(out/'tad.o')],[gcc,*flags,str(out/'oracle.c'),str(out/'tad.o'),'-o',str(out/'oracle.exe')]]:
  run=subprocess.run(cmd,capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 return out/'oracle.exe'

def run_probe(exe,tapes):
 data=str(len(tapes))+'\n'+''.join(str(len(tape))+'\n'+''.join(f'{op} {v}\n' for op,v in tape) for tape in tapes)
 run=subprocess.run([str(exe)],input=data,capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 return [json.loads(line[6:]) for line in run.stdout.splitlines() if line.startswith('AUDIT ')]

@pytest.fixture(scope='module')
def avl_repair_review(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-rotation-repair');exe=build_probe(out);repo=Path(__file__).resolve().parents[1]
 baseline=json.loads((audit_input_path(repo/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-avl-native-documentation-baseline-low/avl-native-baseline-low/endpoint-review.json')).read_text(encoding='utf-8'))['cases'];assert len(baseline)==77
 tapes=[[('I',v) for v in c['seed']]+[(OPS[c['operation']],c['payload'].get('value',0))] for c in baseline]
 # Insert/delete representative prefixes, including all four root/interior rotations and full drains.
 for seed in [[30,20,10],[10,20,30],[30,10,20],[10,30,20],[50,30,70,20,40,60,80,35,37],list(range(-12,13)),list(range(12,-13,-1)),[-2147483648,0,2147483647,-1,1]]:
  tapes.append([('I',v) for v in seed]+[('D',v) for v in seed]+[('D',99),('I',7),('I',7),('C',0)])
 for seed in [[1,2,3,4,6,0,8,7,5],[1,3,0,5,4,2,6],[4,0,1,2,5,3],[5,1,2,3,6,4,0]]:
  tapes.append([('I',v) for v in seed]+[('D',v) for v in seed]+[('C',0)])
 events=run_probe(exe,tapes);rows=[];previous={}
 for event in events:
  tape=tapes[event['case']][:event['prefix']];expected=set()
  for op,v in tape:
   if op=='I':expected.add(v)
   elif op=='D':expected.discard(v)
   elif op=='C':expected.clear()
  errors,tree=invariant(event);values={n['value'] for n in event['nodes']};assert values==expected and len(values)==len(event['nodes'])
  if event['prefix']:
   before=previous[event['case']];old={n['id']:n for n in before['nodes']};now={n['id']:n for n in event['nodes']};op,v=tape[-1]
   if op=='I':
    added=v not in {n['value'] for n in old.values()};assert set(old).issubset(now) and len(set(now)-set(old))==int(added);assert event['created']==before['created']+int(added) and event['freed_ids']==before['freed_ids']
   elif op=='D':
    victim=next((n['id'] for n in old.values() if n['value']==v),None)
    if victim and old[victim]['left'] and old[victim]['right']:
     victim=old[victim]['right']
     while old[victim]['left']:victim=old[victim]['left']
    assert set(old)-set(now)==({victim} if victim else set()) and not set(now)-set(old);assert event['created']==before['created']
   elif op=='C':assert not now and set(event['freed_ids'])==set(range(1,event['created']+1))
   else:assert event['nodes']==before['nodes'] and event['root']==before['root'] and event['created']==before['created'] and event['freed_ids']==before['freed_ids']
  previous[event['case']]=event
  rows.append({'event':event,'errors':errors,'tree':tree})
 report={'cases':baseline,'tapes':tapes,'rows':rows,'limits':['Native whole-operation/prefix invariants only, not instruction/UI closure.','Allocator identities observed only while alive; integer freed IDs retained without reading freed storage.','Recorded finite signed-int cases, not all paths or sanitizers.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

@pytest.mark.parametrize('case',range(89))
def test_avl_actual_downloaded_prefix_invariants(avl_repair_review,case):
 rows=[r for r in avl_repair_review['rows'] if r['event']['case']==case];assert rows
 for row in rows:assert not row['errors'],(case,row['event']['prefix'],row['errors'])

@pytest.mark.parametrize('case',range(77))
def test_avl_native_endpoint_contract_and_backend_comparison(avl_repair_review,case):
 meta=avl_repair_review['cases'][case];a=AVLAdapter()
 for value in meta['seed']:a.execute('insertar',{'value':value})
 try:actual=a.execute(meta['operation'],meta['payload']);success=True
 except ValueError:actual={};success=False
 except Exception as e:
  from app.domain.hierarchical.exceptions import TADError
  assert isinstance(e,TADError);actual={};success=False
 last=[r for r in avl_repair_review['rows'] if r['event']['case']==case][-1];native=last['event'];state=a.to_visual_state();assert state['root']==last['tree']
 if success and meta['operation'] in ['buscar','minimo','maximo','altura','validar']:assert actual.get('result')==native['result']
 if success and meta['operation']=='inorden':assert actual.get('result')==[int(v) for v in bytes.fromhex(native['console_hex']).decode().split()]

def leaf(v):return (v,None,None)
DIRECT=[('avl_RSD',(30,(20,leaf(10),None),None)),('avl_RSI',(10,None,(20,None,leaf(30)))),('avl_RSD',(30,(20,leaf(10),leaf(25)),None)),('avl_RSI',(20,None,(30,leaf(25),leaf(40))))]
for c in [(30,leaf(25),None),(30,leaf(25),leaf(35)),(30,None,leaf(35))]:
 DIRECT.extend([('avl_RDD',(40,(20,leaf(10),c),leaf(50))),('avl_RDI',(20,leaf(10),(40,c,leaf(50))))])

@pytest.fixture(scope='module')
def avl_direct_rotation_review(tmp_path_factory):
 out=tmp_path_factory.mktemp('avl-direct-rotations');exe=build_probe(out);gcc=shutil.which('gcc');flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror'];main='\nint main(void){AVL root,p[32];';expected=[]
 def height(t):return 0 if t is None else 1+max(height(t[1]),height(t[2]))
 for case in range(20):
  name,target=DIRECT[case//2];interior=bool(case%2);h=height(target)-(0 if case//2 in [2,3] else 1)
  right=leaf(150) if h<=2 else (150,leaf(125),leaf(175));whole=(100,target,right) if interior else target;items=[]
  def load(t,parent=None):
   if t is None:return None
   i=len(items);items.append({'value':t[0],'parent':parent,'fe':height(t[2])-height(t[1])});items[i]['left']=load(t[1],i);items[i]['right']=load(t[2],i);return i
  load(whole);a=items[0]['left'] if interior else 0;b=items[a]['left'] if name in ['avl_RSD','avl_RDD'] else items[a]['right'];new=b
  if name=='avl_RDD':new=items[b]['right']
  if name=='avl_RDI':new=items[b]['left']
  expected.append({'case':case,'function':name,'interior':interior,'new_subtree_root_id':new+1,'nodes':len(items)})
  main+=f'case_id={case};count=used=0;prefix=0;'
  for i in range(len(items)):main+=f'p[{i}]=audit_malloc(sizeof *p[{i}]);if(!p[{i}])return 2;'
  for i,n in enumerate(items):
   def ptr(j):return 'NULL' if j is None else f'p[{j}]'
   main+=f'p[{i}]->nro={n["value"]};p[{i}]->FE={n["fe"]};p[{i}]->izq={ptr(n["left"])};p[{i}]->der={ptr(n["right"])};p[{i}]->padre={ptr(n["parent"])};'
  main+=f'root=p[0];emit(root,0,1);{name}(&root,p[{a}]);prefix=1;emit(root,0,1);'
  # Direct helpers update rotated nodes, not ancestor factors; this is an explicit caller instruction.
  if interior:main+='root->FE=avl_altura(root->der)-avl_altura(root->izq);'
  main+='prefix=2;emit(root,0,1);avl_liberarAVL(root);root=NULL;'
 main+='return 0;}'
 (out/'direct.c').write_text(SOURCE+TAIL.split('int main(void)')[0]+main,encoding='utf-8');run=subprocess.run([gcc,*flags,str(out/'direct.c'),str(out/'tad.o'),'-o',str(out/'direct.exe')],capture_output=True,text=True,timeout=30);assert run.returncode==0,run.stderr
 run=subprocess.run([str(out/'direct.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0,run.stderr;events=[json.loads(l[6:]) for l in run.stdout.splitlines() if l.startswith('AUDIT ')];report={'cases':expected,'events':events,'limits':['Direct interior helper does not update ancestor FE; an explicit caller height assignment follows, separately recorded.','Native endpoint rotation proof, not partial-link instruction/UI evidence.']};(out/'review.json').write_text(json.dumps(report,indent=2),encoding='utf-8');return report

@pytest.mark.parametrize('case',range(20))
def test_direct_avl_rotation_factors_identity_parent_and_caller(avl_direct_rotation_review,case):
 meta=avl_direct_rotation_review['cases'][case];before,after,completed=[e for e in avl_direct_rotation_review['events'] if e['case']==case]
 assert before['created']==after['created']==completed['created']==meta['nodes'];assert not before['freed_ids'] and not after['freed_ids'] and not completed['freed_ids'];assert {n['id'] for n in before['nodes']}=={n['id'] for n in after['nodes']}
 assert {n['id']:n['value'] for n in before['nodes']}=={n['id']:n['value'] for n in after['nodes']}
 expected_root=1 if meta['interior'] else meta['new_subtree_root_id'];assert after['root']==expected_root
 if meta['interior']:
  parent=next(n for n in after['nodes'] if n['id']==1);assert parent['left']==meta['new_subtree_root_id'];assert parent['fe']==before['nodes'][0]['fe']
  assert not [e for e in invariant(after)[0] if not(e['kind']=='stored_fe' and e['id']==1)]
 else:assert not invariant(after)[0]
 assert not invariant(completed)[0]

def test_avl_raw_null_missing_child_and_malloc_failure_preserve_contract(tmp_path):
 exe=build_probe(tmp_path);events=run_probe(exe,[[('G',7),('F',7),('I',7),('G',8),('F',8)]])
 for a,b in [(events[0],events[1]),(events[1],events[2]),(events[3],events[4]),(events[4],events[5])]:
  assert a['nodes']==b['nodes'] and a['root']==b['root'] and a['created']==b['created'] and a['freed_ids']==b['freed_ids']
