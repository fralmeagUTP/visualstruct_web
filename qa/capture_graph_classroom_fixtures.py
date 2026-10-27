import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.services.graph_structure_service import GraphStructureService as G
from app.domain.graph.snapshot_pool import expand_graph_trace
h=[];out=[]
for op,p in [('create_graph',{'directed':False}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_edge',{'origin':1,'target':2,'weight':3}),('run_bfs',{'start':1}),('run_dfs',{'start':1})]:
 r=G.execute_operation('graph',op,p,h);assert r['success'],r['message']
 t=expand_graph_trace(r['execution_trace']);out.append({'operation':op,'steps':t['steps']});h.append({'operation':op,'payload':p})
(ROOT/'qa/graph_classroom_fixtures.json').write_text(json.dumps(out,ensure_ascii=False));print([(x['operation'],len(x['steps'])) for x in out])
