"""Actual BFS memory, queue, scopes, forward/back and downloaded canonical caller."""
import pytest
from _book_traversal_browser import run_traversal_browser
pytestmark = pytest.mark.e2e


@pytest.mark.parametrize('case', [1, 3, 4, 5, 6, 7, 8, 9])
def test_bfs_actual_browser_views_and_caller(tmp_path, case):
    run_traversal_browser(tmp_path, case, 'bfs')
