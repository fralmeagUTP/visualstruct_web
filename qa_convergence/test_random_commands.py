import copy,unittest
from app.domain.graph.graph_commands import materialize_random_commands
from app.adapters.graph_adapter import GraphAdapter
class RandomCommandsTests(unittest.TestCase):
 def test_existing_generator_sequence_matches_without_tad_dependency(self):
  for directed in (False,True):
   for count in (1,2,5,15):
    for seed in (0,1,27102026):
     payload={'vertices_count':count,'seed':seed};saved=copy.deepcopy(payload)
     adapter=GraphAdapter();adapter.execute('create_graph',{'directed':directed});adapter.execute('generate_random_graph',payload)
     _,commands=materialize_random_commands(payload,directed,require_seed=True)
     replay=GraphAdapter();replay.execute('create_graph',{'directed':directed})
     for c in commands:replay.execute(c['operation'],c['payload'])
     self.assertEqual(adapter.graph._g._vertices,replay.graph._g._vertices)
     self.assertEqual(adapter.graph._g._arcos,replay.graph._g._arcos);self.assertEqual(payload,saved)
 def test_export_without_seed_is_rejected(self):
  with self.assertRaises(ValueError):materialize_random_commands({'vertices_count':3},require_seed=True)
if __name__=='__main__':unittest.main()
