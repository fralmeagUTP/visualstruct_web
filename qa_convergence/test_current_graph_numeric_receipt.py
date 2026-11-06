"""Canonical caller receipt describes the C pointer before explicit cleanup."""
import unittest
from _canonical_publication_contract import canonical_history, execute, receipt, assert_narration_does_not_change_execution


def history(edges, directed=True):
    return canonical_history([{'operation': 'create_graph', 'payload': {'directed': directed}}] +
        [{'operation': 'insert_vertex', 'payload': {'vertex': v}} for v in [1, 2, 3]] +
        [{'operation': 'insert_edge', 'payload': {'origin': a, 'target': b, 'weight': w}} for a, b, w in edges])


CASES = [('run_bellman_ford', {'start': 1, 'end': 3}, [(1, 2, 1), (2, 3, -3), (3, 2, 1)]),
    ('run_bellman_ford', {'start': 1, 'end': 3}, [(1, 2, 1)]),
    ('run_bellman_ford', {'start': 1, 'end': 3}, [(1, 2, 1), (2, 3, 2)]),
    ('run_dijkstra', {'start': 1, 'end': 3}, [(1, 2, 1)]),
    ('run_dijkstra', {'start': 1, 'end': 3}, [(1, 2, 1), (2, 3, 2)]),
    ('run_kruskal', {}, []), ('run_prim', {'start': 1}, [])]


class Receipt(unittest.TestCase):
    def test_null_and_owned_receipt(self):
        nulls = owned = 0
        for op, payload, edges in CASES:
            with self.subTest(op=op, edges=edges):
                body = execute(op, payload, history(edges, op not in {'run_prim', 'run_kruskal'}))
                trace = body['execution_trace']; frame = receipt(trace, 'grafo_' + op[4:])
                event = frame['instruction_event']
                isnull = event['returned'] == 'NULL'; nulls += isnull; owned += not isnull
                self.assertEqual(event['returned'], body['c_return'])
                self.assertFalse(event['C_executed'])
                for text in frame['narration'].values():
                    if isnull:
                        self.assertIn('NULL', text); self.assertIn('no hay lista', text)
                    else:
                        self.assertIn('lista propia', text); self.assertIn('no la libera', text)
                if not isnull:
                    memory = frame['memory_state']
                    self.assertIn(event['returned'], {n['id'] for n in memory['heap_nodes']})
                    self.assertGreater(memory['allocations'], memory['frees'])
                final = trace['steps'][-1]['pedagogy']['memory_state']
                self.assertEqual(final['allocations'], final['frees'])
                self.assertEqual(trace['steps'][-1]['phase'], 'api_publication')
        self.assertGreater(nulls, 0); self.assertGreater(owned, 0)

    def test_narration_is_independent_of_canonical_execution(self):
        for op, payload, edges in CASES:
            assert_narration_does_not_change_execution(op, payload,
                history(edges, op not in {'run_prim', 'run_kruskal'}))
