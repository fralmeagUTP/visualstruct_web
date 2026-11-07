"""Current Graph allocation acceptance; historical harness remains preserved.

Telemetry is inserted only into a temporary copy of the existing QA harness.
The repository's C/H sources and its thirty scenario/fault inputs are unchanged.
"""
from copy import deepcopy
from pathlib import Path
import subprocess
import tempfile
import re
import unittest
from app.domain.graph.book_c_subset import BookSession

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = {0: ((), ()), 1: ((1,), ()), 2: ((2,), ()),
             3: ((1, 2), ()), 4: ((), ()), 5: ((1, 2), ((1, 2, 3),))}
CASE_KEYS = {(scenario, fault) for scenario in SCENARIOS for fault in range(5)}
# C allocates each missing distinct endpoint and then one new edge; an existing
# edge only changes cost. These counts are independently checked against runs.
NORMAL_ALLOCATION_CALLS = {0: 3, 1: 2, 2: 2, 3: 1, 4: 2, 5: 0}
_CALL_MARKER = 'g = grafo_insertar_arco(g, 1, scenario == 4 ? 1 : 2, 9, &status);'
_TELEMETRY = '''
            printf("attempt scenario=%d fault=%d calls=%d reached=%d atomic=%d\\n",
                   scenario, fault, calls, fault != 0 && calls >= fault,
                   status != GRAFO_MEMORIA || (g.v == before.v && g.a == before.a));
'''


def run_native_harness(source=None, *, instrument=True):
    """Compile and execute a temporary instrumented copy; return exit and text."""
    if source is None:
        source = (ROOT / 'qa_convergence/graph_edge_allocation.c').read_text()
    assert source.count(_CALL_MARKER) == 1, 'Unexpected harness operation marker'
    marker = '            int invariant = 1;'
    assert source.count(marker) == 1, 'Unexpected harness telemetry marker'
    assert source.index(_CALL_MARKER) < source.index(marker), 'Telemetry precedes operation'
    instrumented = source.replace(marker, _TELEMETRY + marker) if instrument else source
    with tempfile.TemporaryDirectory() as td:
        harness = Path(td) / 'instrumented.c'
        harness.write_text(instrumented)
        exe = str(Path(td) / 'graph_faults')
        subprocess.run(['gcc', '-std=c17', '-Wall', '-Wextra', '-Werror', '-pedantic',
            '-I' + str(ROOT / 'docs/tads_C'), str(harness),
            str(ROOT / 'docs/tads_C/tad_grafo.c'),
            '-Wl,--wrap=malloc', '-Wl,--wrap=free', '-o', exe],
            check=True, capture_output=True, timeout=30)
        return subprocess.run([exe], capture_output=True, text=True, timeout=15)


def parse_native_output(output):
    rows, attempts = {}, {}
    for line in output.splitlines():
        match = re.fullmatch(r'scenario=(\d+) fault=(\d+) endpoints=(\d+) vertices=(\d+) edges=(\d+) status=(\d+) cost=(-?\d+) live_after_cleanup=(-?\d+) result=(PASS|FAIL)', line)
        if match:
            scenario, fault, endpoints, vertices, edges, status, cost, live, result = match.groups()
            key = int(scenario), int(fault)
            assert key not in rows, 'Duplicate native case'
            rows[key] = dict(endpoints=int(endpoints), vertices=int(vertices), edges=int(edges),
                             status=int(status), cost=int(cost), live=int(live), result=result)
            continue
        match = re.fullmatch(r'attempt scenario=(\d+) fault=(\d+) calls=(\d+) reached=([01]) atomic=([01])', line)
        assert match, 'Unexpected native output line'
        scenario, fault, calls, reached, atomic = map(int, match.groups())
        key = scenario, fault
        assert key not in attempts, 'Duplicate native attempt'
        attempts[key] = dict(calls=calls, reached=bool(reached), atomic=bool(atomic))
    return rows, attempts


def assert_native_contract(testcase, rows, attempts, returncode):
    testcase.assertEqual(set(rows), CASE_KEYS, 'native case matrix')
    testcase.assertEqual(set(attempts), CASE_KEYS, 'native telemetry matrix')
    for key in sorted(CASE_KEYS):
        scenario, fault = key
        row, attempt = rows[key], attempts[key]
        normal_calls = NORMAL_ALLOCATION_CALLS[scenario]
        reached = bool(fault and fault <= normal_calls)
        testcase.assertEqual(attempt['calls'], fault if reached else normal_calls, 'native allocation attempts')
        testcase.assertEqual(attempt['reached'], reached, 'native fault reachability')
        testcase.assertEqual(row['status'], 1 if reached else 0, 'native status')
        testcase.assertTrue(attempt['atomic'], 'native pointer atomicity')
        testcase.assertEqual(row['endpoints'], 1, 'native endpoints')
        testcase.assertEqual(row['live'], 0, 'native cleanup')
        testcase.assertEqual(row['result'], 'PASS', 'native harness assertions')
        if not reached:
            testcase.assertEqual((row['edges'], row['cost']), (1, 9), 'native successful edge')
    testcase.assertEqual(returncode, 0, 'native executable completion')
    testcase.assertEqual(sum(x['reached'] for x in attempts.values()), 10, 'actual injected failures')


def symbolic_observation(scenario, fault):
    vertices, arcs = SCENARIOS[scenario]
    session = BookSession(vertices, arcs, fail_allocation=fault or None, trace=True)
    before = session.graph_state()
    before_pointers = deepcopy(session.machine.graph)
    result = session.call('grafo_insertar_arco', [1, 1 if scenario == 4 else 2, 9])
    session.call('grafo_destruir')
    return dict(before=before, before_pointers=before_pointers, result=result,
                cleanup_heap=deepcopy(session.machine.heap), cleanup_graph=session.graph_state(),
                cleanup_pointers=deepcopy(session.machine.graph))


def assert_symbolic_contract(testcase, observation, native, attempt, fault):
    result = observation['result']
    state = result['graph_after']
    reachable = set(state['vertices'])
    for origin, target, _ in state['arcs']:
        testcase.assertIn(origin, reachable, 'symbolic endpoint')
        testcase.assertIn(target, reachable, 'symbolic endpoint')
    testcase.assertEqual(len(reachable), native['vertices'], 'symbolic vertex count')
    testcase.assertEqual(len(state['arcs']), native['edges'], 'symbolic edge count')
    testcase.assertEqual(result['status'], native['status'], 'symbolic status')
    cost = state['arcs'][0][2] if state['arcs'] else 0
    testcase.assertEqual(cost, native['cost'], 'symbolic cost')
    testcase.assertEqual(result['memory']['allocation_attempts'], attempt['calls'], 'symbolic allocation attempts')
    testcase.assertEqual(bool(fault and result['memory']['allocation_attempts'] >= fault),
                         attempt['reached'], 'symbolic fault reachability')
    if result['status'] == 1:
        testcase.assertEqual(state, observation['before'], 'symbolic state atomicity')
        testcase.assertEqual(result['memory']['graph'], observation['before_pointers'], 'symbolic pointer atomicity')
        testcase.assertEqual(result['memory']['allocations'], result['memory']['frees'], 'symbolic temporary allocation balance')
    if not attempt['reached']:
        testcase.assertEqual((len(state['arcs']), cost), (1, 9), 'symbolic successful edge')
    testcase.assertEqual(observation['cleanup_heap'], {}, 'symbolic cleanup heap')
    testcase.assertEqual(observation['cleanup_graph'], {'vertices': [], 'arcs': [], 'marks': {}}, 'symbolic cleanup graph')
    testcase.assertEqual(observation['cleanup_pointers'], {'v': 'NULL', 'a': 'NULL'}, 'symbolic cleanup roots')


class GraphAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = run_native_harness()
        cls.native_output = result.stdout
        cls.native_returncode = result.returncode
        cls.native_records, cls.native_attempts = parse_native_output(result.stdout)
        # Compatibility for explicit migrated wrappers; not a legacy execution.
        cls.native_rows = {key: tuple(row[k] for k in ('vertices', 'edges', 'status', 'cost'))
                           for key, row in cls.native_records.items()}

    def test_native_faults_and_cleanup(self):
        assert_native_contract(self, self.native_records, self.native_attempts, self.native_returncode)

    def test_symbolic_same_faults_preserve_endpoints(self):
        self.assertEqual(set(self.native_records), CASE_KEYS)
        self.assertEqual(set(self.native_attempts), CASE_KEYS)
        for scenario, fault in sorted(CASE_KEYS):
            with self.subTest(scenario=scenario, fault=fault):
                assert_symbolic_contract(self, symbolic_observation(scenario, fault),
                                         self.native_records[(scenario, fault)],
                                         self.native_attempts[(scenario, fault)], fault)


if __name__ == '__main__':
    unittest.main()
