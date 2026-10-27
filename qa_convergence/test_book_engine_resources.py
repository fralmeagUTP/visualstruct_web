"""Bounded resource probe; normal-only dense event count is not dense UI certification."""
import json,time,sys
try:
 import resource
except ImportError:
 resource=None
from app.domain.graph.book_c_subset import BookSession,GraphMachine,Program,Reference,UNINIT
from app.domain.graph.book_source import canonical_source
from app.domain.graph.book_trace import BookTraceCollector

def profile(n):
 vertices=list(range(n));arcs=[(a,b,1) for a in vertices for b in vertices if abs(a-b)==1]
 before={'structure':'graph','directed':False,'nodes':[{'id':str(v)} for v in vertices],'edges':[{'source':str(a),'target':str(b),'weight':w} for a,b,w in arcs if a<b],'metadata':{},'last_result':None,'last_operation':None}
 c=BookTraceCollector(operation_name='run_dijkstra',payload={'start':0,'end':n-1},before_state=before);s=BookSession(vertices,arcs,callback=c.callback);start=time.perf_counter();s.call('grafo_dijkstra',[0,n-1]);trace=c.finish(after_state=before,compact=True)
 return {'n':n,'raw_arcs':len(arcs),'steps':len(trace['steps']),'seconds':round(time.perf_counter()-start,3),'pool_records':len(c.pool.records),'wire_bytes':len(json.dumps(trace,ensure_ascii=False).encode()),'raw_transitions_retained':len(s.transitions),'events_retained_in_session':len(s.machine.events),'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if resource is not None else None}

if __name__=='__main__':print(json.dumps(profile(int(sys.argv[1]) if len(sys.argv)>1 else 5)))
