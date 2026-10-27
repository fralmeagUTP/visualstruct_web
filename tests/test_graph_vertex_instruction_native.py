"""The original finite vertex cases against unchanged canonical native C.

Native output/status/state are independent observations. Model instruction
coordinates and temporal memory are checked separately, without claiming that
the retired native statement instrumentation still describes the new C body.
"""
from copy import deepcopy
from pathlib import Path
import json, shutil, subprocess
import pytest
from app.domain.graph.book_c_subset import BookSession
from app.domain.graph.book_trace import build_book_trace
from _book_frame_oracle import assert_book_body

CASES = [
    ('insert_vertex', [], 7, False),
    ('insert_vertex', [1, 2, 3], 4, False),
    ('insert_vertex', [1, 2, 3], 3, False),
    ('insert_vertex', [1, 2, 3], 2, False),
    ('insert_vertex', [1, 2, 3], 1, False),
    ('insert_vertex', [], -2147483648, False),
    ('insert_vertex', [1], 2147483647, False),
    ('insert_vertex', [], 7, True),
    ('insert_vertex', [1, 2], 7, True),
    ('remove_vertex', [], 7, False),
    ('remove_vertex', [7], 7, False),
    ('remove_vertex', [1, 2, 3], 3, False),
    ('remove_vertex', [1, 2, 3], 2, False),
    ('remove_vertex', [1, 2, 3], 1, False),
    ('remove_vertex', [1, 2, 3], 9, False),
]
ROOT = Path(__file__).resolve().parents[1]

def state(vertices, arcs=()):
    return dict(structure='graph', directed=True, weighted=any(w!=1 for _,_,w in arcs),
                nodes=[dict(id=str(v),label=str(v),value=str(v),marked=0) for v in vertices],
                edges=[dict(source=str(a),target=str(b),weight=w) for a,b,w in arcs],
                metadata=dict(vertices_count=len(vertices),edges_count=len(arcs),is_empty=not vertices),
                last_result=None,last_operation=None)

@pytest.mark.parametrize('operation,vertices,x,fail', CASES)
def test_native_vertex_events_and_live_graph(tmp_path, operation, vertices, x, fail):
    gcc = shutil.which('gcc')
    assert gcc, 'Installed GCC is required for the native vertex contract'
    arcs=[(1,2,5)] if operation=='remove_vertex' and len(vertices)==3 else []
    function='grafo_insertar_vertice' if operation=='insert_vertex' else 'grafo_eliminar_vertice'
    session=BookSession(vertices,arcs,trace=True,fail_allocation=1 if fail else None)
    result=session.call(function,[x])
    before=state(vertices,arcs)
    after=state(list(reversed(result['graph_after']['vertices'])),list(reversed(result['graph_after']['arcs'])))
    trace=build_book_trace(operation_name=operation,payload={'vertex':x},before_state=before,
                          after_state=after,execution={'source_code':session.source,'transitions':result['transitions']},
                          success=result['status'] in (None,0),message='native vertex case')
    assert_book_body({'execution_trace':trace,'visual_state':after})
    driver='''#include "tad_grafo.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
static int fail_alloc;static long live;
void *vertex_test_malloc(size_t n){if(fail_alloc)return NULL;void*p=malloc(n);if(p)live++;return p;}
void vertex_test_free(void*p){if(p)live--;free(p);}
int main(void){Grafo g=grafo_crear();GrafoEstado status=GRAFO_OK;
'''
    for v in vertices:driver+=f'g=grafo_insertar_vertice(g,{v},&status);assert(status==GRAFO_OK);\n'
    for a,b,w in arcs:driver+=f'g=grafo_insertar_arco(g,{a},{b},{w},&status);assert(status==GRAFO_OK);\n'
    driver+=f'fail_alloc={int(fail)};status=(GrafoEstado)-1;g={function}(g,{x}'+(',&status' if operation=='insert_vertex' else '')+');\n'
    driver+='''printf("{\\"status\\":%d,\\"vertices\\":[",(int)status);int first=1;
for(ListaVertice v=g.v;v;v=v->sig){printf("%s%d",first?"":",",v->dato);first=0;}
printf("],\\"arcs\\":[");first=1;
for(ListaArco a=g.a;a;a=a->sig){printf("%s[%d,%d,%d]",first?"":",",a->origen,a->destino,a->costo);first=0;}
puts("]}");fail_alloc=0;grafo_destruir(&g);assert(live==0);return 0;}
'''
    (tmp_path/'driver.c').write_text(driver,encoding='utf-8')
    flags=[gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(ROOT/'docs/tads_C')]
    commands=[[*flags,'-Dmalloc=vertex_test_malloc','-Dfree=vertex_test_free','-c',str(ROOT/'docs/tads_C/tad_grafo.c'),'-o',str(tmp_path/'graph.o')],
              [*flags,str(tmp_path/'driver.c'),str(tmp_path/'graph.o'),'-o',str(tmp_path/'native.exe')]]
    for command in commands:
        compiled=subprocess.run(command,text=True,capture_output=True,timeout=30)
        assert compiled.returncode==0,compiled.stderr
    native=subprocess.run([str(tmp_path/'native.exe')],text=True,capture_output=True,timeout=10)
    assert native.returncode==0,native.stderr
    observed=json.loads(native.stdout)
    assert observed['status']==(-1 if result['status'] is None else result['status'])
    assert observed['vertices']==result['graph_after']['vertices']
    assert observed['arcs']==result['graph_after']['arcs']
    if fail:
        assert result['status']==1 and result['graph_after']['vertices']==list(reversed(vertices))
        assert result['memory']['allocations']==result['memory']['frees']
    (tmp_path/'report.json').write_text(json.dumps({'case':[operation,vertices,x,fail],
        'native':observed,'model_graph':result['graph_after'],'model_status':result['status'],
        'native_endpoint_parity':True,'model_event_positions_checked':True},indent=2),encoding='utf-8')
