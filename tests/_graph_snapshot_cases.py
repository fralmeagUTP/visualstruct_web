"""Original boundary cases executed by canonical C, with streaming/raw records."""
from copy import deepcopy
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph.book_trace import BookTraceCollector
CASES=['bellman_ford','bellman_cycle','prim','dijkstra','kruskal']
def capture(name):
 algorithm='bellman_ford' if name=='bellman_cycle' else name;adapter=GraphAdapter()
 adapter.execute('create_graph',{'directed':algorithm in {'bellman_ford','dijkstra'}})
 for v in [1,2,3]:adapter.execute('insert_vertex',{'vertex':v})
 edges=[(1,2,-2147483648),(2,1,-2147483648)] if name=='bellman_cycle' else [(1,2,2147483647),(2,3,2147483647)] if algorithm=='bellman_ford' else [(1,2,2147483646),(2,3,1)] if algorithm=='dijkstra' else [(1,2,-2147483648),(2,3,2147483647)]
 for a,b,w in edges:adapter.execute('insert_edge',{'origin':a,'target':b,'weight':w})
 payload={} if algorithm=='kruskal' else {'start':1}
 if algorithm in {'bellman_ford','dijkstra'}:payload['end']=2 if name=='bellman_cycle' else 3
 operation='run_'+algorithm
 if name!='bellman_cycle':adapter.execute(operation,payload) # Previous query visible at initial boundary.
 before=adapter.to_visual_state();records=[]
 collector=BookTraceCollector(operation_name=operation,payload=payload,before_state=before)
 def observe(event,old,new):
  records.append({'event':deepcopy(event),'before':deepcopy(old),'after':deepcopy(new)})
  collector.callback(event,old,new)
 adapter._book_callback=observe
 result=adapter.execute(operation,payload);after=adapter.to_visual_state()
 logical=collector.finish(after_state=after,success=result['success'],message=result['message'],compact=False)
 return dict(operation_name=operation,payload=payload,before_state=before,after_state=after,execution={'source_code':collector.source,'transitions':records},success=result['success'],message=result['message']),logical

def arguments(name):
 return capture(name)[0]
