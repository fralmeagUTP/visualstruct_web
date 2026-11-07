"""Negative controls for exact Graph browser text and copied C observers."""
import pytest
from _book_graph_browser_contract import assert_browser_row, main_text


def row_and_body(stdout='', prefix=''):
    memory = {'heap_nodes': [], 'graph': {'v': 'NULL', 'a': 'NULL'},
        'retired_objects': [], 'returned': None, 'console_stdout': stdout}
    variable = {'type': 'int', 'name': 'x', 'scope': 'grafo_bfs', 'previous': 1, 'value': 10}
    frame = {'memory_state': memory, 'construction_operation': False,
        'call_stack': [], 'variables': [variable], 'auxiliary': {'items': []},
        'traversal': {'tree_edges': [], 'discovery_order': []}, 'condition': None,
        'instruction_event': {'C_executed': True}}
    body = {'console_prefix': prefix, 'message': 'Final', 'execution_trace': {'steps': [
        {'pedagogy': frame, 'state_after': {'nodes': []}, 'line_index': 0}]}}
    expected = prefix + stdout
    row = {'index': 0, 'direction': 'forward', 'heap': [], 'live': [], 'liveCards': [],
        'heads': 'Grafo prestado: {"v":"NULL","a":"NULL"}',
        'retired': 'Retiradas (sólo registro histórico): []', 'returned': 'Retorno al caller: null',
        'stack': [], 'variables': [{'name': 'x', 'scope': 'grafo_bfs', 'text': 'int x (grafo_bfs): 1 → 10'}],
        'auxiliary': '[]', 'traversal': ['[]', '[]'], 'stdout': expected,
        'stdoutVisible': expected or '(sin salida printf en esta ruta)',
        'message': 'Final', 'svgNodes': 0, 'highlighted': [0]}
    return row, body


@pytest.mark.parametrize('stdout,prefix', [('', ''), ('', 'past\n'), ('\n\n', ''),
    (' áéñ \n áéñ \n', 'prior\n'), ('7 7\n', '')])
def test_graph_visible_stdout_matches_exact_raw_bytes(stdout, prefix):
    row, body = row_and_body(stdout, prefix)
    assert_browser_row(row, body)


@pytest.mark.parametrize('stdout,visible', [('', ''), ('', 'FORGED VISIBLE OUTPUT'),
    ('7 7\n', '7\n'), (' áéñ \n', 'áéñ'), ('\n\n', '\n')])
def test_graph_stdout_rejects_corrupt_screen_even_with_correct_copy(stdout, visible):
    row, body = row_and_body(stdout)
    row['stdoutVisible'] = visible
    with pytest.raises(AssertionError):
        assert_browser_row(row, body)


@pytest.mark.parametrize('text', ['WRONG_TYPE int x (grafo_bfs): 1 → 10 EXTRA_FORGED_TEXT',
    'long x (grafo_bfs): 1 → 10', 'int x (grafo_bfs): 10 → 10',
    'int x (grafo_bfs): 1 → 100', 'int x (wrong_scope): 1 → 10',
    'int y (grafo_bfs): 1 → 10', ' int x (grafo_bfs): 1 → 10',
    'int x (grafo_bfs): 1 → 10 '])
def test_graph_variables_require_exact_type_scope_and_values(text):
    row, body = row_and_body()
    row['variables'][0]['text'] = text
    with pytest.raises(AssertionError):
        assert_browser_row(row, body)


class MainPage:
    """Minimal page protocol to exercise the actual shared strict reader."""
    def __init__(self, lines, raw, indices):
        self.lines, self.raw, self.indices = lines, raw, indices

    def locator(self, selector):
        assert selector in {'.didactic-history-main', '.code-line', '.didactic-history-main .code-line'}
        return self

    def all_text_contents(self):
        return self.lines

    def evaluate_all(self, expression):
        return self.indices

    def evaluate(self, expression):
        return self.raw


def test_graph_main_preserves_raw_indentation_empty_rows_and_trailing_newline():
    raw = 'int main(void) {\n\n    return 0;  \n}\n'
    lines = raw.split('\n')
    # Only a truly empty copied line can use the approved one-space layout sentinel.
    lines[1] = ' '
    assert main_text(MainPage(lines, raw, list(range(len(lines))))) == raw


@pytest.mark.parametrize('lines,raw,indices', [
    (['printf("A\u00a0B");'], 'printf("A\u00a0B");', [0]),
    (['printf("AB");'], 'printf("A\u00a0B");', [0]),
    (['printf("A\u00a0B");'], 'printf("AB");', [0]),
    (['    return 0;'], '   return 0;', [0]),
    (['line'], 'line ', [0]),
    (['a', 'b'], 'a\nb', [1, 0]),
    (['a'], None, [0]),
    (['a'], 'a\n', [0]),
])
def test_graph_main_rejects_nbsp_or_changed_source_instead_of_normalizing(lines, raw, indices):
    with pytest.raises(AssertionError):
        main_text(MainPage(lines, raw, indices))
