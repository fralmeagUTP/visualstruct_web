"""Native canonical allocation faults and the same calls in the symbolic engine."""
from pathlib import Path
import subprocess
import tempfile
import re
import unittest
from app.domain.graph.book_c_subset import BookSession

ROOT = Path(__file__).resolve().parents[1]


class GraphAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            exe = str(Path(td) / 'graph_faults')
            subprocess.run(['gcc', '-std=c17', '-Wall', '-Wextra', '-Werror', '-pedantic',
                '-I' + str(ROOT / 'docs/tads_C'), str(ROOT / 'qa_convergence/graph_edge_allocation.c'),
                str(ROOT / 'docs/tads_C/tad_grafo.c'),
                '-Wl,--wrap=malloc', '-Wl,--wrap=free', '-o', exe], check=True, timeout=30)
            result = subprocess.run([exe], check=True, capture_output=True, text=True, timeout=15)
            cls.native_rows = {(int(a), int(b)): tuple(map(int, (c, d, e, f))) for a, b, c, d, e, f in re.findall(
                r'scenario=(\d+) fault=(\d+) endpoints=1 vertices=(\d+) edges=(\d+) status=(\d+) cost=(-?\d+)', result.stdout)}
            cls.native_output = result.stdout

    def test_native_faults_and_cleanup(self):
        self.assertEqual(self.native_output.count('result=PASS'), 30)
        self.assertEqual(self.native_output.count('live_after_cleanup=0'), 30)
        self.assertEqual(len(self.native_rows), 30)

    def test_symbolic_same_faults_preserve_endpoints(self):
        for scenario in range(6):
            for fault in range(5):
                with self.subTest(scenario=scenario, fault=fault):
                    vertices = {0: [], 1: [1], 2: [2], 3: [1, 2], 4: [], 5: [1, 2]}[scenario]
                    arcs = [(1, 2, 3)] if scenario == 5 else []
                    session = BookSession(vertices, arcs, fail_allocation=fault or None, trace=True)
                    before = session.graph_state()
                    result = session.call('grafo_insertar_arco', [1, 1 if scenario == 4 else 2, 9])
                    state = result['graph_after']; reachable = set(state['vertices'])
                    for origin, target, _ in state['arcs']:
                        self.assertIn(origin, reachable); self.assertIn(target, reachable)
                    cost = state['arcs'][0][2] if state['arcs'] else 0
                    self.assertEqual((len(reachable), len(state['arcs']), result['status'], cost),
                                     self.native_rows[(scenario, fault)])
                    if result['status'] == 1:
                        self.assertEqual(state, before)
                        self.assertEqual(result['memory']['allocations'], result['memory']['frees'])
                    if fault == 0:
                        self.assertEqual(len(state['arcs']), 1); self.assertEqual(cost, 9)
                    session.call('grafo_destruir')
                    self.assertEqual(session.machine.heap, {})
                    self.assertEqual(session.graph_state(), {'vertices': [], 'arcs': [], 'marks': {}})


if __name__ == '__main__':
    unittest.main()
