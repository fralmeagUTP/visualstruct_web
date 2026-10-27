"""Finite query-only Cima oracle, private trace and rejected public API baseline."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,time,tracemalloc
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from app import create_app
from app.config import Config
from app.adapters.stack_adapter import StackAdapter
from app.services.structure_service import StructureService
from app.services.execution_trace_service import ExecutionTraceService
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-cima-baseline-low';N=E/'native';N.mkdir(exist_ok=True)
CASES=[('empty',[]),('single',[17]),('top',[9,17,3]),('duplicate',[7,7]),('minus1',[-1]),('minimum',[-2147483648]),('maximum',[2147483647]),('bounds',[-2147483648,0,2147483647])]
class Q(Config):
    TESTING=True
    SESSION_CACHE_DIR=str(E/'private-API-sessions')
app=create_app(Q);downloads=[]
for kind,ext in [('source','c'),('header','h')]:
    r=app.test_client().get('/help/source/stack/'+kind);assert r.status_code==200;data=r.data;assert data==(R/('docs/tads_C/tad_pila.'+ext)).read_bytes();(N/('tad_pila.'+ext)).write_bytes(data);downloads.append({'kind':kind,'HTTP':200,'SHA':hashlib.sha256(data).hexdigest()})
source=(N/'tad_pila.c').read_text(encoding='utf-8-sig');body='int pila_cima(ptrPila p) {\n    return p == NULL ? -1 : p->nro;\n}'
assert body in source
patched='int pila_cima(ptrPila p) {\n    qa_entry(p);\n    return qa_return(p, qa_condition(p, p == NULL) ? -1 : p->nro);\n}'
(N/'instrumented.c').write_text(source.replace(body,patched),encoding='utf-8')
(N/'hooks.h').write_text('#include <stddef.h>\nstruct NodoPila;\nvoid qa_entry(struct NodoPila*);\nint qa_condition(struct NodoPila*,int);\nint qa_return(struct NodoPila*,int);\n',encoding='utf-8')
driver=r"""#include <assert.h>
#include <stdio.h>
#include <limits.h>
#include "tad_pila.h"
_Static_assert(_Generic(&pila_cima,int(*)(ptrPila):1,default:0),"public Cima signature");
static int sample_id;
static void event(ptrPila p,const char*phase,int condition,int result,int written){
 _Static_assert(_Generic(p,ptrPila:1,default:0),"parameter ptrPila");
 printf("{\"sample\":%d,\"phase\":\"%s\",\"condition\":%d,\"result\":%d,\"result_written\":%d,\"root_NULL\":%d,\"items\":[",sample_id,phase,condition,result,written,p==NULL);
 int comma=0;for(ptrPila n=p;n!=NULL;n=n->sgte){if(comma++)putchar(',');printf("%d",n->nro);}puts("]}");
}
void qa_entry(ptrPila p){event(p,"entry",-1,0,0);}
int qa_condition(ptrPila p,int condition){event(p,"conditional",condition,0,0);return condition;}
int qa_return(ptrPila p,int value){event(p,"return",-1,value,1);return value;}
static void sample(ptrPila p){ptrPila root=p;ptrPila links[8];int values[8],count=0;for(ptrPila n=p;n;n=n->sgte){assert(count<8);links[count]=n->sgte;values[count++]=n->nro;}int expected=p==NULL?-1:p->nro;int value=pila_cima(p);assert(value==expected&&p==root);int i=0;for(ptrPila n=p;n;n=n->sgte){assert(n->sgte==links[i]&&n->nro==values[i]);i++;}assert(i==count);sample_id++;}
int main(void){
"""
for name,values in CASES:
    if not values:driver+='sample(NULL);sample(NULL);\n';continue
    driver+=' {struct NodoPila nodes['+str(len(values))+'];\n'
    for i,v in enumerate(values):
        val='INT_MIN' if v==-2147483648 else 'INT_MAX' if v==2147483647 else str(v);link='&nodes['+str(i+1)+']' if i+1<len(values) else 'NULL';driver+=f'nodes[{i}].nro={val};nodes[{i}].sgte={link};\n'
    driver+='sample(&nodes[0]);sample(&nodes[0]);}\n'
driver+='return 0;}\n';(N/'driver.c').write_text(driver,encoding='utf-8')
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
commands=[flags+['-include',str(N/'hooks.h'),'-c',str(N/'instrumented.c'),'-o',str(N/'pila.o')],flags+[str(N/'driver.c'),str(N/'pila.o'),'-o',str(N/'driver.exe')]]
for i,cmd in enumerate(commands):
    r=subprocess.run(cmd,capture_output=True,text=True);(N/f'compile-{i}.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
r=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(r.stdout,encoding='utf-8');(N/'stderr.log').write_text(r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr
native=[json.loads(x) for x in r.stdout.splitlines()];assert len(native)==48;rows=[];resources=[]
for index,(name,values) in enumerate(CASES):
    a=StackAdapter()
    for v in reversed(values):a.execute('apilar',{'value':v})
    visual=a.to_visual_state();ids=[];node=a._structure._tope_ref[0]
    while node:ids.append((id(node),id(node.sgte),node.nro));node=node.sgte
    outputs=[]
    for repeat in [1,2]:
        try:outputs.append({'result':a.execute('cima',{})['result']})
        except Exception as err:outputs.append({'exception':type(err).__name__})
        assert a.to_visual_state()==visual
    after=[];node=a._structure._tope_ref[0]
    while node:after.append((id(node),id(node.sgte),node.nro));node=node.sgte
    assert ids==after
    trace=ExecutionTraceService.build_trace(structure_id='stack',operation_name='cima',payload={},didactic_data=StructureService._didactic_content('stack'),before_state=visual,after_state=visual,success=bool(values),message='private adapter query',mutates=False,console_events=[])
    client=app.test_client()
    for v in reversed(values):assert client.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':v}}).get_json()['success']
    rejected=[]
    from unittest.mock import patch
    original=StackAdapter.execute;queries=[]
    def observe(self,op,payload):
        if op=='cima':queries.append(op)
        return original(self,op,payload)
    with patch.object(StackAdapter,'execute',observe):
        tracemalloc.start();start=time.perf_counter()
        for repeat in [1,2]:
            response=client.post('/sequential/stack/operate',json={'operation':'cima','payload':{}});d=response.get_json();assert response.status_code==400 and not d['success'];assert d['visual_state']==visual;rejected.append({'HTTP':response.status_code,'data':d})
        elapsed=time.perf_counter()-start;peak=tracemalloc.get_traced_memory()[1];tracemalloc.stop()
        assert client.get('/sequential/stack').status_code==200;assert client.get('/sequential/stack').status_code==200;assert len(queries)==0
    resources.append({'case':name,'two_rejected_POSTs_python_peak_bytes':peak,'last_response_bytes':len(response.data),'instrumented_seconds':elapsed})
    rows.append({'case':name,'items_top_to_bottom':values,'native':native[index*6:index*6+6],'native_result':native[index*6+2]['result'],'adapter_outputs':outputs,'readonly_identity_links_values':True,'visual':visual,'private_trace':trace,'rejected_public':rejected,'public_query_dispatches_POST_and_GET':len(queries),'journal_queries':sum(x['operation']=='cima' for x in rejected[-1]['data']['history']),'public_query_not_registered':not any(x['name']=='cima' for x in a.get_supported_operations())})
(E/'report.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'resources.json').write_text(json.dumps({'samples':resources,'max_peak_bytes':max(x['two_rejected_POSTs_python_peak_bytes'] for x in resources),'max_response_bytes':max(x['last_response_bytes'] for x in resources),'max_instrumented_seconds':max(x['instrumented_seconds'] for x in resources),'scope':'8 fixed cases, rejected unregistered API query including session replay/serialization, not successful query trace cost/RSS/browser/unboundedhistory/SLA/OOM'},indent=2)+'\n',encoding='utf-8');(E/'downloads.json').write_text(json.dumps(downloads,indent=2)+'\n',encoding='utf-8');print('native16querycalls48events16conditions, automatic initialized setup0malloc/free; API16reject400, POST+GET0querydispatch; private8traces')
