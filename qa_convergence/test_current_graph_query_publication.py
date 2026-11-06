"""Scalar flags, cost out-cells and borrowed pointers stay distinct at receipt."""
import unittest
from _canonical_publication_contract import canonical_history, execute, receipt, assert_narration_does_not_change_execution

H = canonical_history([{'operation': 'insert_vertex', 'payload': {'vertex': v}} for v in [1, 2]] +
    [{'operation': 'insert_edge', 'payload': {'origin': 1, 'target': 2, 'weight': 9}}])
CASES = [('exists_vertex', {'vertex': 1}, 'int'), ('exists_vertex', {'vertex': 9}, 'int'),
    ('exists_edge', {'origin': 1, 'target': 2}, 'int'), ('exists_edge', {'origin': 2, 'target': 9}, 'int'),
    ('edge_weight', {'origin': 1, 'target': 2}, 'int'), ('edge_weight', {'origin': 1, 'target': 9}, 'int'),
    ('list_vertices', {}, 'ListaVertice'), ('list_edges', {}, 'ListaArco')]
FUNCTIONS = dict(exists_vertex='grafo_existe_vertice', exists_edge='grafo_existe_arco',
    edge_weight='grafo_costo_arco', list_vertices='grafo_vertices', list_edges='grafo_arcos')


class Publication(unittest.TestCase):
    def test_typed_results(self):
        for op, payload, kind in CASES:
            with self.subTest(op=op, payload=payload):
                body = execute(op, payload, H); trace = body['execution_trace']
                frame = receipt(trace, FUNCTIONS[op]); event = frame['instruction_event']; memory = frame['memory_state']
                self.assertFalse(event['C_executed']); self.assertEqual(event['return_type'], kind)
                self.assertEqual(memory['external']['result'], {'type': kind, 'value': body['c_return']})
                self.assertEqual(trace['steps'][-1]['phase'], 'api_publication')
                if kind.startswith('Lista'):
                    self.assertEqual(body['ownership'], 'borrowed')
                    self.assertEqual(body['c_return'], memory['graph']['v' if kind == 'ListaVertice' else 'a'])
                    self.assertTrue(all('prestada' in text for text in frame['narration'].values()))
                else:
                    self.assertIn(body['c_return'], (0, 1))
                    if op == 'edge_weight':
                        self.assertEqual(body['output'], 9 if body['success'] else 'sin inicializar')
                        self.assertTrue(all('salida entera' in text for text in frame['narration'].values()))
                    else:
                        self.assertIs(body['result'], bool(body['c_return']))
                self.assertEqual(body['history'][:-1], H)

    def test_narration_does_not_change_queries_or_absent_results(self):
        for op, payload, _ in CASES:
            for h in (H, []):
                assert_narration_does_not_change_execution(op, payload, h)
