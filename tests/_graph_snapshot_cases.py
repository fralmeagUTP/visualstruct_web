"""Independent frozen-format fixture inputs for exact Graph snapshot transport."""
from app.adapters.graph_adapter import GraphAdapter
from app.services.c_code_service import CCodeService
CASES=['bellman_ford','bellman_cycle','prim','dijkstra','kruskal']
def arguments(name):
 algorithm='bellman_ford' if name=='bellman_cycle' else name;adapter=GraphAdapter()
 adapter.execute('create_graph',{'directed':algorithm in {'bellman_ford','dijkstra'}})
 for v in [1,2,3]:adapter.execute('insert_vertex',{'vertex':v})
 edges=[(1,2,-2147483648),(2,1,-2147483648)] if name=='bellman_cycle' else [(1,2,2147483647),(2,3,2147483647)] if algorithm=='bellman_ford' else [(1,2,2147483646),(2,3,1)] if algorithm=='dijkstra' else [(1,2,-2147483648),(2,3,2147483647)]
 for a,b,w in edges:adapter.execute('insert_edge',{'origin':a,'target':b,'weight':w})
 payload={} if algorithm=='kruskal' else {'start':1}
 if algorithm in {'bellman_ford','dijkstra'}:payload['end']=2 if name=='bellman_cycle' else 3
 operation='run_'+algorithm
 if name!='bellman_cycle':adapter.execute(operation,payload) # Previous query visible at initial boundary.
 before=adapter.to_visual_state();result=adapter.execute(operation,payload);after=adapter.to_visual_state()
 return dict(operation_name=operation,payload=payload,source_code=CCodeService._build_graph_data()['operations'][operation],code_title='Codigo C',before_state=before,after_state=after,success=bool(result.get('success',True)),message=result.get('message','Operacion ejecutada correctamente.'))
