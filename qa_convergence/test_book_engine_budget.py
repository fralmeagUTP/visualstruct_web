import unittest
from unittest.mock import patch
from app.domain.graph.book_c_subset import BookSession,BookEventLimitExceeded
class BudgetTests(unittest.TestCase):
 def test_no_snapshot_preflight_counts_all_events_and_preserves_result(self):
  seen=[];s=BookSession([1,2],[(1,2,7)],event_observer=seen.append,event_limit=4000)
  with patch.object(s.machine,'snapshot',wraps=s.machine.snapshot) as snapshots:
   r=s.call('grafo_bfs',[1]);self.assertEqual(snapshots.call_count,0)
  t=BookSession([1,2],[(1,2,7)],trace=True);tr=t.call('grafo_bfs',[1])
  self.assertEqual(seen,tr['events']);self.assertEqual(s.machine.event_count,len(seen));self.assertIsNone(r['memory']);self.assertEqual(r['graph_after'],tr['graph_after']);self.assertEqual(s.machine.events,[]);self.assertEqual(s.transitions,[])
 def test_limit_is_inclusive_and_next_event_never_commits(self):
  full=BookSession();full.call('grafo_insertar_arco',[1,2,7]);n=full.machine.event_count
  good=BookSession(event_limit=n);good.call('grafo_insertar_arco',[1,2,7]);self.assertEqual(good.graph_state(),full.graph_state())
  limited=BookSession(event_limit=0);initial=limited.machine.snapshot()
  with self.assertRaises(BookEventLimitExceeded) as caught:limited.call('grafo_insertar_arco',[1,2,7])
  self.assertEqual(caught.exception.limit,0);self.assertEqual(caught.exception.attempted_events,1);self.assertEqual(limited.machine.snapshot(),initial)
 def test_budget_includes_multicall_boundaries(self):
  full=BookSession();full.call('grafo_insertar_vertice',[1]);n=full.machine.event_count
  limited=BookSession(event_limit=n);limited.call('grafo_insertar_vertice',[1]);state=limited.machine.snapshot()
  with self.assertRaises(BookEventLimitExceeded):limited.call('grafo_insertar_vertice',[2])
  self.assertEqual(limited.machine.snapshot(),state)
 def test_dense_disposable_preflight_aborts_without_retaining_trace(self):
  v=list(range(15));a=[(x,y,((min(x,y)*17+max(x,y)*11)%19)-5) for x in v for y in v if x!=y]
  s=BookSession(v,a,event_limit=4000)
  with self.assertRaises(BookEventLimitExceeded) as caught:s.call('grafo_kruskal')
  self.assertEqual(caught.exception.attempted_events,4001);self.assertEqual(s.transitions,[]);self.assertEqual(s.machine.events,[]);self.assertEqual(v,list(range(15)))
if __name__=='__main__':unittest.main(verbosity=2)
