"""Generated main must compile and execute against untouched book C/H only."""
import os,subprocess,tempfile,unittest
from pathlib import Path
from app.services.graph_main_service import build_graph_main
ROOT=Path(__file__).resolve().parents[1];CANON=ROOT/'docs/tads_C'
def call(op,**payload):return {'operation':op,'payload':payload}
def setup(directed=True):return [call('create_graph',directed=directed)]
def edge(a,b,w):return call('insert_edge',origin=a,target=b,weight=w)
TRACK=r'''
#include <stdlib.h>
#include <stdio.h>
#include <stddef.h>
void *__real_malloc(size_t);void *__real_calloc(size_t,size_t);void __real_free(void *);
static long live=0, calls=0;
static int fail(void){const char *s=getenv("FAIL_AT");return s && ++calls==strtol(s,NULL,10);}
void *__wrap_malloc(size_t n){if(fail())return NULL;void *p=__real_malloc(n);if(p)live++;return p;}
void *__wrap_calloc(size_t n,size_t s){if(fail())return NULL;void *p=__real_calloc(n,s);if(p)live++;return p;}
void __wrap_free(void *p){if(p)live--;__real_free(p);}
__attribute__((destructor)) static void check(void){if(live!=0){fprintf(stderr,"live=%ld\n",live);_Exit(86);}}
'''
class BookMain(unittest.TestCase):
 def compile_run(self,history,fail_at=None):
  code=build_graph_main(history)
  self.assertNotIn('tad_cola',code);self.assertNotIn('incident_caller',code)
  with tempfile.TemporaryDirectory() as d:
   d=Path(d);(d/'main.c').write_text(code);(d/'track.c').write_text(TRACK)
   cmd=['gcc','-std=c17','-Wall','-Wextra','-Werror','-I',str(CANON),str(d/'main.c'),str(CANON/'tad_grafo.c'),str(d/'track.c'),'-Wl,--wrap=malloc,--wrap=calloc,--wrap=free','-o',str(d/'main')]
   r=subprocess.run(cmd,text=True,capture_output=True);self.assertEqual(r.returncode,0,r.stderr+'\n'+code)
   env=dict(os.environ);env.pop('FAIL_AT',None)
   if fail_at is not None:env['FAIL_AT']=str(fail_at)
   r=subprocess.run([str(d/'main')],text=True,capture_output=True,env=env,timeout=10);self.assertEqual(r.returncode,0,r.stderr);return r.stdout
 def test_cases(self):
  cases=[
   ('empty',[],[]),
   ('borrowed',setup()+[edge(1,2,0),call('list_vertices'),call('list_edges'),call('exists_vertex',vertex=2),call('exists_edge',origin=1,target=2)],['Vertices:','1->2(0)','exists_vertex: 1','exists_edge: 1']),
   ('cost_zero_and_absent',setup()+[edge(1,2,0),call('edge_weight',origin=1,target=2),call('edge_weight',origin=2,target=1)],['Peso: 0','Peso: no encontrado; salida no escrita']),
   ('self_path',setup()+[call('insert_vertex',vertex=1),call('run_dijkstra',start=1,end=1)],['Dijkstra: estado=0 (sin arcos; resultado valido) | costo=0']),
   ('absent_start',setup()+[call('insert_vertex',vertex=1),call('run_bfs',start=99)],['BFS: estado=2']),
   ('disconnected',setup(False)+[call('insert_vertex',vertex=1),call('insert_vertex',vertex=2),call('run_prim',start=1),call('run_kruskal')],['Prim: estado=5','Kruskal: estado=5']),
   ('singleton_mst',setup(False)+[call('insert_vertex',vertex=1),call('run_prim',start=1),call('run_kruskal')],['Prim: estado=0 (sin arcos; resultado valido) | costo=0','Kruskal: estado=0 (sin arcos; resultado valido) | costo=0']),
   ('negative',setup()+[edge(1,2,-4),call('run_dijkstra',start=1,end=2),call('run_bellman_ford',start=1,end=2)],['Dijkstra: estado=3','Bellman-Ford: estado=0 1->2(-4) | costo=-4']),
   ('negative_cycle',setup()+[edge(1,2,-4),edge(2,1,1),call('run_bellman_ford',start=1,end=2)],['Bellman-Ford: estado=4']),
   ('wide_total',setup()+[edge(1,2,1500000000),edge(2,3,1500000000),call('run_dijkstra',start=1,end=3),call('run_bellman_ford',start=1,end=3)],['Dijkstra: estado=0','Bellman-Ford: estado=0','costo=3000000000']),
   ('delete_incidents',setup()+[edge(1,2,7),edge(2,3,9),call('remove_vertex',vertex=2),call('exists_edge',origin=1,target=2),call('exists_edge',origin=2,target=3),call('list_edges')],['exists_edge: 0','Arcos:\n']),
   ('traversals_neighbors',setup()+[edge(1,2,7),edge(2,3,9),call('run_bfs',start=1),call('run_dfs',start=1),call('neighbors',vertex=2),call('clear_graph'),call('list_vertices')],['BFS: estado=0 1 2 3','DFS: estado=0 1 2 3','Vecinos: estado=0 3','Vertices:\n']),
  ]
  for name,history,expected in cases:
   with self.subTest(name=name):
    text=self.compile_run(history)
    for part in expected:self.assertIn(part,text)
 def test_memory_failure_is_actual_state(self):
  text=self.compile_run(setup()+[edge(1,2,7),call('list_vertices')],fail_at=2)
  self.assertIn('insert_edge: estado=1',text);self.assertIn('Vertices:\n',text)
 def test_undirected_second_call_only_after_ok(self):
  text=self.compile_run(setup(False)+[edge(1,2,7)],fail_at=1)
  self.assertIn('insert_edge: estado=1',text);self.assertNotIn('insert_edge inverso',text)
 def test_reverse_failure_does_not_invent_rollback(self):
  text=self.compile_run(setup(False)+[edge(1,2,7),call('list_edges')],fail_at=4)
  self.assertIn('insert_edge: estado=0',text);self.assertIn('insert_edge inverso: estado=1',text)
  self.assertIn('Arcos: 1->2(7)',text);self.assertNotIn('Arcos: 2->1',text)
 def test_recorded_random_only(self):
  import copy
  for directed in [False,True]:
   for seed in [1,27,300]:
    with self.subTest(directed=directed,seed=seed):
     history=setup(directed)+[call('generate_random_graph',vertices_count=5,seed=seed),call('run_bfs',start=1)]
     saved=copy.deepcopy(history);text=self.compile_run(history);self.assertIn('BFS: estado=0',text);self.assertEqual(history,saved)
  with self.assertRaisesRegex(ValueError,'semilla'):
   build_graph_main([call('generate_random_graph',vertices_count=5)])
  self.assertNotIn('GraphAdapter',(ROOT/'app/services/graph_main_service.py').read_text())
 def test_weight_input_contract(self):
  for weight,expected in [(None,1),('',1),('2.0',2),(2.0,2)]:
   text=self.compile_run(setup()+[edge(1,2,weight),call('edge_weight',origin=1,target=2)])
   self.assertIn(f'Peso: {expected}',text)
  text=self.compile_run(setup()+[call('insert_edge',origin=1,target=2),call('edge_weight',origin=1,target=2)])
  self.assertIn('Peso: 1',text)
  for value in [2.5,'nan',True,2147483648]:
   with self.assertRaises(ValueError):build_graph_main(setup()+[edge(1,2,value)])
if __name__=='__main__':unittest.main(verbosity=2)
