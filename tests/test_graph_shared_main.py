"""Canonical command replay, identical downloads and native caller ownership."""
from pathlib import Path
import json,subprocess,shutil,os
import pytest
from app import create_app
from app.adapters.graph_adapter import GraphAdapter
from app.services.graph_main_service import build_graph_main
from app.services.execution_trace_service import ExecutionTraceService

@pytest.mark.parametrize('algorithm',['bellman_ford','prim','dijkstra','kruskal'])
def test_session_shared_main_duplicate_calls_replay_and_C17_ownership(tmp_path,monkeypatch,algorithm):
 monkeypatch.setattr(ExecutionTraceService,'build_trace',staticmethod(lambda **kwargs:{}))
 app=create_app();client=app.test_client();directed=algorithm in {'bellman_ford','dijkstra'}
 def post(op,payload):
  r=client.post('/graph/graph/operate',json={'operation':op,'payload':payload,'execution_mode':'normal'});assert r.status_code==200;return r.get_json()
 post('create_graph',{'directed':directed})
 for v in [1,2]:post('insert_vertex',{'vertex':v})
 post('insert_edge',{'origin':1,'target':2,'weight':2})
 payload={} if algorithm=='kruskal' else {'start':1}
 if directed:payload['end']=2
 first=post('run_'+algorithm,payload);second=post('run_'+algorithm,payload)
 assert second['main_c'].count('= grafo_'+algorithm+'(')==2
 original=GraphAdapter.execute;calls=[]
 def observe_queries(self,operation,payload):
  calls.append(operation)
  return original(self,operation,payload)
 monkeypatch.setattr(GraphAdapter,'execute',observe_queries)
 for _ in range(2):
  r=client.get('/help/source/graph/main');assert r.status_code==200
  assert r.data==second['main_c'].encode('utf-8') and 'main.c' in r.headers['Content-Disposition']
  assert r.headers['Cache-Control']=='private, no-store'
  assert client.get('/graph/graph/'+('camino-minimo' if directed else 'expansion-minima')).status_code==200
 isolated=app.test_client().get('/help/source/graph/main');assert isolated.status_code==200 and ('= grafo_'+algorithm+'(').encode() not in isolated.data
 assert [op for op in calls if op.startswith('run_')]==['run_'+algorithm]*8
 # Reset/recreate cleanup is caller code; the original graph is released first.
 main=build_graph_main(second['history']+[{'operation':'create_graph','payload':{'directed':False}},{'operation':'insert_vertex','payload':{'vertex':99}},{'operation':'clear_graph','payload':{}}]).replace('    return 0;','    printf("OWNERSHIP %zu %zu %zu\\n", track_allocs, track_frees, track_allocs - track_frees);\n    return 0;')
 out=Path(os.environ.get('GRAPH_MAIN_QA_OUT',str(tmp_path)))/algorithm;out.mkdir(parents=True,exist_ok=True)
 (out/'main.c').write_text(main,encoding='utf-8')
 for stem in ['tad_grafo','tad_cola']:
  for ext in ['c','h']:(out/(stem+'.'+ext)).write_bytes(Path('docs/tads_C',stem+'.'+ext).read_bytes())
 (out/'tracked.h').write_text('#include <stddef.h>\nextern size_t track_allocs, track_frees;\nvoid *tracked_malloc(size_t);\nvoid tracked_free(void *);\nvoid *tracked_calloc(size_t, size_t);\n',encoding='utf-8')
 (out/'tracked.c').write_text('#undef malloc\n#undef free\n#undef calloc\n#include <stdlib.h>\n#include "tracked.h"\nsize_t track_allocs=0, track_frees=0;\nvoid *tracked_malloc(size_t n){void *p=malloc(n);if(p)track_allocs++;return p;}\nvoid *tracked_calloc(size_t n,size_t s){void *p=calloc(n,s);if(p)track_allocs++;return p;}\nvoid tracked_free(void *p){if(p)track_frees++;free(p);}\n',encoding='utf-8')
 compiler=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-Dmalloc=tracked_malloc','-Dfree=tracked_free','-Dcalloc=tracked_calloc','-include',str(out/'tracked.h'),str(out/'main.c'),str(out/'tad_grafo.c'),str(out/'tad_cola.c'),str(out/'tracked.c'),'-o',str(out/'main.exe')]
 run=subprocess.run(compiler,capture_output=True,text=True,timeout=30);(out/'compile.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0 and not run.stderr,run.stderr
 run=subprocess.run([str(out/'main.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0
 (out/'stdout.log').write_text(run.stdout,encoding='utf-8');report=run.stdout.splitlines()[-1].split();assert report[0]=='OWNERSHIP' and report[1]==report[2] and report[3]=='0'
 assert sum(line.startswith({'bellman_ford':'Bellman-Ford','prim':'Prim','dijkstra':'Dijkstra','kruskal':'Kruskal'}[algorithm]+':') for line in run.stdout.splitlines())==2
 (out/'report.json').write_text(json.dumps({'algorithm':algorithm,'duplicate_calls':2,'GET_canonical_query_replays':8,'server_HTTP_main_bytes_equal':True,'session_isolated':True,'alloc':int(report[1]),'free':int(report[2]),'live':0,'ownership_history_extended_with_resets':True}),encoding='utf-8')

def test_seeded_random_graph_and_multiple_resets_export_exact_topology_without_algorithm(monkeypatch):
 from app.services.graph_structure_service import GraphStructureService
 history=[{'operation':'create_graph','payload':{'directed':False}},{'operation':'insert_vertex','payload':{'vertex':99}},{'operation':'generate_random_graph','payload':{'vertices_count':4,'seed':12}}]
 history=[{**row,'source_contract':'graph-book/v1'} for row in history]
 adapter,valid=GraphStructureService._rebuild_adapter('graph',history)
 main=build_graph_main(valid)
 assert 'generate_random_graph(' not in main and 'Operación();' not in main
 for a,b,w in adapter.graph._g._arcos:assert f'grafo_insertar_arco(g, {a}, {b}, {w}, &estado_' in main
 assert main.count('g = grafo_crear();')==3
 assert main.count('grafo_destruir(&g);')==3

@pytest.mark.parametrize('directed',[2,' true '])
def test_main_direction_matches_existing_API_boolean_normalization(directed):
 from app.services.graph_structure_service import GraphStructureService
 history=[{'operation':'create_graph','payload':{'directed':directed}},{'operation':'insert_edge','payload':{'origin':1,'target':2,'weight':2}}]
 history=[{**row,'source_contract':'graph-book/v1'} for row in history]
 model=GraphStructureService.get_view_model('graph',history)
 assert model['visual_state']['directed'] is True
 assert model['main_c'].count('g = grafo_insertar_arco(')==1
