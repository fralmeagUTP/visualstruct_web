"""Finite vertex cases against the minimal public native C API.

Native output/state are checked against original C; status is observed privately
in a derivative whose graph outputs must match the original. Model instruction
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
from _graph_private_diagnostic_observer import instrument_private_diagnostics

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
#ifdef OBSERVED
extern int qa_status;
#else
int qa_status;
#endif
static int fail_alloc;static long live;
void *vertex_test_malloc(size_t n){if(fail_alloc)return NULL;void*p=malloc(n);if(p)live++;return p;}
void vertex_test_free(void*p){if(p)live--;free(p);}
int main(void){Grafo g=grafo_crear();
'''
    for v in vertices:driver+=f'g=grafo_insertar_vertice(g,{v});assert(qa_status==0);\n'
    for a,b,w in arcs:driver+=f'g=grafo_insertar_arco(g,{a},{b},{w});assert(qa_status==0);\n'
    driver+=f'fail_alloc={int(fail)};qa_status=-1;g={function}(g,{x});\n'
    driver+='''printf("{\\"status\\":%d,\\"vertices\\":[",qa_status);int first=1;
for(ListaVertice v=g.v;v;v=v->sig){printf("%s%d",first?"":",",v->dato);first=0;}
printf("],\\"arcs\\":[");first=1;
for(ListaArco a=g.a;a;a=a->sig){printf("%s[%d,%d,%d]",first?"":",",a->origen,a->destino,a->costo);first=0;}
puts("]}");fail_alloc=0;grafo_destruir(&g);assert(live==0);return 0;}
'''
    (tmp_path/'driver.c').write_text(driver,encoding='utf-8')
    flags=[gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(ROOT/'docs/tads_C')]
    original = ROOT/'docs/tads_C/tad_grafo.c'
    observed_source = tmp_path/'observed.c'
    observed_source.write_text(instrument_private_diagnostics(original.read_text(encoding='utf-8-sig')))
    outputs = []
    for source, macros in [(original, []), (observed_source, ['-DOBSERVED'])]:
        commands=[[*flags,'-Dmalloc=vertex_test_malloc','-Dfree=vertex_test_free','-c',str(source),'-o',str(tmp_path/'graph.o')],
                  [*flags,*macros,str(tmp_path/'driver.c'),str(tmp_path/'graph.o'),'-o',str(tmp_path/'native.exe')]]
        for command in commands:
            compiled=subprocess.run(command,text=True,capture_output=True,timeout=30)
            assert compiled.returncode==0,compiled.stderr
        native=subprocess.run([str(tmp_path/'native.exe')],text=True,capture_output=True,timeout=10)
        assert native.returncode==0,native.stderr
        outputs.append(json.loads(native.stdout))
    original_output, observed = outputs
    assert original_output['vertices'] == observed['vertices']
    assert original_output['arcs'] == observed['arcs']
    assert observed['status']==(-1 if result['status'] is None else result['status'])
    assert observed['vertices']==result['graph_after']['vertices']
    assert observed['arcs']==result['graph_after']['arcs']
    if fail:
        assert result['status']==1 and result['graph_after']['vertices']==list(reversed(vertices))
        assert result['memory']['allocations']==result['memory']['frees']
    (tmp_path/'report.json').write_text(json.dumps({'case':[operation,vertices,x,fail],
        'native':observed,'model_graph':result['graph_after'],'model_status':result['status'],
        'native_endpoint_parity':True,'model_event_positions_checked':True},indent=2),encoding='utf-8')
