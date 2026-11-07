"""Explicit current-contract assertions shared by the migrated acceptance oracles."""

LEVELS = {'basic', 'intermediate', 'advanced'}


def narration_levels(case, frame):
    narration = frame['narration']
    case.assertEqual(set(narration), LEVELS, 'narration_levels')
    for text in narration.values():
        case.assertIsInstance(text, str, 'narration_text')
        case.assertTrue(text.strip(), 'narration_text')
    return narration.values()


def assert_caller_receipt(case, frame):
    event = frame['instruction_event']
    case.assertEqual(event['phase'], 'caller_receipt', 'caller_phase')
    case.assertFalse(event['C_executed'], 'caller_non_c')
    case.assertEqual(event['source_role'], 'caller', 'caller_role')
    for text in narration_levels(case, frame):
        case.assertIn('Retorno al caller:', text, 'caller_attribution')
        case.assertIn('No se ejecuta otra instrucción C.', text, 'caller_non_c_narration')
        case.assertNotRegex(text, r'(?i)(?:C|TAD) ejecuta', 'caller_no_c_claim')


def assert_api_publication(case, final, function):
    case.assertEqual(final['phase'], 'api_publication', 'api_phase')
    case.assertEqual(final['line_text'], '', 'api_no_c_line')
    case.assertIsNone(final['line_index'], 'api_no_c_index')
    frame = final['pedagogy']; event = frame['instruction_event']
    case.assertEqual(event['phase'], 'api_publication', 'api_event_phase')
    case.assertFalse(event['C_executed'], 'api_non_c')
    case.assertEqual(event['source_role'], 'application', 'api_role')
    case.assertIsNone(event['function'], 'api_no_c_function')
    case.assertEqual(frame['instruction_state_before'], frame['instruction_state_after'], 'api_no_mutation')
    for text in narration_levels(case, frame):
        case.assertIn('Frontera de la aplicación:', text, 'api_attribution')
        case.assertIn(function, text, 'api_operation')
        case.assertIn('No es una instrucción del TAD.', text, 'api_non_c_narration')
        case.assertNotRegex(text, r'(?i)(?:C|TAD) ejecuta', 'api_no_c_claim')


def assert_query_graph_unchanged(case, trace):
    before = trace['steps'][0]['state_after']
    after = trace['steps'][-1]['state_after']
    for key in ('directed', 'weighted', 'nodes', 'edges', 'c_arcs', 'asymmetric_pairs', 'source_contract'):
        case.assertEqual(before[key], after[key], 'query_graph_unchanged:' + key)

    for key in ('vertices_count', 'edges_count', 'is_empty'):
        case.assertEqual(before['metadata'][key], after['metadata'][key], 'query_graph_metadata:' + key)
    case.assertEqual(after['metadata']['c_arcs_count'], len(after['c_arcs']), 'query_arc_count')
