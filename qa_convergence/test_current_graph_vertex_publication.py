"""Vertex publication is a host boundary after actual canonical C execution."""
import unittest
from _canonical_publication_contract import canonical_history, execute, receipt, assert_narration_does_not_change_execution

H = canonical_history([{'operation': 'insert_vertex', 'payload': {'vertex': v}} for v in [1, 2]] +
    [{'operation': 'insert_edge', 'payload': {'origin': 1, 'target': 2, 'weight': 3}}])
CASES = [('insert_vertex', 3, H), ('insert_vertex', 1, H), ('remove_vertex', 1, H),
         ('remove_vertex', 9, H), ('insert_vertex', 1, [])]


class Publication(unittest.TestCase):
    def test_operation_specific_boundary(self):
        for op, vertex, h in CASES:
            with self.subTest(op=op, vertex=vertex):
                body = execute(op, {'vertex': vertex}, h)
                trace = body['execution_trace']; final = trace['steps'][-1]
                self.assertFalse(final['pedagogy']['instruction_event']['C_executed'])
                self.assertEqual(final['line_text'], ''); self.assertIsNone(final['line_index'])
                self.assertEqual(final['phase'], 'api_publication')
                function = 'grafo_insertar_vertice' if op == 'insert_vertex' else 'grafo_eliminar_vertice'
                frame = receipt(trace, function)
                self.assertEqual(frame['memory_state']['graph'], frame['instruction_event']['returned'])
                self.assertTrue(any(e['function'] == function for e in trace['C_instruction_events']))
                expected_edges = 0 if not h or (op == 'remove_vertex' and vertex == 1) else 1
                self.assertEqual(len(final['state_after']['edges']), expected_edges)
                self.assertEqual(body['history'][:-1], h)
                self.assertEqual(body['history'][-1]['operation'], op)
                self.assertEqual(final['pedagogy']['instruction_state_before'], final['pedagogy']['instruction_state_after'])

    def test_narration_preserves_executed_source_and_all_states(self):
        for op, vertex, h in CASES:
            assert_narration_does_not_change_execution(op, {'vertex': vertex}, h)
