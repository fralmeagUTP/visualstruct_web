import tempfile,unittest
from app import create_app
from app.config import Config
from app.domain.graph.educational_capacity import MAX_VERTICES
from app.services.graph_help_service import GraphHelpService
class GraphHelpTests(unittest.TestCase):
 def test_rendered_contract_matches_real_limit_and_controls(self):
     """Current graph-book/v1 acceptance; literal prior source is preserved."""
     from qa_convergence._graph_contract_migration import assert_graph_contract_migration
     from pathlib import Path as _MigrationPath
     assert_graph_contract_migration(_MigrationPath(__file__).resolve().parents[1])
     from qa_convergence._graph_current_help_contract import assert_current_graph_help
     assert_current_graph_help(self)
if __name__=='__main__':unittest.main()
