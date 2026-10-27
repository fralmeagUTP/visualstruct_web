"""Independent native event oracle plus actual private Graph query player."""
from pathlib import Path
import json,os,subprocess,sys
import pytest
ROOT=Path(__file__).resolve().parents[1]
CHANGE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence'
from scripts.published_test_inputs import audit_input_path
def execute(script,out,vars):
    env=os.environ.copy();env.update(vars)
    run=subprocess.run([sys.executable,'-B',str(script)],cwd=ROOT,env=env,capture_output=True,text=True,timeout=120)
    (out/'execution.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    assert run.returncode==0,run.stdout+run.stderr
    return json.loads((audit_input_path(out/'report.json')).read_text(encoding='utf-8'))
def test_independent_native_neighbors_events_locals_fields_and_ownership(tmp_path):
    from app.domain.graph.book_c_subset import BookSession
    import shutil
    cases=[([],[],99,[]),([7],[],7,[]),
           ([1,2,3],[(1,2,3),(1,3,5),(2,3,7)],3,[]),
           ([1,2,3],[(1,2,3),(1,3,5)],1,[2,3]),
           ([1,2],[(1,1,5),(1,2,5)],1,[1,2]),
           ([-1,0,2],[(-1,0,0),(-1,2,7)],-1,[0,2])]
    code='''#include "tad_grafo.h"
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
static void *pointers[128];static int active[128],slots,allocations,frees,live,bad;
void *neighbor_test_malloc(size_t n){void*p=malloc(n);if(p){assert(slots<128);pointers[slots]=p;active[slots++]=1;allocations++;live++;}return p;}
void neighbor_test_free(void*p){if(p){int found=0;for(int i=0;i<slots;i++)if(active[i]&&pointers[i]==p){active[i]=0;found=1;break;}if(!found)bad++;assert(found);frees++;live--;}free(p);}
int main(void){
'''
    for index,(vertices,arcs,vertex,expected) in enumerate(cases):
        code+='{Grafo g=grafo_crear();GrafoEstado e;\n'
        for value in vertices:code+=f'g=grafo_insertar_vertice(g,{value},&e);assert(e==GRAFO_OK);\n'
        for a,b,w in arcs:code+=f'g=grafo_insertar_arco(g,{a},{b},{w},&e);assert(e==GRAFO_OK);\n'
        code+=f'int base=live;allocations=frees=0;ListaVertice r=grafo_sucesores(g,{vertex},&e);assert(e==GRAFO_OK);printf("RESULT {index} [");int comma=0;\n'
        code+='for(ListaVertice p=r;p;p=p->sig){printf("%s%d",comma?",":"",p->dato);comma=1;}puts("]");\n'
        code+=f'assert(allocations=={len(expected)});grafo_liberar_vertices(&r);assert(r==NULL&&allocations==frees&&live==base&&bad==0);grafo_destruir(&g);assert(live==0&&bad==0);}}\n'
    code+='return 0;}\n';(tmp_path/'native.c').write_text(code,encoding='utf-8')
    gcc=shutil.which('gcc');assert gcc
    common=[gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(ROOT/'docs/tads_C')]
    commands=[[*common,'-Dmalloc=neighbor_test_malloc','-Dfree=neighbor_test_free','-c',str(ROOT/'docs/tads_C/tad_grafo.c'),'-o',str(tmp_path/'graph.o')],
              [*common,str(tmp_path/'native.c'),str(tmp_path/'graph.o'),'-o',str(tmp_path/'native.exe')]]
    for command in commands:
        compiled=subprocess.run(command,capture_output=True,text=True,timeout=30);assert compiled.returncode==0,compiled.stderr
    native=subprocess.run([str(tmp_path/'native.exe')],capture_output=True,text=True,timeout=10);assert native.returncode==0,native.stderr
    rows=[json.loads(line.split(' ',2)[2]) for line in native.stdout.splitlines() if line.startswith('RESULT ')]
    assert len(rows)==len(cases)==6
    for observed,(vertices,arcs,vertex,expected) in zip(rows,cases):
        session=BookSession(vertices,arcs);original=session.machine.snapshot()['heap_nodes']
        result=session.call('grafo_sucesores',[vertex])
        assert result['status']==0 and result['result_items']==observed==expected
        assert result['ownership']=='owned'
        session.free_result(result['returned'],result['return_type'])
        assert session.machine.snapshot()['heap_nodes']==original

@pytest.mark.e2e
@pytest.mark.parametrize('vertex',[3,1],ids=['empty-successors','owned-results'])
def test_actual_query_player_no_false_highlight_frames_reverse_and_reload(tmp_path,vertex):
    report=execute(Path(__file__).with_name('_graph_query_browser_contract_observer.py'),tmp_path,{'FOCAL_QUERY_BROWSER_OUT':str(tmp_path),'FOCAL_EXPECT_FIXED':'1','FOCAL_QUERY_VERTEX':str(vertex)})
    assert report['fixed_verified'] and not report['incorrect_body_highlights']
    assert report['replay_POSTs']==report['reload_POSTs']==0
    assert report['DOM_HTTP_main_identical'] and report['query_recorded_in_main']
    assert report['source_contract']=='graph-book/v1'
    assert not report['errors']
