"""Cross-call native graph marks without historical query redispatch."""
import copy,json,re,shutil,subprocess
from pathlib import Path
import pytest
from _graph_trace_contract import decode_graph_http_trace
from app.adapters.graph_adapter import GraphAdapter
from app.services.graph_structure_service import GraphStructureService as S
from app.services.session_service import SessionService, SESSION_KEY

BASE=[('create_graph',{'directed':True}),*[('insert_vertex',{'vertex':v}) for v in [1,2,3,4]],*[('insert_edge',{'origin':a,'target':b,'weight':1}) for a,b in [(1,2),(1,3),(2,4)]]]
CASES=[
 ('two_dfs',[('run_dfs',{'start':1}),('run_dfs',{'start':1})]),
 ('bfs_dfs',[('run_bfs',{'start':1}),('run_dfs',{'start':3})]),
 ('dfs_bfs',[('run_dfs',{'start':2}),('run_bfs',{'start':1})]),
 ('new_vertex',[('run_dfs',{'start':1}),('insert_vertex',{'vertex':99}),('run_dfs',{'start':99})]),
 ('new_edge',[('run_dfs',{'start':1}),('insert_edge',{'origin':4,'target':99,'weight':1}),('run_dfs',{'start':1})]),
 ('weight_change',[('run_dfs',{'start':1}),('insert_edge',{'origin':1,'target':2,'weight':8}),('run_dfs',{'start':2})]),
 ('removed_edge',[('run_dfs',{'start':1}),('remove_edge',{'origin':1,'target':2}),('run_dfs',{'start':1})]),
 ('deleted_reinserted_isolated',[('insert_vertex',{'vertex':99}),('run_dfs',{'start':99}),('remove_vertex',{'vertex':99}),('insert_vertex',{'vertex':99}),('run_dfs',{'start':99})]),
 ('clear',[('run_dfs',{'start':1}),('clear_graph',{}),('insert_vertex',{'vertex':-1}),('run_dfs',{'start':-1})]),
 ('failed_queries',[('run_dfs',{'start':1}),('run_dfs',{'start':999}),('run_bfs',{'start':999}),('run_dfs',{'start':2})]),
]

def marks(state):return {int(n['id']):n['marked'] for n in state['nodes']}

def c_statement(op,p):
 if op=='create_graph':return 'g=grafo_crear();'
 if op=='insert_vertex':return f'g=grafo_insertar_vertice(g,{p["vertex"]});'
 if op=='insert_edge':return f'g=grafo_insertar_arco(g,{p["origin"]},{p["target"]},{p["weight"]});'
 if op=='remove_edge':return f'g=grafo_eliminar_arco(g,{p["origin"]},{p["target"]});'
 if op=='remove_vertex':return f'g=grafo_eliminar_vertice(g,{p["vertex"]});'
 if op=='clear_graph':return 'release_graph(g);g=grafo_crear();'
 if op in ['run_dfs','run_bfs']:
  if p['start']==999:return '/* Application rejects missing start; no C query invocation. */'
  return f'{{ListaVertice r=grafo_{op[4:]}(g,{p["start"]});while(r){{ListaVertice n=r;r=r->sig;free(n);}}}}'
 raise AssertionError(op)

@pytest.fixture(scope='module')
def native_mark_sequences(tmp_path_factory):
 from app import create_app
 out=tmp_path_factory.mktemp('graph-mark-native');client=create_app().test_client()
 for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
  for part,ext in [('source','c'),('header','h')]:
   response=client.get('/help/source/'+tad+'/'+part);assert response.status_code==200;(out/(stem+'.'+ext)).write_bytes(response.data)
 source='#include "tad_grafo.h"\n#include <stdio.h>\n#include <stdlib.h>\nstatic void release_graph(Grafo g){while(g.a){ListaArco n=g.a;g.a=n->sig;free(n);}while(g.v){ListaVertice n=g.v;g.v=n->sig;free(n);}}\nstatic void emit(Grafo g,int c,int s,const char*phase){printf("\\nMARKS %d %d %s [",c,s,phase);int first=1;for(ListaVertice v=g.v;v;v=v->sig){printf("%s[%d,%d]",first?"":",",v->dato,v->marcado);first=0;}puts("]");}\nint main(void){\n'
 for case,(_,tail) in enumerate(CASES):
  source+='{Grafo g=grafo_crear();'+''.join(c_statement(op,p) for op,p in BASE)
  for step,(op,p) in enumerate(tail):source+=f'emit(g,{case},{step},"before");'+c_statement(op,p)+f'emit(g,{case},{step},"after");'
  source+='release_graph(g);}\n'
 source+='return 0;}';(out/'main.c').write_text(source)
 exe=out/'native.exe';build=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'main.c'),str(out/'tad_grafo.c'),str(out/'tad_cola.c'),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(exe)],capture_output=True,text=True,timeout=10);assert run.returncode==0
 (out/'stdout.log').write_text(run.stdout);rows=[{'case':int(m[1]),'step':int(m[2]),'phase':m[3],'marks':json.loads(m[4])} for m in re.finditer(r'^MARKS (\d+) (\d+) (before|after) (.*)$',run.stdout,re.M)]
 assert len(rows)==2*sum(len(t) for _,t in CASES);(out/'report.json').write_text(json.dumps(rows,indent=2));return {(row['case'],row['step'],row['phase']):dict(row['marks']) for row in rows}

@pytest.mark.parametrize('case',range(len(CASES)),ids=[c[0] for c in CASES])
def test_query_mark_context_matches_downloaded_c(case,native_mark_sequences,monkeypatch):
 h=[]
 for op,p in BASE:h=S.execute_operation('graph',op,copy.deepcopy(p),h)['history']
 actual_calls=[];old=GraphAdapter.execute
 def spy(self,op,p):
  if op in ['run_bfs','run_dfs']:actual_calls.append(op)
  return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 for step,(op,p) in enumerate(CASES[case][1]):
  original=copy.deepcopy(h)
  for _ in range(2):assert marks(S.get_view_model('graph',h)['visual_state'])==native_mark_sequences[case,step,'before']
  data=S.execute_operation('graph',op,copy.deepcopy(p),h)
  assert marks(data['execution_trace']['steps'][0]['state_snapshot'])==native_mark_sequences[case,step,'before']
  assert marks(data['visual_state'])==native_mark_sequences[case,step,'after']
  if not data['success']:assert data['history']==original
  h=data['history']
  for _ in range(2):assert marks(S.get_view_model('graph',h)['visual_state'])==native_mark_sequences[case,step,'after']
 expected=[op for op,_ in CASES[case][1] if op in ['run_bfs','run_dfs']]
 assert actual_calls==expected

@pytest.mark.parametrize('fault',['missing','not_dict','schema','mark_bool','mark_out_of_range','vertex_bool','duplicate','unknown_vertex','operation','start','topology','prefix','signature','extra_field','tampered_valid_mark'])
def test_invalid_effect_is_discarded_without_query_execution(fault,monkeypatch):
 h=[]
 for op,p in BASE:h=S.execute_operation('graph',op,copy.deepcopy(p),h)['history']
 data=S.execute_operation('graph','run_dfs',{'start':1},h);bad=copy.deepcopy(data['history']);effect=bad[-1]['mark_effect']
 if fault=='missing':bad[-1].pop('mark_effect')
 elif fault=='not_dict':bad[-1]['mark_effect']=[]
 elif fault=='schema':effect['schema_version']=True
 elif fault=='mark_bool':effect['marks'][0][1]=True
 elif fault=='mark_out_of_range':effect['marks'][0][1]=2
 elif fault=='vertex_bool':effect['marks'][0][0]=True
 elif fault=='duplicate':effect['marks'][1][0]=effect['marks'][0][0]
 elif fault=='unknown_vertex':effect['marks'][0][0]=999
 elif fault=='operation':effect['operation']='run_bfs'
 elif fault=='start':effect['start']=2
 elif fault=='topology':effect['topology']='0'*64
 elif fault=='prefix':effect['prefix']='0'*64
 elif fault=='signature':effect['signature']='é'*64
 elif fault=='extra_field':effect['other']=1
 elif fault=='tampered_valid_mark':effect['marks'][1][1]=0
 calls=[];old=GraphAdapter.execute
 def spy(self,op,p):calls.append(op);return old(self,op,p)
 monkeypatch.setattr(GraphAdapter,'execute',spy)
 view=S.get_view_model('graph',bad)
 assert all(v==0 for v in marks(view['visual_state']).values())
 assert view['history'][-1]=={'operation':'run_dfs','payload':{'start':1}}
 assert 'run_dfs' not in calls and 'run_bfs' not in calls


def test_snapshot_copy_after_mutation_rejected(monkeypatch):
 h=[]
 for op,p in BASE:h=S.execute_operation('graph',op,copy.deepcopy(p),h)['history']
 good=S.execute_operation('graph','run_dfs',{'start':1},h)['history'][-1]
 mutated=S.execute_operation('graph','insert_vertex',{'vertex':99},h)['history'];forged=mutated+[copy.deepcopy(good)]
 view=S.get_view_model('graph',forged)
 assert marks(view['visual_state'])=={1:0,2:0,3:0,4:0,99:0}
 assert 'mark_effect' not in view['history'][-1]


def test_session_isolation_and_foreign_effect_rejected(app):
 a=app.test_client();b=app.test_client()
 def post(client,op,p):return client.post('/graph/graph/operate',json={'operation':op,'payload':p}).get_json()
 for client in [a,b]:
  for op,p in BASE:assert post(client,op,p)['success']
 one=post(a,'run_dfs',{'start':1});assert marks(one['visual_state'])=={1:1,2:1,3:1,4:1}
 assert b.get('/graph/graph/recorridos').status_code==200
 with b.session_transaction() as session:
  records=session[SESSION_KEY];records['graph::graph']['history']=copy.deepcopy(one['history']);session[SESSION_KEY]=records
 # Inspect through a real request context by asking a nonmutating query. The
 # foreign snapshot must be rejected; this operation itself does not mark.
 other=post(b,'exists_vertex',{'vertex':1});assert marks(other['visual_state'])=={1:0,2:0,3:0,4:0}
 again=post(a,'run_dfs',{'start':2});assert marks(decode_graph_http_trace(again['execution_trace'])['steps'][0]['state_snapshot'])=={1:1,2:1,3:1,4:1}
 assert sum(x['operation']=='run_dfs' for x in again['history'])==2
 assert sum(x['operation']=='run_dfs' for x in other['history'])==1


def test_malformed_history_rows_are_ignored():
 history=[None,1,[],{'operation':[], 'payload':{}},{'operation':'run_dfs','payload':[]},{'operation':'insert_vertex','payload':{'vertex':1}},{'operation':'run_dfs','payload':{'start':999}},{'operation':'run_dfs','payload':{'start':True}}]
 view=S.get_view_model('graph',history);assert view['history']==[{'operation':'insert_vertex','payload':{'vertex':1}}]
 assert S.get_view_model('graph',None)['history']==[]
