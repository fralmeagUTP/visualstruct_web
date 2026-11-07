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
        """Current graph-book/v1 acceptance; literal prior source is preserved."""
        from qa_convergence._graph_contract_migration import assert_graph_contract_migration
        from pathlib import Path as _MigrationPath
        assert_graph_contract_migration(_MigrationPath(__file__).resolve().parents[1])
        from qa_convergence.test_current_graph_edge_allocation import GraphAllocationTests as CurrentContract
        CurrentContract.setUpClass.__func__(cls)

    def test_native_faults_and_cleanup(self):
        """Current graph-book/v1 acceptance; literal prior source is preserved."""
        from qa_convergence._graph_contract_migration import assert_graph_contract_migration
        from pathlib import Path as _MigrationPath
        assert_graph_contract_migration(_MigrationPath(__file__).resolve().parents[1])
        from qa_convergence.test_current_graph_edge_allocation import GraphAllocationTests as CurrentContract
        CurrentContract.test_native_faults_and_cleanup(self)

    def test_symbolic_same_faults_preserve_endpoints(self):
        """Current graph-book/v1 acceptance; literal prior source is preserved."""
        from qa_convergence._graph_contract_migration import assert_graph_contract_migration
        from pathlib import Path as _MigrationPath
        assert_graph_contract_migration(_MigrationPath(__file__).resolve().parents[1])
        from qa_convergence.test_current_graph_edge_allocation import GraphAllocationTests as CurrentContract
        CurrentContract.test_symbolic_same_faults_preserve_endpoints(self)

if __name__ == '__main__': unittest.main()
