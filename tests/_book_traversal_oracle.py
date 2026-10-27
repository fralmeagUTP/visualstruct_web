"""Native endpoint/ownership evidence and canonical recorded traversal traces.

Native observations below are final order/status/marks and allocation counts;
they do not claim per-statement native event parity with the retired observer.
"""
from pathlib import Path
from copy import deepcopy
import hashlib,json,shutil,subprocess
from app import create_app
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph.book_c_subset import BookSession
from app.domain.graph.book_application import _publish_storage
from app.domain.graph.book_trace import build_book_trace
from _audit_graph_bfs_native_observer import CASES

TRACK=r'''
#include <assert.h>
#include <stdlib.h>
#include <stddef.h>
static long live, allocated, released;
void *traversal_malloc(size_t n){void *p=malloc(n);if(p){live++;allocated++;}return p;}
void *traversal_calloc(size_t n,size_t s){void *p=calloc(n,s);if(p){live++;allocated++;}return p;}
void traversal_free(void *p){if(p){assert(live>0);live--;released++;}free(p);}
long traversal_live(void){return live;}
long traversal_allocated(void){return allocated;}
long traversal_released(void){return released;}
'''

def native_cases(algorithm,out,*,initial_mark=0):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    client=create_app().test_client();hashes={}
    for kind,ext in [('source','c'),('header','h')]:
        response=client.get('/help/source/graph/'+kind);assert response.status_code==200
        (out/('tad_grafo.'+ext)).write_bytes(response.data)
        hashes[ext]=hashlib.sha256(response.data).hexdigest()
    source='''#include "tad_grafo.h"
#include <assert.h>
#include <stdio.h>
long traversal_live(void);long traversal_allocated(void);long traversal_released(void);
int main(void){
'''
    for case,record in enumerate(CASES):
        source+='{Grafo g=grafo_crear();GrafoEstado status;'
        for vertex in record['vertices']:source+=f'g=grafo_insertar_vertice(g,{vertex},&status);assert(status==GRAFO_OK);'
        for origin,target in record['edges']:source+=f'g=grafo_insertar_arco(g,{origin},{target},1,&status);assert(status==GRAFO_OK);'
        source+=f'for(ListaVertice v=g.v;v;v=v->sig)v->marcado={initial_mark};'
        for run in range(record.get('repeat',1)):
            source+='{'+'long base=traversal_live(),a=traversal_allocated(),f=traversal_released();'
            source+=f'ListaVertice result=grafo_{algorithm}(g,{record["start"]},&status);'
            source+=f'printf("ROW {case} {run} {{\\"status\\":%d,\\"order\\":[",(int)status);'
            source+='int first=1;for(ListaVertice p=result;p;p=p->sig){printf("%s%d",first?"":",",p->dato);first=0;assert(p->marcado==0);}'
            source+='printf("],\\"marks\\":[");first=1;for(ListaVertice p=g.v;p;p=p->sig){printf("%s[%d,%d]",first?"":",",p->dato,p->marcado);first=0;}'
            source+='printf("],\\"allocations\\":%ld,\\"frees_before_release\\":%ld",traversal_allocated()-a,traversal_released()-f);'
            source+='grafo_liberar_vertices(&result);assert(result==NULL&&traversal_live()==base);'
            source+='printf(",\\"frees_after_release\\":%ld,\\"owned_live\\":0}\\n",traversal_released()-f);}'
        source+='grafo_destruir(&g);assert(g.v==NULL&&g.a==NULL&&traversal_live()==0);}\n'
    source+='return 0;}\n';(out/'main.c').write_text(source,encoding='utf-8');(out/'track.c').write_text(TRACK,encoding='utf-8')
    compiler=shutil.which('gcc');assert compiler
    common=[compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(out)]
    obj=out/'graph.o';exe=out/'native.exe'
    commands=[common+['-Dmalloc=traversal_malloc','-Dcalloc=traversal_calloc','-Dfree=traversal_free','-c',str(out/'tad_grafo.c'),'-o',str(obj)],common+[str(out/'main.c'),str(out/'track.c'),str(obj),'-o',str(exe)]]
    for command in commands:
        result=subprocess.run(command,capture_output=True,text=True,timeout=45);assert result.returncode==0,result.stderr
    result=subprocess.run([str(exe)],capture_output=True,text=True,timeout=20);assert result.returncode==0,result.stderr
    (out/'native.stdout').write_text(result.stdout,encoding='utf-8')
    rows={}
    for line in result.stdout.splitlines():
        if line.startswith('ROW '):
            _,case,run,data=line.split(' ',3);rows[int(case),int(run)]=json.loads(data)
    assert len(rows)==sum(record.get('repeat',1) for record in CASES)
    return {'rows':rows,'hashes':hashes,'source':(out/'tad_grafo.c').read_text(encoding='utf-8')}

def recorded_call(algorithm,case,marks=None):
    vertices=case['vertices'];arcs=[(a,b,1) for a,b in case['edges']]
    session=BookSession(vertices,arcs,marks,trace=True)
    adapter=GraphAdapter();_publish_storage(adapter,session.graph_state(),True);before=adapter.to_visual_state()
    result=session.call('grafo_'+algorithm,[case['start']])
    _publish_storage(adapter,result['graph_after'],True);after=adapter.to_visual_state()
    trace=build_book_trace(operation_name='run_'+algorithm,payload={'start':case['start']},before_state=before,after_state=after,execution={'source_code':session.source,'transitions':result['transitions']},success=result['status']==0,message=result['status_name'])
    return result,trace

def compare_native(result,native):
    assert result['status']==native['status']
    assert result['result_items']==native['order']
    assert result['graph_after']['marks']==dict(native['marks'])
    assert result['memory']['allocations']==native['allocations']
    assert result['memory']['frees']==native['frees_before_release']
    assert native['allocations']==native['frees_after_release'] and native['owned_live']==0

def assert_recorded_instruction_contract(result,trace):
    from _book_frame_oracle import assert_book_frame
    assert len(trace['steps'])==len(result['transitions'])+1
    for index,step in enumerate(trace['steps']):assert_book_frame(step,trace,index)
    assert result['memory']['frames']==[]
