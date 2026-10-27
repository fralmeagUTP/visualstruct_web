"""Actual canonical DFS history, repeated calls and compiled owned-result cleanup."""
import pytest
from _book_traversal_oracle import native_cases
from _canonical_graph_browser_contract import traversal_browser_case
pytestmark=pytest.mark.e2e

@pytest.fixture(scope='module')
def native_dfs_caller(tmp_path_factory):
    return native_cases('dfs',tmp_path_factory.mktemp('dfs-caller-native'))

@pytest.mark.parametrize('case',[1,6,7])
def test_dfs_actual_history_caller(tmp_path,case,native_dfs_caller):
    traversal_browser_case(tmp_path,'dfs',case,native_dfs_caller['rows'][case,0],all_frames=False)
