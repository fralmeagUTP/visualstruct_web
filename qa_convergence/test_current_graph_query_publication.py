"""Scalar flags, cost out-cells and borrowed pointers stay distinct at receipt."""
import unittest
from qa_convergence._graph_publication_assertions import narration_levels, assert_caller_receipt, assert_api_publication, assert_query_graph_unchanged
from qa_convergence._canonical_publication_contract import canonical_history, execute, receipt, assert_narration_does_not_change_execution

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
                self.assertEqual(trace['steps'][-1]['phase'], 'api_publication', 'api_phase')
                assert_caller_receipt(self, frame)
                assert_api_publication(self, trace['steps'][-1], FUNCTIONS[op])
                assert_query_graph_unchanged(self, trace)
                self.assertTrue(any(e['function'] == FUNCTIONS[op] and e['C_executed'] for e in trace['C_instruction_events']), 'query_actual_c')
                if kind.startswith('Lista'):
                    self.assertEqual(body['ownership'], 'borrowed')
                    self.assertEqual(body['c_return'], memory['graph']['v' if kind == 'ListaVertice' else 'a'])
                    self.assertTrue(all('prestada' in text for text in frame['narration'].values()))
                else:
                    self.assertIn(body['c_return'], (0, 1))
                    for text in list(narration_levels(self, frame)) + list(narration_levels(self, trace['steps'][-1]['pedagogy'])):
                        self.assertNotIn('lista', text.lower(), 'scalar_not_list')
                    if op == 'edge_weight':
                        expected_success = payload['target'] == 2
                        self.assertIs(body['success'], expected_success, 'cost_success_flag')
                        self.assertEqual(body['c_return'], int(expected_success), 'cost_return_flag')
                        self.assertEqual(body['output'], 9 if expected_success else 'sin inicializar', 'cost_separate_output')
                        self.assertEqual(memory['external']['salida'], {'type': 'int', 'value': body['output']}, 'cost_external_output')
                        self.assertTrue(all('salida entera' in text for text in frame['narration'].values()))
                    else:
                        self.assertIs(body['result'], bool(body['c_return']))
                self.assertEqual(body['history'][:-1], H)

    def test_narration_does_not_change_queries_or_absent_results(self):
        for op, payload, _ in CASES:
            for h in (H, []):
                assert_narration_does_not_change_execution(op, payload, h)
