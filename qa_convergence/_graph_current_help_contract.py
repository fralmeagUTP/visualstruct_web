"""Rendered Graph help acceptance for the explicitly adopted book contract."""
import html
import json
from pathlib import Path
import re
import tempfile
from app import create_app
from app.config import Config
from app.domain.graph.educational_capacity import MAX_VERTICES
from app.services.graph_help_service import GraphHelpService

ROOT = Path(__file__).resolve().parents[1]
AUXILIARY = ('exists_vertex', 'exists_edge', 'clear_graph')
PHASES = ('construccion', 'recorridos', 'camino-minimo', 'expansion-minima')


def capture_current_graph_help():
    with tempfile.TemporaryDirectory() as folder:
        class T(Config):
            TESTING = True
            SESSION_CACHE_DIR = folder
        client = create_app(T).test_client()
        response = client.get('/help/graph/graph')
        pages = {}
        for phase in PHASES:
            page = client.get('/graph/graph/' + phase)
            pages[phase] = {'status': page.status_code, 'html': page.get_data(as_text=True)}
        return {'status': response.status_code, 'html': response.get_data(as_text=True),
                'structure': GraphHelpService.get_structure_help('graph'),
                'module': GraphHelpService.get_module_help(), 'pages': pages}


def assert_graph_help_capture(case, captured):
    case.assertEqual(captured['status'], 200, 'help_http_status')
    markup = captured['html']
    plain = html.unescape(re.sub('<[^>]+>', '', markup))
    case.assertIn(f'aplicación es {MAX_VERTICES} vértices', plain, 'help_rendered_capacity')
    case.assertNotIn('200 vértices', plain, 'help_obsolete_capacity')
    case.assertIn('no es un límite del TAD C', plain, 'help_app_c_distinction')
    case.assertIn('cola de índices propia, sin depender del TAD Cola', plain, 'help_index_queue')
    case.assertNotRegex(plain, r'(?i)(?:usa|depende del|requiere el) TAD Cola', 'help_no_external_queue')
    case.assertNotIn('>queue</a>', markup, 'help_translated_label')
    for operation in AUXILIARY:
        pattern = r'<dt>[^\n]*<code>' + re.escape(operation) + r'</code></dt>\s*<dd>(.*?)</dd>'
        matches = re.findall(pattern, markup, re.S)
        case.assertEqual(len(matches), 1, 'help_auxiliary_entry:' + operation)
        description = html.unescape(re.sub('<[^>]+>', '', matches[0]))
        case.assertIn('API', description, 'help_auxiliary_api:' + operation)
        case.assertRegex(description, r'(?:no aparece como opción independiente del selector|sin control independiente en el selector)', 'help_auxiliary_selector:' + operation)
        case.assertNotRegex(description, r'(?:con control independiente en el selector|aparece en el selector)', 'help_auxiliary_no_contradiction:' + operation)
    case.assertEqual(captured['structure']['max_vertices'], MAX_VERTICES, 'help_structure_capacity')
    case.assertIn(str(MAX_VERTICES), captured['module']['tips'][0], 'help_tip_capacity')
    case.assertTrue(set(AUXILIARY).issubset(captured['structure']['supported_operations']), 'help_auxiliary_api_support')
    case.assertEqual(set(captured['pages']), set(PHASES), 'help_all_phases')
    for phase, page in captured['pages'].items():
        case.assertEqual(page['status'], 200, 'help_phase_status:' + phase)
        for attribute in ('data-allowed-operations', 'data-allowed-algorithms'):
            matches = re.findall(attribute + r"='([^']*)'", page['html'])
            case.assertEqual(len(matches), 1, 'help_selector_attribute:' + attribute)
            allowed = json.loads(html.unescape(matches[0]))
            case.assertFalse(set(AUXILIARY).intersection(allowed), 'help_no_auxiliary_selector:' + phase)
    case.assertEqual(markup.count('id="graph-canonical-source"'), 1, 'help_source_section')
    code_blocks = re.findall(r'<pre id="graph-canonical-code"[^>]*>([\s\S]*?)</pre>', markup)
    case.assertEqual(len(code_blocks), 1, 'help_source_block')
    code = html.unescape(code_blocks[0])
    canonical = (ROOT / 'docs/tads_C/tad_grafo.c').read_text()
    case.assertEqual(code, canonical, 'help_exact_canonical_code')
    links = re.findall(r'data-book-function="([^"]+)"', markup)
    case.assertTrue(links, 'help_function_links_nonempty')
    case.assertEqual(links.count('grafo_bfs'), 1, 'help_bfs_link')
    for name in ('grafo_existe_vertice', 'grafo_existe_arco'):
        case.assertIn(name, links, 'help_query_function_link')
    for name in links:
        case.assertRegex(code, r'\b' + re.escape(name) + r'\s*\([^;{}]*\)\s*\{', 'help_real_function_definition:' + name)


def assert_current_graph_help(testcase):
    assert_graph_help_capture(testcase, capture_current_graph_help())
