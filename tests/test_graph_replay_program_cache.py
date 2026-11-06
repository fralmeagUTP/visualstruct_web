"""A replay may share syntax but must never share machine state or skip C calls."""
from copy import deepcopy
import pytest
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph import book_c_subset as book
from app.services.graph_structure_service import GraphStructureService as S
from scripts.benchmark_replay import graph_history


def test_replay_compiles_each_source_once_and_discards_request_cache(monkeypatch):
    original = book.Program; calls = []
    def compile_source(source, **kwargs):
        calls.append((source, kwargs.get('caller_output', False)))
        return original(source, **kwargs)
    monkeypatch.setattr(book, 'Program', compile_source)
    history = graph_history(34)
    adapter, valid = S._rebuild_adapter('graph', history)
    assert valid == history and valid is not history
    assert len(calls) == len(set(calls))
    assert sum(not caller for _, caller in calls) == 1
    assert not hasattr(adapter, '_book_program_cache')
    prior = len(calls)
    S._rebuild_adapter('graph', history)
    assert len(calls) == 2 * prior, 'Cache lifetime must end with each reconstruction'


def test_cached_replay_matches_uncached_calls_and_stdout(monkeypatch):
    commands = [('create_graph', {'directed': True}), ('insert_edge', {'origin': 1, 'target': 2, 'weight': 3}),
        ('run_dijkstra', {'start': 1, 'end': 2}), ('list_vertices', {}), ('remove_vertex', {'vertex': 2}),
        ('insert_edge', {'origin': 3, 'target': 4, 'weight': 1, 'fail_allocation': 1}),
        ('run_bfs', {'start': 99}), ('clear_graph', {})]
    history = [dict(operation=op, payload=p, source_contract=S.SOURCE_CONTRACT) for op, p in commands]
    expected = GraphAdapter(); stdout = ''
    for op, payload in commands:
        expected.execute(op, deepcopy(payload)); stdout += expected._last_book_execution['stdout']
    executed = []; original = GraphAdapter.execute
    def observe(self, operation, payload):
        executed.append(operation); return original(self, operation, payload)
    monkeypatch.setattr(GraphAdapter, 'execute', observe)
    actual, valid = S._rebuild_adapter('graph', history)
    assert executed == [op for op, _ in commands]
    assert actual.to_visual_state() == expected.to_visual_state()
    assert actual._console_history_stdout == stdout and valid == history


def test_invalid_c_source_does_not_hit_replay_cache(monkeypatch):
    cache = {}; source = book.canonical_source()
    book.compiled_program(source, cache=cache)
    with pytest.raises(ValueError, match='byte-exact'):
        book.compiled_program(source + '\n', cache=cache)


def test_benchmark_graph_history_is_versioned_and_reaches_capacity():
    from app.domain.graph.educational_capacity import MAX_VERTICES
    history = graph_history(300)
    assert len(history) == 300 and S.history_issue(history) is None
    assert history[0]['operation'] == 'create_graph'
    assert [entry['payload']['vertex'] for entry in history[1:MAX_VERTICES + 1]] == list(range(1, MAX_VERTICES + 1))
    assert history[MAX_VERTICES + 1]['operation'] == 'create_graph'


@pytest.mark.parametrize('function,arguments', [('grafo_insertar_arco', [1, 2, 7]),
    ('grafo_bfs', [1]), ('grafo_dijkstra', [1, 2])])
def test_unobserved_execution_keeps_events_count_and_exact_result(function, arguments):
    traced = book.BookSession([1, 2], [(1, 2, 7)], trace=True)
    untraced = book.BookSession([1, 2], [(1, 2, 7)])
    observed_events = []
    observed = book.BookSession([1, 2], [(1, 2, 7)], event_observer=observed_events.append)
    expected = traced.call(function, arguments)
    for session in (untraced, observed):
        result = session.call(function, arguments)
        for key in ('returned', 'status', 'output', 'graph_after', 'result_items', 'memory', 'event_count', 'call_event_count'):
            assert result[key] == expected[key], key
    assert observed_events == expected['events']
    for token in traced.program.tokens:
        assert token.line == traced.source.count('\n', 0, token.pos)
