"""Canonical vertex deletion owns incident cleanup; callers must not repeat it.

Native compiled output, short-circuit operands and unique ownership are observed
independently. Model temporal/source checks do not claim old synthetic-caller
instruction parity after that caller became unnecessary.
"""
from pathlib import Path
from copy import deepcopy
import json, shutil, subprocess
import pytest
from app import create_app
from app.config import Config
from app.domain.graph.book_source import canonical_source
from app.domain.graph.book_c_subset import Program
from _graph_trace_contract import decode_graph_http_trace
from _book_frame_oracle import assert_book_body

ROOT=Path(__file__).resolve().parents[1]

def private_client(path):
    class PrivateConfig(Config):
        APP_ENV='testing';TESTING=True;SECRET_KEY='graph-incident-private-qa'
        SESSION_CACHE_DIR=str(path/'cache')
    return create_app(PrivateConfig).test_client()

def download_main_fixture(client,folder,history):
    folder.mkdir(parents=True,exist_ok=True);responses=[]
    for index,(operation,payload) in enumerate(history):
        response=client.post('/graph/graph/operate',json={'operation':operation,'payload':payload,
            'execution_mode':'step' if index==len(history)-1 else 'normal'})
        assert response.status_code==200 and response.json['success'];responses.append(response.json)
    response=client.get('/help/source/graph/main');assert response.status_code==200
    assert response.data==responses[-1]['main_c'].encode()
    main=response.data.decode();(folder/'downloaded-main.c').write_bytes(response.data)
    for kind,ext in [('source','c'),('header','h')]:
        downloaded=client.get('/help/source/graph/'+kind);assert downloaded.status_code==200
        assert downloaded.data==(ROOT/'docs/tads_C'/('tad_grafo.'+ext)).read_bytes()
        (folder/('tad_grafo.'+ext)).write_bytes(downloaded.data)
    data=deepcopy(responses[-1]);data['execution_trace']=decode_graph_http_trace(data['execution_trace'])
    return main,data

def native_probe(folder,main,observe_operands=False):
    marker='    grafo_destruir(&g);';pos=main.rfind(marker);assert pos>=0
    observation=r'''    printf("PROBE %d %d\n",grafo_orden(g),grafo_tamano(g));
    for(ListaVertice p=g.v;p;p=p->sig)printf("V %d\n",p->dato);
    for(ListaArco p=g.a;p;p=p->sig)printf("A %d %d %d\n",p->origen,p->destino,p->costo);
'''
    code=main[:pos]+observation+main[pos:]
    assert code.count('    return 0;')==1
    code=code.replace('    return 0;','    tracked_finish();\n    return 0;')
    (folder/'observed-main.c').write_text(code,encoding='utf-8')
    header='''#include <stddef.h>
void *tracked_malloc(size_t); void *tracked_calloc(size_t,size_t); void tracked_free(void *);
void tracked_finish(void); int incident_operand(const char *,int);
'''
    (folder/'tracked.h').write_text(header)
    source=(folder/'tad_grafo.c').read_text(encoding='utf-8')
    if observe_operands:
        expression='actual->origen == x || actual->destino == x'
        assert source.count(expression)==1
        source=source.replace(expression,'incident_operand("origin",actual->origen == x) || incident_operand("target",actual->destino == x)')
    (folder/'observed-graph.c').write_text(source,encoding='utf-8')
    runtime=r'''#include <stdlib.h>
#include <stdio.h>
#include <stdint.h>
static struct {uintptr_t pointer;int live;int freed;} objects[4096];
static size_t allocations,frees;static int duplicate;
static void remember(void*p){if(p){if(allocations==4096)exit(90);objects[allocations].pointer=(uintptr_t)p;objects[allocations].live=1;allocations++;}}
void *tracked_malloc(size_t n){void*p=malloc(n);remember(p);return p;}
void *tracked_calloc(size_t n,size_t s){void*p=calloc(n,s);remember(p);return p;}
void tracked_free(void*p){if(p){int found=-1;for(int i=(int)allocations-1;i>=0;i--)if(objects[i].pointer==(uintptr_t)p&&objects[i].live){found=i;break;}if(found<0){duplicate++;exit(91);}objects[found].live=0;objects[found].freed++;frees++;}free(p);}
int incident_operand(const char*name,int value){fprintf(stderr,"OP|%s|%d\n",name,!!value);return value;}
void tracked_finish(void){int live=0,bad=0;for(size_t i=0;i<allocations;i++){live+=objects[i].live;bad+=objects[i].freed!=1;}printf("OWN %zu %zu %d %d %d\n",allocations,frees,live,duplicate,bad);if(live||duplicate||bad)exit(92);}
'''
    (folder/'runtime.c').write_text(runtime,encoding='utf-8')
    gcc=shutil.which('gcc');assert gcc;objects=[]
    for filename in ['observed-main.c','observed-graph.c','runtime.c']:
        obj=folder/(filename+'.o');command=[gcc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-I',str(folder)]
        if filename!='runtime.c':command+=['-include',str(folder/'tracked.h'),'-Dmalloc=tracked_malloc','-Dcalloc=tracked_calloc','-Dfree=tracked_free']
        compiled=subprocess.run(command+['-c',str(folder/filename),'-o',str(obj)],capture_output=True,text=True,timeout=30)
        assert compiled.returncode==0,compiled.stderr;objects.append(str(obj))
    executable=folder/'native.exe';compiled=subprocess.run([gcc,*objects,'-o',str(executable)],capture_output=True,text=True,timeout=30)
    assert compiled.returncode==0,compiled.stderr
    native=subprocess.run([str(executable)],capture_output=True,text=True,timeout=10);assert native.returncode==0,native.stdout+native.stderr
    result={'vertices':[],'arcs':[],'operands':[]}
    for line in native.stdout.splitlines():
        fields=line.split()
        if fields[0]=='PROBE':result['counts']=list(map(int,fields[1:]))
        elif fields[0]=='V':result['vertices'].append(int(fields[1]))
        elif fields[0]=='A':result['arcs'].append(list(map(int,fields[1:])))
        elif fields[0]=='OWN':result['ownership']=list(map(int,fields[1:]))
        else:assert line.startswith(('insert_vertex: estado=0','insert_edge: estado=0','insert_edge inverso: estado=0'))
    for line in native.stderr.splitlines():
        tag,name,value=line.split('|');assert tag=='OP';result['operands'].append({'name':name,'value':bool(int(value))})
    allocated,freed,live,duplicate,bad=result['ownership']
    assert allocated==freed and live==duplicate==bad==0
    (folder/'report.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

def test_downloaded_main_selfloop_remove_vertex_matches_API_before_final_cleanup(tmp_path):
    folder=tmp_path/'selfloop';main,data=download_main_fixture(private_client(tmp_path),folder,
        [('insert_vertex',{'vertex':1}),('insert_edge',{'origin':1,'target':1,'weight':5}),('remove_vertex',{'vertex':1})])
    assert data['visual_state']['nodes']==data['visual_state']['edges']==[]
    native=native_probe(folder,main)
    assert native['counts']==[0,0] and native['vertices']==native['arcs']==[]

CALLER_FIXTURES=[
    ('directed-mixed',True,[1,2,3,4],[(2,1,3),(1,3,4),(1,1,5),(3,4,6)],1),
    ('undirected-mixed',False,[1,2,3,4],[(2,1,3),(1,3,4),(1,1,5),(3,4,6)],1),
    ('empty-arcs',True,[1,2],[],1),
    ('int-min-selfloop',True,[-2147483648,2],[(-2147483648,-2147483648,-2147483648)],-2147483648),
    ('all-incidents',True,[1,2,3],[(1,2,3),(3,1,4),(1,1,5)],1),
]

@pytest.mark.parametrize('case,directed,vertices,arcs,remove',CALLER_FIXTURES,ids=[c[0] for c in CALLER_FIXTURES])
def test_native_caller_source_events_shortcircuit_and_unique_ownership(tmp_path,case,directed,vertices,arcs,remove):
    history=[('create_graph',{'directed':directed})]+[('insert_vertex',{'vertex':v}) for v in vertices]
    history += [('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in arcs]
    history += [('remove_vertex',{'vertex':remove})]
    main,data=download_main_fixture(private_client(tmp_path),tmp_path/case,history)
    assert data['execution_trace']['book_instruction_model']
    assert main.count('g = grafo_eliminar_vertice(')==1 and '*enlace = actual->sig;' not in main
    assert_book_body(data)
    native=native_probe(tmp_path/case,main,observe_operands=True)
    final=data['visual_state']
    assert native['vertices']==[int(node['id']) for node in reversed(final['nodes'])]
    assert native['arcs']==[[int(a['source']),int(a['target']),a['weight']] for a in reversed(final['c_arcs'])]
    initial=data['execution_trace']['steps'][0]['state_snapshot'];expected=[]
    for arc in reversed(initial['c_arcs']):
        origin=int(arc['source'])==remove;expected.append({'name':'origin','value':origin})
        if not origin:expected.append({'name':'target','value':int(arc['target'])==remove})
    assert native['operands']==expected

def test_unknown_caller_fragment_rejected_instead_of_fabricated_cleanup(monkeypatch):
    from app.domain.graph import vertex_instruction
    def retired(*args,**kwargs):raise AssertionError('retired synthetic caller invoked')
    monkeypatch.setattr(vertex_instruction,'incident_caller_lines',retired)
    client=private_client(Path('.pytest_cache')/'incident-isolated')
    assert client.post('/graph/graph/operate',json={'operation':'remove_vertex','payload':{'vertex':1}}).json['success']
    source=canonical_source();mutated=source.replace('*enlace = actual->sig;','*enlace = NULL;',1);assert mutated!=source
    with pytest.raises(ValueError,match='byte-exact'):Program(mutated)

def test_caller_partial_visual_weight_and_return_alias_follow_live_arcs(tmp_path):
    client=private_client(tmp_path)
    for op,payload in [('insert_vertex',{'vertex':1}),('insert_edge',{'origin':1,'target':1,'weight':5})]:
        assert client.post('/graph/graph/operate',json={'operation':op,'payload':payload,'execution_mode':'normal'}).json['success']
    data=client.post('/graph/graph/operate',json={'operation':'remove_vertex','payload':{'vertex':1}}).json
    data['execution_trace']=decode_graph_http_trace(data['execution_trace']);assert_book_body(data)
    steps=data['execution_trace']['steps']
    unlink=next(s for s in steps if s['line_text'].strip()=='*enlace = actual->sig;')
    assert unlink['state_snapshot']['weighted'] is True
    assert unlink['state_after']['weighted'] is False and unlink['state_after']['edges']==[]
    assert any(node['kind']=='struct NodoA' for node in unlink['pedagogy']['memory_state']['heap_nodes'])
    freed=next(s for s in steps if s['phase']=='free' and s['pedagogy']['instruction_event']['function']=='grafo_eliminar_vertice')
    assert freed['state_after']['edges']==[] and freed['state_after']['last_result'] is None
    assert freed['pedagogy']['memory']['retired_references']
    assert all(ref['usable'] is False for ref in freed['pedagogy']['memory']['retired_references'])
    assert steps[-1]['pedagogy']['memory_state']['frames']==[]
    assert steps[-1]['state_after']==data['visual_state']
