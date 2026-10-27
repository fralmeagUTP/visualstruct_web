"""Actual canonical DFS browser frames plus independent native endpoint evidence."""
import pytest
from _book_traversal_oracle import native_cases
from _canonical_graph_browser_contract import traversal_browser_case
pytestmark=pytest.mark.e2e

@pytest.fixture(scope='module')
def native_dfs(tmp_path_factory):
    return native_cases('dfs',tmp_path_factory.mktemp('dfs-browser-native'))

@pytest.mark.parametrize('case',[1,3,4,5,6,7,8,9])
def test_dfs_actual_browser_views_and_caller(tmp_path,case,native_dfs):
    traversal_browser_case(tmp_path,'dfs',case,native_dfs['rows'][case,0])
