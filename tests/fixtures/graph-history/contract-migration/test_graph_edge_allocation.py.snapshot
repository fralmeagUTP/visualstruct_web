"""Native allocation faults and identical source-bound symbolic construction."""
from pathlib import Path
import subprocess
import tempfile
import re
import unittest
from app.services.c_code_service import CCodeService
from app.domain.graph.construction_instruction import ConstructionProgram, ConstructionMachine

ROOT = Path(__file__).resolve().parents[1]

class GraphAllocationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with tempfile.TemporaryDirectory() as td:
            exe = str(Path(td)/'graph_faults')
            subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic',
                '-I'+str(ROOT/'docs/tads_C'),str(ROOT/'qa/graph_edge_allocation.c'),
                str(ROOT/'docs/tads_C/tad_grafo.c'),str(ROOT/'docs/tads_C/tad_cola.c'),
                '-Wl,--wrap=malloc','-Wl,--wrap=free','-o',exe],check=True)
            result = subprocess.run([exe],check=True,capture_output=True,text=True)
            cls.native_rows = {(int(a),int(b)):(int(c),int(d)) for a,b,c,d in re.findall(
                r"scenario=(\d+) fault=(\d+) endpoints=1 vertices=(\d+) edges=(\d+)",result.stdout)}
            cls.native_output=result.stdout

    def test_native_faults_and_cleanup(self):
        self.assertEqual(self.native_output.count("result=PASS"),30)
        self.assertEqual(len(self.native_rows),30)

    def test_symbolic_same_faults_preserve_endpoints(self):
        source = (ROOT/'docs/tads_C/tad_grafo.c').read_text()
        snippets = '\n\n'.join(CCodeService._extract_function_with_comment(source,n) for n in
            ['grafo_insertar_vertice','grafo_existe_vertice','grafo_insertar_arco'])
        program = ConstructionProgram(snippets)
        for scenario in range(6):
            for fault in range(5):
                with self.subTest(scenario=scenario,fault=fault):
                    vertices = {0:[],1:[1],2:[2],3:[1,2],4:[],5:[1,2]}[scenario]
                    arcs = [(1,2,3)] if scenario==5 else []
                    machine = ConstructionMachine(program,vertices,arcs,fail_allocation=fault or None)
                    machine.graph = machine.invoke('grafo_insertar_arco',[machine.graph,1,1 if scenario==4 else 2,9])
                    reachable_vertices=set(); p=machine.graph['v']
                    while p != 'NULL':
                        node=machine.heap[p]['fields']; reachable_vertices.add(node['dato']); p=node['sig']
                    edges=[]; p=machine.graph['a']
                    while p != 'NULL':
                        node=machine.heap[p]['fields']; edges.append(node)
                        self.assertIn(node['origen'],reachable_vertices);self.assertIn(node['destino'],reachable_vertices)
                        p=node['sig']
                    self.assertEqual((len(reachable_vertices),len(edges)),self.native_rows[(scenario,fault)])
                    if fault==0:
                        self.assertEqual(len(edges),1); self.assertEqual(edges[0]['costo'],9)

if __name__ == '__main__': unittest.main()
